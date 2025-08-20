import streamlit as st
import requests

st.set_page_config(page_title="Chatbot", page_icon="🤖")
st.title("🤖 Chatbot")

API_URL = "http://localhost:8000/infer"  # Change to your FastAPI endpoint

if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_chat_response(user_message):
    with requests.post(API_URL, json={"prompt": user_message}, stream=True) as resp:
        resp.raise_for_status()
        for chunk in resp.iter_lines(decode_unicode=True):
            if chunk:
                yield chunk

def send_message():
    st.session_state.messages.append({"role": "user", "content": st.session_state["user_input"]})
    response_placeholder = st.empty()
    bot_response = ""
    for chunk in stream_chat_response(st.session_state["user_input"]):
        bot_response += chunk
        response_placeholder.markdown(f"**Bot:** {bot_response}")
    st.session_state.messages.append({"role": "bot", "content": bot_response})
    st.session_state.user_input = ""

user_input = st.text_input("You:", key="user_input", placeholder="Type your message...")
st.button("Send", on_click=send_message, disabled=not st.session_state["user_input"])

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
