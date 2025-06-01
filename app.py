import streamlit as st
import ollama
import PyPDF2
import io
import json
import os
import re
from datetime import datetime
import time

# Import our new modules
from analytics_utils import InterviewAnalytics
from session_recorder import InterviewRecorder
from model_config import ModelManager

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {}
if 'resume_text' not in st.session_state:
    st.session_state['resume_text'] = ""
if 'analytics' not in st.session_state:
    st.session_state['analytics'] = InterviewAnalytics()
if 'recorder' not in st.session_state:
    st.session_state['recorder'] = InterviewRecorder()
if 'model_manager' not in st.session_state:
    st.session_state['model_manager'] = ModelManager()
if 'selected_model' not in st.session_state:
    st.session_state['selected_model'] = 'deepseek-r1:7b'
if 'response_start_time' not in st.session_state:
    st.session_state['response_start_time'] = None

# File-based user storage
USERS_FILE = "users.json"

def load_users():
    """Load users from JSON file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def register_user(username, password):
    """Register a new user."""
    users = load_users()
    if username in users:
        return False
    users[username] = {
        'password': password,
        'created_at': str(datetime.now())
    }
    save_users(users)
    return True

def authenticate_user(username, password):
    """Authenticate user credentials."""
    users = load_users()
    return username in users and users[username]['password'] == password

def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def clean_llm_response(response):
    """Remove thinking/planning section from LLM response."""
    think_pattern = r'<think>.*?</think>'
    cleaned_response = re.sub(think_pattern, '', response, flags=re.DOTALL)
    return cleaned_response.strip()

def generate_interview_questions(resume_text, model_name):
    """Generate interview questions based on resume content using selected model."""
    model_config = st.session_state['model_manager'].get_model_config(model_name)
    
    system_prompt = model_config['system_prompt'] + f"""
    Based on the following resume, generate relevant interview questions that assess both technical knowledge and behavioral aspects.

    Resume content:
    {resume_text}

    Generate 3 technical questions and 2 behavioral questions. Format your response as a numbered list."""

    response = ollama.chat(model=model_name, messages=[
        {'role': 'system', 'content': system_prompt}
    ])
    
    return clean_llm_response(response['message']['content'])

def chat_with_ai(prompt, resume_context=""):
    """Handle chat interaction with AI using selected model."""
    model_name = st.session_state['selected_model']
    model_config = st.session_state['model_manager'].get_model_config(model_name)
    
    messages = [
        {'role': 'system', 'content': model_config['system_prompt'] + f"\nResume context: {resume_context}"},
        {'role': 'user', 'content': prompt}
    ]
    
    response = ollama.chat(model=model_name, messages=messages)
    return clean_llm_response(response['message']['content'])

def show_analytics():
    """Display interview analytics."""
    st.subheader("Interview Performance Analytics")
    
    report = st.session_state['analytics'].generate_report()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Response Time", f"{report['summary']['average_response_time']:.1f}s")
    with col2:
        st.metric("Technical Accuracy", f"{report['summary']['technical_accuracy']*100:.1f}%")
    with col3:
        st.metric("Keyword Match Rate", f"{report['summary']['keyword_match_rate']*100:.1f}%")
    
    # Display recommendations
    st.subheader("Recommendations")
    for rec in report['recommendations']:
        st.write(f"• {rec}")

def show_session_history():
    """Display previous interview sessions."""
    st.subheader("Previous Sessions")
    
    sessions = st.session_state['recorder'].list_sessions(st.session_state['user_data']['username'])
    
    for session in sessions:
        with st.expander(f"Session: {session['start_time']}"):
            st.write(f"Model used: {session['model_used']}")
            st.write(f"Duration: {datetime.fromisoformat(session['end_time']).timestamp() - datetime.fromisoformat(session['start_time']).timestamp():.0f} seconds")
            
            if st.button("Load Session", key=session['session_id']):
                session_data = st.session_state['recorder'].load_session(session['session_id'])
                st.session_state['chat_history'] = session_data['interactions']
                st.experimental_rerun()

# Streamlit UI
st.title("AI Interview Assessment System")

if not st.session_state['authenticated']:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if authenticate_user(login_username, login_password):
                st.session_state['authenticated'] = True
                st.session_state['user_data']['username'] = login_username
                # Start new session recording
                st.session_state['recorder'].start_session(login_username)
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        st.header("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register"):
            if register_user(reg_username, reg_password):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists")

else:
    st.write(f"Welcome, {st.session_state['user_data']['username']}!")
    
    # Model selection
    st.sidebar.header("Interview Settings")
    models = st.session_state['model_manager'].list_models()
    selected_model = st.sidebar.selectbox(
        "Select AI Model",
        options=[m[0] for m in models],
        format_func=lambda x: next(m[1] for m in models if m[0] == x),
        index=0
    )
    st.session_state['selected_model'] = selected_model
    
    # Show model description
    model_desc = next(m[2] for m in models if m[0] == selected_model)
    st.sidebar.write(f"*{model_desc}*")
    
    if not st.session_state['resume_text']:
        st.header("Upload Resume")
        uploaded_file = st.file_uploader("Choose your resume (PDF format)", type="pdf")
        
        if uploaded_file is not None:
            try:
                resume_text = extract_text_from_pdf(uploaded_file)
                st.session_state['resume_text'] = resume_text
                st.session_state['recorder'].set_resume_text(resume_text)
                
                questions = generate_interview_questions(resume_text, selected_model)
                st.session_state['chat_history'].append({
                    "role": "assistant",
                    "content": f"Based on your resume, let's start with these questions:\n\n{questions}"
                })
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
    
    # Main chat interface
    tab1, tab2, tab3 = st.tabs(["Interview Chat", "Analytics", "Session History"])
    
    with tab1:
        st.header("Interview Chat")
        
        # Display chat history
        for chat in st.session_state['chat_history']:
            if chat['role'] == 'user':
                st.write(f"**You:** {chat['content']}")
            else:
                st.write(f"**AI:** {chat['content']}")
        
        # User input
        user_input = st.text_input("Your response:", key="user_input")
        
        if st.button("Send"):
            if user_input.strip():
                # Record response time
                if st.session_state['response_start_time']:
                    response_time = time.time() - st.session_state['response_start_time']
                else:
                    response_time = 0
                
                # Add user message to chat history
                st.session_state['chat_history'].append({
                    "role": "user",
                    "content": user_input
                })
                
                # Record in session recorder
                st.session_state['recorder'].record_interaction("user", user_input)
                
                try:
                    # Get AI response
                    ai_response = chat_with_ai(user_input, st.session_state['resume_text'])
                    
                    # Add AI response to chat history
                    st.session_state['chat_history'].append({
                        "role": "assistant",
                        "content": ai_response
                    })
                    
                    # Record in session recorder
                    st.session_state['recorder'].record_interaction("assistant", ai_response)
                    
                    # Update analytics
                    st.session_state['analytics'].analyze_response(
                        user_input,
                        st.session_state['chat_history'][-2]['content'],  # Previous AI message
                        response_time
                    )
                    
                    # Reset response start time
                    st.session_state['response_start_time'] = time.time()
                    
                except Exception as e:
                    st.error(f"Error getting AI response: {str(e)}")
                
                st.experimental_rerun()
    
    with tab2:
        show_analytics()
    
    with tab3:
        show_session_history()
    
    # End Interview button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("End Interview", type="primary"):
            # Save analytics to session recording
            st.session_state['recorder'].add_analytics(
                st.session_state['analytics'].generate_report()
            )
            # End and save session
            st.session_state['recorder'].end_session()
            
            # Reset session state
            st.session_state['authenticated'] = False
            st.session_state['chat_history'] = []
            st.session_state['resume_text'] = ""
            st.session_state['analytics'] = InterviewAnalytics()
            st.session_state['response_start_time'] = None
            st.experimental_rerun()

# Footer
st.write("---")
st.write("**Note:** This is a demo project. Data is stored temporarily and locally.")