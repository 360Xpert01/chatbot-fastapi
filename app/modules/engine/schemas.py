"""
Chat engine request/response schemas.
"""
from typing import List
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Schema for a single chat message in the conversation thread."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Schema for chat request payload."""
    message: str
    thread: List[ChatMessage] = []


class ChatResponse(BaseModel):
    """
    Schema for chat response data.

    Note: This is NOT wrapped in an Envelope at this level.
    The router will wrap this in Envelope[ChatResponse].
    Removed the nested 'success' field to avoid double-nesting.
    """
    response: str

    class Config:
        from_attributes = True
