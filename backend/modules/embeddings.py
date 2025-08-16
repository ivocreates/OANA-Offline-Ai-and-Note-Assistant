import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import os

logger = logging.getLogger(__name__)

class EmbeddingsGenerator:
    """Generate embeddings for document chunks using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embeddings generator
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        self.model_name = model_name
        
        try:
            # Initialize the model
            self.model = SentenceTransformer(model_name)
            logger.info(f"Embeddings model '{model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embeddings model '{model_name}': {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of text chunks
        
        Args:
            texts: List of text chunks to embed
            
        Returns:
            Numpy array of embeddings
        """
        try:
            # Generate embeddings
            embeddings = self.model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query string
        
        Args:
            query: Query string to embed
            
        Returns:
            Numpy array of embedding
        """
        try:
            # Generate embedding
            embedding = self.model.encode([query])
            return embedding[0]
        except Exception as e:
            logger.error(f"Failed to embed query: {str(e)}")
            raise
    
    def test(self):
        """Test the embeddings generator is working"""
        try:
            # Test with a simple string
            test_text = "This is a test."
            embedding = self.model.encode([test_text])
            
            if embedding.shape[1] > 0:
                return True
            else:
                raise ValueError("Embedding model returned empty embedding")
        except Exception as e:
            logger.error(f"Embeddings model test failed: {str(e)}")
            raise ValueError(f"embeddings_generator: {str(e)}")
