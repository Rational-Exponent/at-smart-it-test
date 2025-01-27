import os
import json
from functools import wraps
from typing import Any
import traceback

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
    envelope: dict = None

    def __init__(self, session: Session, data_model: DataModel, publish_message_function: callable, llm_client: LLMClient, agent_queue: str):
        self.session = session
        self.data = data_model
        self.publish_to_queue = publish_message_function
        self.client = llm_client
        self.agent_queue = agent_queue
        self.reply_queue = agent_queue
        
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
        
    def pack_message(self, content: str, to_queue: str, from_queue: str = None):
        return {
            "from_session": self.session.to_dict(),
            "from_queue": from_queue or self.reply_queue,
            "to_queue": to_queue,
            "content": content
        }
    
    @staticmethod
    def unpack_message(queue_name: str, message: str):
        try:
            # Decode message envelope
            if type(message) is dict:
                message_obj = message
            else:
                message_obj = json.loads(message)

            return message_obj["content"]

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"ERROR ({type(e)}): [{queue_name}] - Could not decode message envelope:  {message}")
            raise e

    @classmethod
    def with_unpacking(cls, method):
        """Decorator that automatically unpacks messages before processing"""
        @wraps(method)
        async def wrapper(self: AgentBase, queue_name: str, message: Any, *args, **kwargs):
            unpacked_message = AgentBase.unpack_message(queue_name, message)
            return await method(self, unpacked_message, *args, **kwargs)
        return wrapper
    
    async def publish_message(self, message: str, to_queue: str, from_queue: str = None):
        """
        Wraps a message in an envelope and publishes it to a queue
        """
        print("\n\n>> publish_message")
        message_obj = self.pack_message(message, to_queue, from_queue)
        await self.publish_to_queue(to_queue, json.dumps(message_obj))

    async def save_message(self, message):
        if isinstance(message, str):
            try:
                message_obj = json.loads(message)
            except json.JSONDecodeError:
                message_obj = dict(role="assistant", content=message)
        elif isinstance(message, dict):
            message_obj = message
        else:
            try:
                message_obj = dict(role="assistant", content=json.dumps(message))
            except json.JSONDecodeError:
                message_obj = dict(role="assistant", content=str(message))

        try:
            # Store new message
            new_message = MessageType(
                session=self.session,
                role=message_obj["role"],
                content=message_obj["content"]
            )
            self.data.messages.add_item(new_message)
        except Exception as e:
            error_details = {
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
            logger.error(f">> agent > save_message: \nmessage: {message}\nerror: {error_details}")
        

    async def handle_user_message(self, input_message):
        raise NotImplementedError
    
    async def handle_main(self, message):
        raise NotImplementedError
