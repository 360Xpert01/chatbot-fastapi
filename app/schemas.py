from pydantic import BaseModel
from typing import List, Dict

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    thread: List[ChatMessage] = []

class ChatResponse(BaseModel):
    reply: str