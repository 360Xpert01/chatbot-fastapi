"""
Application configuration settings.
Loads from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # API Keys
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str

    # Cloudinary Storage
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # Embedding Configuration
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 3072

    # Text Chunking Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MIN_CHUNK_SIZE: int = 100

    # RAG Retrieval Configuration
    TOP_K_RESULTS: int = 4
    RELEVANCE_THRESHOLD: float = 0.7

    # LLM Configuration
    LLM_PROVIDER_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "openai/gpt-4o-mini"
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.4

    # Logging
    LOG_LEVEL: str = "INFO"

    # Allowed upload file extensions (lowercase, without dot)
    ALLOWED_FILE_EXTENSIONS: list[str] = ["pdf", "txt", "docx", "md"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
