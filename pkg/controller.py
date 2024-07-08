import json
import uuid
import os
import time
from typing import List, Dict
import streamlit as st
from pathlib import Path
from advanced_chatbot.services.rag_service import RagService
from advanced_chatbot.config import DATA_PATH
from llama_index_client import ChatMessage

def handle_file_upload() -> List[Dict]:
    """
    Handle file upload and display document list with a progress bar.
    """
    uploaded_files = st.sidebar.file_uploader("Upload documents", accept_multiple_files=True)
    documents = []
    if uploaded_files and not st.session_state.get("uploaded"):
        st.session_state.uploaded = True
        progress_window = st.empty()
        progress_bar = st.sidebar.progress(0)

        num_files = len(uploaded_files)
        for i, uploaded_file in enumerate(uploaded_files):
            file_path = DATA_PATH / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            documents.append({
                "id": str(uuid.uuid4()),  # Generate unique ID for each document
                "name": uploaded_file.name,
                "path": str(file_path),
                "use_in_rag": True
            })
            progress_window.text(f"Uploading {uploaded_file.name}...")
            progress_bar.progress((i + 1) / num_files)
            time.sleep(1)  # Simulate upload time

        progress_window.empty()
        progress_bar.empty()
    return documents

def load_history(file_path='chat_history.json') -> Dict:
    """
    Load conversation history from JSON file.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def save_history(history: Dict, file_path='chat_history.json'):
    """
    Save conversation history to JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(history, file)

def add_message(role: str, content: str):
    """
    Add message to session state and update JSON file.
    """
    message = {
        "id": str(uuid.uuid4()),  # Generate unique ID
        "role": role,
        "content": content
    }
    if st.session_state.current_conversation is not None:
        st.session_state.chat_history[st.session_state.current_conversation].append(message)
        save_history(st.session_state.chat_history)

def list_data_files() -> List[str]:
    """
    List all files in the data directory.
    """
    return [str(f) for f in DATA_PATH.glob('*') if f.is_file()]

def get_file_paths(selected_files: List[str]) -> List[str]:
    """
    Get the file paths from the selected files.
    """
    file_paths = []
    for file in selected_files:
        file_path = DATA_PATH / file
        if file_path.exists():
            file_paths.append(str(file_path))
    return file_paths

def create_index_for_files(files: List[str]) -> List[str]:
    """
    Create indexes for the selected files.
    """
    index_ids = []
    for file in files:
        index_id, _ = RagService.create_vector_store_index(Path(file))
        index_ids.append(index_id)
    return index_ids

def get_bot_response(user_input: str, selected_files: List[str], system_prompt: str) -> str:
    """
    Get bot response using RAG service.
    """
    if not selected_files:
        return "No documents selected for retrieval."

    index_ids = create_index_for_files(selected_files)
    if not index_ids:
        return "Failed to create indexes for the selected documents."

    conversation_history = [ChatMessage(role="user", content=user_input)]
    response_gen, _ = RagService.complete_chat(
        query=user_input,
        conversation_history=conversation_history,
        index_ids=index_ids,
        system_prompt=system_prompt
    )
    response = "".join(list(response_gen))
    return response
