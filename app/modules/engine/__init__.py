"""
RAG chat engine module.
Handles retrieval-augmented generation for chat responses.
"""
from app.modules.engine.schemas import ChatMessage, ChatRequest, ChatResponse
from app.rag.services import RAGService
from app.modules.engine.router import router

__all__ = [
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "RAGService",
    "router",
]
