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
    /* Hide the Deploy button */
    .stDeployButton {
        display: none !important;
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
    if 'selected_chat' not in st.session_state:
        st.session_state.selected_chat = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'auto_initialized' not in st.session_state:
        st.session_state.auto_initialized = False
    if 'loaded_docs' not in st.session_state:
        st.session_state.loaded_docs = []
    if 'selected_provider' not in st.session_state:
        st.session_state.selected_provider = None
    if 'provider_changed' not in st.session_state:
        st.session_state.provider_changed = False
    if 'failed_providers' not in st.session_state:
        st.session_state.failed_providers = []
    if 'last_failover_time' not in st.session_state:
        st.session_state.last_failover_time = None

def get_available_providers():
    """Get list of providers that have valid API keys and haven't failed recently"""
    available_providers = []
    providers = get_supported_providers()
    
    for provider in providers:
        api_key, _ = get_api_key_and_provider(provider)
        if validate_api_key(api_key, provider) and provider not in st.session_state.failed_providers:
            available_providers.append(provider)
    
    return available_providers

def is_provider_failure(error_message):
    """Check if an error indicates a provider failure that should trigger failover"""
    failure_indicators = [
        "quota exceeded",
        "rate limit",
        "billing",
        "insufficient credits",
        "api key invalid",
        "incorrect api key",
        "invalid api key",
        "unauthorized",
        "forbidden",
        "service unavailable",
        "timeout",
        "connection error",
        "api error",
        "provider error",
        "your_goo",
        "your_openai",
        "your_anthropic"
    ]
    
    error_lower = error_message.lower()
    return any(indicator in error_lower for indicator in failure_indicators)

def try_failover():
    """Try to switch to another available provider"""
    available_providers = get_available_providers()
    
    if not available_providers:
        return False, "No other providers available"
    
    for provider in available_providers:
        if provider != st.session_state.selected_provider:
            success, message = initialize_chatbot_with_provider(provider)
            if success:
                st.session_state.failed_providers.append(st.session_state.selected_provider)
                import time
                st.session_state.last_failover_time = time.time()
                return True, f"Switched to {provider.upper()}"
    
    return False, "All providers failed"

def reset_failed_providers():
    """Reset the list of failed providers to allow retrying them"""
    st.session_state.failed_providers = []
    st.session_state.last_failover_time = None
    st.success("🔄 Failed providers reset - all providers available again")

def check_provider_recovery():
    """Check if failed providers should be recovered (after 5 minutes)"""
    if st.session_state.last_failover_time:
        import time
        current_time = time.time()
        # Recover failed providers after 1 minute
        if current_time - st.session_state.last_failover_time > 60:
            st.session_state.failed_providers = []
            st.session_state.last_failover_time = None

def process_query_with_failover(query):
    """Process query with automatic failover on provider failure (transparent to user)"""
    if not st.session_state.initialized or not st.session_state.chatbot:
        return {"error": True, "response": "Chatbot not initialized"}
    
    try:
        result = st.session_state.chatbot.process_query(query)
        
        if result.get("error") and is_provider_failure(result.get("response", "")):
            # Silently try to failover to another provider
            success, message = try_failover()
            
            if success:
                # Retry the query with the new provider
                result = st.session_state.chatbot.process_query(query)
            else:
                result["response"] = f"Service temporarily unavailable. Please try again later."
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        if is_provider_failure(error_msg):
            # Silently try to failover to another provider
            success, message = try_failover()
            
            if success:
                # Retry the query with the new provider
                try:
                    result = st.session_state.chatbot.process_query(query)
                    return result
                except Exception as retry_error:
                    return {"error": True, "response": "Service temporarily unavailable. Please try again later."}
            else:
                return {"error": True, "response": "Service temporarily unavailable. Please try again later."}
        else:
            return {"error": True, "response": f"Unexpected error: {error_msg}"}

def initialize_chatbot_with_provider(provider):
    """Initialize chatbot with specific provider"""
    api_key, _ = get_api_key_and_provider(provider)
    
    if not validate_api_key(api_key, provider):
        return False, f"No valid API key found for provider '{provider}'"
    
    try:
        chatbot = InsuranceChatbot()
        success, message = chatbot.initialize(api_key, provider)
        
        if success:
            st.session_state.chatbot = chatbot
            st.session_state.initialized = True
            st.session_state.selected_provider = provider
            return True, f"Successfully initialized with {provider}"
        else:
            return False, f"Initialization failed: {message}"
            
    except Exception as e:
        return False, f"Initialization error: {str(e)}"

def auto_initialize_chatbot():
    """Auto-initialize chatbot with best available provider (transparent to user)"""
    if st.session_state.auto_initialized and not st.session_state.provider_changed:
        return
    
    available_providers = get_available_providers()
    
    if not available_providers:
        st.error("No valid API keys found. Please check your .env file.")
        st.session_state.auto_initialized = True
        return
    
    # Auto-select best available provider
    if not st.session_state.selected_provider or st.session_state.provider_changed:
        provider = available_providers[0]
        st.session_state.selected_provider = provider
        st.session_state.provider_changed = False
    
    success, message = initialize_chatbot_with_provider(st.session_state.selected_provider)
    
    if success:
        st.session_state.auto_initialized = True
        auto_load_documents()
    else:
        # Check if initialization failed due to provider error and try failover
        if is_provider_failure(message):
            st.warning("Provider failed during initialization, trying failover...")
            success, failover_msg = try_failover()
            if success:
                st.session_state.auto_initialized = True
                auto_load_documents()
            else:
                st.error(f"All providers failed: {failover_msg}")
                st.session_state.auto_initialized = True
        else:
            st.error(f"Initialization failed: {message}")
            st.session_state.auto_initialized = True

def auto_load_documents():
    """Automatically load all PDF documents from policy_docs folder with failover"""
    if not st.session_state.initialized:
        return
    
    # Check if vector store already exists
    vectorstore_path = "models/faiss_index"
    if os.path.exists(vectorstore_path) and os.path.exists(f"{vectorstore_path}/index.faiss"):
        # Vector store exists, mark all PDF files as loaded
        policy_docs_dir = "policy_docs"
        if os.path.exists(policy_docs_dir):
            pdf_files = [f for f in os.listdir(policy_docs_dir) if f.endswith('.pdf')]
            st.session_state.loaded_docs = pdf_files
        return
    
    policy_docs_dir = "policy_docs"
    if os.path.exists(policy_docs_dir):
        pdf_files = [f for f in os.listdir(policy_docs_dir) if f.endswith('.pdf')]
        loaded_docs = st.session_state.get('loaded_docs', [])
        
        # Only process files that haven't been loaded yet
        files_to_process = [f for f in pdf_files if f not in loaded_docs]
        
        if files_to_process:
            for pdf_file in files_to_process:
                file_path = os.path.join(policy_docs_dir, pdf_file)
                try:
                    success, message = st.session_state.chatbot.load_policy_document(file_path)
                    if success:
                        st.session_state.loaded_docs = st.session_state.get('loaded_docs', []) + [pdf_file]
                    else:
                        # Check if this is a provider failure and try failover
                        if is_provider_failure(message):
                            success, failover_msg = try_failover()
                            if success:
                                # Retry with new provider
                                success, message = st.session_state.chatbot.load_policy_document(file_path)
                                if success:
                                    st.session_state.loaded_docs = st.session_state.get('loaded_docs', []) + [pdf_file]
                                else:
                                    st.warning(f"Could not load {pdf_file} even after failover: {message}")
                            else:
                                st.warning(f"Could not load {pdf_file}: {message}")
                        else:
                            st.warning(f"Could not load {pdf_file}: {message}")
                except Exception as e:
                    # Check if this is a provider failure and try failover
                    if is_provider_failure(str(e)):
                        success, failover_msg = try_failover()
                        if success:
                            try:
                                success, message = st.session_state.chatbot.load_policy_document(file_path)
                                if success:
                                    st.session_state.loaded_docs = st.session_state.get('loaded_docs', []) + [pdf_file]
                                    # Don't show success messages in sidebar - silent loading
                                else:
                                    st.warning(f"Could not load {pdf_file} even after failover: {message}")
                            except Exception as retry_error:
                                st.error(f"Error loading {pdf_file} even after failover: {str(retry_error)}")
                        else:
                            st.error(f"Error loading {pdf_file}: {str(e)}")
                    else:
                        st.error(f"Error loading {pdf_file}: {str(e)}")

def main():
    initialize_session_state()
    check_provider_recovery()
    
    st.markdown('<h1 class="main-header"> VIA - Virtual Insurance Assistant</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🤖 VIA History")
        
        available_providers = get_available_providers()
        
        if not available_providers:
            return
        
        # Auto-select best available provider
        if not st.session_state.initialized or st.session_state.provider_changed:
            if available_providers:
                selected_provider = available_providers[0]
                st.session_state.selected_provider = selected_provider
                st.session_state.provider_changed = False
                
                with st.spinner("Initializing VIA..."):
                    success, message = initialize_chatbot_with_provider(selected_provider)
                    if success:
                        st.session_state.auto_initialized = True
                        auto_load_documents()
                    else:
                        return
            else:
                return
        
        if st.session_state.initialized:
            st.success("✅ Ready to help!")
            
            # Display chat history
            if st.session_state.chat_history:
                st.markdown("**Previous Conversations:**")
                for i, chat in enumerate(st.session_state.chat_history):
                    button_text = chat['user'][:50] + "..." if len(chat['user']) > 50 else chat['user']
                    if st.button(f"💬 {button_text}", key=f"history_{i}"):
                    
                        st.session_state.selected_chat = i
                        st.rerun()
            
            if st.button("Clear Chat History"):
                st.session_state.chatbot.clear_chat_history()
                st.session_state.chat_history = []
                st.session_state.selected_chat = None
                st.success("Chat history cleared!")
                st.rerun()
    
    # Show error messages in main area
    available_providers = get_available_providers()
    if not available_providers:
        st.error("No valid API keys found. Please check your .env file.")
        st.info("Make sure you have set your API keys in the .env file")
        return
    
    if not st.session_state.initialized:
        st.error("Chatbot not ready. Please check your .env file configuration.")
        st.info("Make sure you have set your API keys in the .env file")
        return
    
    # Check if there are any errors that prevent the app from being fully ready
    has_errors = False
    policy_docs_dir = "policy_docs"
    if os.path.exists(policy_docs_dir):
        pdf_files = [f for f in os.listdir(policy_docs_dir) if f.endswith('.pdf')]
        if pdf_files:
            loaded_docs = st.session_state.get('loaded_docs', [])
            # Check if any files failed to load (not just count comparison)
            files_to_process = [f for f in pdf_files if f not in loaded_docs]
            if files_to_process:
                has_errors = True
    
    if has_errors:
        st.warning("⚠️ Some documents failed to load. The chatbot may not have complete information.")
        st.info("You can still ask questions, but some policy details might be missing.")
    elif not st.session_state.get('loaded_docs'):
        st.warning("⚠️ No documents loaded. The chatbot may have limited information.")
        st.info("Add PDF files to the policy_docs folder for better assistance.")
    
    st.markdown("## Chat with VIA")
    
    # Display chat history from session state
    for i, chat in enumerate(st.session_state.chat_history):
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>
            {chat['user']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 VIA:</strong><br>
            {chat['response']}
        </div>
        """, unsafe_allow_html=True)
    
    # Create a form to handle input clearing
    with st.form(key=f"chat_form_{len(st.session_state.chat_history)}"):
        user_input = st.text_input(
            "Ask questions about your insurance policy and get instant answers!",
            placeholder="e.g., What is covered under my policy? What is my deductible?",
            key=f"user_input_{len(st.session_state.chat_history)}"
        )
        
        submitted = st.form_submit_button("Send", type="primary")
        
        if submitted and user_input:
            with st.spinner("Thinking..."):
                result = process_query_with_failover(user_input)
                
                if result.get("error"):
                    st.error(f"❌ {result['response']}")
                else:
                    # Save the chat to history
                    st.session_state.chat_history.append({
                        "user": user_input,
                        "response": result['response']
                    })
                    st.rerun()
    
    # handle Enter key press for prompt submission
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && event.target.tagName === 'INPUT') {
            event.preventDefault();
            // Find the form submit button and click it
            const submitButton = document.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

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
                    result = process_query_with_failover(question)
                    if not result.get("error"):
                        st.rerun()

if __name__ == "__main__":
    main()
