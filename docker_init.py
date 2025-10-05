#!/usr/bin/env python3
"""
Docker initialization script to create vector store from policy documents
This script runs during Docker build to pre-process PDF files and create the FAISS vector store
"""

import os
import sys
import logging
from dotenv import load_dotenv
from rag_system import InsuranceRAGSystem
from utils import get_api_key_and_provider, validate_api_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_vectorstore():
    """Create vector store from policy documents"""
    logger.info("Starting vector store creation in Docker container...")
    
    load_dotenv()
    
    api_key, provider = get_api_key_and_provider()
    
    if not validate_api_key(api_key, provider):
        logger.warning(f"No valid API key found for provider '{provider}'")
        logger.info("Vector store will be created when the app starts with valid API keys")
        return True  # Don't fail the build, just skip vector store creation
    
    logger.info(f"Using {provider} provider with API key configured")
   
    try:
        rag_system = InsuranceRAGSystem(api_key, provider)
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}")
        return False

    policy_docs_dir = "policy_docs"
    if not os.path.exists(policy_docs_dir):
        logger.warning(f"⚠️  {policy_docs_dir} directory not found")
        return True  # Don't fail the build
    
    pdf_files = [f for f in os.listdir(policy_docs_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"⚠️  No PDF files found in {policy_docs_dir} directory")
        return True  # Don't fail the build
    
    logger.info(f"📄 Found {len(pdf_files)} PDF file(s): {', '.join(pdf_files)}")
    
    total_chunks = 0
    for pdf_file in pdf_files:
        file_path = os.path.join(policy_docs_dir, pdf_file)
        logger.info(f"📖 Processing {pdf_file}...")
        
        try:
            success, message = rag_system.load_policy_document(file_path)
            if success:
                logger.info(f"{message}")
                if "chunks" in message:
                    try:
                        chunks = int(message.split()[0])
                        total_chunks += chunks
                    except:
                        pass
            else:
                logger.error(f"Error processing {pdf_file}: {message}")
                return False
                
        except Exception as e:
            logger.error(f"Exception while processing {pdf_file}: {str(e)}")
            return False
    
    logger.info(f"Saving vector store...")
    try:
        rag_system.save_vectorstore()
        logger.info("Vector store saved successfully")
    except Exception as e:
        logger.error(f"Error saving vector store: {str(e)}")
        return False
    
    if os.path.exists("models/faiss_index/index.faiss"):
        logger.info("Vector store files created successfully")
        logger.info(f"Total document chunks processed: {total_chunks}")
        logger.info("Vector store creation completed successfully!")
        return True
    else:
        logger.error("Error: Vector store files were not created")
        return False

if __name__ == "__main__":
    success = create_vectorstore()
    if success:
        logger.info("Docker initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Docker initialization failed")
        sys.exit(1)
