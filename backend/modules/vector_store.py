import os
import json
import logging
import faiss
import numpy as np
from typing import List, Dict, Any, Optional
import pickle
from pathlib import Path

from modules.parser import DocumentChunk

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector database for storing and retrieving document embeddings"""
    
    def __init__(self, embeddings_dir: str):
        """
        Initialize the vector store
        
        Args:
            embeddings_dir: Directory to store embeddings and indices
        """
        self.embeddings_dir = Path(embeddings_dir)
        os.makedirs(self.embeddings_dir, exist_ok=True)
        
        # In-memory storage of document chunks
        self.document_chunks = {}
        
        # In-memory FAISS indices
        self.indices = {}
        
        # Load existing indices if available
        self._load_indices()
    
    def _load_indices(self):
        """Load all existing document indices"""
        try:
            # Find all document directories
            for doc_dir in self.embeddings_dir.iterdir():
                if doc_dir.is_dir():
                    doc_id = doc_dir.name
                    
                    # Check if index and chunks files exist
                    index_path = doc_dir / "faiss_index.bin"
                    chunks_path = doc_dir / "chunks.pkl"
                    
                    if index_path.exists() and chunks_path.exists():
                        # Load FAISS index
                        index = faiss.read_index(str(index_path))
                        
                        # Load chunks
                        with open(chunks_path, 'rb') as f:
                            chunks = pickle.load(f)
                        
                        # Store in memory
                        self.indices[doc_id] = index
                        self.document_chunks[doc_id] = chunks
                        
                        logger.info(f"Loaded index and chunks for document {doc_id}")
        
        except Exception as e:
            logger.error(f"Error loading indices: {str(e)}")
    
    def add_document(self, doc_id: str, chunks: List[DocumentChunk], embeddings: np.ndarray):
        """
        Add or update a document in the vector store
        
        Args:
            doc_id: Document identifier
            chunks: List of document chunks
            embeddings: Numpy array of embeddings for the chunks
        """
        try:
            # Create document directory
            doc_dir = self.embeddings_dir / doc_id
            os.makedirs(doc_dir, exist_ok=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            
            # Add embeddings to index
            index.add(embeddings)
            
            # Store in memory
            self.indices[doc_id] = index
            self.document_chunks[doc_id] = chunks
            
            # Save to disk
            faiss.write_index(index, str(doc_dir / "faiss_index.bin"))
            
            with open(doc_dir / "chunks.pkl", 'wb') as f:
                pickle.dump(chunks, f)
            
            logger.info(f"Added document {doc_id} with {len(chunks)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding document {doc_id} to vector store: {str(e)}")
            raise
    
    def search(self, doc_id: str, query_embedding: np.ndarray, top_k: int = 5) -> List[DocumentChunk]:
        """
        Search for similar chunks in a document
        
        Args:
            doc_id: Document identifier
            query_embedding: Embedding of the query
            top_k: Number of top results to return
            
        Returns:
            List of DocumentChunk objects
        """
        if doc_id not in self.indices:
            raise ValueError(f"Document {doc_id} not found in vector store")
        
        try:
            # Get index and chunks
            index = self.indices[doc_id]
            chunks = self.document_chunks[doc_id]
            
            # Search
            D, I = index.search(query_embedding.reshape(1, -1), top_k)
            
            # Get matching chunks
            results = [chunks[i] for i in I[0] if i < len(chunks)]
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching document {doc_id}: {str(e)}")
            raise
    
    def delete_document(self, doc_id: str):
        """
        Delete a document from the vector store
        
        Args:
            doc_id: Document identifier
        """
        try:
            # Remove from memory
            if doc_id in self.indices:
                del self.indices[doc_id]
            
            if doc_id in self.document_chunks:
                del self.document_chunks[doc_id]
            
            # Remove from disk
            doc_dir = self.embeddings_dir / doc_id
            if doc_dir.exists():
                import shutil
                shutil.rmtree(doc_dir)
                
            logger.info(f"Deleted document {doc_id} from vector store")
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            raise
    
    def get_document_chunks(self, doc_id: str) -> List[DocumentChunk]:
        """
        Get all chunks for a document
        
        Args:
            doc_id: Document identifier
            
        Returns:
            List of DocumentChunk objects
        """
        if doc_id not in self.document_chunks:
            raise ValueError(f"Document {doc_id} not found in vector store")
        
        return self.document_chunks[doc_id]
    
    def test(self):
        """Test if the vector store is working properly"""
        try:
            # Create a simple test index
            dimension = 128
            test_index = faiss.IndexFlatL2(dimension)
            
            # Add a random vector
            test_vector = np.random.random(dimension).astype('float32').reshape(1, dimension)
            test_index.add(test_vector)
            
            # Search
            D, I = test_index.search(test_vector, 1)
            
            # Verify
            if I[0][0] == 0:
                return True
            else:
                raise ValueError("FAISS test search failed")
        
        except Exception as e:
            logger.error(f"Vector store test failed: {str(e)}")
            raise ValueError(f"vector_store: {str(e)}")
