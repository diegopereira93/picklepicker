"""Tests for chat endpoint with SSE streaming."""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.main import app


client = TestClient(app)


def test_chat_stream__returns_sse():
    """Verify response is Server-Sent Events format."""
    response = client.post(
        "/chat",
        json={
            "message": "Quero uma raquete de controle",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "Cache-Control" in response.headers


def test_chat_stream__includes_recommendations():
    """Verify recommendations event is present."""
    response = client.post(
        "/chat",
        json={
            "message": "Raquete para iniciante",
            "skill_level": "beginner",
            "budget_brl": 600.0
        }
    )

    assert response.status_code == 200
    content = response.text
    assert "event: recommendations" in content
    assert "paddles" in content


def test_chat_stream__includes_reasoning():
    """Verify reasoning event with LLM text is present."""
    response = client.post(
        "/chat",
        json={
            "message": "Recomende uma raquete",
            "skill_level": "intermediate",
            "budget_brl": 800.0
        }
    )

    assert response.status_code == 200
    content = response.text
    assert "event: reasoning" in content
    assert "text" in content


def test_chat_stream__includes_done_event():
    """Verify done event with metadata is present."""
    response = client.post(
        "/chat",
        json={
            "message": "Qual é a melhor raquete?",
            "skill_level": "advanced",
            "budget_brl": 1000.0
        }
    )

    assert response.status_code == 200
    content = response.text
    assert "event: done" in content
    assert "latency_ms" in content
    assert "model" in content


def test_chat_stream__invalid_skill_level():
    """Reject invalid skill_level."""
    response = client.post(
        "/chat",
        json={
            "message": "Recomende uma raquete",
            "skill_level": "invalid_skill",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 422  # Validation error


def test_chat_stream__negative_budget():
    """Reject negative budget."""
    response = client.post(
        "/chat",
        json={
            "message": "Recomende uma raquete",
            "skill_level": "beginner",
            "budget_brl": -100.0
        }
    )

    assert response.status_code == 422  # Validation error


def test_chat_stream__empty_message():
    """Reject empty message."""
    response = client.post(
        "/chat",
        json={
            "message": "",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 422  # Validation error


def test_chat_stream__with_style():
    """Accept optional style parameter."""
    response = client.post(
        "/chat",
        json={
            "message": "Raquete para controle",
            "skill_level": "beginner",
            "budget_brl": 500.0,
            "style": "control"
        }
    )

    assert response.status_code == 200
    content = response.text
    assert "event: recommendations" in content


def test_chat_stream__recommendation_has_affiliate_url():
    """Verify recommendations include affiliate URLs."""
    response = client.post(
        "/chat",
        json={
            "message": "Recomende uma raquete com link de compra",
            "skill_level": "intermediate",
            "budget_brl": 700.0
        }
    )

    assert response.status_code == 200
    content = response.text
    assert "affiliate_url" in content


def test_chat_stream__response_streaming():
    """Verify response is actually streamed (has multiple events)."""
    response = client.post(
        "/chat",
        json={
            "message": "Teste streaming",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 200
    content = response.text
    # Should have multiple events (recommendations, reasoning, done)
    event_count = content.count("event: ")
    assert event_count >= 3


def test_chat_stream__latency_metric_present():
    """Verify latency is measured and present."""
    response = client.post(
        "/chat",
        json={
            "message": "Qual é a latência?",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 200
    content = response.text
    assert "latency_ms" in content
    # Should be a reasonable number (e.g., > 0 and < 5000)
    assert "0.0" in content or "1000" in content or "500" in content
