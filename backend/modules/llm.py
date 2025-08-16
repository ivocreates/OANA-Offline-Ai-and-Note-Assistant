import os
import logging
import time
import ctypes
from typing import List, Dict, Any, Optional
from llama_cpp import Llama

logger = logging.getLogger(__name__)

class LocalLLM:
    """Interface for local LLMs using llama.cpp Python bindings"""
    
    def __init__(self, model_path: str):
        """
        Initialize the local LLM
        
        Args:
            model_path: Path to the GGUF model file
        """
        self.model_path = model_path
        
        try:
            # Check if model file exists
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Initialize model
            self.llm = Llama(
                model_path=model_path,
                n_ctx=4096,  # Context window
                n_threads=4,  # Number of CPU threads
                n_gpu_layers=0  # No GPU by default
            )
            
            logger.info(f"Successfully loaded LLM model from {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load LLM model from {model_path}: {str(e)}")
            raise
    
    def generate(self, prompt: str, 
                 max_tokens: int = 1024, 
                 temperature: float = 0.7,
                 stop_sequences: List[str] = None) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            stop_sequences: Optional list of strings to stop generation
            
        Returns:
            Generated text
        """
        try:
            # Generate text
            output = self.llm(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop_sequences or [],
                echo=False
            )
            
            # Extract text from output
            if isinstance(output, dict):
                return output.get("choices", [{}])[0].get("text", "")
            elif isinstance(output, list) and len(output) > 0:
                return output[0].get("text", "")
            else:
                return ""
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: Failed to generate text. {str(e)}"
    
    def test(self):
        """Test if the LLM is working properly"""
        try:
            # Simple test prompt
            test_prompt = "Hello, my name is"
            
            # Generate with minimal tokens
            output = self.generate(test_prompt, max_tokens=5, temperature=0.1)
            
            # Check output
            if output and isinstance(output, str):
                return True
            else:
                raise ValueError("LLM test failed: empty or invalid response")
                
        except Exception as e:
            logger.error(f"LLM test failed: {str(e)}")
            raise ValueError(f"llm: {str(e)}")
