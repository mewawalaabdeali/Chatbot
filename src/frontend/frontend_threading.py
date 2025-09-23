import os, sys
CURRENT_FILE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(CURRENT_FILE), "..", ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
for p in (PROJECT_ROOT, SRC_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)
        
import streamlit as st
from src.backend.langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# **************************************** utility functions *************************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state=chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    #Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

# **************************************** Session Setup ******************************
#session state is a dictionary
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[]

add_thread(st.session_state['thread_id'])

# **************************************** Sidebar UI *********************************


st.sidebar.title('✨ChatBuddy')


if st.sidebar.button('➕ New Chat'):
    reset_chat()

st.sidebar.header('🕰️ History')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages=[]

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'

            temp_messages.append({'role':role, 'content':msg.content})

        st.session_state['message_history'] = temp_messages



# **************************************** Main UI ************************************
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    #first add the message to message history
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # response = chatbot.invoke({'messages':[HumanMessage(content=user_input)]}, config=CONFIG)
    # ai_message = response['messages'][-1].content
    CONFIG = {'configurable':{'thread_id':st.session_state['thread_id']}} 
    with st.chat_message('assistant'):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content


        ai_message = st.write_stream(ai_only_stream())
    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})