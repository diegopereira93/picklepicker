"""Tests for Clerk JWT auth middleware and protected endpoints."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


# --- Auth middleware unit tests ---


@pytest.mark.asyncio
async def test_require_clerk_auth__missing_header__401():
    """Return 401 when no Authorization header."""
    from app.middleware.auth import require_clerk_auth

    mock_request = MagicMock()
    mock_request.headers = {}

    with pytest.raises(Exception) as exc_info:
        await require_clerk_auth(mock_request)

    assert exc_info.value.status_code == 401
    assert "Authorization" in exc_info.value.detail or "requerido" in exc_info.value.detail


@pytest.mark.asyncio
async def test_require_clerk_auth__invalid_scheme__401():
    """Return 401 when Authorization scheme is not Bearer."""
    from app.middleware.auth import require_clerk_auth

    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Basic abc123"}

    with pytest.raises(Exception) as exc_info:
        await require_clerk_auth(mock_request)

    assert exc_info.value.status_code == 401
    assert "Bearer" in exc_info.value.detail


@pytest.mark.asyncio
async def test_require_clerk_auth__empty_token__401():
    """Return 401 when Bearer token is empty."""
    from app.middleware.auth import require_clerk_auth

    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer "}

    with pytest.raises(Exception) as exc_info:
        await require_clerk_auth(mock_request)

    assert exc_info.value.status_code == 401
    assert "vazio" in exc_info.value.detail.lower() or "empty" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_require_clerk_auth__no_jwks_url__503():
    """Return 503 when Clerk JWKS URL is not configured."""
    from app.middleware.auth import require_clerk_auth

    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer some.jwt.token"}

    with patch("app.middleware.auth.CLERK_JWKS_URL", ""):
        with pytest.raises(Exception) as exc_info:
            await require_clerk_auth(mock_request)

        assert exc_info.value.status_code == 503


# --- Protected endpoint integration tests ---


def test_create_price_alert__no_auth__401():
    """POST /price-alerts returns 401 without auth."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/price-alerts",
        json={"user_id": "user_123", "paddle_id": 1, "target_price_brl": 500.0},
    )
    assert response.status_code == 401


def test_get_user_profile__no_auth__401():
    """GET /users/profile/me returns 401 without auth."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/users/profile/me")
    assert response.status_code == 401


def test_save_user_profile__no_auth__401():
    """POST /users/profile returns 401 without auth."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/users/profile",
        json={
            "user_id": "user_123",
            "level": "beginner",
            "style": "control",
            "budget_max": 500.0,
        },
    )
    assert response.status_code == 401


def test_migrate_anonymous__no_auth__401():
    """POST /users/migrate returns 401 without auth."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/users/migrate?old_uuid=old-user-uuid",
    )
    assert response.status_code == 401


# --- Public endpoint tests ---


def test_health__public__200():
    """GET /health works without auth."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/health")
    assert response.status_code == 200
