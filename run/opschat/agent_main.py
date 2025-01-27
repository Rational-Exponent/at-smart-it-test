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

        context = {
            "instructions": instructions,
            "message-history": [m.to_dict() for m in message_history] if message_history else []
        }
        input_str = json.dumps(context)
        response = self.client.get_chat_completion(input_str)

        await self.publish_message(response, self.qmap.USER_OUTPUT_QUEUE)

        if "<tool_ip>" in response:
            await self.tool_ip()


    async def tool_ip(self):
        hostname = socket.gethostname()
        response = f"Host info: {hostname}, {socket.gethostbyname(hostname)}"
        
        await self.publish_message(response, self.qmap.MAIN_INPUT_QUEUE, "TOOL-CALL")