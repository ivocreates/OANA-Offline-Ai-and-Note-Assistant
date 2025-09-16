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
        # Check for local GGUF models in multiple possible locations
        possible_model_dirs = [
            os.path.join(os.path.dirname(__file__), "..", "models"),  # Default location
            os.path.join(os.getcwd(), "models"),  # Current working directory
            os.path.join(os.path.expanduser("~"), ".oana", "models"),  # User home directory
        ]
        
        gguf_files = []
        self.models_dir = None
        
        for models_dir in possible_model_dirs:
            if os.path.exists(models_dir):
                found_files = [f for f in os.listdir(models_dir) if f.endswith('.gguf')]
                if found_files:
                    gguf_files = found_files
                    self.models_dir = models_dir
                    print(f"Found {len(gguf_files)} GGUF model(s) in {models_dir}")
                    break
        
        if not gguf_files:
            print("No GGUF models found in any of the following locations:")
            for dir_path in possible_model_dirs:
                print(f"  - {dir_path}")
            
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
            raise Exception("llama-cpp-python not available. Install with: pip install llama-cpp-python")
            
        # Use the models directory found during auto-detection
        if not self.models_dir or not os.path.exists(self.models_dir):
            raise Exception("No models directory found. Please create a 'models' folder and add GGUF model files.")
            
        model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.gguf')]
            
        if not model_files:
            raise Exception(f"No GGUF model files found in {self.models_dir}. Please download models using 'python download_models.py'")
            
        # Use the first available model or a specific one if provided
        if self.model_path and os.path.exists(self.model_path):
            model_path = self.model_path
            model_name = os.path.basename(model_path)
        else:
            # Sort models by size (smaller models load faster)
            model_files_with_size = []
            for f in model_files:
                full_path = os.path.join(self.models_dir, f)
                size = os.path.getsize(full_path)
                model_files_with_size.append((f, size))
            
            # Sort by size and use the smallest for faster loading
            model_files_with_size.sort(key=lambda x: x[1])
            model_name = model_files_with_size[0][0]
            model_path = os.path.join(self.models_dir, model_name)
        
        print(f"Loading model: {model_name}")
        print(f"Model path: {model_path}")
        
        try:
            self.model = Llama(
                model_path=model_path,
                n_ctx=2048,  # Context length
                n_threads=4,  # Number of CPU threads
                verbose=False
            )
            
            self.is_loaded = True
            self.model_name = model_name
            print(f"✅ llama-cpp backend initialized with {model_name}")
            
        except Exception as e:
            raise Exception(f"Failed to load model {model_name}: {str(e)}")
        
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
        # Provide helpful setup instructions
        setup_instructions = """
🚫 OANA is running in FALLBACK MODE

To enable full AI functionality, you need to:

1. Install AI backend:
   pip install llama-cpp-python

2. Download a model:
   python download_models.py

3. Or manually place a .gguf model file in the 'models/' folder

Available backends status:
"""
        
        backend_status = []
        backend_status.append(f"• llama-cpp-python: {'✅ Available' if LLAMA_CPP_AVAILABLE else '❌ Not installed'}")
        backend_status.append(f"• Ollama: {'✅ Available' if OLLAMA_AVAILABLE else '❌ Not installed'}")
        backend_status.append(f"• Transformers: {'✅ Available' if TRANSFORMERS_AVAILABLE else '❌ Not installed'}")
        
        # Check for models
        models_found = []
        if hasattr(self, 'models_dir') and self.models_dir and os.path.exists(self.models_dir):
            gguf_files = [f for f in os.listdir(self.models_dir) if f.endswith('.gguf')]
            if gguf_files:
                models_found.append(f"Found {len(gguf_files)} GGUF models in {self.models_dir}")
            else:
                models_found.append(f"No GGUF models found in {self.models_dir}")
        else:
            models_found.append("No models directory found")
        
        full_message = setup_instructions + "\n".join(backend_status) + "\n\nModels status:\n" + "\n".join(models_found)
        
        # Simple keyword-based responses for different queries
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["setup", "install", "help", "how"]):
            return full_message
        elif "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! " + full_message
        elif "model" in prompt_lower:
            return "Model not loaded. " + full_message
        else:
            return "I'm in fallback mode and cannot provide AI responses. " + full_message
            
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
