import streamlit as st
from pathlib import Path
from get_llm_response import chatbot_response
import json
import pyperclip


style_file = f"{Path(__file__).parent.absolute().as_posix()}/style.css"
# st.markdown(style_file)

with open(style_file) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


image = "DSI_rgb_120206.jpg"
# st.logo(image, "medium")
st.logo(image)

st.title("BDM Super Search")

# st.title("Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []



# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

# # Display assistant response in chat message container
    result = chatbot_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": result})

# Display chat messages from history on app rerun
message_num = 0
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # if message["role"] == "assistant":
        #     if st.button('copy', key='copy' + str(message_num)):
        #         pyperclip.copy(message["content"])
        st.markdown(message["content"])
    message_num += 1