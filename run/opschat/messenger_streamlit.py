import streamlit as st
import asyncio

from creo.messenger.base import MessengerBase
from opschat import main

class StreamlitMessenger(MessengerBase):
    def __init__(self, message_received_callback):
        MessengerBase.__init__(self, message_received_callback)
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def send_user_message(self, message):
        st.session_state.messages.append(message)

    async def receive_user_message(self, message):
        await self.message_received_callback(message)

    def send_user_image(self, message):
        return super().send_user_image(message)
    
    def run(self):
        main(self.receive_user_message)