#!/usr/bin/env python3
"""
Script to create vector store from policy documents
This script processes PDF files in the policy_docs folder and creates a FAISS vector store
"""

import os
import sys
from dotenv import load_dotenv
from rag_system import InsuranceRAGSystem
from utils import get_api_key_and_provider, validate_api_key

def main():
    """Main function to create vector store from policy documents"""
    print("🚀 Starting vector store creation...")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key and provider
    api_key, provider = get_api_key_and_provider()
    
    if not validate_api_key(api_key, provider):
        print(f"❌ Error: No valid API key found for provider '{provider}'")
        print("Please check your .env file and ensure you have set a valid API key.")
        print("\nExample .env file content:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        print("DEFAULT_LLM_PROVIDER=openai")
        return False
    
    print(f"✅ Using {provider} provider with API key configured")
    
    # Initialize RAG system
    try:
        rag_system = InsuranceRAGSystem(api_key, provider)
        print("✅ RAG system initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing RAG system: {str(e)}")
        return False
    
    # Check if policy_docs directory exists
    policy_docs_dir = "policy_docs"
    if not os.path.exists(policy_docs_dir):
        print(f"❌ Error: {policy_docs_dir} directory not found")
        return False
    
    # Find PDF files
    pdf_files = [f for f in os.listdir(policy_docs_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ Error: No PDF files found in {policy_docs_dir} directory")
        return False
    
    print(f"📄 Found {len(pdf_files)} PDF file(s): {', '.join(pdf_files)}")
    
    # Process each PDF file
    total_chunks = 0
    for pdf_file in pdf_files:
        file_path = os.path.join(policy_docs_dir, pdf_file)
        print(f"\n📖 Processing {pdf_file}...")
        
        try:
            success, message = rag_system.load_policy_document(file_path)
            if success:
                print(f"✅ {message}")
                # Extract number of chunks from message if possible
                if "chunks" in message:
                    try:
                        chunks = int(message.split()[0])
                        total_chunks += chunks
                    except:
                        pass
            else:
                print(f"❌ Error processing {pdf_file}: {message}")
                return False
                
        except Exception as e:
            print(f"❌ Exception while processing {pdf_file}: {str(e)}")
            return False
    
    # Save the vector store
    print(f"\n💾 Saving vector store...")
    try:
        rag_system.save_vectorstore()
        print("✅ Vector store saved successfully")
    except Exception as e:
        print(f"❌ Error saving vector store: {str(e)}")
        return False
    
    # Verify the vector store was created
    if os.path.exists("models/faiss_index/index.faiss"):
        print("✅ Vector store files created successfully")
        print(f"📊 Total document chunks processed: {total_chunks}")
        print("\n🎉 Vector store creation completed successfully!")
        print("You can now run the Streamlit app: streamlit run app.py")
        return True
    else:
        print("❌ Error: Vector store files were not created")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
