"""
Unified RAG (Retrieval-Augmented Generation) Module.
Consolidates all smart sentence-aware chunking, vector embedding, 
LLM interface, and vector database similarity search operations.
"""
from app.rag.chunking import chunk_text_smart, chunk_text_with_metadata
from app.rag.embedding import EmbeddingService
from app.rag.llm import LLMService
from app.rag.services import RAGService

__all__ = [
    "chunk_text_smart",
    "chunk_text_with_metadata",
    "EmbeddingService",
    "LLMService",
    "RAGService",
]
