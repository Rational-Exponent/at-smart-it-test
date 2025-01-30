import os
import json
import asyncio
import re
from datetime import datetime

from creo.agent.agent import AgentBase
from creo.llm.llm_aws import LLMClientBedrock as LLMClient
from creo.data import DataModel
from creo.data.types import (
    MessageType
)
from creo.xml import XMLParser
from creo.session import Session
from queue_map import QueueMap

from tool_quadrant import tool_query_program_logs

import socket

import logging
logger = logging.getLogger(__name__)

class MainAgent(AgentBase):
    data: DataModel

    def __init__(self, session: Session, data: DataModel, publish_message_function: callable, queue_map: QueueMap):
        super().__init__(session, data, publish_message_function, LLMClient(data,session), queue_map.MAIN_INPUT_QUEUE)
        self.qmap = queue_map
        self.register_tools([
            self.tool_local_ip,
            self.tool_system_time,
            self.handle_query_program_logs
        ])


    @AgentBase.with_unpacking
    async def handle_main(self, message):
        """
        MAIN handler.
        This handler will receive and process inputs from many sources and take action as the LLM agent.
        """
        print(">> MAIN handler")

        # TODO: State management

        # Instructions
        path = os.path.join(os.path.dirname(__file__), "config", "MAIN.txt")
        instructions = self.load_file(path)

        # Message History
        await self.save_message(message)
        message_history = self.data.messages.get_items_by_session(self.session)

        # Tool belt
        tools = self.get_tool_prompt()
        
        context = {
            "instructions": instructions,
            "tools": tools,
            "system-time": str(datetime.now()),
            "important": "Never include <tool-output> tags in your response text."
        }

        # context = {
        #     "instructions": instructions,
        #     "message-history": [dict(role=m.role, content=m.content) for m in message_history] if message_history else []
        # }
        input_str = json.dumps(context)
        # response = self.client.get_chat_completion(input_str)

        context = [
            f"# Instructions\n{instructions}",
            f"# Tools\n{tools}",
            f"# System Information\n## system time: 2024-07-04T11:16:52.644950", # {str(datetime.now())}",
        ]
        input_str = '\n\n'.join(context)
        

        input_list = [
            dict(role="user", content=input_str),
            dict(role="assistant", content="Waiting for input.")
        ]
        for m in message_history:
            input_list.append(dict(role=m.role, content=m.content))

        input_list = self.fuse_history_roles(input_list)
        response = self.client.get_chat_completion(input_list)

        await self.save_message({"role": "assistant", "content": response})

        # Send copy to user
        await self.publish_message(response, self.qmap.USER_OUTPUT_QUEUE)

        # Process all tool calls
        error = await self.handle_tool_calling(response)

        if error:
            await self.publish_message(error, self.qmap.MAIN_INPUT_QUEUE)


    async def tool_local_ip(self):
        """
        Retrieves the local system host name and IP address
        """
        logger.info(">> tool_local_ip ")
        hostname = socket.gethostname()
        response = f"<tool-output>Host info: {hostname}, {socket.gethostbyname(hostname)}</tool-output>"
        await self.publish_message(dict(role="user", content=response), self.qmap.MAIN_INPUT_QUEUE, "TOOL-CALL")


    async def tool_system_time(self):
        """
        Retrieves the local system time
        """
        logger.info(">> tool_system_time")
        from datetime import datetime
        response = f"<tool-output>System time: {str(datetime.now())}</tool-output>"
        await self.publish_message(dict(role="user", content=response), self.qmap.MAIN_INPUT_QUEUE, "TOOL-CALL")


    async def handle_query_program_logs(self,**kwargs):
        """
        This tool will query program log entries based on the provided application details and date periods.
        The following must always be provided to limit the scope of the logs:
            begin_date,
            end_date,
            prompt 
        The following are additional filters that can be added to reduce the scope of the logs:
            application: name of application, 
            ip: ip address of server,
            change_id: related change_id
        """
        logger.info(">> agent.handle_query_program_logs")
        
        result = await tool_query_program_logs(**kwargs)
        await self.publish_message(dict(role="user", content=result), self.qmap.MAIN_INPUT_QUEUE, "TOOL-CALL")
        