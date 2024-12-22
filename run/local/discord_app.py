import asyncio
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from creo.bot import MessageBot
from creo.messenger.discord import DiscordMessenger
from creo.llm.llm_openai import LLMClientOpenAI as LLMClient
from creo.session import Session
from creo.data import DataModel

from agent_main import MainAgent

from logging import basicConfig, getLogger, INFO
basicConfig(level=INFO)

logger = getLogger(__name__)

logger_discord = getLogger("discord.gateway")
# silence
logger_discord.setLevel(40)

class DiscordBotApp():
    bot: MessageBot
    messenger: DiscordMessenger
    main_agent: MainAgent
    data: DataModel

    USER_INPUT_QUEUE = 'USER_INPUT'
    USER_OUTPUT_QUEUE = 'USER_OUTPUT'

    def __init__(self):
        self.session = Session.new_session()
        self.messenger = DiscordMessenger(self.receive_user_message)
        self.data = DataModel()
        self.main_agent = MainAgent(
            session = self.session,
            data = self.data,
            publish_message_function = self.publish_message,
            client = LLMClient(self.data, self.session),
            user_output_queue = self.USER_OUTPUT_QUEUE
        )
        self.queue_consumer_map = {
            self.USER_OUTPUT_QUEUE: self.messenger.send_user_message,
            self.USER_INPUT_QUEUE: self.main_agent.handle_user_message,
            'MAIN_INPUT': self.main_agent.handle_main,
        }
        self.bot = MessageBot(self.queue_consumer_map, user_input_queue=self.USER_INPUT_QUEUE)


    async def receive_user_message(self, message: str):
        await self.bot.publish_to_rabbitmq(message, self.USER_INPUT_QUEUE)

    async def publish_message(self, message: str, queue_name: str):
        await self.bot.publish_to_rabbitmq(message, queue_name)


    def run(self):
        self.bot.run()
        self.messenger.run()


if __name__ == '__main__':
    DiscordBotApp().run()
