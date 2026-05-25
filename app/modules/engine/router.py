"""
RAG chat engine API endpoint.
"""
import uuid
from fastapi import APIRouter, Depends, Header, UploadFile, File, Form
from sqlmodel import Session

from app.core.database import get_session
from app.core.responses import Envelope, success_response
from app.core.constants import ResponseCode
from app.modules.engine.schemas import ChatRequest, ChatResponse
from app.rag.services import RAGService
from app.modules.tenants.services import TenantService
from app.core.logging import get_logger
from app.core.exceptions import InvalidTenantHeaderError
import uuid
import json

from app.modules.engine.schemas import ChatMessage, VoiceChatResponse
from app.rag.stt import STTService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=Envelope[ChatResponse])
async def chat_endpoint(
    payload: ChatRequest,
    x_tenant_id: uuid.UUID = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_session)
) -> Envelope[ChatResponse]:
    """
    Generate a chat response using RAG (Retrieval-Augmented Generation).

    This endpoint:
    1. Validates the X-Tenant-ID header
    2. Retrieves relevant context from the tenant's knowledge base
    3. Generates a response using the LLM with context and conversation history

    Args:
        payload: Chat request with message and conversation thread
        x_tenant_id: Tenant UUID from X-Tenant-ID header
        db: Database session

    Returns:
        Envelope containing the chat response

    Raises:
        TenantNotFoundError: If tenant not found (handled by global exception handler)
        InvalidTenantHeaderError: If X-Tenant-ID header is invalid
        EmbeddingProcessingError: If query embedding fails
        LLMError: If response generation fails
    """
    logger.info(f"POST /api/v1/chat - Tenant: {x_tenant_id}, Message: {payload.message[:50]}...")

    # Validate tenant exists
    tenant = TenantService.get_tenant(x_tenant_id, db)

    # Get custom system prompt or use default
    system_prompt = tenant.custom_prompt or "You are a helpful customer support assistant."

    # Generate RAG response
    response_text = await RAGService.generate_response(
        query=payload.message,
        thread=payload.thread,
        tenant_id=x_tenant_id,
        system_prompt=system_prompt,
        db=db
    )

    # Return response (note: ChatResponse no longer has nested 'success' field)
    return success_response(
        code=ResponseCode.CHAT_COMPLETED,
        message="Chat response generated successfully",
        data=ChatResponse(response=response_text)
    )


@router.post("/chat/voice", response_model=Envelope[VoiceChatResponse])
async def voice_chat_endpoint(
    audio: UploadFile = File(...),
    thread: str = Form(default="[]"),
    x_tenant_id: uuid.UUID = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_session)
) -> Envelope[VoiceChatResponse]:
    """
    Generate a chat response from voice input using Whisper + RAG.

    This endpoint:
    1. Validates the X-Tenant-ID header
    2. Transcribes audio via OpenAI Whisper
    3. Retrieves relevant context from the tenant's knowledge base
    4. Generates a response using the LLM with context and conversation history

    Args:
        audio: Audio file (webm, mp4, wav, m4a)
        thread: JSON stringified conversation history
        x_tenant_id: Tenant UUID from X-Tenant-ID header
        db: Database session

    Returns:
        Envelope containing transcript and chat response

    Raises:
        TenantNotFoundError: If tenant not found
        STTError: If Whisper transcription fails
        EmbeddingProcessingError: If query embedding fails
        LLMError: If response generation fails
    """
    logger.info(f"POST /api/v1/chat/voice - Tenant: {x_tenant_id}, File: {audio.filename}")

    # Validate tenant exists
    tenant = TenantService.get_tenant(x_tenant_id, db)

    # Get custom system prompt or use default
    system_prompt = tenant.custom_prompt or "You are a helpful customer support assistant."

    # Read audio bytes before any async ops
    audio_bytes = await audio.read()
    filename = audio.filename or "audio.webm"

    # Parse thread
    try:
        thread_data = json.loads(thread)
        thread_messages = [ChatMessage(**msg) for msg in thread_data]
    except Exception:
        thread_messages = []

    # Step 1: Transcribe via Whisper
    transcript = STTService.transcribe(audio_bytes, filename)

    logger.info(f"Transcript: {transcript[:80]}... - Tenant: {x_tenant_id}")

    # Step 2: RAG pipeline with transcript as query (existing flow, unchanged)
    response_text = await RAGService.generate_response(
        query=transcript,
        thread=thread_messages,
        tenant_id=x_tenant_id,
        system_prompt=system_prompt,
        db=db
    )

    return success_response(
        code=ResponseCode.CHAT_COMPLETED,
        message="Voice message processed successfully",
        data=VoiceChatResponse(
            transcript=transcript,
            reply=response_text
        )
    )