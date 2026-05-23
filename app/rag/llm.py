"""
LLM service for generating chat responses using OpenRouter.
"""
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMError

logger = get_logger(__name__)

# Initialize OpenRouter client (OpenAI-compatible API)
openai_client = AsyncOpenAI(
    base_url=settings.LLM_PROVIDER_URL,
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
        """
        Generate a chat response using RAG context and conversation history.

        Args:
            system_prompt: Base system instructions
            context: Retrieved context from knowledge base
            thread: List of previous messages in the conversation
            user_message: Current user message

        Returns:
            Generated response text

        Raises:
            LLMError: If response generation fails
        """
        try:
            logger.info(f"Generating LLM response for message: {user_message[:50]}...")

            # Construct RAG context instruction set
            full_system_instructions = (
                f"{system_prompt}\n\n"
                f"Context from organizational database:\n"
                f"====================================\n"
                f"{context}\n"
                f"====================================\n"
                f"Answer the user query relying strictly on the context provided above."
            )

            # Build message history
            messages = [{"role": "system", "content": full_system_instructions}]

            for msg in thread:
                messages.append({"role": msg.role, "content": msg.content})

            messages.append({"role": "user", "content": user_message})

            # Safe adaptation of payload structure to OpenRouter requirements
            formatted_messages = [
                {
                    "role": m["role"] if isinstance(m, dict) else m.role,
                    "content": m["content"] if isinstance(m, dict) else m.content
                }
                for m in messages
            ]

            logger.debug(f"Sending {len(formatted_messages)} messages to LLM")

            # Call OpenRouter API
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
