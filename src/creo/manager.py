from typing import Callable, Optional
import json
import uuid
import asyncio

from .data import DataModel
from .data.types import (
    OutputType,
)
from .llm.llm_client import LLMClient
from .agent.agent_main import MainAgent
from .session import Session

from logging import getLogger
logger = getLogger(__name__)


class Manager():
    data: DataModel
    publish_to_rabbitmq: Callable
    client: LLMClient
    agent: MainAgent

    def __init__(self, publish_to_rabbitmq: Callable, client_class: LLMClient):
        self.data = DataModel()
        self.publish_message = publish_to_rabbitmq
        self.session = self.new_session()
        self.client = client_class(self.data, self.session)
        self.agent = MainAgent(self.data, self.session.thread_id, self.publish_message, self.client)

    def new_session(self)->Session:
        return Session(str(uuid.uuid4()), str(uuid.uuid4()))
    
    async def handle_user_message(self, message):
        await self.agent.handle_user_message(message)

    async def handle_main(self, message):
        await self.agent.handle_main(message)
