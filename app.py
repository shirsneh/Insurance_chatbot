import streamlit as st
import os
from dotenv import load_dotenv
from chatbot import InsuranceChatbot
from utils import get_api_key_and_provider, validate_api_key, get_supported_providers

load_dotenv()

st.set_page_config(
    page_title="Insurance Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'auto_initialized' not in st.session_state:
        st.session_state.auto_initialized = False
    if 'loaded_docs' not in st.session_state:
        st.session_state.loaded_docs = []

def auto_initialize_chatbot():
    """Auto-initialize chatbot with environment variables and load documents"""
    if st.session_state.auto_initialized:
        return
    
    # Get API key and provider from environment
    api_key, provider = get_api_key_and_provider()
    
    if not validate_api_key(api_key, provider):
        st.error(f"No valid API key found for provider '{provider}'. Please check your .env file.")
        st.session_state.auto_initialized = True
        return
    
    if not st.session_state.initialized:
        try:
            chatbot = InsuranceChatbot()
            success, message = chatbot.initialize(api_key, provider)
            
            if success:
                st.session_state.chatbot = chatbot
                st.session_state.initialized = True
                st.session_state.auto_initialized = True
                
                auto_load_documents()
            else:
                st.error(f"Initialization failed: {message}")
                
        except Exception as e:
            st.error(f"Auto-initialization failed: {str(e)}")
    
    st.session_state.auto_initialized = True

def auto_load_documents():
    """Automatically load all PDF documents from policy_docs folder"""
    if not st.session_state.initialized:
        return
    
    policy_docs_dir = "policy_docs"
    if os.path.exists(policy_docs_dir):
        pdf_files = [f for f in os.listdir(policy_docs_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            file_path = os.path.join(policy_docs_dir, pdf_file)
            try:
                success, message = st.session_state.chatbot.load_policy_document(file_path)
                if success:
                    st.session_state.loaded_docs = st.session_state.get('loaded_docs', []) + [pdf_file]
            except Exception as e:
                st.error(f"Error loading {pdf_file}: {str(e)}")

def main():
    initialize_session_state()
    auto_initialize_chatbot()
    
    st.markdown('<h1 class="main-header"> VIA - Virtual Insurance Assistant</h1>', unsafe_allow_html=True)
    st.markdown("Ask questions about your insurance policy and get instant answers!")
    
    # Check if chatbot is ready
    if not st.session_state.initialized:
        st.error("Chatbot not ready. Please check your .env file configuration.")
        st.info("Make sure you have set your API keys in the .env file")
        return
    
    with st.sidebar:
        st.success("✅ Ready to help!")
        if st.session_state.get('loaded_docs'):
            st.markdown("**Loaded Documents:**")
            for doc in st.session_state.loaded_docs:
                st.text(f"• {doc}")
        else:
            st.info("No documents loaded yet")
        
        if st.button("Clear Chat History"):
            st.session_state.chatbot.clear_chat_history()
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
    
    st.markdown("## Chat with VIA")
    
    for i, chat in enumerate(st.session_state.chatbot.get_chat_history()):
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>
            {chat['query']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 VIA:</strong><br>
            {chat['response']}
        </div>
        """, unsafe_allow_html=True)
    
    user_input = st.text_input(
        "Ask a question about your insurance policy:",
        placeholder="e.g., What is covered under my policy? What is my deductible?",
        key="user_input"
    )
    
    if st.button("Send", type="primary") and user_input:
        with st.spinner("Thinking..."):
            result = st.session_state.chatbot.process_query(user_input)
            
            if result.get("error"):
                st.error(f"❌ {result['response']}")
            else:
                st.session_state.user_input = ""
                st.rerun()

    st.markdown("## Quick Questions")
    sample_questions = [
        "What is covered under my policy?",
        "What is my deductible?",
        "How do I file a claim?",
        "What are the coverage limits?",
        "What are the policy exclusions?",
        "What is the claims process?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(sample_questions):
        with cols[i % 2]:
            if st.button(f"❓ {question}", key=f"sample_{i}"):
                with st.spinner("Thinking..."):
                    result = st.session_state.chatbot.process_query(question)
                    if not result.get("error"):
                        st.rerun()

if __name__ == "__main__":
    main()
