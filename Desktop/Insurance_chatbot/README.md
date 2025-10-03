# Insurance Chatbot with RAG

A comprehensive insurance policy chatbot that uses Retrieval-Augmented Generation (RAG) to answer questions based on insurance policy documents. The chatbot supports multiple LLM providers (OpenAI, Anthropic Claude, Google Gemini) and provides both a web UI and REST API.

## Features

- **RAG System**: Processes insurance policy documents and provides context-aware answers
- **Multiple LLM Support**: OpenAI GPT, Anthropic Claude, Google Gemini
- **Friendly UI**: Beautiful Streamlit interface with chat history
- **REST API**: Complete FastAPI backend for integration
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Postman Collection**: Ready-to-use API testing collection
- **Document Processing**: Upload and process PDF insurance policies

## Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)
- API key for a LLM provider:
  - OpenAI API key
  - Anthropic API key
  - Google API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Insurance_chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your API keys
   ```

4. **Run the application**
   ```bash
   # Streamlit UI
   streamlit run app.py
   
   # FastAPI backend (in another terminal)
   python api.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Streamlit UI: http://localhost:8501
   - FastAPI docs: http://localhost:8000/docs

## Usage

### Web Interface

1. Open http://localhost:8501 in your browser
2. Enter your API key and select a provider in the sidebar
3. Click "Initialize Chatbot"
4. **Load existing policy documents** from the `policy_docs` folder, or upload new ones
5. Start asking questions about your policy!

### Using Policy Documents

The system automatically looks for PDF files in the `policy_docs` folder. You can:

- **Add new policy documents**: Place PDF files directly in the `policy_docs` folder
- **Load existing documents**: Use the buttons in the web interface to load specific documents
- **Upload via API**: Use the `/upload-document` endpoint to upload new documents
- **List available documents**: Use the `/policy-documents` endpoint to see all available PDFs

### API Usage

#### Initialize the chatbot
```bash
curl -X POST "http://localhost:8000/initialize" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "api_key": "your-api-key"
  }'
```

#### List available policy documents
```bash
curl -X GET "http://localhost:8000/policy-documents"
```

#### Load a specific policy document
```bash
curl -X POST "http://localhost:8000/load-policy-document/car_insurance_policy.pdf"
```

#### Upload a new policy document
```bash
curl -X POST "http://localhost:8000/upload-document" \
  -F "file=@policy.pdf"
```

#### Send a message
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is my deductible?",
    "provider": "openai",
    "api_key": "your-api-key"
  }'
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Default provider
DEFAULT_LLM_PROVIDER=openai

# Model configurations
OPENAI_MODEL=gpt-3.5-turbo
ANTHROPIC_MODEL=claude-3-sonnet-20240229
GOOGLE_MODEL=gemini-pro
```

## Project Structure

```
Insurance_chatbot/
├── app.py                          # Streamlit UI
├── api.py                          # FastAPI backend
├── chatbot.py                      # Main chatbot class
├── rag_system.py                   # RAG implementation
├── llm_handlers.py                 # LLM provider handlers
├── requirements.txt                
├── Dockerfile                      
├── docker-compose.yml              
├── env.example                     # Environment variables template
├── Insurance_Chatbot_API.postman_collection.json 
├── policy_docs/                    
│   └── car_insurance_policy.pdf    # Sample policy document
├── data/                           
├── models/                         # Vector store storage
└── README.md                       
```

## Testing with Postman

1. Import the `Insurance_Chatbot_API.postman_collection.json` file into Postman
2. Set up environment variables in Postman:
   - `base_url`: http://localhost:8000
   - `openai_api_key`: Your OpenAI API key
   - `anthropic_api_key`: Your Anthropic API key
   - `google_api_key`: Your Google API key
3. Run the collection to test all endpoints

## API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check

### Chatbot Management
- `POST /initialize` - Initialize chatbot with API key
- `GET /providers` - Get available LLM providers

### Document Management
- `GET /policy-documents` - Get list of available policy documents
- `POST /load-policy-document/{filename}` - Load a specific policy document from policy_docs folder
- `POST /upload-document` - Upload and process new policy document

### Chat Operations
- `POST /chat` - Send message to chatbot
- `GET /chat-history` - Get chat history
- `DELETE /chat-history` - Clear chat history

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API keys are correctly set in the `.env` file
2. **Document Processing**: Make sure PDF files are not corrupted and are readable
3. **Memory Issues**: For large documents, consider reducing chunk size
4. **Rate Limiting**: Some providers have rate limits; consider adding delays