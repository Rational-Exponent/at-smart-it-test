import os, sys
import dotenv
import asyncio
from aio_pika import connect, Message
import json
from typing import Any

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)


#from creo.llm.llm_openai import LLMClientOpenAI as LLMClient
from creo.vision import VisionClientBase
from creo.session import Session
from creo.data import DataModel
from creo.bot import MessageBot

from database import generate_datase

from message_handler import MessageHandler
from queue_map import QueueMap
from agent_main import MainAgent


from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)

dotenv.load_dotenv('.env')


class RetryError(Exception):
    pass


class OpschatQueueManager():
    session: Session = Session.new_session()
    data: DataModel = generate_datase()
    
    que_manager: MessageBot = None
    qmap: QueueMap = QueueMap()
    que_consumer_map: dict = None

    agent_main: MainAgent

    def __init__(self):
        self.messenger = MessageHandler(self.receive_user_message)
        
        self.loop = asyncio.get_event_loop()
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None

        

    async def setup(self):        
        if self.que_manager is None:
            self.agent_main = MainAgent(
                session=self.session,
                data = self.data,
                publish_message_function = self.publish_message,
                queue_map=self.qmap
            )

            self.que_consumer_map = {
                    self.qmap.USER_INPUT_QUEUE: self.receive_user_message,
                    # self.qmap.USER_OUTPUT_QUEUE: None, # Read by API
                    self.qmap.MAIN_INPUT_QUEUE: self.agent_main.handle_main
            }

            self.que_manager = MessageBot(self.que_consumer_map, user_input_queue=self.qmap.USER_INPUT_QUEUE)
            await self.que_manager.setup()
    
    async def publish_message(self, to_queue: str, message: str):
        # NOTE: We need to ue this App method in the queue map instead of the bot method directly.
        # This is because due to the *order of operations*, the queue manager instance does not exist when the agents and queue map is created.
        if not to_queue:
            logger.error(f"ERROR: (APP) - publish_message - No destination queue specified: {to_queue}/{message}")
            return
        if not message:
            logger.error(f"ERROR: (APP) - publish_message - No message content specified: {to_queue}/{message}")
            return
        await self.que_manager.publish_to_rabbitmq(to_queue, message)


    async def mock_handler(self, queue, message):
        """
        Placeholder handler for not implemented queues.
        Sends message back to original queue.

        message: str of json data = {
            "from_session": Session,
            "from_queue": str,
            "to_queue": str,
            "content": str | dict
        }
        """
        try:
            message_obj = json.loads(message)
        except json.JSONDecodeError:
            logger.error(f"ERROR: (APP) - mock_handler - Could not decode message envelope: {message}")
            return

        response = {
            "from_session": self.session.to_dict(),
            "from_queue": queue,
            "to_queue": message_obj.get("from_queue"),
            "content": "NOT IMPLEMENTED"
        }
        
        await self.que_manager.publish_to_rabbitmq(message_obj.get("from_queue"), response)

    async def receive_user_message(self, _, message: str):
        """
        Query pre-processing goes here. Things like guardrails, intent, other feature extraction
        """
        if message.startswith('!'):
            # await self.manager.handle_command(message)
            pass
        else:
            # Pass the message through to the main agent
            await self.que_manager.publish_to_rabbitmq(self.qmap.MAIN_INPUT_QUEUE, dict(role="user", content=message))
            
            # # ECHO the message to output
            # await self.que_manager.publish_to_rabbitmq(self.qmap.USER_OUTPUT_QUEUE, message)

    async def publish_message(self, to_queue: str, message: str):
        # NOTE: We need to ue this class method in the queue map instead of the queue manager method directly.
        # This is because the bot instance does not exist when the agents and queue map is created.
        if not to_queue:
            logger.error(f"ERROR: (APP) - publish_message - No destination queue specified: {to_queue}/{message}")
            return
        if not message:
            logger.error(f"ERROR: (APP) - publish_message - No message content specified: {to_queue}/{message}")
            return
        await self.que_manager.publish_to_rabbitmq(to_queue, message)

    def run(self):
        # Run the bot
        self.loop.run_until_complete(self.setup())

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            logger.info("\n\n>> DONE. Termintedated by user.")


if __name__ == '__main__':
    OpschatQueueManager().run()