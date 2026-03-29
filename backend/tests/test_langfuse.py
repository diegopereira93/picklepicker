"""Tests for Langfuse observability integration."""

import pytest
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.langfuse_handler import LangfuseHandler


@pytest.fixture
def langfuse():
    """Create Langfuse handler for testing."""
    return LangfuseHandler(
        public_key="test_public_key",
        secret_key="test_secret_key"
    )


@pytest.mark.asyncio
async def test_langfuse_trace__includes_metadata(langfuse):
    """Trace includes all required metadata."""
    trace = await langfuse.log_chat_trace(
        query_id="query_001",
        user_profile={"skill_level": "beginner", "budget_brl": 500.0},
        model_used="groq",
        input_text="Raquete de iniciante",
        output_text="Recomendo a Raquete A",
        input_tokens=50,
        output_tokens=100,
        latency_ms=1250.5,
        cache_hit=False,
        degraded_mode=False
    )

    assert trace["metadata"]["model"] == "groq"
    assert trace["metadata"]["cache_hit"] is False
    assert trace["metadata"]["degraded"] is False
    assert trace["metadata"]["latency_ms"] == 1250.5
    assert trace["metadata"]["phase"] == "phase-3"


@pytest.mark.asyncio
async def test_langfuse_trace__includes_input_output(langfuse):
    """Trace includes input and output."""
    trace = await langfuse.log_chat_trace(
        query_id="query_002",
        user_profile={"skill_level": "intermediate", "budget_brl": 800.0},
        model_used="claude-sonnet",
        input_text="Melhor raquete para controle",
        output_text="Para controle, a Raquete B é excelente",
        input_tokens=25,
        output_tokens=50,
        latency_ms=800.0,
        cache_hit=False
    )

    assert trace["input"]["query"] == "Melhor raquete para controle"
    assert trace["output"]["response"] == "Para controle, a Raquete B é excelente"
    assert trace["input"]["profile"]["skill_level"] == "intermediate"


@pytest.mark.asyncio
async def test_langfuse_trace__logs_token_counts(langfuse):
    """Token counts logged in usage field."""
    trace = await langfuse.log_chat_trace(
        query_id="query_003",
        user_profile={"skill_level": "advanced", "budget_brl": 1000.0},
        model_used="groq",
        input_text="Query",
        output_text="Response",
        input_tokens=100,
        output_tokens=200,
        latency_ms=500.0,
        cache_hit=True
    )

    assert trace["usage"]["input_tokens"] == 100
    assert trace["usage"]["output_tokens"] == 200
    assert trace["usage"]["total_tokens"] == 300


@pytest.mark.asyncio
async def test_langfuse_trace__cache_hit_flag(langfuse):
    """Cache hit flag recorded correctly."""
    # Cache miss
    trace1 = await langfuse.log_chat_trace(
        query_id="query_004a",
        user_profile={"skill_level": "beginner", "budget_brl": 500.0},
        model_used="groq",
        input_text="Test",
        output_text="Response",
        input_tokens=10,
        output_tokens=20,
        latency_ms=1000.0,
        cache_hit=False
    )
    assert trace1["metadata"]["cache_hit"] is False

    # Cache hit
    trace2 = await langfuse.log_chat_trace(
        query_id="query_004b",
        user_profile={"skill_level": "beginner", "budget_brl": 500.0},
        model_used="groq",
        input_text="Test",
        output_text="Response",
        input_tokens=10,
        output_tokens=20,
        latency_ms=50.0,
        cache_hit=True
    )
    assert trace2["metadata"]["cache_hit"] is True


@pytest.mark.asyncio
async def test_langfuse_trace__degraded_mode_flag(langfuse):
    """Degraded mode flag recorded when timeout occurs."""
    trace = await langfuse.log_chat_trace(
        query_id="query_005",
        user_profile={"skill_level": "beginner", "budget_brl": 500.0},
        model_used="groq",
        input_text="Query",
        output_text="Fallback recommendation",
        input_tokens=10,
        output_tokens=15,
        latency_ms=8500.0,
        cache_hit=False,
        degraded_mode=True
    )

    assert trace["metadata"]["degraded"] is True


@pytest.mark.asyncio
async def test_langfuse_flush__on_shutdown(langfuse):
    """Traces flushed on shutdown."""
    await langfuse.log_chat_trace(
        query_id="query_006",
        user_profile={"skill_level": "beginner", "budget_brl": 500.0},
        model_used="groq",
        input_text="Test",
        output_text="Response",
        input_tokens=10,
        output_tokens=20,
        latency_ms=500.0,
        cache_hit=False
    )

    # Flush should succeed without errors
    await langfuse.flush()


@pytest.mark.asyncio
async def test_langfuse_get_traces__returns_all(langfuse):
    """Get all recorded traces."""
    await langfuse.log_chat_trace(
        query_id="trace_1",
        user_profile={},
        model_used="groq",
        input_text="Query 1",
        output_text="Response 1",
        input_tokens=10,
        output_tokens=20,
        latency_ms=500.0,
        cache_hit=False
    )

    await langfuse.log_chat_trace(
        query_id="trace_2",
        user_profile={},
        model_used="groq",
        input_text="Query 2",
        output_text="Response 2",
        input_tokens=15,
        output_tokens=25,
        latency_ms=600.0,
        cache_hit=False
    )

    traces = langfuse.get_traces()
    assert len(traces) == 2
    assert traces[0]["trace_id"] == "trace_1"
    assert traces[1]["trace_id"] == "trace_2"


@pytest.mark.asyncio
async def test_langfuse_tags__includes_rag_and_chat(langfuse):
    """Traces tagged with chat, rag, paddle-recommendation."""
    trace = await langfuse.log_chat_trace(
        query_id="query_007",
        user_profile={},
        model_used="groq",
        input_text="Test",
        output_text="Response",
        input_tokens=10,
        output_tokens=20,
        latency_ms=500.0,
        cache_hit=False
    )

    assert "chat" in trace["tags"]
    assert "rag" in trace["tags"]
    assert "paddle-recommendation" in trace["tags"]


@pytest.mark.asyncio
async def test_langfuse_clear_traces(langfuse):
    """Clear all traces."""
    await langfuse.log_chat_trace(
        query_id="query_008",
        user_profile={},
        model_used="groq",
        input_text="Test",
        output_text="Response",
        input_tokens=10,
        output_tokens=20,
        latency_ms=500.0,
        cache_hit=False
    )

    assert len(langfuse.get_traces()) == 1

    langfuse.clear_traces()
    assert len(langfuse.get_traces()) == 0
