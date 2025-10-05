#!/usr/bin/env python3
"""
Test script to verify Docker API setup
"""

import requests
import json
import time
import sys

def test_api_endpoints():
    """Test the API endpoints to ensure Docker setup is working"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Insurance Chatbot API...")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Root endpoint working")
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Root endpoint error: {e}")
        return False
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Health check working")
            health_data = response.json()
            print(f"   📊 Status: {health_data.get('status', 'Unknown')}")
            print(f"   🤖 Chatbot initialized: {health_data.get('chatbot_initialized', False)}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 3: Providers endpoint
    print("\n3. Testing providers endpoint...")
    try:
        response = requests.get(f"{base_url}/providers", timeout=10)
        if response.status_code == 200:
            print("   ✅ Providers endpoint working")
            providers = response.json()
            print(f"   🔧 Available providers: {len(providers.get('providers', []))}")
        else:
            print(f"   ❌ Providers endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Providers endpoint error: {e}")
        return False
    
    # Test 4: Policy documents
    print("\n4. Testing policy documents endpoint...")
    try:
        response = requests.get(f"{base_url}/policy-documents", timeout=10)
        if response.status_code == 200:
            print("   ✅ Policy documents endpoint working")
            docs = response.json()
            print(f"   📄 Available documents: {len(docs.get('documents', []))}")
        else:
            print(f"   ❌ Policy documents endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Policy documents endpoint error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All basic tests passed! API is ready for Postman testing.")
    print("\nNext steps:")
    print("1. Import the Postman collection")
    print("2. Set up your environment variables")
    print("3. Initialize the chatbot with your API key")
    print("4. Start testing the chat functionality")
    
    return True

if __name__ == "__main__":
    print("Waiting for API to start...")
    time.sleep(5)  # Give the API time to start
    
    success = test_api_endpoints()
    if not success:
        print("\n❌ Some tests failed. Check the Docker logs:")
        print("   docker-compose -f docker/docker-compose.api.yml logs")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)
