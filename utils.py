"""
Utility functions for the Insurance Chatbot application
"""
import os
from typing import Optional, Tuple


def get_api_key_and_provider(provider: Optional[str] = None) -> Tuple[Optional[str], str]:
    if provider is None:
        provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    
    api_key = None
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
    elif provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
    else:
        # Fallback to OpenAI if provider is unknown
        provider = "openai"
        api_key = os.getenv("OPENAI_API_KEY")
    
    return api_key, provider


def validate_api_key(api_key: Optional[str], provider: str) -> bool:
    if api_key is None or api_key.strip() == "":
        return False
    
    # Check for placeholder API keys
    placeholder_indicators = [
        "your_",
        "your_openai",
        "your_anthropic", 
        "your_google",
        "your_goo",
        "sk-proj-your",
        "sk-ant-your",
        "api_key_here",
        "key_here"
    ]
    
    api_key_lower = api_key.lower()
    for indicator in placeholder_indicators:
        if indicator in api_key_lower:
            return False
    
    return True


def get_supported_providers() -> list:
    return ["openai", "anthropic", "google"]
