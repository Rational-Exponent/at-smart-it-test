"""
TEST FILE

First test of building streamlit application
"""
import asyncio

import streamlit as st

AGENT_STAGE_START = "Classification"

def setup():
    if 'setup_complete' not in st.session_state:
        st.session_state.messages = []
        st.session_state.agent_stage = AGENT_STAGE_START
        st.session_state.setup_complete = True

def main(post_message_func):
    setup()

    # Initialize the page
    st.header("Caution: Experimental AI ahead!")

    query = st.text_input("What is your query?")
    if query:
        if post_message_func:
            asyncio.run(post_message_func(query))
        st.session_state.messages.append(query)
    
    if st.session_state.messages:
        for idx, q in enumerate(st.session_state.messages):
            st.write(f"{idx + 1}. {q}")


if __name__ == "__main__":
    main(None)