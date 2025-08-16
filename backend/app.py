from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil
import uuid
from typing import List, Dict, Any, Optional
import json
import numpy as np
import logging
from pathlib import Path
import time

# Import our modules
from modules.parser import DocumentParser
from modules.embeddings import EmbeddingsGenerator
from modules.vector_store import VectorStore
from modules.llm import LocalLLM
from modules.rag import RAGEngine
from config import Settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load settings
settings = Settings()

# Create data directories if they don't exist
os.makedirs(settings.documents_dir, exist_ok=True)
os.makedirs(settings.embeddings_dir, exist_ok=True)
os.makedirs(settings.models_dir, exist_ok=True)

# Initialize the FastAPI app
app = FastAPI(title="OANA Backend", description="Offline AI Note Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_parser = DocumentParser()
embeddings_generator = EmbeddingsGenerator(model_name=settings.embeddings_model)
vector_store = VectorStore(embeddings_dir=settings.embeddings_dir)
llm = LocalLLM(model_path=os.path.join(settings.models_dir, settings.llm_model_file))
rag_engine = RAGEngine(embeddings_generator=embeddings_generator, 
                       vector_store=vector_store, 
                       llm=llm)

# Global state for document processing
processing_documents = {}

@app.get("/")
async def root():
    return {"message": "OANA Backend API is running"}

@app.post("/upload-document")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(None)
):
    """
    Upload a document (PDF, DOCX, TXT, MD) for processing
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Please upload one of: {', '.join(allowed_extensions)}"
        )
    
    # Generate a unique document ID
    doc_id = str(uuid.uuid4())
    
    # Create document directory
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    os.makedirs(doc_dir, exist_ok=True)
    
    # Save file path
    file_path = os.path.join(doc_dir, file.filename)
    
    # Save the uploaded file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Document metadata
    doc_title = title or os.path.splitext(file.filename)[0]
    doc_metadata = {
        "id": doc_id,
        "title": doc_title,
        "original_filename": file.filename,
        "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "file_path": file_path,
        "status": "processing"
    }
    
    # Save metadata
    metadata_path = os.path.join(doc_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(doc_metadata, f)
    
    # Set processing status
    processing_documents[doc_id] = "processing"
    
    # Process document in background
    background_tasks.add_task(
        process_document,
        doc_id=doc_id,
        file_path=file_path
    )
    
    return {"document_id": doc_id, "status": "processing"}

async def process_document(doc_id: str, file_path: str):
    """Background task to process a document"""
    try:
        # Parse document
        doc_chunks = document_parser.parse(file_path)
        
        # Generate embeddings
        embeddings = embeddings_generator.generate_embeddings([chunk.content for chunk in doc_chunks])
        
        # Store in vector store
        vector_store.add_document(doc_id, doc_chunks, embeddings)
        
        # Update processing status
        processing_documents[doc_id] = "completed"
        
        # Update metadata
        doc_dir = os.path.join(settings.documents_dir, doc_id)
        metadata_path = os.path.join(doc_dir, "metadata.json")
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        metadata["status"] = "completed"
        metadata["chunks_count"] = len(doc_chunks)
        metadata["processed_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
            
    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {str(e)}")
        processing_documents[doc_id] = "error"
        
        # Update metadata with error
        doc_dir = os.path.join(settings.documents_dir, doc_id)
        metadata_path = os.path.join(doc_dir, "metadata.json")
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        metadata["status"] = "error"
        metadata["error"] = str(e)
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

@app.get("/document-status/{doc_id}")
async def get_document_status(doc_id: str):
    """
    Get the processing status of a document
    """
    # Check if document exists
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    if not os.path.exists(doc_dir):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read metadata
    metadata_path = os.path.join(doc_dir, "metadata.json")
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    return metadata

@app.get("/documents")
async def list_documents():
    """
    List all uploaded documents
    """
    documents = []
    
    # Loop through document directories
    for doc_id in os.listdir(settings.documents_dir):
        doc_dir = os.path.join(settings.documents_dir, doc_id)
        
        # Skip if not a directory
        if not os.path.isdir(doc_dir):
            continue
        
        # Read metadata
        metadata_path = os.path.join(doc_dir, "metadata.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                documents.append(metadata)
    
    return {"documents": documents}

@app.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document and its associated data
    """
    # Check if document exists
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    if not os.path.exists(doc_dir):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove from vector store
    vector_store.delete_document(doc_id)
    
    # Delete document directory
    shutil.rmtree(doc_dir)
    
    return {"message": "Document deleted successfully"}

