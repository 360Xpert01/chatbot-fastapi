"""
Knowledge base module.
Handles document upload, processing, and embedding generation.
"""
from app.modules.knowledge.models import Document, DocumentEmbedding
from app.modules.knowledge.schemas import DocumentResponse
from app.modules.knowledge.services import DocumentService
from app.modules.knowledge.router import router

__all__ = [
    "Document",
    "DocumentEmbedding",
    "DocumentResponse",
    "DocumentService",
    "router",
]
