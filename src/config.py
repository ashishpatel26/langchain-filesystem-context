import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class LLMProvider(Enum):
    OPENAI = "openai"
    OPENROUTER = "openrouter"

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-sonnet")
    DOCUMENTS_DIR = "data/documents"
    FILES_DIR = "data/files"
    VECTOR_DB_PATH = "data/vector_db"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200