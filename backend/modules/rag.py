import logging
import time
from typing import List, Dict, Any, Optional, Union

from modules.parser import DocumentChunk
from modules.embeddings import EmbeddingsGenerator
from modules.vector_store import VectorStore
from modules.llm import LocalLLM

logger = logging.getLogger(__name__)

class RAGEngine:
    """Retrieval-Augmented Generation engine for query answering"""
    
    def __init__(self, 
                 embeddings_generator: EmbeddingsGenerator,
                 vector_store: VectorStore,
                 llm: LocalLLM,
                 top_k: int = 5):
        """
        Initialize the RAG engine
        
        Args:
            embeddings_generator: EmbeddingsGenerator instance
            vector_store: VectorStore instance
            llm: LocalLLM instance
            top_k: Number of top documents to retrieve
        """
        self.embeddings_generator = embeddings_generator
        self.vector_store = vector_store
        self.llm = llm
        self.top_k = top_k
    
    def query(self, 
             query: str, 
             doc_id: str,
             chat_history: List[Dict[str, str]] = None) -> str:
        """
        Generate an answer for a query using RAG
        
        Args:
            query: User query string
            doc_id: Document ID to search
            chat_history: Optional list of previous chat messages
            
        Returns:
            Generated answer
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings_generator.embed_query(query)
            
            # Retrieve relevant chunks
            chunks = self.vector_store.search(
                doc_id=doc_id,
                query_embedding=query_embedding,
                top_k=self.top_k
            )
            
            # Create context from chunks
            context = "\n\n".join([
                f"{chunk.section + ': ' if chunk.section else ''}{chunk.content}" 
                for chunk in chunks
            ])
            
            # Format chat history if provided
            history_text = ""
            if chat_history:
                history_text = "\n".join([
                    f"User: {msg['user']}\nAssistant: {msg['assistant']}"
                    for msg in chat_history[-3:]  # Use last 3 exchanges for context
                ])
            
            # Build prompt
            prompt = self._build_rag_prompt(query, context, history_text)
            
            # Generate answer
            answer = self.llm.generate(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.7,
                stop_sequences=["User:", "\n\nUser:"]
            )
            
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"I'm sorry, I couldn't process your request. Error: {str(e)}"
    
    def summarize(self, doc_id: str, section: Optional[str] = None) -> str:
        """
        Generate a summary of a document or section
        
        Args:
            doc_id: Document ID
            section: Optional section name to summarize
            
        Returns:
            Generated summary
        """
        try:
            # Get document chunks
            chunks = self.vector_store.get_document_chunks(doc_id)
            
            # Filter by section if specified
            if section:
                chunks = [c for c in chunks if c.section == section]
            
            if not chunks:
                return "No content found to summarize."
            
            # Combine content from chunks
            content = "\n\n".join([chunk.content for chunk in chunks])
            
            # Build summary prompt
            prompt = self._build_summary_prompt(content)
            
            # Generate summary
            summary = self.llm.generate(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.7
            )
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"I'm sorry, I couldn't generate a summary. Error: {str(e)}"
    
    def get_topics(self, doc_id: str) -> List[str]:
        """
        Get the topics/sections in a document
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of topic strings
        """
        try:
            # Get document chunks
            chunks = self.vector_store.get_document_chunks(doc_id)
            
            # Extract sections
            sections = set()
            for chunk in chunks:
                if chunk.section:
                    sections.add(chunk.section)
            
            return list(sections)
            
        except Exception as e:
            logger.error(f"Error getting topics: {str(e)}")
            return []
    
    def _build_rag_prompt(self, query: str, context: str, history: str = "") -> str:
        """Build RAG prompt with context"""
        
        if history:
            prompt = f"""You are OANA, a helpful Offline AI Note Assistant. You provide answers based on the provided context from user notes. If the information is not in the context, say you don't know rather than making up information.

Previous conversation:
{history}

Context information from user's notes:
{context}

User: {query}
Assistant: """
        else:
            prompt = f"""You are OANA, a helpful Offline AI Note Assistant. You provide answers based on the provided context from user notes. If the information is not in the context, say you don't know rather than making up information.

Context information from user's notes:
{context}

User: {query}
Assistant: """
        
        return prompt
    
    def _build_summary_prompt(self, content: str) -> str:
        """Build summary prompt"""
        
        prompt = f"""You are OANA, a helpful Offline AI Note Assistant. Summarize the following content clearly and concisely, preserving key information, main ideas, and important details:

{content}

Summary:"""
        
        return prompt
