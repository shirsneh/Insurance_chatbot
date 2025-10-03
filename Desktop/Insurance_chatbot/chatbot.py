import os
import streamlit as st
from typing import Dict, Any, List
from rag_system import InsuranceRAGSystem
from llm_handlers import LLMHandler

class InsuranceChatbot:
    def __init__(self):
        self.rag_system = None
        self.llm_handler = None
        self.chat_history = []
        
    def initialize(self, api_key: str, provider: str = "openai"):
        """Initialize the chatbot with API key and provider"""
        try:
            self.rag_system = InsuranceRAGSystem(api_key, provider)
            self.llm_handler = LLMHandler(provider, api_key)
            
            # Try to load existing vector store
            success, message = self.rag_system.load_vectorstore()
            if not success:
                st.warning(f"Could not load existing vector store: {message}")
            
            return True, "Chatbot initialized successfully"
        except Exception as e:
            return False, f"Error initializing chatbot: {str(e)}"
    
    def load_policy_document(self, file_path: str):
        """Load a new policy document"""
        if not self.rag_system:
            return False, "Chatbot not initialized"
        
        return self.rag_system.load_policy_document(file_path)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query and return response"""
        if not self.rag_system or not self.llm_handler:
            return {
                "response": "Chatbot not properly initialized. Please check your API keys.",
                "error": True
            }
        
        try:
            # Get relevant context from RAG system
            context = self.rag_system.get_context_for_query(query)
            
            # Generate response using LLM
            result = self.llm_handler.generate_response(query, context)
            
            # Add to chat history
            self.chat_history.append({
                "query": query,
                "response": result.get("response", "No response generated"),
                "provider": result.get("provider", "unknown"),
                "model": result.get("model", "unknown")
            })
            
            return result
            
        except Exception as e:
            return {
                "response": f"Error processing query: {str(e)}",
                "error": True
            }
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get chat history"""
        return self.chat_history
    
    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []
