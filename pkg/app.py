import streamlit as st
import uuid
import os
from streamlit_chat import message
import openai
from dotenv import load_dotenv
from controller import handle_file_upload, generate_summary, load_history, save_history, add_message, list_data_files, get_file_paths

# Load environment variables from .env.local
load_dotenv(dotenv_path=".env.local")

# Custom CSS to style the app
st.markdown("""
    <style>
    .main-container {
        display: flex;
        flex-direction: row;
        height: 100vh;
    }
    .sidebar {
        background-color: #f0f0f0;
        padding: 20px;
        width: 25%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .chat-container {
        flex-grow: 1;
        padding: 20px;
        display: flex;
        flex-direction: column;
    }
    .document-list {
        list-style-type: none;
        padding: 0;
    }
    .document-list li {
        padding: 5px;
        border-bottom: 1px solid #ddd;
    }
    .chat-bubble {
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 10px;
    }
    .chat-bubble.user {
        background-color: #dcf8c6;
        text-align: right;
    }
    .chat-bubble.bot {
        background-color: #fff;
        text-align: left;
    }
    .chat-header {
        text-align: center;
    }
    .chat-input {
        width: 100%;
        padding: 10px;
        margin-top: 20px;
        box-sizing: border-box;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "documents" not in st.session_state:
    st.session_state.documents = []
if "summaries" not in st.session_state:
    st.session_state.summaries = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_history()
if not isinstance(st.session_state.chat_history, dict):
    st.session_state.chat_history = {}
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = None
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful assistant."
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []

# Sidebar Layout
st.sidebar.title("AI Assistant")

# System Prompt
st.sidebar.header("System Prompt")
st.session_state.system_prompt = st.sidebar.text_area("Set System Prompt", value=st.session_state.system_prompt)

# Conversation History at the top
st.sidebar.header("Conversation History")
if st.sidebar.button("Create New Conversation", key="create_new_conv", help="Click to start a new conversation"):
    new_conversation_id = str(uuid.uuid4())
    st.session_state.chat_history[new_conversation_id] = []
    st.session_state.current_conversation = new_conversation_id
    save_history(st.session_state.chat_history)
    st.experimental_rerun()

if isinstance(st.session_state.chat_history, dict):
    for conv_id in st.session_state.chat_history.keys():
        if st.sidebar.button(f"Load Conversation {conv_id}"):
            st.session_state.current_conversation = conv_id
            st.experimental_rerun()

# Documents at the bottom
st.sidebar.header("Your documents:")
st.session_state.documents = handle_file_upload()

if st.session_state.documents:
    st.sidebar.subheader("Select documents to use in RAG:")
    for index, doc in enumerate(st.session_state.documents):
        checkbox_key = f"checkbox_{index}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = doc["use_in_rag"]
        use_in_rag = st.sidebar.checkbox(doc["name"], value=st.session_state[checkbox_key], key=checkbox_key)
        doc["use_in_rag"] = use_in_rag
        if use_in_rag:
            st.session_state.selected_files.append(doc["name"])
else:
    st.sidebar.write("No documents uploaded.")

# List files in data directory and allow selection
st.sidebar.header("Files in Data Directory")
data_files = list_data_files()
if data_files:
    for file in data_files:
        file_checkbox_key = f"file_checkbox_{file.name}"
        if file_checkbox_key not in st.session_state:
            st.session_state[file_checkbox_key] = False
        use_in_rag = st.sidebar.checkbox(file.name, value=st.session_state[file_checkbox_key], key=file_checkbox_key)
        if use_in_rag and file.name not in st.session_state.selected_files:
            st.session_state.selected_files.append(file.name)
else:
    st.sidebar.write("No files found in data directory.")

# Main section - Chat display
st.markdown("<h2 class='chat-header'>Welcome to the AI Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p class='chat-header'>You can upload documents or ask me something...</p>", unsafe_allow_html=True)

if st.session_state.current_conversation is not None:
    for chat in st.session_state.chat_history[st.session_state.current_conversation]:
        if chat["role"] == "user":
            st.markdown(f"<div class='chat-bubble user'>{chat['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble bot'>{chat['content']}</div>", unsafe_allow_html=True)

    def add_user_message():
        user_input = st.session_state.user_input
        if user_input:
            add_message("user", user_input)
            
            # Get file paths from selected files
            selected_file_paths = get_file_paths(st.session_state.selected_files)
            # Use the system prompt for generating the bot response
            bot_response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=st.session_state.system_prompt + "\nUser: " + user_input + "\nAssistant:",
                max_tokens=150
            ).choices[0].text.strip()
            
            add_message("bot", bot_response)
            st.session_state.user_input = ""

    st.text_input("Type your request...", key="user_input", on_change=add_user_message, placeholder="Type your request here...")
else:
    st.write("Please create or load a conversation to start chatting.")

if st.button("Save Chat History"):
    save_history(st.session_state.chat_history)
