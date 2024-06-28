import streamlit as st
import time
from streamlit_chat import message
import openai

# Initialize OpenAI API (replace 'your_openai_api_key_here' with your actual API key)
openai_api_key = "your_openai_api_key_here"
openai.api_key = openai_api_key

# Function to handle file upload and display document list with a progress bar
def handle_file_upload():
    uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True)
    if uploaded_files:
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = []

        st.session_state.uploaded_files = uploaded_files

        if "documents" not in st.session_state:
            st.session_state.documents = []
        if "summaries" not in st.session_state:
            st.session_state.summaries = []
        if "uploaded" not in st.session_state:
            st.session_state.uploaded = []

        progress_window = st.empty()
        progress_bar = st.progress(0)
        
        num_files = len(uploaded_files)
        for i, uploaded_file in enumerate(uploaded_files):
            if uploaded_file.name not in st.session_state.uploaded:
                st.session_state.documents.append({
                    "name": uploaded_file.name,
                    "file": uploaded_file,
                    "use_in_rag": True
                })
                st.session_state.uploaded.append(uploaded_file.name)
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

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "documents" not in st.session_state:
    st.session_state.documents = []
if "summaries" not in st.session_state:
    st.session_state.summaries = []
if "uploaded" not in st.session_state:
    st.session_state.uploaded = []

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

# Display document summaries
if st.session_state.summaries:
    st.sidebar.header("Document Summaries:")
    for summary in st.session_state.summaries:
        st.sidebar.write(f"**{summary['name']}**: {summary['summary']}")

# Sidebar - Past conversation history (for illustration, this section is static in this example)
st.sidebar.header("Conversation History")
st.sidebar.write("Increase Sales Strategy")
st.sidebar.write("IHM and AI")
st.sidebar.write("Weather Tomorrow")
st.sidebar.write("Persona Identification")
st.sidebar.write("Sales Forecast")
st.sidebar.write("How to Code a RAG?")

# Main section - Chat display
st.title("AI Assistant")
st.write("Welcome to the AI Assistant. You can upload documents or ask me something...")

# Display chat history
for chat in st.session_state.chat_history:
    if chat["sender"] == "user":
        message(chat["message"], is_user=True)
    else:
        message(chat["message"])

# Main section - User input for new message
def add_user_message():
    st.session_state.chat_history.append({"sender": "user", "message": st.session_state.user_input})

st.text_input("Type your request...", key="user_input", on_change=add_user_message)

# Placeholder AI response generation (for illustration, echoing user's message)
if st.session_state.chat_history and st.session_state.chat_history[-1]["sender"] == "user":
    last_user_message = st.session_state.chat_history[-1]["message"]
    st.session_state.chat_history.append({"sender": "ai", "message": f"AI Response to: {last_user_message}"})
