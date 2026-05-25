"""
LLM service for generating chat responses using OpenRouter.
"""
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMError
import uuid

logger = get_logger(__name__)

# Initialize OpenRouter client (OpenAI-compatible API)
openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)


class LLMService:
    """Service for generating LLM responses using OpenRouter."""

    @staticmethod
    async def generate_response(
        system_prompt: str,
        context: str,
        thread: list,
        user_message: str
    ) -> str:
        try:
            logger.info(f"Generating LLM response for message: {user_message[:50]}...")

            full_system_instructions = (
                f"{system_prompt}\n\n"
                f"Context from organizational database:\n"
                f"====================================\n"
                f"{context}\n"
                f"====================================\n"
                f"Answer the user query relying strictly on the context provided above."
            )

            messages = [{"role": "system", "content": full_system_instructions}]

            for msg in thread:
                messages.append({"role": msg.role, "content": msg.content})

            messages.append({"role": "user", "content": user_message})

            formatted_messages = [
                {
                    "role": m["role"] if isinstance(m, dict) else m.role,
                    "content": m["content"] if isinstance(m, dict) else m.content
                }
                for m in messages
            ]

            logger.debug(f"Sending {len(formatted_messages)} messages to LLM")

            # Non-streaming — no stream=True, no yield
            response = await openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=formatted_messages
            )

            generated_text = response.choices[0].message.content
            logger.info(f"LLM response generated successfully (length: {len(generated_text)} chars)")
            return generated_text

        except Exception as e:
            logger.error(f"Failed to generate LLM response: {str(e)}", exc_info=True)
            raise LLMError(f"Failed to generate response: {str(e)}")
        
    @staticmethod
    async def generate_response_stream(
        system_prompt: str,
        context: str,
        thread: list,
        user_message: str
    ):
        """
        Stream chat response chunks using Server-Sent Events.

        Yields:
            str: Text chunks as they are generated
        """
        try:
            logger.info(f"Streaming LLM response for message: {user_message[:50]}...")

            full_system_instructions = (
                f"{system_prompt}\n\n"
                f"Context from organizational database:\n"
                f"====================================\n"
                f"{context}\n"
                f"====================================\n"
                f"Answer the user query relying strictly on the context provided above."
            )

            messages = [{"role": "system", "content": full_system_instructions}]

            for msg in thread:
                messages.append({"role": msg.role, "content": msg.content})

            messages.append({"role": "user", "content": user_message})

            formatted_messages = [
                {
                    "role": m["role"] if isinstance(m, dict) else m.role,
                    "content": m["content"] if isinstance(m, dict) else m.content
                }
                for m in messages
            ]

            # Stream response
            stream = await openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=formatted_messages,
                stream=True      # <-- only change from non-streaming
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        except Exception as e:
            logger.error(f"Failed to stream LLM response: {str(e)}", exc_info=True)
            raise LLMError(f"Failed to stream response: {str(e)}")