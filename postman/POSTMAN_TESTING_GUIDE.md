# Postman Testing Guide - Insurance Chatbot API

## Overview

This comprehensive guide explains how to test the Insurance Chatbot API using Postman. You can test the API either locally or using Docker containers.

## Prerequisites

- Postman installed
- API keys for your preferred LLM provider (OpenAI, Anthropic, or Google)
- Python 3.9+
- Docker (for containerized testing)

## Quick Start

### Option 1: Local Testing

1. **Start the API locally:**
   ```bash
   python api.py
   ```

2. **Import Postman Collection:**
   - Open Postman
   - Click "Import" button
   - Select `postman/Insurance_Chatbot_API.postman_collection.json`

3. **Set up environment variables:**
   - Create new environment in Postman
   - Add variables (see Environment Variables section below)

### Option 2: Docker Testing (Recommended)

1. **Set up environment:**
   ```bash
   # Copy environment template
   cp config/env.example config/.env
   
   # Edit config/.env with your API keys
   # OPENAI_API_KEY=your_actual_key_here
   # ANTHROPIC_API_KEY=your_actual_key_here
   # GOOGLE_API_KEY=your_actual_key_here
   ```

2. **Start with Docker:**
   ```bash
   # Windows
   scripts\start_api_docker.bat
   
   # Linux/Mac
   ./scripts/start_api_docker.sh
   
   # Or manually
   docker-compose -f docker/docker-compose.api.yml up --build
   ```

3. **Test the API:**
   ```bash
   python scripts/test_docker_api.py
   ```

4. **Import Postman Collection:**
   - Open Postman
   - Import `postman/Insurance_Chatbot_API.postman_collection.json`

## Environment Variables

Create a new environment in Postman with these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `openai_api_key` | `your_openai_api_key_here` | OpenAI API key |
| `anthropic_api_key` | `your_anthropic_api_key_here` | Anthropic API key |
| `google_api_key` | `your_google_api_key_here` | Google API key |

## API Endpoints

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Health check and status |
| GET | `/docs` | Interactive API documentation |

### Chatbot Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/providers` | Get available LLM providers |
| POST | `/initialize` | Initialize chatbot with provider |

**Initialize Request Body:**
```json
{
  "provider": "openai",
  "api_key": "{{openai_api_key}}"
}
```

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/policy-documents` | List available policy documents |
| POST | `/load-policy-document/{filename}` | Load specific document |
| POST | `/upload-document` | Upload new document (form-data) |

### Chat Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send message to chatbot |
| GET | `/chat-history` | Get conversation history |
| DELETE | `/chat-history` | Clear conversation history |

**Chat Request Body:**
```json
{
  "query": "What is covered under my insurance policy?",
  "provider": "openai",
  "api_key": "{{openai_api_key}}"
}
```

## Testing Workflow

### Step 1: Health Check
1. Send `GET {{base_url}}/health`
2. Verify status 200 and chatbot status

### Step 2: Initialize Chatbot
1. Send `POST {{base_url}}/initialize`
2. Use your preferred provider and API key
3. Verify successful initialization

### Step 3: Load Policy Documents
1. Send `POST {{base_url}}/load-policy-document/car_insurance_policy.pdf`
2. Verify document loads successfully
3. Check that vector store is created

### Step 4: Test Chat Functionality
1. Send `POST {{base_url}}/chat`
2. Ask questions about insurance coverage
3. Verify RAG-powered responses

### Step 5: Test Additional Features
1. Upload new documents
2. Check chat history
3. Test different providers

## Docker Commands (for Docker testing)

### Start Services
```bash
# Start in background
docker-compose -f docker/docker-compose.api.yml up -d

# Start with logs
docker-compose -f docker/docker-compose.api.yml up

# Rebuild and start
docker-compose -f docker/docker-compose.api.yml up --build
```

### Stop Services
```bash
# Stop services
docker-compose -f docker/docker-compose.api.yml down

# Stop and remove volumes
docker-compose -f docker/docker-compose.api.yml down -v
```

### View Logs
```bash
# View logs
docker-compose -f docker/docker-compose.api.yml logs

# Follow logs
docker-compose -f docker/docker-compose.api.yml logs -f
```

### Debug Container
```bash
# Access container shell
docker-compose -f docker/docker-compose.api.yml exec insurance-api bash

# Check container status
docker-compose -f docker/docker-compose.api.yml ps
```

## Troubleshooting

### Common Issues

1. **Connection Refused:**
   - Ensure API server is running on port 8000
   - Check if port is available
   - For Docker: verify container is running

2. **Authentication Errors:**
   - Verify API keys are correct
   - Check API keys have sufficient credits
   - Ensure environment variables are set

3. **Document Not Found:**
   - Ensure PDF files are in `policy_docs/` folder
   - Check file permissions
   - For Docker: verify volume mounts

4. **Timeout Errors:**
   - Large documents may take time to process
   - Check server logs for processing status
   - Increase timeout settings in Postman

### Health Check Commands

```bash
# Check if API is responding
curl http://localhost:8000/health

# Check API documentation
curl http://localhost:8000/docs

# Check available providers
curl http://localhost:8000/providers
```

### Port Already in Use

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

## Advanced Testing

### Batch Testing with Postman Runner

1. Create a test collection with multiple requests
2. Use Postman Runner to execute all tests
3. Set up test scripts to validate responses
4. Use environment variables for different test scenarios

### Load Testing

```bash
# Install Apache Bench (if not installed)
# On Ubuntu/Debian: sudo apt-get install apache2-utils
# On macOS: brew install httpd

# Test health endpoint
ab -n 100 -c 10 http://localhost:8000/health

# Test chat endpoint (requires authentication)
ab -n 50 -c 5 -p chat_request.json -T application/json http://localhost:8000/chat
```

## Success Indicators

✅ **API is working correctly when:**
- Health check returns status 200
- Chatbot initializes successfully
- Documents load without errors
- Chat responses are generated
- File uploads complete successfully
- All Postman tests pass

## Collection Variables

The Postman collection includes these pre-configured variables:

- `{{base_url}}` - API base URL
- `{{openai_api_key}}` - OpenAI API key
- `{{anthropic_api_key}}` - Anthropic API key
- `{{google_api_key}}` - Google API key

## Next Steps

1. **Integration Testing:** Test with your frontend application
2. **Performance Testing:** Monitor response times and resource usage
3. **Security Testing:** Validate API security measures
4. **Production Deployment:** Deploy to your production environment

---

**Happy Testing! 🚀**

For more information, see the main [README.md](../README.md) file.
