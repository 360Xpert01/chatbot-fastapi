import io
from groq import Groq
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import STTError

logger = get_logger(__name__)
client = Groq(api_key=settings.GROQ_API_KEY)


class STTService:

    @staticmethod
    def _convert_to_mp3(audio_bytes: bytes) -> bytes:
        """Convert any audio format to mp3 for Groq compatibility."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            output = io.BytesIO()
            audio.export(output, format="mp3")
            return output.getvalue()
        except Exception as e:
            logger.warning(f"Audio conversion failed, using raw bytes: {e}")
            return audio_bytes

    @staticmethod
    def transcribe(audio_bytes: bytes, filename: str = "audio.webm") -> str:
        try:
            logger.info(f"Transcribing audio ({len(audio_bytes)} bytes)")
    
            # DEBUG: save raw incoming bytes to disk to inspect
            import tempfile, os
            debug_path = os.path.join(tempfile.gettempdir(), "debug_audio.webm")
            with open(debug_path, "wb") as f:
                f.write(audio_bytes)
            logger.info(f"DEBUG: raw audio saved to {debug_path}")
    
            # Convert to mp3
            mp3_bytes = STTService._convert_to_mp3(audio_bytes)
            logger.info(f"Converted to mp3 ({len(mp3_bytes)} bytes)")
    
            # DEBUG: save converted mp3 too
            debug_mp3_path = os.path.join(tempfile.gettempdir(), "debug_audio.mp3")
            with open(debug_mp3_path, "wb") as f:
                f.write(mp3_bytes)
            logger.info(f"DEBUG: mp3 saved to {debug_mp3_path}")
    
            response = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=("audio.mp3", mp3_bytes, "audio/mp3"),
            )
    
            transcript = response.text.strip()
            logger.info(f"Transcription complete: '{transcript[:80]}'")
            return transcript
    
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise STTError(f"Transcription failed: {str(e)}")