import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage,AIMessage

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

def load_conversation():
    val = chatbot.get_state(config=CONFIG).values
    if 'messages' in val:
        return val['messages']
    return []

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    msgs=load_conversation()
    for msg in msgs:
        if isinstance(msg, HumanMessage):
            st.session_state['message_history'].append({'role': 'user', 'content': msg.content})
        elif isinstance(msg, AIMessage) and msg.content.strip() != "":
            st.session_state['message_history'].append({'role': 'assistant', 'content': msg.content})

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')
if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message = response['messages'][-1].content
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)