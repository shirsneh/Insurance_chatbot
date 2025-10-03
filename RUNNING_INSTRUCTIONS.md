# Running Instructions - VIA Insurance Chatbot

## Quick Start

### 1. Environment Setup

1. **Copy environment template:**
   ```bash
   cp env.example .env
   ```

2. **Configure your API keys in `.env`:**
   ```env
   # API Keys for different LLM providers
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Default LLM provider (openai, anthropic, or google)
   DEFAULT_LLM_PROVIDER=openai
   ```

### 2. Install Dependencies

**Option A: Using pip (Recommended for Python 3.9-3.11)**
```bash
pip install -r requirements.txt
```

**Option B: Using Docker (Recommended)**
```bash
docker-compose up --build
```

### 3. Run the Application

**Streamlit Web Interface:**
```bash
streamlit run app.py
```
- Open http://localhost:8501 in your browser
- The app will automatically initialize and load policy documents
- Start chatting immediately!

**FastAPI Backend (Optional):**
```bash
python api.py
```
- API available at http://localhost:8000
- Interactive docs at http://localhost:8000/docs

## Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes (if using OpenAI) |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes (if using Anthropic) |
| `GOOGLE_API_KEY` | Google API key | Yes (if using Google) |
| `DEFAULT_LLM_PROVIDER` | Default provider | No (defaults to openai) |

## Troubleshooting

### Common Issues

1. **"Chatbot not ready" error:**
   - Check your `.env` file has valid API keys
   - Ensure the API key matches the selected provider

2. **"No documents loaded" message:**
   - Add PDF files to the `policy_docs/` folder
   - Restart the application

## Success!

Once running, you should see:
- ✅ "Ready to help!" status in the sidebar
- 💬 Chat interface ready for questions
- 🤖 VIA responding to your insurance questions

**Happy chatting with VIA!**
