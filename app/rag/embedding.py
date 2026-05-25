"""
Embedding service for generating text embeddings using Google Gemini.
"""
from google import genai
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import EmbeddingProcessingError
import time

logger = get_logger(__name__)

# Initialize Google Gemini AI client
ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)


class EmbeddingService:
    """Service for generating text embeddings using Google Gemini."""

    @staticmethod
    def get_embedding(text: str, retries: int = 3, backoff: float = 2.0) -> list[float]:
        last_exc = None
        for attempt in range(retries):
            try:
                logger.debug(f"Generating embedding attempt {attempt + 1} (length: {len(text)} chars)")
                response = ai_client.models.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    contents=text
                )
                if isinstance(response.embeddings, list):
                    embedding = response.embeddings[0].values
                else:
                    embedding = response.embedding.values
                logger.debug(f"Embedding generated (dimension: {len(embedding)})")
                return embedding
            except Exception as e:
                last_exc = e
                wait = backoff ** attempt
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
        logger.error(f"All {retries} embedding attempts failed: {last_exc}", exc_info=True)
        raise EmbeddingProcessingError(f"Failed to generate embedding after {retries} retries: {last_exc}")