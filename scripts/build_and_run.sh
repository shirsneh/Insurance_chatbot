#!/bin/bash

echo "Building Insurance Chatbot Docker container..."

if [ ! -f "config/.env" ]; then
    echo "Warning: .env file not found. Creating from template..."
    cp config/env.example config/.env
    echo "Please edit config/.env file with your API keys before running the container"
    echo "Example: OPENAI_API_KEY=your_actual_api_key_here"
    exit 1
fi

if [ ! -d "policy_docs" ] || [ ! "$(ls -A policy_docs/*.pdf 2>/dev/null)" ]; then
    echo "Warning: No PDF files found in policy_docs directory"
    echo "The vector store will be created when you add PDF files to policy_docs/"
fi

echo "Building Docker image..."
cd docker
docker-compose build

if [ $? -eq 0 ]; then
    echo "Docker image built successfully"
    echo "Starting container..."
    docker-compose up
else
    echo "Docker build failed"
    exit 1
fi
