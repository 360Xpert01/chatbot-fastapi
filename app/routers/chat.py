from fastapi import APIRouter, HTTPException, status
from openai import AsyncOpenAI, OpenAIError, RateLimitError
from app.schemas import ChatRequest, ChatResponse
from app.data import SYSTEM_PROMPT, build_user_prompt
from app.config import settings

router = APIRouter()

# Initialize the asynchronous OpenAI client using the validated api key
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",  # <-- CRITICAL CHANGE: Routes traffic to OpenRouter
    api_key=settings.OPENAI_API_KEY          # Pass your OpenRouter key here
)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        user_content = build_user_prompt(
            thread=[m.model_dump() for m in payload.thread], 
            message=payload.message
        )
        
        # Async call to OpenAI API
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b:free",
            max_tokens=1024,
            temperature=0.4,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ]
        )
        
        ai_reply = response.choices[0].message.content
        return ChatResponse(reply=ai_reply)

    except RateLimitError as e:
        # Handles rate limits / heavy traffic errors gracefully
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="heavy traffic on the server. Please try again later."
        )
    except OpenAIError as e:
        # Handles standard API errors coming directly from OpenAI
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=getattr(e, "message", "Error from OpenAI API")
        )
    except Exception as e:
        # Catch-all fallback for internal bugs or loss of connectivity
        print(f"Backend Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server is currently unable to handle your request. Please try again later."
        )