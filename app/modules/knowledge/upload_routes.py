
import uuid
import asyncio
from functools import partial
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.db import get_db
from app.core.config import settings
from app.modules.knowledge.models import Document, DocumentEmbedding
from app.core.constants import DocumentStatus
from app.rag.chunking import chunk_text_smart
from app.rag.embedding import EmbeddingService
from app.rag.parsers import DocumentParser
from app.services.storage import StorageService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload-chunked")
async def upload_chunked(
    tenant_id: uuid.UUID,          # replace with your auth dependency
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Single endpoint that streams progress events back as JSON lines.
    Frontend reads the response body incrementally to show progress.

    Response: newline-delimited JSON (NDJSON) stream:
      {"stage": "uploading",   "pct": 10}
      {"stage": "parsing",     "pct": 20}
      {"stage": "chunking",    "pct": 30}
      {"stage": "embedding",   "pct": 45, "chunk": 3, "total": 20}
      {"stage": "done",        "pct": 100, "document_id": "..."}
      {"stage": "error",       "message": "..."}
    """
    from fastapi.responses import StreamingResponse
    import json

    async def event_stream():
        try:
            # ── 1. Read file ──────────────────────────────────────────────
            yield json.dumps({"stage": "uploading", "pct": 5}) + "\n"
            file_bytes = await file.read()
            file_size = len(file_bytes)

            # ── 2. Validate extension ─────────────────────────────────────
            import os
            ext = os.path.splitext(file.filename)[1].lower().lstrip('.')
            if ext not in settings.ALLOWED_FILE_EXTENSIONS:
                yield json.dumps({"stage": "error", "message": "Invalid file type"}) + "\n"
                return

            # ── 3. Upload to storage ──────────────────────────────────────
            yield json.dumps({"stage": "uploading", "pct": 15}) + "\n"
            loop = asyncio.get_event_loop()
            file_url = await loop.run_in_executor(
                None, partial(StorageService.upload_file, file_bytes, file.filename)
            )

            # ── 4. Create DB record ───────────────────────────────────────
            db_doc = Document(
                tenant_id=tenant_id,
                filename=file.filename,
                file_url=file_url,
                file_type=file.content_type,
                file_size=file_size,
                embedding_status=DocumentStatus.PROCESSING
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)
            yield json.dumps({"stage": "parsing", "pct": 25}) + "\n"

            # ── 5. Parse (blocking → executor) ────────────────────────────
            raw_text = await loop.run_in_executor(
                None, partial(DocumentParser.extract_text, file_bytes, file.filename)
            )
            yield json.dumps({"stage": "chunking", "pct": 35}) + "\n"

            # ── 6. Chunk ──────────────────────────────────────────────────
            chunks = chunk_text_smart(
                raw_text,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                min_chunk_size=settings.MIN_CHUNK_SIZE
            )

            if not chunks:
                db_doc.embedding_status = DocumentStatus.FAILED
                db.add(db_doc); db.commit()
                yield json.dumps({"stage": "error", "message": "No content extracted from file"}) + "\n"
                return

            total = len(chunks)
            yield json.dumps({"stage": "embedding", "pct": 40, "chunk": 0, "total": total}) + "\n"

            # ── 7. Embed + batch commit ───────────────────────────────────
            BATCH = 10
            for idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                vector_values = await loop.run_in_executor(
                    None, partial(EmbeddingService.get_embedding, chunk)
                )
                db.add(DocumentEmbedding(
                    tenant_id=tenant_id,
                    document_id=db_doc.id,
                    chunk_content=chunk,
                    embedding=vector_values
                ))

                if (idx + 1) % BATCH == 0:
                    db.commit()

                pct = 40 + int((idx + 1) / total * 55)   # 40 → 95
                yield json.dumps({"stage": "embedding", "pct": pct, "chunk": idx + 1, "total": total}) + "\n"

            db.commit()
            db_doc.embedding_status = DocumentStatus.DONE
            db.add(db_doc); db.commit()

            yield json.dumps({"stage": "done", "pct": 100, "document_id": str(db_doc.id)}) + "\n"

        except Exception as exc:
            logger.error(f"Chunked upload failed: {exc}", exc_info=True)
            yield json.dumps({"stage": "error", "message": str(exc)}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")