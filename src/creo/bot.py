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
READ_QUEUE_TIMEOUT = 2

class MessageBot():
    def __init__(self, consumers: dict, user_input_queue=QUEUE_USER_INPUT):
        self.consumers = consumers  # Store the consumers
        self.user_input_queue = user_input_queue

        self.loop = asyncio.get_event_loop()
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None

        #self.manager = Manager(self.publish_to_rabbitmq, client_cls)

    async def setup(self):
        
        if not self.rabbitmq_connection or self.rabbitmq_connection.is_closed:
            self.rabbitmq_connection = await connect(host=os.getenv('RABBITMQ_HOST'))
        
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            self.rabbitmq_channel = await self.rabbitmq_connection.channel()

        for queue_name, consumer in self.consumers.items():
            logger.info(f">> SETUP: Setting up queue {queue_name}")
            queue = await self.rabbitmq_channel.declare_queue(queue_name, durable=True)
            await queue.purge()
            # Create background tasks for consumers
            self.loop.create_task(self.start_consumer(queue, consumer))
    
    async def start_consumer(self, queue, consumer):
        await queue.consume(lambda message: self.on_rabbitmq_message(message, consumer))

    async def publish_to_rabbitmq(self, routing_key: str, message_content: str, ):
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            await self.setup()
        if type(message_content) is dict:
            message_content = json.dumps(message_content)
        elif type(message_content) is not str:
            message_content = str(message_content)
        message = Message(message_content.encode())
        
        logger.info(f"\n\n>> bot.publish_to_rabbitmq [{routing_key}] {message_content}")
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

    async def read_queue_messages(self, queue_name):
        """
        Read all messages in an existing RabbitMQ queue
        For non-consumer queues like front end messages
        """
        try:
            await self.setup()
            
            queue = await self.rabbitmq_channel.declare_queue(queue_name, durable=True)
            
            # Use iterator with timeout to prevent blocking indefinitely
            async with queue.iterator(timeout=READ_QUEUE_TIMEOUT) as queue_iter:
                async for message in queue_iter:
                    async with message.process():  # This handles ack/nack automatically
                        print(f"READ from RabbitMQ: [{queue_name}]:\n{message.body.decode()}\n\n")
                        # yield the message
                        yield message.body.decode()  # Or however you want to return the message
                        # delete from queue
                        
                        
        except Exception as e:
            print(f"Error reading from queue {queue_name}: {e}")
            raise e

    def run(self):
        # Run the bot
        self.loop.run_until_complete(self.setup())
