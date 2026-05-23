"""
RAG (Retrieval-Augmented Generation) engine business logic.
Integrates vector similarity searches with isolated context generation.
"""
import uuid
from typing import List
from sqlmodel import Session, select
from sqlalchemy import cast
from pgvector.sqlalchemy import Vector

from app.modules.knowledge.models import DocumentEmbedding
from app.core.logging import get_logger
from app.core.config import settings
from app.rag.embedding import EmbeddingService
from app.rag.llm import LLMService

logger = get_logger(__name__)


class RAGService:
    """Service class for RAG chat operations."""

    @staticmethod
    def retrieve_context(
        query: str,
        tenant_id: uuid.UUID,
        db: Session
    ) -> str:
        """
        Retrieve relevant context from the knowledge base using vector similarity search.

        Uses parameterized queries with pgvector's cosine_distance.
        Strictly filters by tenant_id for data isolation.

        Args:
            query: User query text
            tenant_id: Tenant UUID for data isolation
            db: Database session

        Returns:
            Concatenated relevant context chunks

        Raises:
            EmbeddingProcessingError: If query embedding generation fails
        """
        logger.info(f"Retrieving context for query: {query[:50]}...")

        # Generate query embedding using localized EmbeddingService
        query_vector = EmbeddingService.get_embedding(query)
        logger.debug(f"Query embedding generated (dimension: {len(query_vector)})")

        # SQL Injection Prevention
        # Use pgvector's cosine_distance method with proper type casting
        stmt = (
            select(
                DocumentEmbedding.chunk_content,
                DocumentEmbedding.embedding.cosine_distance(
                    cast(query_vector, Vector(settings.EMBEDDING_DIMENSION))
                ).label('distance')
            )
            .where(DocumentEmbedding.tenant_id == tenant_id)
            .order_by('distance')
            .limit(settings.TOP_K_RESULTS)
        )

        results = db.exec(stmt).all()
        logger.debug(f"Retrieved {len(results)} chunks from vector search")

        # Apply relevance filtering
        # Cosine distance: 0 = identical, 2 = opposite
        # Similarity = 1 - (distance / 2)
        relevant_chunks = []
        for chunk_content, distance in results:
            similarity = 1 - (distance / 2)
            logger.debug(f"Chunk similarity: {similarity:.3f} (distance: {distance:.3f})")

            if similarity >= settings.RELEVANCE_THRESHOLD:
                relevant_chunks.append(chunk_content)
            else:
                logger.debug(f"Chunk filtered out (similarity {similarity:.3f} < threshold {settings.RELEVANCE_THRESHOLD})")

        logger.info(f"Filtered to {len(relevant_chunks)} relevant chunks (threshold: {settings.RELEVANCE_THRESHOLD})")

        # Concatenate relevant chunks
        if relevant_chunks:
            context = "\n\n".join(relevant_chunks)
        else:
            context = "No relevant context found in the knowledge base."
            logger.warning("No relevant context found for query")

        return context

    @staticmethod
    async def generate_response(
        query: str,
        thread: List["ChatMessage"],
        tenant_id: uuid.UUID,
        system_prompt: str,
        db: Session
    ) -> str:
        """
        Generate a chat response using RAG.

        Pipeline:
        1. Retrieve relevant context from knowledge base
        2. Generate response using LLM with context and conversation history

        Args:
            query: User query text
            thread: Conversation history
            tenant_id: Tenant UUID
            system_prompt: Custom system prompt for the tenant
            db: Database session

        Returns:
            Generated response text

        Raises:
            EmbeddingProcessingError: If query embedding fails
            LLMError: If response generation fails
        """
        from app.modules.engine.schemas import ChatMessage

        logger.info(f"Generating RAG response for tenant: {tenant_id}")

        # Step 1: Retrieve context
        context = RAGService.retrieve_context(query, tenant_id, db)

        # Step 2: Generate response using localized LLMService
        response = await LLMService.generate_response(
            system_prompt=system_prompt,
            context=context,
            thread=thread,
            user_message=query
        )

        logger.info(f"RAG response generated successfully (length: {len(response)} chars)")
        return response
