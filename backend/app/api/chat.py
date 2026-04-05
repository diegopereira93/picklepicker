"""Chat endpoint with SSE streaming for paddle recommendations."""

import asyncio
import json
import os
import time
from typing import Optional

import structlog
from groq import AsyncGroq
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from app.agents.rag_agent import RAGAgent, UserProfile

logger = structlog.get_logger()

# Initialize Groq client (lazy initialization)
groq_client = None

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request with user profile."""

    message: str
    skill_level: str
    budget_brl: float
    style: Optional[str] = None

    @field_validator("skill_level")
    @classmethod
    def validate_skill_level(cls, v: str) -> str:
        """Validate skill_level is one of allowed values."""
        allowed = ["beginner", "intermediate", "advanced"]
        if v.lower() not in allowed:
            raise ValueError(f"skill_level must be one of {allowed}")
        return v.lower()

    @field_validator("budget_brl")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        """Validate budget is positive."""
        if v <= 0:
            raise ValueError("budget_brl must be greater than 0")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is non-empty."""
        if not v or not v.strip():
            raise ValueError("message cannot be empty")
        return v.strip()


def format_paddles_for_prompt(recommendations) -> str:
    """Format paddle recommendations for LLM prompt."""
    text = ""
    for r in recommendations:
        text += f"- {r.brand} {r.name}: R${r.price_min_brl:.0f}\n"
    return text


@router.post("/chat")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Stream paddle recommendations with SSE.

    Returns:
    - "recommendations" event with top-3 paddles
    - "reasoning" event with LLM reasoning
    - "done" event with metadata

    On timeout (>8s), sends "degraded" event and returns by-price fallback.
    """

    async def event_generator():
        start_time = time.time()
        input_tokens = 0
        output_tokens = 0
        model_used = "degraded"

        try:
            # Initialize RAG agent
            agent = RAGAgent()

            # Create user profile
            profile = UserProfile(
                skill_level=request.skill_level,
                budget_max_brl=request.budget_brl,
                style=request.style,
            )

            # Fetch recommendations by profile
            recommendations = await agent.search_by_profile(
                profile, user_message=request.message
            )

            # Per-paddle reason templates
            def _paddle_reason(rank: int, skill: str, price: float) -> str:
                if rank == 0:
                    return f"Melhor opção para {skill} com ótimo custo-benefício (R${price:.0f})"
                if rank == 1:
                    return "Excelente equilíbrio entre controle e potência para o seu nível"
                return "Opção alternativa com specs complementares ao seu estilo de jogo"

            # Send recommendations event
            rec_data = {
                "paddles": [
                    {
                        "paddle_id": r.paddle_id,
                        "name": r.name,
                        "brand": r.brand,
                        "price_min_brl": r.price_min_brl,
                        "affiliate_url": r.affiliate_url,
                        "similarity_score": r.similarity_score,
                        "reason": _paddle_reason(i, request.skill_level, r.price_min_brl),
                    }
                    for i, r in enumerate(recommendations)
                ]
            }
            yield f"event: recommendations\ndata: {json.dumps(rec_data)}\n\n"

            # Try LLM reasoning with timeout
            try:
                # Check if Groq API key is available
                groq_api_key = os.environ.get("GROQ_API_KEY")
                if not groq_api_key:
                    raise ValueError("GROQ_API_KEY not set")

                # Initialize Groq client if not already initialized
                global groq_client
                if groq_client is None:
                    groq_client = AsyncGroq(api_key=groq_api_key)

                # Build prompt with context
                prompt = f"""Você é um especialista em pickleball. 

Perfil do usuário:
- Nível: {request.skill_level}
- Orçamento: R${request.budget_brl:.0f}
- Estilo: {request.style or 'não especificado'}

Raquetes recomendadas:
{format_paddles_for_prompt(recommendations)}

Pergunta do usuário: {request.message}

Forneça uma explicação em português de por que estas raquetes são adequadas, em 2-3 frases."""

                response = await asyncio.wait_for(
                    groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1024,
                        stream=True,
                    ),
                    timeout=8.0,
                )

                reasoning_text = ""
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        reasoning_text += chunk.choices[0].delta.content

                reasoning = reasoning_text
                model_used = "llama-3.3-70b-versatile"

                # Get token counts if available
                if hasattr(response, "usage") and response.usage:
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens

            except (asyncio.TimeoutError, Exception) as e:
                logger.error(
                    "groq_api_error",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    model="llama-3.3-70b-versatile",
                )
                
                # Degraded mode: use template response
                if isinstance(e, asyncio.TimeoutError):
                    reasoning = f"Com base no seu perfil de {request.skill_level} jogador com orçamento de R${request.budget_brl:.0f}, recomendo estas raquetes que equilibram qualidade e preço. (Resposta rápida devido a timeout)"
                else:
                    reasoning = f"Com base no seu perfil de {request.skill_level} jogador com orçamento de R${request.budget_brl:.0f}, recomendo estas raquetes que equilibram qualidade e preço."
                model_used = "degraded"
                input_tokens = 0
                output_tokens = 0

            yield f"event: reasoning\ndata: {json.dumps({'text': reasoning})}\n\n"

            # Send done event with metadata
            latency_ms = (time.time() - start_time) * 1000
            done_data = {
                "tokens": input_tokens + output_tokens,
                "latency_ms": latency_ms,
                "model": model_used,
                "cache_hit": False,
            }
            yield f"event: done\ndata: {json.dumps(done_data)}\n\n"

        except Exception as e:
            error_event = {"error": str(e)}
            yield f"event: error\ndata: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
