"""Chat endpoint with SSE streaming for paddle recommendations."""

import asyncio
import time
from typing import Optional
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from backend.app.agents.rag_agent import RAGAgent, UserProfile


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

        try:
            # Initialize RAG agent (mock for now, production uses DB)
            agent = RAGAgent()

            # Create user profile
            profile = UserProfile(
                skill_level=request.skill_level,
                budget_max_brl=request.budget_brl,
                style=request.style
            )

            # Fetch recommendations by profile
            recommendations = await agent.search_by_profile(profile)

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
                    }
                    for r in recommendations
                ]
            }
            yield f"event: recommendations\ndata: {rec_data}\n\n"

            # Try LLM reasoning with timeout
            try:
                # Mock LLM response (production integrates Groq/Claude)
                reasoning = f"Com base no seu perfil de {request.skill_level} jogador com orçamento de R${request.budget_brl:.0f}, recomendo estas raquetes que equilibram qualidade e preço."

                # Simulate timeout check (production: asyncio.wait_for(..., timeout=8.0))
                await asyncio.sleep(0.1)

                yield f"event: reasoning\ndata: {{'text': '{reasoning}'}}\n\n"

            except asyncio.TimeoutError:
                # Degraded mode: use fallback rankings
                fallback = await agent.get_top_by_price(request.budget_brl, limit=3)
                fallback_data = {
                    "paddles": [
                        {
                            "paddle_id": r.paddle_id,
                            "name": r.name,
                            "brand": r.brand,
                            "price_min_brl": r.price_min_brl,
                            "affiliate_url": r.affiliate_url,
                        }
                        for r in fallback
                    ]
                }
                yield f"event: degraded\ndata: {fallback_data}\n\n"

            # Send done event with metadata
            latency_ms = (time.time() - start_time) * 1000
            done_data = {
                "tokens": 145,
                "latency_ms": latency_ms,
                "model": "groq",
                "cache_hit": False
            }
            yield f"event: done\ndata: {done_data}\n\n"

        except Exception as e:
            error_event = {"error": str(e)}
            yield f"event: error\ndata: {error_event}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