@app.post("/chat")
async def chat(
    query: str = Form(...),
    doc_id: str = Form(...),
    history: Optional[List[Dict[str, str]]] = Form(None)
):
    """
    Chat with an uploaded document using RAG
    """
    # Check if document exists and is processed
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    if not os.path.exists(doc_dir):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read metadata to check status
    metadata_path = os.path.join(doc_dir, "metadata.json")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    if metadata["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Document is still being processed or had an error"
        )
    
    # Process history if provided
    chat_history = [] if not history else history
    
    # Get response from RAG engine
    response = rag_engine.query(
        query=query,
        doc_id=doc_id,
        chat_history=chat_history
    )
    
    # Return response
    return {
        "query": query,
        "response": response,
        "document_id": doc_id
    }

@app.post("/summarize")
async def summarize_document(
    doc_id: str = Form(...),
    section: Optional[str] = Form(None)
):
    """
    Generate a summary of the document or a specific section
    """
    # Check if document exists and is processed
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    if not os.path.exists(doc_dir):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read metadata to check status
    metadata_path = os.path.join(doc_dir, "metadata.json")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    if metadata["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Document is still being processed or had an error"
        )
    
    # Generate summary
    summary = rag_engine.summarize(doc_id=doc_id, section=section)
    
    return {
        "document_id": doc_id,
        "section": section,
        "summary": summary
    }

@app.get("/topics/{doc_id}")
async def get_document_topics(doc_id: str):
    """
    Get the topics/sections detected in a document
    """
    # Check if document exists
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    if not os.path.exists(doc_dir):
        raise HTTPException(status_code=404, detail="Document not found")
    
    topics = rag_engine.get_topics(doc_id)
    
    return {
        "document_id": doc_id,
        "topics": topics
    }

@app.get("/models")
async def list_available_models():
    """
    List all available local LLM models
    """
    models = []
    
    # List all files in the models directory
    for file in os.listdir(settings.models_dir):
        if file.endswith('.gguf'):
            models.append({
                "filename": file,
                "path": os.path.join(settings.models_dir, file),
                "size_mb": round(os.path.getsize(os.path.join(settings.models_dir, file)) / (1024 * 1024), 2)
            })
    
    return {"models": models}

@app.post("/change-model")
async def change_llm_model(
    model_file: str = Form(...)
):
    """
    Change the active LLM model
    """
    model_path = os.path.join(settings.models_dir, model_file)
    
    # Check if model exists
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model file not found")
    
    # Reload LLM with new model
    try:
        global llm
        llm = LocalLLM(model_path=model_path)
        
        # Update rag_engine
        global rag_engine
        rag_engine = RAGEngine(
            embeddings_generator=embeddings_generator,
            vector_store=vector_store,
            llm=llm
        )
        
        # Update settings
        settings.llm_model_file = model_file
        
        return {"message": f"Model changed to {model_file}"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading model: {str(e)}"
        )

@app.post("/study-tips")
async def get_study_tips(
    doc_id: str = Form(...),
    subject: Optional[str] = Form(None)
):
    """
    Generate study tips for a specific document and subject
    """
    # Check if document exists and is processed
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    if not os.path.exists(doc_dir):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read metadata to check status
    metadata_path = os.path.join(doc_dir, "metadata.json")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    if metadata["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Document is still being processed or had an error"
        )
    
    # Prepare query for study tips
    subject_text = f" for {subject}" if subject else ""
    query = f"Generate 5 effective study tips{subject_text} based on this document."
    
    # Get response from RAG engine
    tips = rag_engine.query(
        query=query,
        doc_id=doc_id,
        chat_history=[]
    )
    
    return {
        "document_id": doc_id,
        "subject": subject,
        "study_tips": tips
    }

@app.post("/flashcards")
async def generate_flashcards(
    doc_id: str = Form(...),
    count: int = Form(10)
):
    """
    Generate flashcards for studying a document
    """
    # Check if document exists and is processed
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    if not os.path.exists(doc_dir):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read metadata to check status
    metadata_path = os.path.join(doc_dir, "metadata.json")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    if metadata["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Document is still being processed or had an error"
        )
    
    # Prepare query for flashcards
    query = f"Generate {count} flashcards in JSON format with 'question' and 'answer' fields based on this document."
    
    # Get response from RAG engine
    flashcards_response = rag_engine.query(
        query=query,
        doc_id=doc_id,
        chat_history=[]
    )
    
    # Try to extract JSON from response
    try:
        # Look for JSON in the response
        import re
        json_match = re.search(r'```json\n([\s\S]*?)\n```', flashcards_response) or \
                     re.search(r'```\n([\s\S]*?)\n```', flashcards_response) or \
                     re.search(r'\[([\s\S]*?)\]', flashcards_response)
        
        if json_match:
            json_str = json_match.group(1)
            if not json_str.startswith('['):
                json_str = '[' + json_str + ']'
            flashcards = json.loads(json_str)
        else:
            # If no JSON format is found, return the raw response
            flashcards = {"raw_response": flashcards_response}
    except Exception as e:
        logger.error(f"Error parsing flashcards JSON: {str(e)}")
        flashcards = {"raw_response": flashcards_response, "error": str(e)}
    
    return {
        "document_id": doc_id,
        "flashcards": flashcards
    }

