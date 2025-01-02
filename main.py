import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import json
import pandas as pd
import fitz  # PyMuPDF
from docx import Document
import yaml

# App title and page setup
st.set_page_config(page_title="G/D Chatbot", layout="centered")
page = "GENERAL CHATBOT"
st.title("Welcome to My App!")

# Radio button for selecting chatbot type
page = st.sidebar.radio("Choose Type", ["GENERAL CHATBOT", "DOCUMENT CHATBOT"])

# Load API key from config file
with open('config.yaml') as config_file:
    config = yaml.safe_load(config_file)

os.environ["GOOGLE_API_KEY"] = config["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    convert_system_message_to_human=True
)

# Define CSS for consistent chat styling
st.markdown("""
    <style>
    .user-container, .bot-container { display: flex; margin-bottom: 10px; }
    .user-container { justify-content: flex-end; }
    .bot-container { justify-content: flex-start; }
    .user-message, .bot-message { padding: 10px 15px; border-radius: 15px; max-width: 80%; word-wrap: break-word; font-size: 16px; }
    .user-message { background-color: #007bff; color: white; }
    .bot-message { background-color: #f1f0f0; color: black; }
    .avatar { width: 40px; height: 40px; border-radius: 50%; margin: 0 10px; }
    .send-button { background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 10px; cursor: pointer; }
    </style>
""", unsafe_allow_html=True)

# Main chatbot function for general conversations
def general_chatbot():
    system_message = "You are a helpful assistant for general purpose created by Sahil Umar gmail sonuarain46@gmail.com and linkedin www.linkedin.com/in/sonu-arain-ab705930b. Keep responses concise."
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    prompt = st.chat_input("Say something", key="unique_chat_input_key")

    if prompt:
        messages = [SystemMessage(content=system_message)]
        recent_conversations = st.session_state.conversation_history[-5:]
        
        for item in recent_conversations:
            messages.append(HumanMessage(content=item['input']))
            messages.append(HumanMessage(content=item['response']))
        messages.append(HumanMessage(content=prompt))

        ai_msg = llm.invoke(messages)
        response = ai_msg.content.strip()[:500]

        st.session_state.conversation_history.append({
            'input': prompt,
            'response': response
        })

    # Display conversation history
    for chat in st.session_state.conversation_history:
        st.markdown(f'''
            <div class="user-container">
                <div class="user-message">{chat["input"]}</div>
                <img src="https://th.bing.com/th/id/R.6b0022312d41080436c52da571d5c697?rik=ejx13G9ZroRrcg&riu=http%3a%2f%2fpluspng.com%2fimg-png%2fuser-png-icon-young-user-icon-2400.png&ehk=NNF6zZUBr0n5i%2fx0Bh3AMRDRDrzslPXB0ANabkkPyv0%3d&risl=&pid=ImgRaw&r=0" class="avatar"/>
            </div>
            <div class="bot-container">
                <img src="https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2023/10/13075034/sl-blue-chat-bot-scaled.jpg" class="avatar"/>
                <div class="bot-message">{chat["response"]}</div>
            </div>
        ''', unsafe_allow_html=True)

# Document chatbot function for handling document-based interactions


def document_chatbot():
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'pdf', 'docx'}

    # Move file upload to sidebar
    uploaded_file = st.sidebar.file_uploader("Upload a document", type=list(ALLOWED_EXTENSIONS))
    file_content = ""

    # Read file and store content
    if uploaded_file:
        def read_file(file):
            ext = os.path.splitext(file.name)[1].lower()
            if ext == '.txt':
                return file.read().decode('utf-8')
            elif ext == '.csv':
                df = pd.read_csv(file)
                return df.to_string()
            elif ext == '.json':
                data = json.load(file)
                return json.dumps(data, indent=4)
            elif ext == '.pdf':
                doc = fitz.open(stream=file.read(), filetype="pdf")
                text = ''
                for page_num in range(len(doc)):
                    text += doc[page_num].get_text()
                return text
            elif ext == '.docx':
                doc = Document(file)
                return '\n'.join([para.text for para in doc.paragraphs])

        file_content = read_file(uploaded_file)
        st.sidebar.success("File uploaded successfully")

    # Session state to store chat history for document chatbot
    if 'doc_chat_history' not in st.session_state:
        st.session_state.doc_chat_history = []

    # Function to handle document-based input
    def handle_doc_input(user_input, file_content):
        system_message = f"""
            Based on the content of the uploaded file, please respond naturally to the user's query. 
            Provide clear, relevant, and concise answers. If the file does not contain sufficient information to answer the query, let the user know politely and suggest providing more details if necessary.
            If the user indicates they wish to end the conversation (e.g., with responses like "fine" or "okay or thank you"), politly ask for furthur questions.
            Don’t give any responses from your side, and if a question is not understood, confirm with an example similar to the question that the user is asking
            If the user asks for a summary, provide a concise 2-3 line summary of the relevant content from the file.
            Here is the content of the uploaded file:{file_content}
        """
        ai_msg = llm.invoke([SystemMessage(content=system_message), HumanMessage(content=user_input)])
        return ai_msg.content.strip()

    # Only show the chat input field if the file has been uploaded successfully
    if uploaded_file:
        # Chat input with send button for document chatbot
        prompt = st.chat_input("Ask about the document", key="document_chat_input_key")

        if prompt:
            # Get the response based on the document content
            response = handle_doc_input(prompt, file_content)

            # Store conversation in session state
            st.session_state.doc_chat_history.append({
                'user': prompt,
                'bot': response
            })

        # Display conversation history for document chatbot
        for chat in st.session_state.doc_chat_history:
            st.markdown(f'''
                <div class="user-container">
                    <div class="user-message">{chat["user"]}</div>
                    <img src="https://th.bing.com/th/id/R.6b0022312d41080436c52da571d5c697?rik=ejx13G9ZroRrcg&riu=http%3a%2f%2fpluspng.com%2fimg-png%2fuser-png-icon-young-user-icon-2400.png&ehk=NNF6zZUBr0n5i%2fx0Bh3AMRDRDrzslPXB0ANabkkPyv0%3d&risl=&pid=ImgRaw&r=0" class="avatar"/>
                </div>
                <div class="bot-container">
                    <img src="https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2023/10/13075034/sl-blue-chat-bot-scaled.jpg" class="avatar"/>
                    <div class="bot-message">{chat["bot"]}</div>
                </div>
            ''', unsafe_allow_html=True)

    # If no file uploaded, display a message asking the user to upload a file
    else:
        st.markdown("<h5 style='color:red;'>Please upload a document to start chatting!</h5>", unsafe_allow_html=True)

    # Additional code for styling, such as chat bubbles, input field, etc.
    # Already included in the previous style section.


# Run chatbot based on selection
if page == "GENERAL CHATBOT":
    general_chatbot()
elif page == "DOCUMENT CHATBOT":
    document_chatbot()
