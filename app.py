import streamlit as st
import os
from dotenv import load_dotenv
from chatbot import InsuranceChatbot
import tempfile

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

def main():
    initialize_session_state()
    
    st.markdown('<h1 class="main-header">🏥 Insurance Policy Assistant</h1>', unsafe_allow_html=True)
    st.markdown("Ask questions about your insurance policy and get instant, accurate answers!")
    
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Key input
        api_provider = st.selectbox(
            "Choose LLM Provider",
            ["openai", "anthropic", "google"],
            help="Select which AI model to use for responses"
        )
        
        api_key = st.text_input(
            f"Enter {api_provider.upper()} API Key",
            type="password",
            help=f"Enter your {api_provider} API key to enable the chatbot"
        )
        
        # Initialize chatbot
        if st.button("🚀 Initialize Chatbot", type="primary"):
            if api_key:
                with st.spinner("Initializing chatbot..."):
                    chatbot = InsuranceChatbot()
                    success, message = chatbot.initialize(api_key, api_provider)
                    
                    if success:
                        st.session_state.chatbot = chatbot
                        st.session_state.initialized = True
                        st.success("✅ Chatbot initialized successfully!")
                    else:
                        st.error(f"❌ {message}")
            else:
                st.error("Please enter an API key")
        
        # Document upload section
        st.markdown("## 📄 Policy Document")
        
        # Show available policy documents
        policy_docs_dir = "policy_docs"
        if os.path.exists(policy_docs_dir):
            policy_files = [f for f in os.listdir(policy_docs_dir) if f.endswith('.pdf')]
            if policy_files:
                st.markdown("**Available Policy Documents:**")
                for i, file in enumerate(policy_files):
                    if st.button(f"📄 {file}", key=f"policy_{i}"):
                        file_path = os.path.join(policy_docs_dir, file)
                        with st.spinner("Processing document..."):
                            success, message = st.session_state.chatbot.load_policy_document(file_path)
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
        
        uploaded_file = st.file_uploader(
            "Or Upload New Insurance Policy (PDF)",
            type=['pdf'],
            help="Upload a new insurance policy document in PDF format"
        )
        
        if uploaded_file and st.session_state.initialized:
            if st.button("📚 Process Document"):
                with st.spinner("Processing document..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    # Process document
                    success, message = st.session_state.chatbot.load_policy_document(tmp_file_path)
                    
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                    
                    # Clean up temp file
                    os.unlink(tmp_file_path)
        
        # Chat controls
        st.markdown("## 💬 Chat Controls")
        
        if st.button("🗑️ Clear Chat History"):
            if st.session_state.initialized:
                st.session_state.chatbot.clear_chat_history()
                st.session_state.chat_history = []
                st.success("Chat history cleared!")
        
        # Status indicator
        if st.session_state.initialized:
            st.success("🟢 Chatbot Ready")
        else:
            st.warning("🟡 Initialize chatbot to start")
    
    # Main chat interface
    if not st.session_state.initialized:
        st.info("👈 Please initialize the chatbot using the sidebar to get started!")
        return
    
    # Chat history display
    st.markdown("## 💬 Chat with your Insurance Assistant")
    
    # Display chat history
    for i, chat in enumerate(st.session_state.chatbot.get_chat_history()):
        # User message
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>
            {chat['query']}
        </div>
        """, unsafe_allow_html=True)
        
        # Bot response
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 Assistant ({chat['provider'].upper()}):</strong><br>
            {chat['response']}
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input(
        "Ask a question about your insurance policy:",
        placeholder="e.g., What is covered under my policy? What is my deductible?",
        key="user_input"
    )
    
    if st.button("Send", type="primary") and user_input:
        with st.spinner("Thinking..."):
            # Process the query
            result = st.session_state.chatbot.process_query(user_input)
            
            if result.get("error"):
                st.error(f"❌ {result['response']}")
            else:
                # Clear the input
                st.session_state.user_input = ""
                # Rerun to show the new message
                st.rerun()
    
    # Sample questions
    st.markdown("## 💡 Sample Questions")
    sample_questions = [
        "What is covered under my insurance policy?",
        "What is my deductible amount?",
        "How do I file a claim?",
        "What is the coverage limit for property damage?",
        "Are there any exclusions in my policy?",
        "What is the claims process?",
        "How long does it take to process a claim?",
        "What documents do I need for a claim?"
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
