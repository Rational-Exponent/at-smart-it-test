import os, sys
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from creo.bot import MessageBot
from creo.messenger.base import MessengerBase
from creo.agent.agent import AgentBase

from queue_map import QueueMap

from logging import basicConfig, getLogger, INFO
basicConfig(level=INFO)

logger = getLogger(__name__)


class MessageHandler(MessengerBase):
    qmap: QueueMap = QueueMap()

    def __init__(self, message_received_callback=None):
        MessengerBase.__init__(self, message_received_callback)
        
        self.queue_consumer_map = {
            # self.qmap.USER_INPUT_QUEUE: self.handle_received_message,
            # self.qmap.MAIN_INPUT_QUEUE: self.main_agent.handle_main
        }
    
        self.que_manager = MessageBot(self.queue_consumer_map, user_input_queue=self.qmap.USER_INPUT_QUEUE)

    async def receive_user_message(self, message):
        await self.que_manager.publish_to_rabbitmq(self.qmap.USER_INPUT_QUEUE,  {"role":"user", "content": message})
        # # echo to output
        # await self.que_manager.publish_to_rabbitmq(self.qmap.USER_OUTPUT_QUEUE, message)

    async def send_user_message(self, message):
        await self.que_manager.publish_to_rabbitmq(self.qmap.USER_OUTPUT_QUEUE, message)

    async def get_messages_for_user(self):
        async for message in self.que_manager.read_queue_messages(self.qmap.USER_OUTPUT_QUEUE):
            yield AgentBase.unpack_message(None, message)

    async def send_user_image(self, message):
        pass
    
    def run(self):
        pass