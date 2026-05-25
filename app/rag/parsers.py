import io
import os
import re  # <-- Ensure re is imported
from pypdf import PdfReader
from docx import Document
from app.core.exceptions import HTTPException
from app.core.logging import get_logger

logger = get_logger(__name__)

class DocumentParser:
    """Extracts clean plain text strings from various file formats."""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Removes hidden control characters and null bytes that break the Gemini API."""
        if not text:
            return ""
        
        # 1. Strip out null bytes entirely
        text = text.replace('\x00', '')
        
        # 2. Replace common PDF page breaks (\x0c) with standard newlines
        text = text.replace('\x0c', '\n')
        
        # 3. Strip out unsafe control characters (ASCII 0-31), except normal tabs and newlines
        text = re.sub(r'[\x00-\x08\x0B\x0E-\x1F\x7F]', '', text)
        
        # 4. Normalize multiple consecutive spaces or trailing spaces per line
        text = "\n".join([line.strip() for line in text.splitlines()])
        
        return text

    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        raw_extracted_text = ""
        
        try:
            if ext in ['txt', 'md']:
                raw_extracted_text = file_bytes.decode("utf-8", errors="ignore")
                
            elif ext == 'pdf':
                pdf_file = io.BytesIO(file_bytes)
                reader = PdfReader(pdf_file)
                text_content = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                raw_extracted_text = "\n".join(text_content)
                
            elif ext in ['docx', 'doc']:
                docx_file = io.BytesIO(file_bytes)
                doc = Document(docx_file)
                parts = []

                # Body paragraphs
                for p in doc.paragraphs:
                    if p.text.strip():
                        parts.append(p.text)

                # Tables (your current code misses these entirely)
                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join(
                            cell.text.strip() for cell in row.cells if cell.text.strip()
                        )
                        if row_text:
                            parts.append(row_text)
                
                # Headers and footers
                for section in doc.sections:
                    for hf in [section.header, section.footer]:
                        if hf:
                            for p in hf.paragraphs:
                                if p.text.strip():
                                    parts.append(p.text)

                raw_extracted_text = "\n".join(parts)
    
            else:
                raise ValueError(f"Unsupported file format: .{ext}")
                
            # ─── CRITICAL: SANITIZE EXTRACTED RAW STRING ────────────────────
            clean_text = DocumentParser.sanitize_text(raw_extracted_text)
            return clean_text
            # ────────────────────────────────────────────────────────────────
            
        except Exception as e:
            logger.error(f"Failed parsing file {filename}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Failed to parse .{ext} file: {str(e)}")