from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import tempfile
from chatbot import InsuranceChatbot
from dotenv import load_dotenv
from utils import get_api_key_and_provider, validate_api_key, get_supported_providers

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Insurance Chatbot API",
    description="API for insurance policy chatbot with RAG capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot_instance = None

class ChatRequest(BaseModel):
    query: str
    provider: str = "openai"
    api_key: str

class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str
    success: bool
    error: Optional[str] = None

class InitializeRequest(BaseModel):
    provider: str = "openai"
    api_key: str

class InitializeResponse(BaseModel):
    success: bool
    message: str

class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    chunks_processed: Optional[int] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Insurance Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "chatbot_initialized": chatbot_instance is not None}

@app.post("/initialize", response_model=InitializeResponse)
async def initialize_chatbot(request: InitializeRequest = None):
    """Initialize the chatbot with API key and provider"""
    global chatbot_instance
    
    try:
        if request is None or not request.api_key:
            api_key, provider = get_api_key_and_provider(request.provider if request else None)
        else:
            api_key = request.api_key
            provider = request.provider
        
        if not validate_api_key(api_key, provider):
            return InitializeResponse(
                success=False,
                message=f"No valid API key found for provider '{provider}'. Please set the appropriate environment variable."
            )
        
        chatbot_instance = InsuranceChatbot()
        success, message = chatbot_instance.initialize(api_key, provider)
        
        return InitializeResponse(
            success=success,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing chatbot: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the chatbot"""
    global chatbot_instance
    
    if not chatbot_instance:
        try:
            if not request.api_key:
                api_key, provider = get_api_key_and_provider(request.provider)
            else:
                api_key = request.api_key
                provider = request.provider
            
            if not validate_api_key(api_key, provider):
                raise HTTPException(status_code=400, detail=f"No valid API key found for provider '{provider}'. Please set the appropriate environment variable.")
            
            chatbot_instance = InsuranceChatbot()
            success, message = chatbot_instance.initialize(api_key, provider)
            
            if not success:
                raise HTTPException(status_code=400, detail=f"Failed to initialize chatbot: {message}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Chatbot not initialized and auto-initialization failed: {str(e)}")
    
    try:
        result = chatbot_instance.process_query(request.query)
        
        return ChatResponse(
            response=result.get("response", "No response generated"),
            provider=result.get("provider", "unknown"),
            model=result.get("model", "unknown"),
            success=not result.get("error", False),
            error=result.get("error") if result.get("error") else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process an insurance policy document"""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized. Please call /initialize first.")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        policy_docs_dir = "policy_docs"
        os.makedirs(policy_docs_dir, exist_ok=True)
        
        file_path = os.path.join(policy_docs_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        success, message = chatbot_instance.load_policy_document(file_path)
        
        return DocumentUploadResponse(
            success=success,
            message=message,
            chunks_processed=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/policy-documents")
async def get_policy_documents():
    """Get list of available policy documents in policy_docs folder"""
    policy_docs_dir = "policy_docs"
    
    if not os.path.exists(policy_docs_dir):
        return {"documents": [], "message": "No policy documents folder found"}
    
    try:
        policy_files = [f for f in os.listdir(policy_docs_dir) if f.endswith('.pdf')]
        return {
            "documents": policy_files,
            "count": len(policy_files),
            "directory": policy_docs_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing policy documents: {str(e)}")

@app.post("/load-policy-document/{filename}")
async def load_policy_document(filename: str):
    """Load a specific policy document from policy_docs folder"""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized. Please call /initialize first.")
    
    policy_docs_dir = "policy_docs"
    file_path = os.path.join(policy_docs_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Policy document '{filename}' not found")
    
    try:
        success, message = chatbot_instance.load_policy_document(file_path)
        return DocumentUploadResponse(
            success=success,
            message=message,
            chunks_processed=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading policy document: {str(e)}")

@app.get("/chat-history")
async def get_chat_history():
    """Get chat history"""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    return {
        "chat_history": chatbot_instance.get_chat_history(),
        "total_messages": len(chatbot_instance.get_chat_history())
    }

@app.delete("/chat-history")
async def clear_chat_history():
    """Clear chat history"""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    chatbot_instance.clear_chat_history()
    return {"message": "Chat history cleared successfully"}

@app.get("/providers")
async def get_available_providers():
    """Get list of available LLM providers"""
    return {
        "providers": [
            {
                "name": "openai",
                "display_name": "OpenAI GPT",
                "models": ["gpt-3.5-turbo", "gpt-4"]
            },
            {
                "name": "anthropic",
                "display_name": "Anthropic Claude",
                "models": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            },
            {
                "name": "google",
                "display_name": "Google Gemini",
                "models": ["gemini-pro", "gemini-pro-vision"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
