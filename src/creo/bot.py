import os
import dotenv
import asyncio
from aio_pika import connect, Message
import json

from creo.session import Session
from creo.messenger.base import MessengerBase
from creo.llm.llm_client import LLMClient
from creo.manager import Manager

from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)

dotenv.load_dotenv('.env')


QUEUE_USER_INPUT = 'QUEUE_USER_INPUT'

class MessageBot():
    def __init__(self, consumers: dict, user_input_queue=QUEUE_USER_INPUT):
        self.consumers = consumers  # Store the consumers
        self.user_input_queue = user_input_queue

        # self.loop = asyncio.get_event_loop()
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None

        #self.manager = Manager(self.publish_to_rabbitmq, client_cls)

    async def setup(self):
        await self.start_rabbitmq_consumer()

    async def start_rabbitmq_consumer(self):
        self.rabbitmq_connection = await connect(host=os.getenv('RABBITMQ_HOST'))
        self.rabbitmq_channel = await self.rabbitmq_connection.channel()

        # Iterate over the consumer map to set up consumers for each queue
        async def consume_queue(queue_name, consumer):
            queue = await self.rabbitmq_channel.declare_queue(queue_name, durable=True)
            await queue.purge()
            await queue.consume(lambda message: self.on_rabbitmq_message(message, consumer))

        # Create a list of tasks to run for each queue-consumer pair
        tasks = [consume_queue(queue_name, consumer) for queue_name, consumer in self.consumers.items()]
        
        # Gather all the consumer tasks to run them concurrently
        await asyncio.gather(*tasks)

    async def publish_to_rabbitmq(self, routing_key: str, message_content: str, ):
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            await self.setup()
        if type(message_content) is dict:
            message_content = json.dumps(message_content)
        elif type(message_content) is not str:
            message_content = str(message_content)
        message = Message(message_content.encode())
        
        print(f"\n\n>> bot.publish_to_rabbitmq[{routing_key}] {message_content}")
        try:
            await self.rabbitmq_channel.default_exchange.publish(
                message, routing_key=routing_key
            )
        except Exception as e:
            print(f">> ERROR: {e}")
        else:
            print(f"SENT to RabbitMQ: [{routing_key}]: {message_content}\n\n")

    async def on_rabbitmq_message(self, message, consumer):
        print(f"RECEIVED from RabbitMQ: [{message.routing_key}]:\n{message.body.decode()}\n\n")
        async with message.process():
            print(f"handing to process... {consumer}")
            # Use the consumer to process the message
            await consumer(message.routing_key, message.body.decode())

    async def receive_user_message(self, message: str):
        await self.publish_to_rabbitmq(self.user_input_queue, message)

    def run(self):
        # Run the bot
        asyncio.run(self.setup())
