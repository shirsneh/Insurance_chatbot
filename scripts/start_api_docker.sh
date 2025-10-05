#!/bin/bash

echo "Starting Insurance Chatbot API with Docker..."
echo

# Check if .env file exists
if [ ! -f "config/.env" ]; then
    echo "Creating .env file from template..."
    cp "config/env.example" "config/.env"
    echo
    echo "Please edit config/.env with your API keys before running again."
    exit 1
fi

echo "Starting Docker services..."
docker-compose -f docker/docker-compose.api.yml up --build
