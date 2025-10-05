@echo off

echo Building Insurance Chatbot Docker container...

if not exist ".env" (
    echo Warning: .env file not found. Creating from template...
    copy env.example .env
    echo Please edit .env file with your API keys before running the container
    echo Example: OPENAI_API_KEY=your_actual_api_key_here
    pause
    exit /b 1
)

if not exist "policy_docs\*.pdf" (
    echo Warning: No PDF files found in policy_docs directory
    echo The vector store will be created when you add PDF files to policy_docs\
)

echo Building Docker image...
docker-compose build

if %errorlevel% equ 0 (
    echo Docker image built successfully
    echo Starting container...
    docker-compose up
) else (
    echo Docker build failed
    pause
    exit /b 1
)
