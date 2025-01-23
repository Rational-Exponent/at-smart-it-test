import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from creo.bot import MessageBot, QUEUE_USER_INPUT
from creo.session import Session
from creo.data import DataModel
from creo.data.mongodb_connection import generate_database
from creo.llm.llm_openai import LLMClientOpenAI as LLMClient

from agent_main import MainAgent

from logging import basicConfig, getLogger, INFO
basicConfig(level=INFO)

logger = getLogger(__name__)

class QueueMap():
    USER_INPUT_QUEUE = 'USER_INPUT_QUEUE'   # Recieve from user. API post. handle_received_message
    USER_OUTPUT_QUEUE = 'USER_OUTPUT_QUEUE' # Send to user. API polling. get_messages_for_user
    MAIN_INPUT_QUEUE = 'MAIN_INPUT_QUEUE'   # Send to main agent

class MessageHandler:
    qmap: QueueMap = QueueMap()

    def __init__(self):

        self.queue_consumer_map = {
            # self.qmap.USER_INPUT_QUEUE: self.handle_received_message,
            # self.qmap.MAIN_INPUT_QUEUE: self.main_agent.handle_main
        }
    
        self.bot = MessageBot(self.queue_consumer_map, user_input_queue=self.qmap.USER_INPUT_QUEUE)

    async def handle_received_message(self, message):
        #await self.bot.publish_to_rabbitmq(self.qmap.USER_INPUT_QUEUE, message)
        # echo to output
        await self.bot.publish_to_rabbitmq(self.qmap.USER_OUTPUT_QUEUE, message)

    async def get_messages_for_user(self):
        async for message in self.bot.read_queue_messages(self.qmap.USER_OUTPUT_QUEUE):
            yield message

    async def publish_message(self, to_queue: str, message: str):
        # NOTE: We need to ue this App method in the queue map instead of the bot method directly.
        # This is because the bot instance does not exist when the agents and queue map is created.
        if not to_queue:
            logger.error(f"ERROR: (APP) - publish_message - No destination queue specified: {to_queue}/{message}")
            return
        if not message:
            logger.error(f"ERROR: (APP) - publish_message - No message content specified: {to_queue}/{message}")
            return
        await self.bot.publish_to_rabbitmq(to_queue, message)