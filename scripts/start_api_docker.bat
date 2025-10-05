@echo off
echo Starting Insurance Chatbot API with Docker...
echo.

REM Check if .env file exists
if not exist "config\.env" (
    echo Creating .env file from template...
    copy "config\env.example" "config\.env"
    echo.
    echo Please edit config\.env with your API keys before running again.
    pause
    exit /b 1
)

echo Starting Docker services...
docker-compose -f docker/docker-compose.api.yml up --build

pause
