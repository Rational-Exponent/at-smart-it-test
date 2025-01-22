import streamlit as st
import requests

IMAGE_DATA = "data:image/png;base64,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"

class StreamlitApp:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def run(self):
        # UI Elements
        st.image(image=IMAGE_DATA)
        st.title("Opschat test client")
        
        # Input area
        query = st.text_input("What is your query?")
        if query:
            try:
                response = requests.post(
                    f"{self.api_url}/message", 
                    json={"content": query}
                )
                if response.ok:
                    st.session_state.messages.append({"role": "user", "content": query})
            except Exception as e:
                st.error(f"Error sending message: {e}")

        # Display messages
        messages_container = st.container()
        with messages_container:
            for msg in st.session_state.messages:
                role = msg.get("role", "system")
                prefix = "🧑 You: " if role == "user" else "🤖 Bot: "
                st.write(f"{prefix} {msg['content']}")

        # Long polling for new messages
        try:
            response = requests.get(
                f"{self.api_url}/messages",
                timeout=35  # Slightly longer than server timeout
            )
            if response.ok:
                new_messages = response.json().get('messages')
                if new_messages:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": new_messages
                    })
                    st.experimental_rerun()
        except requests.exceptions.Timeout:
            # Expected timeout - just let it refresh
            pass
        except Exception as e:
            print(f"Error polling messages: {e}")

if __name__ == "__main__":
    StreamlitApp().run()