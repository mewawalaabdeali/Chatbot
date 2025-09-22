import os, sys
CURRENT_FILE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(CURRENT_FILE), "..", ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
for p in (PROJECT_ROOT, SRC_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)
import streamlit as st
from src.backend.langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import os,sys

#session state is a dictionary
CONFIG = {'configurable':{'thread_id':'thread-1'}}
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]


for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    #first add the message to message history
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    response = chatbot.invoke({'messages':[HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message = response['messages'][-1].content
    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)