"""
Sentence-aware text chunking for improved RAG quality.
Replaces naive character-based chunking that breaks mid-sentence.
"""
import re
from typing import List
from app.core.logging import get_logger

logger = get_logger(__name__)


def chunk_text_smart(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    min_chunk_size: int = 100
) -> List[str]:
    """
    Split text into chunks at sentence boundaries for better semantic coherence.

    This function improves upon naive character-based chunking by:
    1. Splitting on sentence boundaries (., !, ?, paragraph breaks)
    2. Combining sentences until chunk_size is reached
    3. Adding overlap from the previous chunk for context continuity
    4. Falling back to character-based splitting for very long sentences

    Args:
        text: Input text to chunk
        chunk_size: Target maximum size for each chunk (characters)
        chunk_overlap: Number of characters to overlap between chunks
        min_chunk_size: Minimum chunk size to avoid tiny fragments

    Returns:
        List of text chunks with sentence-aware boundaries

    Example:
        >>> text = "First sentence. Second sentence. Third sentence."
        >>> chunks = chunk_text_smart(text, chunk_size=30, chunk_overlap=10)
        >>> # Returns chunks that don't break mid-sentence
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for chunking")
        return []

    # Normalize whitespace
    text = text.strip()

    # Split into sentences using regex
    # Matches: . ! ? followed by space/newline, or paragraph breaks
    sentence_pattern = r'(?<=[.!?])\s+|\n\n+'
    sentences = re.split(sentence_pattern, text)

    # Filter out empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        logger.warning("No sentences found after splitting")
        return [text] if len(text) >= min_chunk_size else []

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        # Handle very long sentences that exceed chunk_size
        if sentence_length > chunk_size:
            # Save current chunk if it exists
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0

            # Split long sentence by character with overlap
            for i in range(0, sentence_length, chunk_size - chunk_overlap):
                chunk_part = sentence[i:i + chunk_size]
                if len(chunk_part) >= min_chunk_size:
                    chunks.append(chunk_part)

            continue

        # Check if adding this sentence would exceed chunk_size
        if current_length + sentence_length + 1 > chunk_size and current_chunk:
            # Save current chunk
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)

            # Start new chunk with overlap from previous chunk
            if chunk_overlap > 0 and chunks:
                overlap_text = chunk_text[-chunk_overlap:]
                # Find sentence boundary in overlap
                overlap_sentences = re.split(sentence_pattern, overlap_text)
                overlap_sentences = [s.strip() for s in overlap_sentences if s.strip()]

                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk) + len(current_chunk) - 1
            else:
                current_chunk = []
                current_length = 0

        # Add sentence to current chunk
        current_chunk.append(sentence)
        current_length += sentence_length + (1 if current_chunk else 0)  # +1 for space

    # Add final chunk if it meets minimum size
    if current_chunk:
        final_chunk = ' '.join(current_chunk)
        if len(final_chunk) >= min_chunk_size:
            chunks.append(final_chunk)

    logger.info(f"Chunked text into {len(chunks)} chunks (avg size: {sum(len(c) for c in chunks) // len(chunks) if chunks else 0} chars)")

    return chunks


def chunk_text_with_metadata(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    min_chunk_size: int = 100
) -> List[dict]:
    """
    Chunk text and return with metadata about each chunk.

    Args:
        text: Input text to chunk
        chunk_size: Target maximum size for each chunk
        chunk_overlap: Number of characters to overlap
        min_chunk_size: Minimum chunk size

    Returns:
        List of dicts with 'content', 'index', 'start_pos', 'end_pos'

    Example:
        >>> chunks = chunk_text_with_metadata("Long text...")
        >>> chunks[0]
        {'content': '...', 'index': 0, 'start_pos': 0, 'end_pos': 150}
    """
    chunks = chunk_text_smart(text, chunk_size, chunk_overlap, min_chunk_size)

    result = []
    current_pos = 0

    for idx, chunk in enumerate(chunks):
        # Find approximate position in original text
        start_pos = text.find(chunk[:50], current_pos) if len(chunk) >= 50 else text.find(chunk, current_pos)
        if start_pos == -1:
            start_pos = current_pos

        end_pos = start_pos + len(chunk)
        current_pos = end_pos

        result.append({
            'content': chunk,
            'index': idx,
            'start_pos': start_pos,
            'end_pos': end_pos
        })

    return result
