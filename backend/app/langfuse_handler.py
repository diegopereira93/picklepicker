"""Langfuse observability integration for chat traces."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone


class LangfuseHandler:
    """Mock Langfuse handler for development (production uses Langfuse v3)."""

    def __init__(self, public_key: Optional[str] = None, secret_key: Optional[str] = None):
        """Initialize Langfuse handler.

        Args:
            public_key: Langfuse public key
            secret_key: Langfuse secret key
        """
        self.public_key = public_key
        self.secret_key = secret_key
        self.traces: list[Dict[str, Any]] = []

    async def log_chat_trace(
        self,
        query_id: str,
        user_profile: Dict[str, Any],
        model_used: str,
        input_text: str,
        output_text: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        cache_hit: bool,
        degraded_mode: bool = False,
    ) -> Dict[str, Any]:
        """Log a chat trace to Langfuse.

        Args:
            query_id: Unique trace ID
            user_profile: {skill_level, budget_brl, style}
            model_used: Model name (groq, claude-sonnet)
            input_text: User message
            output_text: LLM response
            input_tokens: Input token count
            output_tokens: Output token count
            latency_ms: Response latency in ms
            cache_hit: Was this a cache hit?
            degraded_mode: Was degraded mode triggered?

        Returns:
            Trace dict with metadata
        """
        trace = {
            "trace_id": query_id,
            "name": "chat_recommendation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": {
                "query": input_text,
                "profile": user_profile
            },
            "output": {
                "response": output_text
            },
            "metadata": {
                "model": model_used,
                "cache_hit": cache_hit,
                "degraded": degraded_mode,
                "latency_ms": latency_ms,
                "phase": "phase-3"
            },
            "tags": ["chat", "rag", "paddle-recommendation"],
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }
        }

        self.traces.append(trace)
        return trace

    async def flush(self) -> None:
        """Flush pending traces (production: sends to Langfuse API)."""
        # In production, this sends traces to Langfuse
        # For development, we just clear the buffer (traces are already stored)
        pass

    def get_traces(self) -> list[Dict[str, Any]]:
        """Get all recorded traces (for testing)."""
        return self.traces

    def clear_traces(self) -> None:
        """Clear all traces (for testing)."""
        self.traces.clear()
