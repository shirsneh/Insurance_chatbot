import os
from typing import Dict, Any, Optional
import openai
import anthropic
import google.generativeai as genai
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class LLMHandler:
    def __init__(self, provider: str = "openai", api_key: str = None):
        self.provider = provider
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider"""
        if self.provider == "openai":
            openai.api_key = self.api_key
            self.client = ChatOpenAI(
                openai_api_key=self.api_key,
                model_name="gpt-3.5-turbo",
                temperature=0.7
            )
        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == "google":
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, query: str, context: str = "") -> Dict[str, Any]:
        """Generate response using the configured LLM provider"""
        try:
            if self.provider == "openai":
                return self._generate_openai_response(query, context)
            elif self.provider == "anthropic":
                return self._generate_anthropic_response(query, context)
            elif self.provider == "google":
                return self._generate_google_response(query, context)
            else:
                return {"error": "Unsupported provider"}
        except Exception as e:
            return {"error": f"Error generating response: {str(e)}"}
    
    def _generate_openai_response(self, query: str, context: str) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        system_prompt = f"""You are a helpful insurance assistant. Use the following context from insurance policy documents to answer user questions accurately and helpfully.

Context from policy documents:
{context}

Instructions:
- Answer questions based on the provided context
- If the context doesn't contain enough information, say so
- Be friendly, professional, and helpful
- Provide specific details when available
- If asked about coverage, deductibles, or claims, refer to the specific policy information
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = self.client(messages)
        return {
            "response": response.content,
            "provider": "openai",
            "model": "gpt-3.5-turbo"
        }
    
    def _generate_anthropic_response(self, query: str, context: str) -> Dict[str, Any]:
        """Generate response using Anthropic Claude"""
        system_prompt = f"""You are a helpful insurance assistant. Use the following context from insurance policy documents to answer user questions accurately and helpfully.

Context from policy documents:
{context}

Instructions:
- Answer questions based on the provided context
- If the context doesn't contain enough information, say so
- Be friendly, professional, and helpful
- Provide specific details when available
- If asked about coverage, deductibles, or claims, refer to the specific policy information
"""
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        
        return {
            "response": response.content[0].text,
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229"
        }
    
    def _generate_google_response(self, query: str, context: str) -> Dict[str, Any]:
        """Generate response using Google Gemini"""
        prompt = f"""You are a helpful insurance assistant. Use the following context from insurance policy documents to answer user questions accurately and helpfully.

Context from policy documents:
{context}

Instructions:
- Answer questions based on the provided context
- If the context doesn't contain enough information, say so
- Be friendly, professional, and helpful
- Provide specific details when available
- If asked about coverage, deductibles, or claims, refer to the specific policy information

User Question: {query}"""
        
        response = self.client.generate_content(prompt)
        
        return {
            "response": response.text,
            "provider": "google",
            "model": "gemini-pro"
        }
