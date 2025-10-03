# Postman Testing Guide - VIA Insurance Chatbot

## Overview

This guide explains how to test the VIA Insurance Chatbot API using Postman. The API provides endpoints for chatbot initialization, document management, and chat operations.

## Setup

### 1. Import Postman Collection

1. **Download the collection file:**
   - `Insurance_Chatbot_API.postman_collection.json`

2. **Import into Postman:**
   - Open Postman
   - Click "Import" button
   - Select the JSON file or paste the collection data

### 2. Set Up Environment Variables

Create a new environment in Postman with the following variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `openai_api_key` | `your_openai_api_key_here` | OpenAI API key |
| `anthropic_api_key` | `your_anthropic_api_key_here` | Anthropic API key |
| `google_api_key` | `your_google_api_key_here` | Google API key |

### 3. Start the API Server

Before testing, make sure the API server is running:

```bash
python api.py
```

The API will be available at `http://localhost:8000`

## API Endpoints Testing

### Health & Status

#### 1. Root Endpoint
- **Method:** `GET`
- **URL:** `{{base_url}}/`
- **Description:** Get API information and status

#### 2. Health Check
- **Method:** `GET`
- **URL:** `{{base_url}}/health`
- **Description:** Check if the API is running and chatbot is initialized

### Chatbot Management

#### 3. Initialize Chatbot
- **Method:** `POST`
- **URL:** `{{base_url}}/initialize`
- **Body (JSON):**
  ```json
  {
    "provider": "openai",
    "api_key": "{{openai_api_key}}"
  }
  ```
- **Description:** Initialize the chatbot with a specific provider

#### 4. Get Available Providers
- **Method:** `GET`
- **URL:** `{{base_url}}/providers`
- **Description:** Get list of supported LLM providers

### Document Management

#### 5. List Policy Documents
- **Method:** `GET`
- **URL:** `{{base_url}}/policy-documents`
- **Description:** Get list of available policy documents

#### 6. Load Specific Document
- **Method:** `POST`
- **URL:** `{{base_url}}/load-policy-document/car_insurance_policy.pdf`
- **Description:** Load a specific policy document from the policy_docs folder

#### 7. Upload New Document
- **Method:** `POST`
- **URL:** `{{base_url}}/upload-document`
- **Body (form-data):**
  - Key: `file`
  - Type: `File`
  - Value: Select a PDF file
- **Description:** Upload and process a new policy document

### Chat Operations

#### 8. Send Message
- **Method:** `POST`
- **URL:** `{{base_url}}/chat`
- **Body (JSON):**
  ```json
  {
    "query": "What is my deductible?",
    "provider": "openai",
    "api_key": "{{openai_api_key}}"
  }
  ```
- **Description:** Send a message to the chatbot

#### 9. Get Chat History
- **Method:** `GET`
- **URL:** `{{base_url}}/chat-history`
- **Description:** Retrieve conversation history

#### 10. Clear Chat History
- **Method:** `DELETE`
- **URL:** `{{base_url}}/chat-history`
- **Description:** Clear all conversation history

## Troubleshooting

### Common Issues

1. **Connection Refused:**
   - Ensure the API server is running on port 8000
   - Check if the port is available

2. **Authentication Errors:**
   - Verify your API keys are correct
   - Check if the API keys have sufficient credits

3. **Document Not Found:**
   - Ensure PDF files are in the `policy_docs/` folder
   - Check file permissions

4. **Timeout Errors:**
   - Large documents may take time to process
   - Check server logs for processing status


## Collection Variables

If using the provided Postman collection, these variables are pre-configured:

- `{{base_url}}` - API base URL
- `{{openai_api_key}}` - OpenAI API key
- `{{anthropic_api_key}}` - Anthropic API key
- `{{google_api_key}}` - Google API key

## Success Indicators

✅ **API is working correctly when:**
- Health check returns status 200
- Chatbot initializes successfully
- Documents load without errors
- Chat responses are generated
- File uploads complete successfully

### Enjoy 💖
