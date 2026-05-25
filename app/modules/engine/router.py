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
from app.core.exceptions import HTTPException
from app.core.config import settings
from app.modules.usage.service import UsageService
from app.modules.engine.schemas import ChatMessage, VoiceChatResponse
from app.rag.stt import STTService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


from fastapi.responses import StreamingResponse as FastAPIStreamingResponse

@router.post("/chat")
async def chat_endpoint(
    payload: ChatRequest,
    x_tenant_id: uuid.UUID = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_session)
):
    logger.info(f"POST /api/v1/chat - Tenant: {x_tenant_id}, Message: {payload.message[:50]}...")

    tenant = TenantService.get_tenant(x_tenant_id, db)
    system_prompt = tenant.custom_prompt or "You are a helpful customer support assistant."


    if not UsageService.check_and_increment(db):
        raise HTTPException(
            status_code=429,
            detail=f"The application-wide limit of {settings.CHAT_MESSAGE_LIMIT} messages has been reached."
        )

    async def event_stream():
        import json
        try:
            async for chunk in RAGService.generate_response_stream(
                query=payload.message,
                thread=payload.thread,
                tenant_id=x_tenant_id,
                system_prompt=system_prompt,
                db=db
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Signal done
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Streaming failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return FastAPIStreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/chat/voice")
async def voice_chat_endpoint(
    audio: UploadFile = File(...),
    thread: str = Form(default="[]"),
    x_tenant_id: uuid.UUID = Header(..., alias="X-Tenant-ID"),
    db: Session = Depends(get_session)
):
    logger.info(f"POST /api/v1/chat/voice - Tenant: {x_tenant_id}, File: {audio.filename}")

    tenant = TenantService.get_tenant(x_tenant_id, db)
    system_prompt = tenant.custom_prompt or "You are a helpful customer support assistant."


    audio_bytes = await audio.read()
    filename = audio.filename or "audio.webm"

    try:
        thread_data = json.loads(thread)
        thread_messages = [ChatMessage(**msg) for msg in thread_data]
    except Exception:
        thread_messages = []

    if not UsageService.check_and_increment(db):
        raise HTTPException(
            status_code=429,
            detail=f"The application-wide limit of {settings.CHAT_MESSAGE_LIMIT} messages has been reached."
        )
    
    # Transcribe first (blocking — must finish before streaming)
    transcript = STTService.transcribe(audio_bytes, filename)
    logger.info(f"Transcript: {transcript[:80]} - Tenant: {x_tenant_id}")

    async def event_stream():
        import json as json_mod
        try:
            # Send transcript first so frontend can update user bubble
            yield f"data: {json_mod.dumps({'transcript': transcript})}\n\n"

            # Then stream LLM response
            async for chunk in RAGService.generate_response_stream(
                query=transcript,
                thread=thread_messages,
                tenant_id=x_tenant_id,
                system_prompt=system_prompt,
                db=db
            ):
                yield f"data: {json_mod.dumps({'chunk': chunk})}\n\n"

            yield f"data: {json_mod.dumps({'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Voice streaming failed: {e}", exc_info=True)
            yield f"data: {json_mod.dumps({'error': str(e)})}\n\n"

    return FastAPIStreamingResponse(event_stream(), media_type="text/event-stream")