import os
import json
from functools import wraps
from typing import Any

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
    agent_queue: str = None
    reply_queue: str = None

    def __init__(self, session: Session, data_model: DataModel, publish_message_function: callable, llm_client: LLMClient, agent_queue: str):
        self.session = session
        self.data = data_model
        self.publish_to_queue = publish_message_function
        self.client = llm_client
        self.agent_queue = agent_queue
        self.reply_queue = None
        
    @staticmethod
    def load_file(filename):
        try:
            with open(filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            path = os.path.join(os.path.dirname(__file__), "config", filename)
            with open(path, "r") as file:
                return file.read()

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
        
    def pack_message(self, content: str, reply_queue: str = None):
        return {
            "from_session": self.session.to_dict(),
            "reply_queue": reply_queue or self.reply_queue,
            "content": content
        }
    
    def unpack_message(self, queue_name: str, message: str):
        try:
            # Decode message envelope
            if type(message) is dict:
                message_obj = message
            else:
                message_obj = json.loads(message)

            # Extract header details
            self.session = Session(
                message_obj["from_session"]["session_id"], 
                message_obj["from_session"]["thread_id"]
            )
            self.reply_queue = message_obj["reply_queue"]

            # Extract message content
            message = message_obj["content"]

            return message

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"ERROR ({type(e)}): [{queue_name}] - Could not decode message envelope:  {message}")
            raise e

    @classmethod
    def with_unpacking(cls, method):
        """Decorator that automatically unpacks messages before processing"""
        @wraps(method)
        async def wrapper(self: AgentBase, queue_name: str, message: Any, *args, **kwargs):
            unpacked_message = self.unpack_message(queue_name, message)
            return await method(self, unpacked_message, *args, **kwargs)
        return wrapper
    
    async def publish_message(self, queue_name: str, message: str, reply_queue: str = None):
        """
        Wraps a message in an envelope and publishes it to a queue
        """
        message_obj = self.pack_message(message, reply_queue)
        await self.publish_to_queue(queue_name, json.dumps(message_obj)) 

    async def save_message(self, message):
        if type(message) is str:
            try:
                message_obj = json.loads(message)
            except json.JSONDecodeError:
                message_obj = dict(role="system", content=message)
        elif type(message) is dict:
            message_obj = message
        else:
            message_obj = dict(role="system", content=json.dumps(message))

        # Store new message
        if message_obj is None or type(message_obj) is str:
            new_message = MessageType(
                session_id=self.session.session_id,
                thread_id=self.session.thread_id,
                role="user",
                content=message
            )
        else:
            new_message = MessageType(
                session_id=self.session.session_id,
                thread_id=self.session.thread_id,
                role=message_obj["role"],
                content=message_obj["content"]
            )
        self.data.messages.add_message(new_message)
        

    async def handle_user_message(self, input_message):
        raise NotImplementedError
    
    async def handle_main(self, message):
        raise NotImplementedError
