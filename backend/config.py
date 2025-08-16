from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    # Base directories
    base_dir: Path = Path(__file__).parent
    data_dir: Path = Path(__file__).parent.parent / "data"
    
    # Subdirectories
    documents_dir: Path = data_dir / "documents"
    embeddings_dir: Path = data_dir / "embeddings"
    models_dir: Path = data_dir / "models"
    
    # Model settings
    embeddings_model: str = "all-MiniLM-L6-v2"  # Default lightweight embedding model
    llm_model_file: str = "phi-2.Q4_K_M.gguf"   # Default lightweight LLM
    
    # RAG settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5
    
    # API settings
    allow_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **data):
        super().__init__(**data)
        
        # Ensure all directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.embeddings_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
