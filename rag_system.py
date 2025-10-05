import os
import pickle
import numpy as np
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
import streamlit as st

class InsuranceRAGSystem:
    def __init__(self, api_key: str, provider: str = "openai"):
        self.api_key = api_key
        self.provider = provider
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def initialize_embeddings(self):
        """Initialize embeddings based on provider"""
        if self.provider == "openai":
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        else:
            # For other providers, we'll use OpenAI as fallback
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
    
    def load_policy_document(self, file_path: str):
        """Load and process insurance policy document"""
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
            if not file_path.lower().endswith('.pdf'):
                return False, "Only PDF files are supported"
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            if not documents:
                return False, "No content found in PDF file - the PDF may be image-based or corrupted"

            texts = self.text_splitter.split_documents(documents)
            
            if not texts:
                return False, "No text chunks could be extracted from the document - try a different PDF or check if it's text-based"
            
            if self.embeddings is None:
                self.initialize_embeddings()
            
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(texts, self.embeddings)
            else:
                self.vectorstore.add_documents(texts)
            
            self.save_vectorstore()
            
            return True, f"Successfully loaded and processed {len(texts)} document chunks"
            
        except Exception as e:
            return False, f"Error loading document: {str(e)}"
    
    def save_vectorstore(self):
        """Save vector store to disk"""
        if self.vectorstore:
            os.makedirs("models", exist_ok=True)
            self.vectorstore.save_local("models/faiss_index")
    
    def load_vectorstore(self):
        """Load vector store from disk"""
        try:
            if self.embeddings is None:
                self.initialize_embeddings()
            
            if not os.path.exists("models/faiss_index"):
                return False, "No vector store found. Please load policy documents first."
            
            if not os.path.exists("models/faiss_index/index.faiss"):
                return False, "Vector store index file not found. Please load policy documents first."
            
            self.vectorstore = FAISS.load_local("models/faiss_index", self.embeddings)
            return True, "Vector store loaded successfully"
        except Exception as e:
            return False, f"Error loading vector store: {str(e)}"
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        if not self.vectorstore:
            return []
        
        try:
            docs = self.vectorstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            return results
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str, max_chunks: int = 3) -> str:
        """Get relevant context for a query"""
        search_results = self.search_documents(query, k=max_chunks)
        
        if not search_results:
            return "No relevant information found in the policy documents."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"Context {i}:\n{result['content']}\n")
        
        return "\n".join(context_parts)
