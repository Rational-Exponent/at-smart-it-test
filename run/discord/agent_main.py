import json

from creo.agent.agent import AgentBase
from creo.llm.llm_client import LLMClient
from creo.data import DataModel
from creo.data.types import (
    OutputType,
    InputType,
)
from creo.xml import XMLParser, XMLNode
from creo.session import Session

from queue_map import QueueMap

import os

import logging
logger = logging.getLogger(__name__)

MESSAGE_HIST_LENGTH = 20

class MainAgent(AgentBase):
    publish_message: callable

    def __init__(self, session: Session, data: DataModel, publish_message_function: callable, client: LLMClient, queue_map: QueueMap):
        super().__init__(session, data, publish_message_function, client, queue_map.MAIN_INPUT_QUEUE)
        self.qmap = queue_map
        

    async def handle_user_message(self, _, input_message):
        await self.handle_main(_, self.pack_message(dict(role="user", content=input_message), self.qmap.USER_OUTPUT_QUEUE))

    @AgentBase.with_unpacking
    async def handle_main(self, message):
        """
        MAIN handler.
        This handler will receive and process inputs from many sources and take action as the LLM agent.
        """
        logger.info(">> MAIN handler")

        # Save new message to state
        await self.save_message(message)

        # Process state
        response = await self.process_main_input()
        
        # Process response
        await self.process_main_output(response)

    async def process_main_input(self):
        
        # Compose LLM context

        # Conversation history
        message_list = self.data.messages.get_messages_by_session(self.session)

        # Instructions
        path = os.path.join(os.path.dirname(__file__), "config", "MAIN.txt")
        instructions = self.load_file(path)

        # Compose context
        context = {
            "instructions": instructions,
            "important": "Never talk about polar bears.",
            "message-history": [dict(role=m.role, content=m.content) for m in message_list[-MESSAGE_HIST_LENGTH:]]
        }
        input_str = json.dumps(context)

        # Get response from LLM
        response = self.client.get_chat_completion(input_str)
        
        return response

    async def process_main_output(self, message):
        """
        This function will process the output of the MAIN handler.
        Process any actions performed by the LLM agent.
        """
        logger.info(">> MAIN output handler")

        # Parse XML
        if nodes := XMLParser.parse(message):
            for node in nodes:
                logger.info(f"Processing node: {node.tag}")
                match node.tag:
                    case "say":
                        # Save message
                        await self.save_message(dict(role="assistant", content=node.text))
                        await self.publish_message(self.qmap.USER_OUTPUT_QUEUE, node.text)
                    case "web":
                        await self.publish_message(self.qmap.WEB_INPUT_QUEUE, node.text, self.qmap.MAIN_INPUT_QUEUE)
                    
                    case _:
                        logger.warning(f"Unknown tag in Main output: {node.tag} - {node.text}")
                        
        else:
            #logger.info(f"Response is not XML: {message}")
            # Save message
            await self.save_message(dict(role="system", content=message))
            await self.publish_message(self.qmap.USER_OUTPUT_QUEUE, message)