@app.post("/chat-conversation")
async def chat_conversation(
    query: str = Form(...),
    doc_id: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    conversation_title: Optional[str] = Form(None)
):
    """
    Chat with an uploaded document and save the conversation to the server
    """
    # Check if document exists and is processed
    doc_dir = os.path.join(settings.documents_dir, doc_id)
    if not os.path.exists(doc_dir):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read metadata to check status
    metadata_path = os.path.join(doc_dir, "metadata.json")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    if metadata["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Document is still being processed or had an error"
        )
    
    # Create or load conversation
    if conversation_id:
        conversation_path = os.path.join(settings.conversations_dir, f"{conversation_id}.json")
        if os.path.exists(conversation_path):
            with open(conversation_path, "r") as f:
                conversation = json.load(f)
            chat_history = conversation.get("messages", [])
        else:
            # If conversation ID doesn't exist, create a new one
            conversation_id = str(uuid.uuid4())
            conversation_path = os.path.join(settings.conversations_dir, f"{conversation_id}.json")
            chat_history = []
            conversation = {
                "id": conversation_id,
                "title": conversation_title or "Untitled Conversation",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "document_id": doc_id,
                "messages": chat_history
            }
    else:
        # Create new conversation
        conversation_id = str(uuid.uuid4())
        conversation_path = os.path.join(settings.conversations_dir, f"{conversation_id}.json")
        chat_history = []
        conversation = {
            "id": conversation_id,
            "title": conversation_title or "Untitled Conversation",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "document_id": doc_id,
            "messages": chat_history
        }
    
    # Add user message to history
    user_message = {"role": "user", "content": query}
    chat_history.append(user_message)
    
    # Get response from RAG engine
    response = rag_engine.query(
        query=query,
        doc_id=doc_id,
        chat_history=chat_history
    )
    
    # Add assistant response to history
    assistant_message = {"role": "assistant", "content": response}
    chat_history.append(assistant_message)
    
    # Update and save conversation
    conversation["messages"] = chat_history
    with open(conversation_path, "w") as f:
        json.dump(conversation, f, indent=2)
    
    # Return response
    return {
        "conversation_id": conversation_id,
        "query": query,
        "response": response,
        "document_id": doc_id,
        "history": chat_history
    }

@app.get("/conversations")
async def list_conversations():
    """
    List all conversation history stored on the server
    """
    conversations = []
    
    # Loop through conversation files
    for filename in os.listdir(settings.conversations_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(settings.conversations_dir, filename)
            with open(file_path, 'r') as f:
                conversation = json.load(f)
                # Add a summary of the conversation
                conversation_summary = {
                    "id": os.path.splitext(filename)[0],
                    "title": conversation.get("title", "Untitled Conversation"),
                    "timestamp": conversation.get("timestamp", "Unknown"),
                    "document_id": conversation.get("document_id", None),
                    "message_count": len(conversation.get("messages", [])),
                }
                conversations.append(conversation_summary)
    
    return {"conversations": conversations}

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation by ID
    """
    conversation_path = os.path.join(settings.conversations_dir, f"{conversation_id}.json")
    if not os.path.exists(conversation_path):
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    with open(conversation_path, "r") as f:
        conversation = json.load(f)
    
    return conversation

@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a specific conversation by ID
    """
    conversation_path = os.path.join(settings.conversations_dir, f"{conversation_id}.json")
    if not os.path.exists(conversation_path):
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    os.remove(conversation_path)
    
    return {"message": "Conversation deleted successfully"}

@app.get("/health")
async def health_check():
    """
    Check the health of the API and its components
    """
    health_status = {
        "status": "healthy",
        "components": {
            "document_parser": "ok",
            "embeddings_generator": "ok",
            "vector_store": "ok",
            "llm": "ok",
        }
    }
    
    # Check components
    try:
        # Basic tests for each component
        document_parser.test()
        embeddings_generator.test()
        vector_store.test()
        llm.test()
    except Exception as e:
        health_status["status"] = "unhealthy"
        component = str(e).split(":")[0] if ":" in str(e) else "unknown"
        health_status["components"][component] = str(e)
    
    return health_status

# Run the application
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
