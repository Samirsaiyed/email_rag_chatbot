"""
Central configuration for the email RAG chatbot.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
THREADS_DIR = PROCESSED_DATA_DIR / "threads"
ATTACHMENTS_DIR = PROCESSED_DATA_DIR / "attachments"
INDEXES_DIR = DATA_DIR / "indexes"
RUNS_DIR = PROJECT_ROOT / "runs"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, THREADS_DIR, 
                 ATTACHMENTS_DIR, INDEXES_DIR, RUNS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Model Configuration
@dataclass
class ModelConfig:
    """Model configuration"""
    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # LLM for query rewriting and QA
    llm_model: str = "google/flan-t5-base"
    llm_max_length: int = 512
    llm_temperature: float = 0.3
    
    # Device
    device: str = "cpu"  # Change to "cuda" if GPU available

# Retrieval Configuration
@dataclass
class RetrievalConfig:
    """Retrieval configuration"""
    # Chunking
    chunk_size: int = 400
    chunk_overlap: int = 50
    
    # Retrieval
    top_k_bm25: int = 10
    top_k_vector: int = 10
    top_k_final: int = 5
    
    # Hybrid weights
    bm25_weight: float = 0.5
    vector_weight: float = 0.5

# Ingestion Configuration
@dataclass
class IngestionConfig:
    """Data ingestion configuration"""
    # Thread selection
    min_messages_per_thread: int = 5
    max_messages_per_thread: int = 20
    target_thread_count: int = 12
    
    # Date range (Enron dataset has emails from 1998-2002)
    date_range_start: Optional[str] = "2001-01-01"
    date_range_end: Optional[str] = "2001-06-30"
    
    # Text cleaning
    min_body_length: int = 50  # Minimum email body length
    remove_forwarding_headers: bool = True
    remove_signatures: bool = True

@dataclass
class LLMConfig:
    """LLM configuration - supports both Ollama and OpenAI."""
    
    # LLM Provider Selection
    use_ollama: bool = False  # Set to True to use Ollama, False for OpenAI
    
    # Ollama settings (open-source, local, free)
    ollama_model: str = "llama3.2:3b"  # Options: gemma3:1b, phi3:mini, llama3.2:3b
    ollama_base_url: str = "http://localhost:11434"
    
    # OpenAI settings
    model_name: str = "gpt-3.5-turbo"
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Common settings
    max_tokens: int = 500
    temperature: float = 0.1


# Global config instances
MODEL_CONFIG = ModelConfig()
RETRIEVAL_CONFIG = RetrievalConfig()
INGESTION_CONFIG = IngestionConfig()
LLM_CONFIG = LLMConfig()