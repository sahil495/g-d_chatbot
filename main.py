import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import json
import pandas as pd
import fitz  # PyMuPDF
from docx import Document
import yaml

# App ka title
st.set_page_config(page_title="G/D CHATBOT", layout="centered")



page = "GENERAL CHATBOT"

st.title("Welcome to My App!")


# Radio button for page selection
page = st.radio("Choose Type", ["GENERAL CHATBOT", "DOCUMENT CHATBOT"])

# Display content based on selected page
if page == "GENERAL CHATBOT":
    
    with open('config.yaml') as config_file:
        config = yaml.safe_load(config_file)

    # Set the API key in the environment
    os.environ["GOOGLE_API_KEY"] = config["GOOGLE_API_KEY"]
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        convert_system_message_to_human=True
    )

    def main():
        system_message = "You are a helpful assistant for general purposes. Please keep responses concise."

        # Initialize session state variables if not present
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []

        if 'input' not in st.session_state:
            st.session_state.input = ''

        if 'response_content' not in st.session_state:
            st.session_state.response_content = ''

        def submit():
            if st.session_state.widget:
                st.session_state.input = st.session_state.widget
                st.session_state.widget = ''

                # Prepare messages for the AI model
                messages = [HumanMessage(content=system_message)]

                # Add only the last few interactions to avoid excessive length
                recent_conversations = st.session_state.conversation_history[-5:]  # Adjust the number as needed
                for item in recent_conversations:
                    messages.append(HumanMessage(content=item['input']))
                    messages.append(HumanMessage(content=item['response']))

                messages.append(HumanMessage(content=st.session_state.input))

                # Get AI response
                ai_msg = llm.invoke(messages)

                # Limit response length and update session state
                st.session_state.response_content = ai_msg.content.strip()[:500]  # Adjust the length as needed
                st.session_state.conversation_history.append({
                    'input': st.session_state.input,
                    'response': st.session_state.response_content,
                    'sender': 'user'
                })

        # Streamlit UI components
        st.text_input('Ready to ASK from GENEREAL CHATBOT', key='widget')
        st.button('Send', on_click=submit)

        # Display conversation history
        if st.session_state.conversation_history:
            for item in reversed(st.session_state.conversation_history):
                st.markdown(f'''
                <div style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 3rem;">
                    <div style="text-align: left; font-size: 20px;">🤖  {item["response"]}</div>
                    <div style="text-align: right; font-size: 20px;">{item["input"]}  🧑</div>
                </div>
            ''', unsafe_allow_html=True)

    main()

    # Display name in smaller font using Markdown
    st.markdown(f"<h5 style='text-align: left;'>Created by SAHIL UMAR</h5>", unsafe_allow_html=True)
    st.markdown(f"<h7 style='text-align: left;'>Gmail ( sonuarain46@gmail.com )</h7>", unsafe_allow_html=True)
    st.markdown(f"<h7 style='text-align: left;'>Linkedin ( www.linkedin.com/in/sonu-arain-ab705930b )</h7>", unsafe_allow_html=True)
    
elif page == "DOCUMENT CHATBOT":
    with open('config.yaml') as config_file:
        config = yaml.safe_load(config_file)

    # Set the API key in the environment
    os.environ["GOOGLE_API_KEY"] = config["GOOGLE_API_KEY"]
    # Initialize the ChatGoogleGenerativeAI model
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        convert_system_message_to_human=True
    )

    # Define allowed file extensions
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'pdf', 'docx'}

    def allowed_file(filename):
        """Check if the file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def read_text_file(file_path):
        """Read and return content from a text file."""
        with open(file_path, 'r') as file:
            content = file.read()
        return content

    def read_csv_file(file_path):
        """Read and return content from a CSV file."""
        df = pd.read_csv(file_path)
        return df.to_string()

    def read_json_file(file_path):
        """Read and return content from a JSON file."""
        with open(file_path, 'r') as file:
            data = json.load(file)
        return json.dumps(data, indent=4)

    def read_pdf_file(file_path):
        """Read and return content from a PDF file."""
        doc = fitz.open(file_path)
        text = ''
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text

    def read_docx_file(file_path):
        """Read and return content from a DOCX file."""
        doc = Document(file_path)
        text = [para.text for para in doc.paragraphs]
        return '\n'.join(text)

    def extract_text_from_file(file_path):
        """Extract text from a file based on its extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.txt':
            return read_text_file(file_path)
        elif ext == '.csv':
            return read_csv_file(file_path)
        elif ext == '.json':
            return read_json_file(file_path)
        elif ext == '.pdf':
            return read_pdf_file(file_path)
        elif ext == '.docx':
            return read_docx_file(file_path)
        else:
            raise ValueError("Unsupported file format")

    def handle_uploaded_file(uploaded_file_path, user_input):
        """Handle the uploaded file and generate a response based on its content."""
        if not os.path.isfile(uploaded_file_path):
            return "Error processing file: File not found."

        try:
            extracted_text = extract_text_from_file(uploaded_file_path)
            system_message = f"""
            Based on the content of the uploaded file, please respond naturally to the user's query. 
            Provide clear, relevant, and concise answers. If the file does not contain sufficient information to answer the query, let the user know politely and suggest providing more details if necessary.
            If the user indicates they wish to end the conversation (e.g., with responses like "fine" or "okay or thank you"), politly ask for furthur questions.
            Don’t give any responses from your side, and if a question is not understood, confirm with an example similar to the question that the user is asking
            If the user asks for a summary, provide a concise 2-3 line summary of the relevant content from the file.
            Here is the content of the uploaded file:
            {extracted_text}
            """
            ai_msg = llm.invoke([
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ])
            return ai_msg.content.strip()

        except Exception as e:
            return f"Error processing file: {str(e)}"

    def submit_input():
        """Handle user input submission."""
        user_input = st.session_state.user_input
        if user_input:
            response = handle_uploaded_file(file_path, user_input)
            st.session_state.chat_history.append({"user": user_input, "bot": response})
            # Clear the input field
            st.session_state.user_input = ""

    # Streamlit app setup
    uploaded_file = st.file_uploader("Upload a file", type=list(ALLOWED_EXTENSIONS))

    if uploaded_file is not None:
        # Ensure the 'uploads' directory exists
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        ready_to_chat = True
    else:
        ready_to_chat = False

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if ready_to_chat:
        st.markdown(
    "<h7 style='text-align: left;'>🔔 Ensure your queries are clear and specific, as they will be matched from the provided document. Even in general conversations, the context from the document will be considered.</h7>", 
    unsafe_allow_html=True
)

        st.text_input("Ready to ASK from DOCUMENT CHATBOT", value="", key='user_input')

        # Add a button to submit the input
        st.button("Send", on_click=submit_input)

        for chat in reversed(st.session_state.chat_history):
            st.markdown(f'''
                <div style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 3rem;">
                    <div style="text-align: left; font-size: 20px;">🤖  {chat["bot"]}</div>
                    <div style="text-align: right; font-size: 20px;">{chat["user"]}  🧑</div>
                </div>
            ''', unsafe_allow_html=True)
            
   
