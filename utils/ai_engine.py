"""
AI Engine for handling local LLM inference
Supports multiple backends: llama-cpp-python, Ollama, transformers
"""

import os
import json
from typing import Optional, List, Dict

# Try different AI backends
LLAMA_CPP_AVAILABLE = False
OLLAMA_AVAILABLE = False
TRANSFORMERS_AVAILABLE = False

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    pass

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    pass

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    pass


class AIEngine:
    def __init__(self, model_path=None, backend="auto"):
        self.model = None
        self.backend = None
        self.model_path = model_path
        self.is_loaded = False
        self.config = self._load_config()
        
        # Initialize with best available backend
        if backend == "auto":
            self._auto_detect_backend()
        else:
            self._initialize_backend(backend)
            
    def _load_config(self):
        """Load configuration settings"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        default_config = {
            "temperature": 0.7,
            "max_tokens": 512,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "system_prompt": "You are a helpful AI assistant. Provide accurate, helpful, and concise responses."
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            return default_config
        except:
            return default_config
            
    def _auto_detect_backend(self):
        """Auto-detect best available backend"""
        # Check for local GGUF models
        models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
        gguf_files = []
        
        if os.path.exists(models_dir):
            gguf_files = [f for f in os.listdir(models_dir) if f.endswith('.gguf')]
            
        # Priority order: llama-cpp > ollama > transformers > fallback
        if LLAMA_CPP_AVAILABLE and gguf_files:
            self._initialize_backend("llama-cpp")
        elif OLLAMA_AVAILABLE:
            self._initialize_backend("ollama")
        elif TRANSFORMERS_AVAILABLE:
            self._initialize_backend("transformers")
        else:
            self._initialize_backend("fallback")
            
    def _initialize_backend(self, backend):
        """Initialize specific backend"""
        self.backend = backend
        
        try:
            if backend == "llama-cpp":
                self._init_llama_cpp()
            elif backend == "ollama":
                self._init_ollama()
            elif backend == "transformers":
                self._init_transformers()
            else:
                self._init_fallback()
                
        except Exception as e:
            print(f"Failed to initialize {backend} backend: {e}")
            if backend != "fallback":
                print("Falling back to mock backend...")
                self._init_fallback()
                
    def _init_llama_cpp(self):
        """Initialize llama-cpp-python backend"""
        if not LLAMA_CPP_AVAILABLE:
            raise Exception("llama-cpp-python not available")
            
        models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
        model_files = []
        
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith('.gguf')]
            
        if not model_files:
            raise Exception("No GGUF model files found in models directory")
            
        # Use the first available model
        model_path = os.path.join(models_dir, model_files[0])
        
        print(f"Loading model: {model_files[0]}")
        self.model = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context length
            n_threads=4,  # Number of CPU threads
            verbose=False
        )
        
        self.is_loaded = True
        print(f"llama-cpp backend initialized with {model_files[0]}")
        
    def _init_ollama(self):
        """Initialize Ollama backend"""
        if not OLLAMA_AVAILABLE:
            raise Exception("Ollama not available")
            
        # Check if Ollama is running and has models
        try:
            models = ollama.list()
            if not models.get('models'):
                raise Exception("No Ollama models available. Install with: ollama pull llama2")
                
            # Use first available model
            self.model_name = models['models'][0]['name']
            self.model = ollama
            self.is_loaded = True
            print(f"Ollama backend initialized with {self.model_name}")
            
        except Exception as e:
            raise Exception(f"Ollama initialization failed: {e}")
            
    def _init_transformers(self):
        """Initialize Transformers backend with a small model"""
        if not TRANSFORMERS_AVAILABLE:
            raise Exception("Transformers not available")
            
        try:
            # Use a small, fast model
            model_name = "microsoft/DialoGPT-small"
            print(f"Loading transformers model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = pipeline(
                "text-generation",
                model=model_name,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.is_loaded = True
            print("Transformers backend initialized")
            
        except Exception as e:
            raise Exception(f"Transformers initialization failed: {e}")
            
    def _init_fallback(self):
        """Initialize fallback mock backend for testing"""
        self.model = "fallback"
        self.backend = "fallback"
        self.is_loaded = True
        print("Fallback backend initialized (mock responses)")
        
    def is_ready(self):
        """Check if AI engine is ready"""
        return self.is_loaded
        
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate AI response"""
        if not self.is_loaded:
            return "AI engine not ready. Please check model installation."
            
        try:
            # Combine context and prompt
            full_prompt = self._build_full_prompt(prompt, context)
            
            if self.backend == "llama-cpp":
                return self._generate_llama_cpp(full_prompt)
            elif self.backend == "ollama":
                return self._generate_ollama(full_prompt)
            elif self.backend == "transformers":
                return self._generate_transformers(full_prompt)
            else:
                return self._generate_fallback(full_prompt)
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
            
    def _build_full_prompt(self, prompt: str, context: str = "") -> str:
        """Build full prompt with system message and context"""
        system_prompt = self.config.get("system_prompt", "You are a helpful assistant.")
        
        if context:
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nUser: {prompt}\n\nAssistant:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            
        return full_prompt
        
    def _generate_llama_cpp(self, prompt: str) -> str:
        """Generate response using llama-cpp"""
        try:
            response = self.model(
                prompt,
                max_tokens=self.config.get("max_tokens", 512),
                temperature=self.config.get("temperature", 0.7),
                top_p=self.config.get("top_p", 0.9),
                top_k=self.config.get("top_k", 40),
                repeat_penalty=self.config.get("repeat_penalty", 1.1),
                stop=["User:", "Human:", "\n\n"],
            )
            
            return response['choices'][0]['text'].strip()
            
        except Exception as e:
            return f"Error with llama-cpp generation: {str(e)}"
            
    def _generate_ollama(self, prompt: str) -> str:
        """Generate response using Ollama"""
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': self.config.get("temperature", 0.7),
                    'top_p': self.config.get("top_p", 0.9),
                    'top_k': self.config.get("top_k", 40),
                    'num_predict': self.config.get("max_tokens", 512)
                }
            )
            
            return response['response'].strip()
            
        except Exception as e:
            return f"Error with Ollama generation: {str(e)}"
            
    def _generate_transformers(self, prompt: str) -> str:
        """Generate response using Transformers"""
        try:
            # Truncate prompt if too long
            max_input_length = 512
            if len(prompt) > max_input_length:
                prompt = prompt[-max_input_length:]
                
            response = self.model(
                prompt,
                max_length=len(prompt) + self.config.get("max_tokens", 256),
                temperature=self.config.get("temperature", 0.7),
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            # Remove the input prompt from response
            response_text = generated_text[len(prompt):].strip()
            
            return response_text if response_text else "I understand your question, but I need more context to provide a helpful response."
            
        except Exception as e:
            return f"Error with Transformers generation: {str(e)}"
            
    def _generate_fallback(self, prompt: str) -> str:
        """Generate mock response for testing"""
        # Simple fallback responses
        fallback_responses = [
            "I'm running in fallback mode. To get real AI responses, please install a supported model.",
            "This is a mock response. Install llama-cpp-python and download a GGUF model for real AI.",
            "Fallback mode active. For full functionality, set up an AI model in the models directory.",
            "I'm a placeholder AI. Install dependencies and models for actual chat functionality."
        ]
        
        # Simple keyword-based responses
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm running in fallback mode. Please install an AI model for real conversations."
        elif "help" in prompt_lower:
            return "I can help, but I'm in fallback mode. Install llama-cpp-python and download a GGUF model for full AI capabilities."
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            return "I can summarize documents when a proper AI model is installed. Currently in fallback mode."
        elif "document" in prompt_lower or "pdf" in prompt_lower:
            return "Document analysis requires a real AI model. Please install dependencies and models."
        else:
            import random
            return random.choice(fallback_responses)
            
    def get_model_info(self) -> Dict:
        """Get information about loaded model"""
        return {
            "backend": self.backend,
            "is_loaded": self.is_loaded,
            "model_path": getattr(self, 'model_path', None),
            "available_backends": {
                "llama-cpp": LLAMA_CPP_AVAILABLE,
                "ollama": OLLAMA_AVAILABLE,
                "transformers": TRANSFORMERS_AVAILABLE
            }
        }
        
    def reload_model(self, model_path=None):
        """Reload model with new path"""
        self.is_loaded = False
        self.model = None
        
        if model_path:
            self.model_path = model_path
            
        self._auto_detect_backend()
