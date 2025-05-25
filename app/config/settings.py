import os
import sys
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Try to load dotenv but don't fail if it doesn't work
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except Exception as e:
    print(f"Warning: Error loading .env file: {e}")
    # If dotenv fails, try to load manually
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8-sig") as f:  # Try with utf-8-sig to handle BOMs
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            os.environ[key] = value
                        except ValueError:
                            print(f"Warning: Skipping invalid line in .env: {line}")
            print("Loaded environment variables manually")
        except Exception as e2:
            print(f"Warning: Could not manually load .env file: {e2}")

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI API settings
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-4.1-mini", description="Default OpenAI model to use")
    MAX_TOKENS: int = Field(750, description="Maximum number of tokens to generate")
    TEMPERATURE: float = Field(0.7, description="Temperature for response generation")
    TOP_P: float = Field(1.0, description="Top-p sampling parameter")
    FREQUENCY_PENALTY: float = Field(0.0, description="Frequency penalty parameter")
    PRESENCE_PENALTY: float = Field(0.0, description="Presence penalty parameter")
    
    # Performance settings
    ENABLE_RESPONSE_CACHE: bool = Field(True, description="Enable response caching")
    CACHE_TTL_SECONDS: int = Field(300, description="Cache time-to-live in seconds")
    CACHE_MAX_SIZE: int = Field(100, description="Maximum number of items in cache")
    MAX_HISTORY_LENGTH: int = Field(10, description="Maximum conversation history length")
    
    # API settings
    API_KEY: Optional[str] = Field(None, description="API key for authentication")
    API_KEY_HEADER: str = Field("X-API-Key", description="Header name for API key")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        ["*"], 
        description="List of allowed origins for CORS"
    )
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        60, 
        description="Number of requests allowed per minute"
    )
    
    # Logging
    LOG_LEVEL: str = Field("INFO", description="Log level")
    DEVELOPMENT_MODE: bool = Field(os.environ.get("DEVELOPMENT_MODE", "False").lower() == "true", description="Development mode flag to enable detailed logging")
    
    # Pinecone settings (vector database)
    PINECONE_API_KEY: str = Field(os.environ.get("PINECONE_API_KEY", ""), description="Pinecone API key")
    PINECONE_INDEX_NAME: str = Field(os.environ.get("PINECONE_INDEX_NAME", "healthnivaran-providers"), description="Pinecone index name")
    PINECONE_ENVIRONMENT: str = Field(os.environ.get("PINECONE_ENVIRONMENT", "us-east-1"), description="Pinecone environment")
    PINECONE_HOST: str = Field(os.environ.get("PINECONE_HOST", "https://healthnivaran-providers-m0irgug.svc.aped-4627-b74a.pinecone.io"), description="Pinecone host")
    
    # Embedding model settings
    EMBEDDING_MODEL: str = Field("text-embedding-3-large", description="Embedding model")
    EMBEDDING_DIMENSIONS: int = Field(3072, description="Embedding dimensions")
    
    # Redis settings
    REDIS_HOST: str = Field(os.environ.get("REDIS_HOST", "localhost"), description="Redis host")
    REDIS_PORT: int = Field(int(os.environ.get("REDIS_PORT", "6379")), description="Redis port")
    REDIS_USERNAME: str = Field(os.environ.get("REDIS_USERNAME", ""), description="Redis username")
    REDIS_PASSWORD: str = Field(os.environ.get("REDIS_PASSWORD", ""), description="Redis password")
    REDIS_SSL: bool = Field(os.environ.get("REDIS_SSL", "False").lower() == "True", description="Use SSL for Redis connection")
    REDIS_DECODE_RESPONSES: bool = Field(True, description="Automatically decode Redis responses to Python strings")
    REDIS_CONVERSATIONS_TTL_HOURS: int = Field(24, description="TTL for conversation data in Redis (hours)")
    REDIS_MAX_CONVERSATIONS: int = Field(1000, description="Maximum number of conversations to store in Redis")

    # Gemini API settings
    GEMINI_API_MODEL_NAME: str = Field("gemini-2.0-flash", description="Default Gemini model to use")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Create settings instance with error handling
try:
    settings = Settings()
    print(f"Settings loaded successfully. Using model: {settings.OPENAI_MODEL}")
    print(f"Development mode: {'Enabled' if settings.DEVELOPMENT_MODE else 'Disabled'}")
except Exception as e:
    print(f"Error loading settings: {e}")
    sys.exit(1)

# Validate required settings
if not settings.OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY is not set. OpenAI API calls will fail.")

if not settings.PINECONE_API_KEY:
    logging.warning("PINECONE_API_KEY is not set. Pinecone vector searches will fail.") 