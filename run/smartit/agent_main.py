import os

from creo.agent.agent import AgentBase
from creo.llm.llm_client import LLMClient
from creo.data import DataModel
from creo.data.types import (
    NoteType,
)
from creo.xml import XMLParser
from creo.session import Session
from queue_map import QueueMap

import streamlit as st

import logging
logger = logging.getLogger(__name__)

class MainAgent(AgentBase):
    data: DataModel

    def __init__(self, session: Session, data: DataModel, publish_message_function: callable, client: LLMClient, queue_map: QueueMap):
        super().__init__(session, data, publish_message_function, client, queue_map.MAIN_INPUT_QUEUE)
        self.qmap = queue_map

    async def handle_user_message(self, _, input_message):
        print("\n\n>>> handle_user_message")
        await self.handle_main(_, self.pack_message(dict(role="user", content=input_message), self.qmap.USER_OUTPUT_QUEUE))
    
    @AgentBase.with_unpacking
    async def handle_main(self, message):
        """
        MAIN handler.
        This handler will receive and process inputs from many sources and take action as the LLM agent.
        """
        print(">> MAIN handler")

        # # Instructions
        # path = os.path.join(os.path.dirname(__file__), "config", "MAIN.txt")
        # instructions = self.load_file(path)

        # # Stage
        # stage = st.session_state.agent_stage

        await self.publish_message("MOCK-OUTPUT", self.qmap.USER_OUTPUT_QUEUE)

