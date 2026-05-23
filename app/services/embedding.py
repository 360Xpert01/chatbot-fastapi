"""
Embedding service for generating text embeddings using Google Gemini.
"""
from google import genai
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import EmbeddingProcessingError

logger = get_logger(__name__)

# Initialize Google Gemini AI client
ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)


class EmbeddingService:
    """Service for generating text embeddings using Google Gemini."""

    @staticmethod
    def get_embedding(text: str) -> list[float]:
        """
        Generate embedding vector for the given text.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector

        Raises:
            EmbeddingProcessingError: If embedding generation fails
        """
        try:
            logger.debug(f"Generating embedding for text (length: {len(text)} chars)")

            response = ai_client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text
            )

            # Handle single vs batch output returns safely
            if isinstance(response.embeddings, list):
                embedding = response.embeddings[0].values
            else:
                embedding = response.embedding.values

            logger.debug(f"Embedding generated successfully (dimension: {len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}", exc_info=True)
            raise EmbeddingProcessingError(f"Failed to generate embedding: {str(e)}")
