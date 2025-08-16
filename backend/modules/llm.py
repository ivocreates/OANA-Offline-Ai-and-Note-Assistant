import os
import logging
import time
import ctypes
import glob
from typing import List, Dict, Any, Optional
from llama_cpp import Llama

logger = logging.getLogger(__name__)

class LocalLLM:
    """Interface for local LLMs using llama.cpp Python bindings"""
    
    def __init__(self, model_path: str, fallback_dir: Optional[str] = None):
        """
        Initialize the local LLM
        
        Args:
            model_path: Path to the GGUF model file
            fallback_dir: Optional directory to look for alternative models if the specified one fails
        """
        self.model_path = model_path
        self.fallback_dir = fallback_dir or os.path.dirname(model_path)
        self.model_loaded = False
        
        try:
            # Check if model file exists
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Try to initialize the model with standard parameters
            try:
                self._initialize_model(model_path)
            except Exception as e:
                logger.warning(f"Failed to load model with standard parameters: {str(e)}")
                # Try with phi2 specific parameters
                self._initialize_model_with_params(model_path)
            
        except Exception as e:
            logger.error(f"Failed to load LLM model from {model_path}: {str(e)}")
            
            # Try to find alternative models
            if self._try_fallback_models():
                logger.info(f"Successfully loaded fallback model")
            else:
                # If all fails, raise the original exception
                raise
    
    def _initialize_model(self, model_path: str):
        """Initialize model with default parameters"""
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,  # Context window
            n_threads=4,  # Number of CPU threads
            n_gpu_layers=0  # No GPU by default
        )
        self.model_loaded = True
        logger.info(f"Successfully loaded LLM model from {model_path}")
    
    def _initialize_model_with_params(self, model_path: str):
        """Initialize model with specific parameters for different architectures"""
        model_basename = os.path.basename(model_path).lower()
        
        # Parameters based on model type
        if 'phi' in model_basename:
            # Phi-2 specific parameters
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,  # Smaller context for Phi
                n_threads=4,
                n_gpu_layers=0,
                seed=42,
                verbose=False,
                model_format="gguf",  # Explicitly set format
                use_mmap=True,
                use_mlock=False,
                logits_all=False,
                embedding=False,
                rope_freq_base=0,
                rope_freq_scale=0
            )
        elif 'mistral' in model_basename:
            # Mistral specific parameters
            self.llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_threads=4,
                n_gpu_layers=0,
                model_format="gguf",
                verbose=False
            )
        else:
            # Generic attempt with different parameters
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0,
                verbose=False
            )
            
        self.model_loaded = True
        logger.info(f"Successfully loaded LLM model from {model_path} with model-specific parameters")
    
    def _try_fallback_models(self) -> bool:
        """Try to load other GGUF models in the fallback directory"""
        if not os.path.exists(self.fallback_dir):
            logger.error(f"Fallback directory does not exist: {self.fallback_dir}")
            return False
        
        # Find all GGUF models in the fallback directory
        model_files = glob.glob(os.path.join(self.fallback_dir, "*.gguf"))
        
        # Remove the original model path from the list
        if self.model_path in model_files:
            model_files.remove(self.model_path)
            
        if not model_files:
            logger.error(f"No fallback models found in {self.fallback_dir}")
            return False
        
        # Try each model in order
        for model_file in model_files:
            logger.info(f"Trying fallback model: {model_file}")
            try:
                # Try standard initialization first
                try:
                    self._initialize_model(model_file)
                    self.model_path = model_file  # Update the model path
                    return True
                except:
                    # If that fails, try with model-specific parameters
                    self._initialize_model_with_params(model_file)
                    self.model_path = model_file  # Update the model path
                    return True
            except Exception as e:
                logger.warning(f"Failed to load fallback model {model_file}: {str(e)}")
                continue
        
        return False
    
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
