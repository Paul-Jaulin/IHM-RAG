import streamlit as st
import time
import json
import uuid
import os
from streamlit_chat import message
import openai

# Initialize OpenAI API (replace 'your_openai_api_key_here' with your actual API key)
openai_api_key = "your_openai_api_key_here"
openai.api_key = openai_api_key


# Function to handle file upload and display document list with a progress bar
def handle_file_upload():
    uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True)
    if uploaded_files and not st.session_state.get("uploaded"):
        st.session_state.uploaded = True
        progress_window = st.empty()
        progress_bar = st.progress(0)

        num_files = len(uploaded_files)
        for i, uploaded_file in enumerate(uploaded_files):
            st.session_state.documents.append({
                "id": str(uuid.uuid4()),  # Generate unique ID for each document
                "name": uploaded_file.name,
                "file": uploaded_file,
                "use_in_rag": True
            })
            progress_window.text(f"Uploading {uploaded_file.name}...")
            progress_bar.progress((i + 1) / num_files)
            time.sleep(1)  # Simulate upload time

            # Generate and display summary for each document
            summary = generate_summary(uploaded_file)
            st.session_state.summaries.append({
                "name": uploaded_file.name,
                "summary": summary
            })

        progress_window.empty()
        progress_bar.empty()


# Function to generate summary using OpenAI API
def generate_summary(file):
    # For illustration, using a dummy summary. Replace this with actual OpenAI API call
    return f"Summary of {file.name}"


# Function to load conversation history from JSON file
def load_history(file_path='chat_history.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}


# Function to save conversation history to JSON file
def save_history(history, file_path='chat_history.json'):
    with open(file_path, 'w') as file:
        json.dump(history, file)


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


# Function to add message to session state and update JSON file
def add_message(role, content):
    message = {
        "id": str(uuid.uuid4()),  # Generate unique ID
        "role": role,
        "content": content
    }
    if st.session_state.current_conversation is not None:
        st.session_state.chat_history[st.session_state.current_conversation].append(message)
        save_history(st.session_state.chat_history)


# Sidebar - Document list and upload button
st.sidebar.title("AI Assistant")
st.sidebar.header("Your documents:")
handle_file_upload()

if st.session_state.documents:
    st.sidebar.subheader("Select documents to use in RAG:")
    for index, doc in enumerate(st.session_state.documents):
        checkbox_key = f"checkbox_{index}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = doc["use_in_rag"]
        use_in_rag = st.sidebar.checkbox(doc["name"], value=st.session_state[checkbox_key], key=checkbox_key)
        doc["use_in_rag"] = use_in_rag
else:
    st.sidebar.write("No documents uploaded.")

# Main section - Create new conversation button
st.markdown("<h2 style='text-align: center;'>Welcome to the AI Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>You can upload documents or ask me something...</p>",
            unsafe_allow_html=True)

if st.button("Create New Conversation", key="create_new_conv", help="Click to start a new conversation"):
    new_conversation_id = str(uuid.uuid4())
    st.session_state.chat_history[new_conversation_id] = []
    st.session_state.current_conversation = new_conversation_id
    save_history(st.session_state.chat_history)
    st.experimental_rerun()

# Sidebar - Past conversation history (right sidebar)
st.sidebar.title("Conversation History", anchor="end")

if isinstance(st.session_state.chat_history, dict):
    for conv_id in st.session_state.chat_history.keys():
        if st.sidebar.button(f"Load Conversation {conv_id}"):
            st.session_state.current_conversation = conv_id
            st.experimental_rerun()

# Main section - Chat display
if st.session_state.current_conversation is not None:
    # Display chat history
    for chat in st.session_state.chat_history[st.session_state.current_conversation]:
        if chat["role"] == "user":
            message(chat["content"], is_user=True, key=chat["id"])
        else:
            message(chat["content"], key=chat["id"])


    # Main section - User input for new message
    def add_user_message():
        user_input = st.session_state.user_input
        if user_input:
            add_message("user", user_input)

            # Placeholder AI response generation (replace this with actual RAG service call)
            bot_response = f"AI Response to: {user_input}"
            add_message("bot", bot_response)

            # Clear the input box
            st.session_state.user_input = ""


    st.text_input("Type your request...", key="user_input", on_change=add_user_message)
else:
    st.write("Please create or load a conversation to start chatting.")

# Save updated history when the app closes
if st.button("Save Chat History"):
    save_history(st.session_state.chat_history)