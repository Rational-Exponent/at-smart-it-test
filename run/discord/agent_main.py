import json

from creo.agent.agent import AgentBase
from creo.llm.llm_client import LLMClient
from creo.data import DataModel
from creo.data.types import (
    OutputType,
    InputType,
    NoteType,
)
from creo.xml import XMLParser, XMLNode
from creo.session import Session

from queue_map import QueueMap

import os

import logging
logger = logging.getLogger(__name__)

MESSAGE_HIST_LENGTH = 20

class MainAgent(AgentBase):

    def __init__(self, session: Session, data: DataModel, publish_message_function: callable, client: LLMClient, queue_map: QueueMap):
        super().__init__(session, data, publish_message_function, client, queue_map.MAIN_INPUT_QUEUE)
        self.qmap = queue_map
        

    async def handle_user_message(self, _, input_message):
        logger.info(">> MAIN - handle user message")
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

        # Notes
        notes = self.data.notes.get_notes_by_session(self.session)

        # Compose context
        context = {
            "instructions": instructions,
            "important": "Never talk about polar bears.",
            "notes": [dict(id=n.id, content=n.content) for n in notes],
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
                        await self.publish_message(node.text, self.qmap.USER_OUTPUT_QUEUE)
                    case "web":
                        await self.publish_message(node.text, self.qmap.WEB_INPUT_QUEUE )
                    case "notes":
                        await self.publish_message(f"tool[agent notes] <agent is taking notes>", self.qmap.USER_OUTPUT_QUEUE)
                        await self.publish_message(node.text, self.qmap.NOTES_QUEUE)
                    case _:
                        logger.warning(f"Unknown tag in Main output: {node.tag} - {node.text}")
        else:
            #logger.info(f"Response is not XML: {message}")
            # Save message
            await self.save_message(dict(role="system", content=message))
            await self.publish_message(message, self.qmap.USER_OUTPUT_QUEUE)


    @AgentBase.with_unpacking
    async def handle_notes(self, message):
        """
        This handler process a message to add or remove a note from memory.
        message: str of json data = {
            "content": str,
            "delete_id": str | None
        }
        """
        logger.info(">> NOTES handler")

        message_obj = json.loads(message)

        if delete_id := message_obj.get("delete_id"):
            self.data.notes.delete_note(delete_id)
            await self.publish_message(f"tool[agent notes] <Note deleted: {delete_id}>", self.qmap.USER_OUTPUT_QUEUE)
            await self.publish_message(f"tool[agent notes] <Note deleted: {delete_id}>", self.qmap.MAIN_INPUT_QUEUE)
        else:
            note_id = self.data.notes.add_note(NoteType(
                session_id=self.session.session_id,
                thread_id=self.session.thread_id,
                content=message_obj["content"]
            ))
            await self.publish_message(f"tool[agent notes] <Note added: {note_id}>", self.qmap.USER_OUTPUT_QUEUE)
            await self.publish_message(f"tool[agent notes] <Note added: {note_id}>", self.qmap.MAIN_INPUT_QUEUE)

        