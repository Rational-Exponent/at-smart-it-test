"""
DEPRICATED

Initial test of Streamlit application integration with an Agent platform

ISSUES:
Streamlit app async loop management does not work with running other async process like RabbitMQ
Requires backend API separation for queue management tasks
"""

import asyncio
import sys
import os
import json
import streamlit as st

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from creo.bot import MessageBot
from creo.llm.llm_openai import LLMClientOpenAI as LLMClient
from creo.session import Session
from creo.data import DataModel
from creo.data.mongodb_connection import generate_database

from agent_main import MainAgent
from queue_map import QueueMap
from messenger_streamlit import StreamlitMessenger

from logging import basicConfig, getLogger, INFO
basicConfig(level=INFO)

logger = getLogger(__name__)

logger_discord = getLogger("discord.gateway")
# silence
logger_discord.setLevel(40)


class StreamlitApp():
    session: Session = Session.new_session()
    bot: MessageBot
    messenger: StreamlitMessenger
    main_agent: MainAgent
    data: DataModel

    qmap: QueueMap = QueueMap()

    def __init__(self):
        try:
            self.loop = asyncio.get_event_loop()
        except:
            self.loop = asyncio.new_event_loop()
        finally:
            asyncio.set_event_loop(self.loop)

        self.session = Session.new_session()
        self.messenger = StreamlitMessenger(self.receive_user_message)
        self.data = generate_database()
        # TODO: Move to agent factory
        self.main_agent = MainAgent(
            session = self.session,
            data = self.data,
            publish_message_function = self.publish_message,
            client = LLMClient(self.data, self.session),
            queue_map = self.qmap
        )
        self.queue_consumer_map = {
            self.qmap.USER_OUTPUT_QUEUE: self.send_user_message,
            self.qmap.USER_INPUT_QUEUE: self.main_agent.handle_user_message,
            self.qmap.MAIN_INPUT_QUEUE: self.main_agent.handle_main
        }
        self.bot = MessageBot(self.queue_consumer_map, user_input_queue=self.qmap.USER_INPUT_QUEUE)

    async def setup(self):
        await self.bot.setup()

    def run(self):
        self.loop.run_until_complete(self.setup())
        self.messenger.run()

    async def mock_handler(self, queue, message):
        """
        message: str of json data = {
            "from_session": Session,
            "reply_queue": str,
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
            "reply_queue": queue,
            "content": "NOT IMPLEMENTED"
        }
        
        await self.bot.publish_to_rabbitmq(message_obj.get("reply_queue"), response)

    async def receive_user_message(self, message: str):
        await self.bot.publish_to_rabbitmq(self.qmap.USER_INPUT_QUEUE, message)

    async def send_user_message(self, _, message: str):
        try:
            message_obj = json.loads(message)
            content = message_obj["content"]
            await self.messenger.send_user_message(content)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"ERROR: (APP) - send_user_message - Could not decode message envelope: {message}")
            raise e

    async def publish_message(self, to_queue: str, message: str):
        # NOTE: We need to ue this App method in the queue map instead of the bot method directly.
        # This is because the bot instance does not exist when the agents and queue map is created.
        print("\n\n>> app.publish_message")
        if not to_queue:
            print(f"ERROR: (APP) - publish_message - No destination queue specified: {to_queue}/{message}")
            return
        if not message:
            print(f"ERROR: (APP) - publish_message - No message content specified: {to_queue}/{message}")
            return
        await self.bot.publish_to_rabbitmq(to_queue, message)
    

if __name__ == '__main__':
    if 'app' not in st.session_state:
        logger.info("\n\n>> Creating new app\n\n")
        st.session_state.app = StreamlitApp()
    st.session_state.app.run()
    
