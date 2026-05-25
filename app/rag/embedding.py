"""
Embedding service for generating text embeddings using OpenAI.
"""
import io
import time
from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import EmbeddingProcessingError

logger = get_logger(__name__)

# Initialize OpenAI client
ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    @staticmethod
    def get_embedding(text: str, retries: int = 3, backoff: float = 2.0) -> list[float]:
        last_exc = None
        for attempt in range(retries):
            try:
                logger.debug(f"Generating embedding attempt {attempt + 1} (length: {len(text)} chars)")
                
                # Shifted from Gemini models.embed_content to OpenAI embeddings.create
                response = ai_client.embeddings.create(
                    model=settings.EMBEDDING_MODEL,
                    input=text
                )
                
                # OpenAI returns an array of embedding objects; we grab the values array from the first entry
                embedding = response.data[0].embedding
                
                logger.debug(f"Embedding generated (dimension: {len(embedding)})")
                return embedding
            except Exception as e:
                last_exc = e
                wait = backoff ** attempt
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
        logger.error(f"All {retries} embedding attempts failed: {last_exc}", exc_info=True)
        raise EmbeddingProcessingError(f"Failed to generate embedding after {retries} retries: {last_exc}")