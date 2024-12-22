import os
import json

from ..llm.llm_client import LLMClient
from ..data import DataModel
from ..data.types import MessageType
from ..session import Session

import logging
logger = logging.getLogger(__name__)

class AgentBase():
    publish_message: callable
    llm_client : LLMClient
    data: DataModel
    session: Session

    def __init__(self, session: Session, data_model: DataModel, publish_message_function: callable, llm_client: LLMClient):
        self.session = session
        self.data = data_model
        self.publish_message = publish_message_function
        self.client = llm_client
        
    @staticmethod
    def load_file(filename):
        try:
            with open(filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            path = os.path.join(os.path.dirname(__file__), "config", filename)
            with open(path, "r") as file:
                return file.read()
                    

    def publish_message():
        pass

    
    @staticmethod
    def response_from_json(response):
        if response.startswith("```json"):
            response = response[8:-3]
        elif response.startswith("```"):
            response = response[3:-3]
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return response
        

    async def save_message(self, message):
        if type(message) is str:
            try:
                message_obj = json.loads(message)
            except json.JSONDecodeError:
                message_obj = None
        else:
            message_obj = message

        # Store new message
        if message_obj is None or type(message_obj) is str:
            new_message = MessageType(
                thread_id=self.session.thread_id,
                role="user",
                content=message
            )
        else:
            new_message = MessageType(
                thread_id=self.session.thread_id,
                role=message_obj["role"],
                content=message_obj["content"]
            )
        self.data.messages.add_message(new_message)
        

    async def handle_user_message(self, input_message):
        raise NotImplementedError
    
    async def handle_main(self, message):
        raise NotImplementedError