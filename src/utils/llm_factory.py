# src/utils/llm_factory.py

from langchain_openai import ChatOpenAI
from src.config import Config, LLMProvider

def create_llm(provider: LLMProvider = None, model: str = None, temperature: float = 0):
    """Create an LLM instance based on the specified provider."""
    if provider is None:
        provider = LLMProvider(Config.DEFAULT_LLM_PROVIDER)
    
    if provider == LLMProvider.OPENAI:
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        return ChatOpenAI(
            model=model or "gpt-4o-mini",
            temperature=temperature,
            openai_api_key=Config.OPENAI_API_KEY
        )
    elif provider == LLMProvider.OPENROUTER:
        if not Config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables.")
        return ChatOpenAI(
            model=model or Config.OPENROUTER_MODEL,
            temperature=temperature,
            openai_api_key=Config.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")