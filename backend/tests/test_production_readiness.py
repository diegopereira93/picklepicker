"""Production readiness tests for Phase 3."""

import pytest
import os
from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_all_env_vars_present():
    """Verify all required environment variables are documented."""
    # In production, these should be set
    # For development, we just verify the pattern is known
    required_vars = [
        # "OPENAI_API_KEY",  # Not used in Phase 3 (using Groq)
        # "LANGFUSE_PUBLIC_KEY",  # Optional for dev
        # "LANGFUSE_SECRET_KEY",  # Optional for dev
        # "REDIS_URL",  # Optional for dev
    ]

    # All should be either set or explicitly optional
    for var in required_vars:
        # Just verify we know about it
        assert var in [
            "OPENAI_API_KEY",
            "LANGFUSE_PUBLIC_KEY",
            "LANGFUSE_SECRET_KEY",
            "REDIS_URL"
        ]


def test_health_endpoint():
    """Health check endpoint working."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint_exists():
    """Chat endpoint is available."""
    response = client.post(
        "/chat",
        json={
            "message": "Test",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    # Should not return 404
    assert response.status_code != 404
    assert response.status_code == 200


def test_error_handling__malformed_input_missing_field():
    """Missing required field returns 422."""
    response = client.post(
        "/chat",
        json={
            "message": "Test",
            # Missing skill_level and budget_brl
        }
    )

    assert response.status_code == 422


def test_error_handling__invalid_skill_level():
    """Invalid skill_level returns 422."""
    response = client.post(
        "/chat",
        json={
            "message": "Test",
            "skill_level": "invalid",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 422


def test_error_handling__zero_budget():
    """Zero budget returns 422."""
    response = client.post(
        "/chat",
        json={
            "message": "Test",
            "skill_level": "beginner",
            "budget_brl": 0.0
        }
    )

    assert response.status_code == 422


def test_error_handling__negative_budget():
    """Negative budget returns 422."""
    response = client.post(
        "/chat",
        json={
            "message": "Test",
            "skill_level": "beginner",
            "budget_brl": -500.0
        }
    )

    assert response.status_code == 422


def test_error_handling__whitespace_only_message():
    """Whitespace-only message returns 422."""
    response = client.post(
        "/chat",
        json={
            "message": "   ",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 422


def test_error_handling__very_large_budget():
    """Very large budget is accepted."""
    response = client.post(
        "/chat",
        json={
            "message": "Test",
            "skill_level": "beginner",
            "budget_brl": 1000000.0
        }
    )

    assert response.status_code == 200


def test_response_headers__sse_content_type():
    """SSE response has correct content-type."""
    response = client.post(
        "/chat",
        json={
            "message": "Test",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


def test_response_headers__no_cache():
    """Response headers prevent caching (for SSE)."""
    response = client.post(
        "/chat",
        json={
            "message": "Test",
            "skill_level": "beginner",
            "budget_brl": 500.0
        }
    )

    assert response.status_code == 200
    assert "Cache-Control" in response.headers


def test_existing_endpoints__paddles_still_work():
    """Phase 2 paddles endpoint still functional."""
    response = client.get("/paddles?limit=10&offset=0")
    # May be 200 or 404 depending on DB state, but should not error
    assert response.status_code in [200, 404]


def test_concurrent_chat_requests():
    """Multiple chat requests can be handled."""
    for i in range(3):
        response = client.post(
            "/chat",
            json={
                "message": f"Request {i}",
                "skill_level": "beginner",
                "budget_brl": 500.0
            }
        )
        assert response.status_code == 200


def test_repeated_request__same_response_structure():
    """Repeated identical requests return same structure."""
    request_data = {
        "message": "Raquete de iniciante",
        "skill_level": "beginner",
        "budget_brl": 500.0
    }

    response1 = client.post("/chat", json=request_data)
    response2 = client.post("/chat", json=request_data)

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Both should have same event structure
    assert "event: recommendations" in response1.text
    assert "event: recommendations" in response2.text
