"""
Streamlit web interface for the Conversational Knowledge Bot
"""

import streamlit as st
import os
from datetime import datetime
from working_langchain_bot import WorkingLangChainBot

# Page configuration
st.set_page_config(
    page_title="Conversational Knowledge Bot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS 
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left: 4px solid #4e8cff;
    }
    .bot-message {
        background-color: #e6f7ff;
        border-left: 4px solid #00b894;
    }
    .stButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'bot' not in st.session_state:
    try:
        st.session_state.bot = WorkingLangChainBot()
        st.session_state.has_full_features = True
    except Exception as e:
        st.error(f"Error initializing bot: {e}")
        st.session_state.has_full_features = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("Knowledge Bot Controls")
    
    st.markdown("---")
    st.subheader("Settings")
    
    st.info("Using: Wikipedia Search + Memory")
    
    st.markdown("---")
    st.subheader("Conversation")
    
    # Clear conversation button
    if st.button("Clear Conversation", use_container_width=True):
        if 'bot' in st.session_state:
            st.session_state.bot.clear_memory()
        st.session_state.messages = []
        st.rerun()
    
    # Export conversation
    if st.button("Export Chat", use_container_width=True):
        chat_text = "Conversation History:\n\n"
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Bot"
            chat_text += f"{role}: {msg['content']}\n\n"
        
        st.download_button(
            label="Download Conversation",
            data=chat_text,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.markdown("---")
    st.subheader("About")
    st.info("""
    This bot can:
    - Remember previous conversations
    - Search Wikipedia for facts
    - Answer factual questions with context
    - Maintain conversation flow
    """)

# Main content
st.title("Conversational Knowledge Bot")
st.markdown("Ask me anything! I can search Wikipedia and remember our conversation.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if 'bot' in st.session_state:
                    response = st.session_state.bot.chat(prompt)
                else:
                    # Create a new bot instance if needed
                    bot = WorkingLangChainBot()
                    response = bot.chat(prompt)
                
                st.markdown(response)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                response = "I encountered an error. Please try again."
                st.markdown(response)
    
    # Adding bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Example questions
st.markdown("---")
st.subheader("Try these examples:")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Who is the CEO of OpenAI?"):
        st.chat_input("Who is the CEO of OpenAI?", key="example1")

with col2:
    if st.button("What is quantum computing?"):
        st.chat_input("What is quantum computing?", key="example2")

with col3:
    if st.button("Tell me about the French Revolution"):
        st.chat_input("Tell me about the French Revolution", key="example3")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    Conversational Knowledge Bot • Uses Wikipedia API • Maintains conversation memory
    </div>
    """,
    unsafe_allow_html=True
)
