import os
import json

from creo.agent.agent import AgentBase
from creo.llm.llm_aws import LLMClientBedrock as LLMClient
from creo.data import DataModel
from creo.data.types import (
    MessageType
)
from creo.xml import XMLParser
from creo.session import Session
from queue_map import QueueMap

import socket

import logging
logger = logging.getLogger(__name__)

class MainAgent(AgentBase):
    data: DataModel

    def __init__(self, session: Session, data: DataModel, publish_message_function: callable, queue_map: QueueMap):
        super().__init__(session, data, publish_message_function, LLMClient(data,session), queue_map.MAIN_INPUT_QUEUE)
        self.qmap = queue_map

    async def handle_user_message(self, _, input_message):
        print("\n\n>>> handle_user_message")
        await self.handle_main(_, self.pack_message(dict(role="user", content=input_message), self.qmap.USER_OUTPUT_QUEUE))
    
    
    def fuse_history_roles(self, messages):
        if not messages:
            return []
        
        fused = []
        for message in messages:
            if not fused or fused[-1]["role"] != message["role"]:
                # If this is first message or role is different, add as new message
                fused.append(message.copy())  # Make a copy to avoid modifying original
            else:
                # If same role as previous, concatenate content
                fused[-1]["content"] += "\n\n"+ message["content"]
        
        return fused
    

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

        # context = {
        #     "instructions": instructions,
        #     "message-history": [dict(role=m.role, content=m.content) for m in message_history] if message_history else []
        # }
        # input_str = json.dumps(context)
        # response = self.client.get_chat_completion(input_str)

        input_list = [
            dict(role="user", content=instructions),
            dict(role="assistant", content="Waiting for input.")
        ]
        for m in message_history:
            input_list.append(dict(role=m.role, content=m.content))

        input_list = self.fuse_history_roles(input_list)
        response = self.client.get_chat_completion(input_list)

        await self.save_message({"role": "assistant", "content": response})

        await self.publish_message(response, self.qmap.USER_OUTPUT_QUEUE)

        if "<tool-local-ip/>" in response:
            await self.tool_local_ip()


    async def tool_local_ip(self):
        logger.info(">> tool_local_ip ")
        hostname = socket.gethostname()
        response = f"<tool-output>Host info: {hostname}, {socket.gethostbyname(hostname)}</tool-output>"
        
        await self.publish_message(response, self.qmap.MAIN_INPUT_QUEUE, "TOOL-CALL")