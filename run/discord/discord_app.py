import asyncio
import sys
import os
import json

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from creo.bot import MessageBot
from creo.messenger.discord import DiscordMessenger
from creo.llm.llm_openai import LLMClientOpenAI as LLMClient
from creo.session import Session
from creo.data import DataModel

from agent_main import MainAgent
from agent_web import WebAgent

from queue_map import QueueMap

from logging import basicConfig, getLogger, INFO
basicConfig(level=INFO)

logger = getLogger(__name__)

logger_discord = getLogger("discord.gateway")
# silence
logger_discord.setLevel(40)


class DiscordBotApp():
    session: Session = Session.new_session()
    bot: MessageBot
    messenger: DiscordMessenger
    main_agent: MainAgent
    data: DataModel

    qmap: QueueMap = QueueMap()

    def __init__(self):
        self.session = Session.new_session()
        self.messenger = DiscordMessenger(self.receive_user_message)
        self.data = DataModel()
        self.main_agent = MainAgent(
            session = self.session,
            data = self.data,
            publish_message_function = self.publish_message,
            client = LLMClient(self.data, self.session),
            queue_map = self.qmap
        )
        self.web_agent = WebAgent(
            session = self.session,
            data = self.data,
            publish_message_function = self.publish_message,
            client = LLMClient(self.data, self.session),
            queue_map = self.qmap
        )
        self.queue_consumer_map = {
            self.qmap.USER_OUTPUT_QUEUE: self.send_user_message,
            self.qmap.USER_INPUT_QUEUE: self.main_agent.handle_user_message,
            self.qmap.MAIN_INPUT_QUEUE: self.main_agent.handle_main,
            self.qmap.WEB_INPUT_QUEUE: self.web_agent.handle_main,
            self.qmap.WEB_CALLBACK_QUEUE: self.web_agent.handle_callback,
            self.qmap.SEARCH_INPUT_QUEUE: self.mock_handler,
            self.qmap.REQUEST_INPUT_QUEUE: self.mock_handler,
        }
        self.bot = MessageBot(self.queue_consumer_map, user_input_queue=self.qmap.USER_INPUT_QUEUE)

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
        
        await self.bot.publish_to_rabbitmq(message_obj.get("reply_queue"), response )    

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

    async def publish_message(self, queue_name: str, message: str):
        # NOTE: We need to ue this App method in the queue map instead of the bot method directly.
        # This is because the bot instance does not exist when the agents and queue map is created.
        await self.bot.publish_to_rabbitmq(queue_name, message)


    def run(self):
        self.bot.run()
        self.messenger.run()


if __name__ == '__main__':
    DiscordBotApp().run()
