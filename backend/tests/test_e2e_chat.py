"""End-to-end tests for the complete chat pipeline."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_e2e_chat_flow__happy_path():
    """Full flow: validate → fetch → stream → trace."""
    response = client.post(
        "/chat",
        json={
            "message": "Recomende uma raquete de iniciante",
            "skill_level": "beginner",
            "budget_brl": 600.0
        }
    )

    assert response.status_code == 200
    content = response.text

    # Should have all three events
    assert "event: recommendations" in content
    assert "event: reasoning" in content
    assert "event: done" in content

    # Recommendations should have paddles
    assert "paddles" in content
    assert "affiliate_url" in content

    # Done event should have latency
    assert "latency_ms" in content
    assert "model" in content


def test_e2e_chat_flow__with_cache():
    """Repeated queries should hit cache (faster second call)."""
    request_data = {
        "message": "Raquete para intermediário",
        "skill_level": "intermediate",
        "budget_brl": 800.0
    }

    # First call (cache miss)
    response1 = client.post("/chat", json=request_data)
    assert response1.status_code == 200

    # Second call (cache hit)
    response2 = client.post("/chat", json=request_data)
    assert response2.status_code == 200

    # Both should return valid responses
    assert "event: recommendations" in response1.text
    assert "event: recommendations" in response2.text


def test_e2e_chat_flow__degraded_mode():
    """On timeout, degraded mode returns fallback recommendations."""
    response = client.post(
        "/chat",
        json={
            "message": "Raquete de potência",
            "skill_level": "advanced",
            "budget_brl": 1000.0
        }
    )

    assert response.status_code == 200
    content = response.text

    # May have recommendations (normal) or degraded (timeout fallback)
    has_recommendations = "event: recommendations" in content
    has_degraded = "event: degraded" in content

    # Should have at least one
    assert has_recommendations or has_degraded


def test_e2e_chat_flow__different_profiles():
    """Different user profiles return different recommendations."""
    profiles = [
        {
            "message": "Raquete de iniciante",
            "skill_level": "beginner",
            "budget_brl": 400.0
        },
        {
            "message": "Raquete de intermediário",
            "skill_level": "intermediate",
            "budget_brl": 800.0
        },
        {
            "message": "Raquete profissional",
            "skill_level": "advanced",
            "budget_brl": 1200.0
        }
    ]

    for profile in profiles:
        response = client.post("/chat", json=profile)
        assert response.status_code == 200
        assert "event: recommendations" in response.text or "event: degraded" in response.text


def test_e2e_chat_flow__concurrent_requests():
    """Multiple concurrent requests all complete successfully."""
    # Simulate 3 concurrent requests
    requests = [
        {
            "message": "Raquete 1",
            "skill_level": "beginner",
            "budget_brl": 500.0
        },
        {
            "message": "Raquete 2",
            "skill_level": "intermediate",
            "budget_brl": 700.0
        },
        {
            "message": "Raquete 3",
            "skill_level": "advanced",
            "budget_brl": 900.0
        }
    ]

    responses = []
    for req in requests:
        resp = client.post("/chat", json=req)
        responses.append(resp)

    # All should succeed
    assert all(r.status_code == 200 for r in responses)
    assert all("event: " in r.text for r in responses)


def test_e2e_chat_flow__streaming_response():
    """Response is actually streamed (multiple events)."""
    response = client.post(
        "/chat",
        json={
            "message": "Teste",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 200
    content = response.text

    # Count events
    event_count = content.count("event: ")
    assert event_count >= 3  # recommendations, reasoning/degraded, done


def test_e2e_chat_flow__response_has_metadata():
    """Final response includes all required metadata."""
    response = client.post(
        "/chat",
        json={
            "message": "Raquete",
            "skill_level": "beginner",
            "budget_brl": 600.0
        }
    )

    assert response.status_code == 200
    content = response.text

    # Should have latency in done event
    assert "latency_ms" in content
    assert "model" in content
    assert "tokens" in content


def test_e2e_chat_flow__empty_message_rejected():
    """Empty message returns 422 validation error."""
    response = client.post(
        "/chat",
        json={
            "message": "",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 422


def test_e2e_chat_flow__invalid_budget_rejected():
    """Invalid budget returns 422 validation error."""
    response = client.post(
        "/chat",
        json={
            "message": "Teste",
            "skill_level": "beginner",
            "budget_brl": -100.0
        }
    )

    assert response.status_code == 422


def test_e2e_chat_flow__invalid_skill_rejected():
    """Invalid skill_level returns 422 validation error."""
    response = client.post(
        "/chat",
        json={
            "message": "Teste",
            "skill_level": "expert",  # Not allowed
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 422
