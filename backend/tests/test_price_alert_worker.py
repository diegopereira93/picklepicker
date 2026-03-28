"""Unit tests for price alert worker.

Tests use mocked DB connections and Resend API — no real network calls.
"""

import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch, call

from backend.workers.price_alert_check import (
    check_price_alerts,
    send_email,
    _build_alert_email_html,
    COOLDOWN_HOURS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_alert_row(
    alert_id=1,
    user_id="user-1",
    paddle_id=10,
    price_target=Decimal("500.00"),
    last_triggered=None,
    paddle_name="Joola Ben Johns Hyperion",
    email="player@example.com",
):
    return (alert_id, user_id, paddle_id, price_target, last_triggered, paddle_name, email)


def _make_price_row(price_brl):
    return (Decimal(str(price_brl)),)


# ---------------------------------------------------------------------------
# Email HTML builder
# ---------------------------------------------------------------------------

def test_email_html_contains_paddle_name():
    html = _build_alert_email_html("Joola Ben Johns", 450.00, 500.00)
    assert "Joola Ben Johns" in html


def test_email_html_contains_current_price():
    html = _build_alert_email_html("Any Paddle", 399.90, 500.00)
    assert "399.90" in html


def test_email_html_contains_subject_keyword():
    html = _build_alert_email_html("Any", 100.0, 200.0)
    assert "promocao" in html.lower() or "promoção" in html.lower() or "Raquete" in html


# ---------------------------------------------------------------------------
# send_email
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_send_email_returns_true_on_200():
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch.dict("os.environ", {"RESEND_API_KEY": "test-key"}):
        result = await send_email(mock_client, "a@b.com", "Paddle X", 450.0, 500.0)

    assert result is True


@pytest.mark.asyncio
async def test_send_email_returns_false_on_4xx():
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.text = "Unprocessable"

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch.dict("os.environ", {"RESEND_API_KEY": "test-key"}):
        result = await send_email(mock_client, "a@b.com", "Paddle X", 450.0, 500.0)

    assert result is False


@pytest.mark.asyncio
async def test_send_email_payload_has_correct_subject():
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch.dict("os.environ", {"RESEND_API_KEY": "test-key"}):
        await send_email(mock_client, "a@b.com", "Paddle X", 399.99, 500.0)

    call_kwargs = mock_client.post.call_args.kwargs
    payload = call_kwargs["json"]
    assert "399.99" in payload["subject"]
    assert "promocao" in payload["subject"].lower() or "Raquete" in payload["subject"]


# ---------------------------------------------------------------------------
# check_price_alerts — core logic
# ---------------------------------------------------------------------------

def _build_mock_conn(alert_rows, price_value):
    """Build a mock psycopg AsyncConnection with execute returning configured rows."""
    # cursor for alerts query
    alerts_cursor = AsyncMock()
    alerts_cursor.fetchall = AsyncMock(return_value=alert_rows)

    # cursor for price query
    price_cursor = AsyncMock()
    price_cursor.fetchone = AsyncMock(return_value=_make_price_row(price_value) if price_value is not None else None)

    conn = AsyncMock()
    conn.execute = AsyncMock(side_effect=[alerts_cursor, price_cursor])
    conn.commit = AsyncMock()

    # Support async context manager
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=False)

    return conn


@pytest.mark.asyncio
async def test_email_sent_when_price_below_target():
    """When current_price <= price_target, email must be sent and last_triggered updated."""
    alert = _make_alert_row(price_target=Decimal("500.00"))
    current_price = 450.0  # below target

    mock_conn = _build_mock_conn([alert], current_price)

    with (
        patch("backend.workers.price_alert_check.psycopg.AsyncConnection.connect", return_value=mock_conn),
        patch("backend.workers.price_alert_check.RESEND_API_KEY", "test-key"),
        patch("backend.workers.price_alert_check.DATABASE_URL", "postgresql://fake"),
        patch("backend.workers.price_alert_check.send_email", new_callable=AsyncMock) as mock_send,
    ):
        mock_send.return_value = True
        checked, triggered = await check_price_alerts()

    assert checked == 1
    assert triggered == 1
    mock_send.assert_called_once()
    # Verify last_triggered was updated (conn.execute called 3 times: alerts, price, update)
    assert mock_conn.execute.call_count == 3
    mock_conn.commit.assert_called_once()


@pytest.mark.asyncio
async def test_email_sent_when_price_equals_target():
    """Edge case: price exactly equal to target should trigger."""
    alert = _make_alert_row(price_target=Decimal("500.00"))
    current_price = 500.0  # equal to target

    mock_conn = _build_mock_conn([alert], current_price)

    with (
        patch("backend.workers.price_alert_check.psycopg.AsyncConnection.connect", return_value=mock_conn),
        patch("backend.workers.price_alert_check.RESEND_API_KEY", "test-key"),
        patch("backend.workers.price_alert_check.DATABASE_URL", "postgresql://fake"),
        patch("backend.workers.price_alert_check.send_email", new_callable=AsyncMock) as mock_send,
    ):
        mock_send.return_value = True
        checked, triggered = await check_price_alerts()

    assert triggered == 1


@pytest.mark.asyncio
async def test_email_not_sent_when_price_above_target():
    """When current_price > price_target, no email should be sent."""
    alert = _make_alert_row(price_target=Decimal("400.00"))
    current_price = 550.0  # above target

    mock_conn = _build_mock_conn([alert], current_price)

    with (
        patch("backend.workers.price_alert_check.psycopg.AsyncConnection.connect", return_value=mock_conn),
        patch("backend.workers.price_alert_check.RESEND_API_KEY", "test-key"),
        patch("backend.workers.price_alert_check.DATABASE_URL", "postgresql://fake"),
        patch("backend.workers.price_alert_check.send_email", new_callable=AsyncMock) as mock_send,
    ):
        checked, triggered = await check_price_alerts()

    assert checked == 1
    assert triggered == 0
    mock_send.assert_not_called()
    mock_conn.commit.assert_not_called()


@pytest.mark.asyncio
async def test_last_triggered_not_updated_when_email_fails():
    """If Resend returns error, last_triggered must NOT be updated."""
    alert = _make_alert_row(price_target=Decimal("500.00"))
    current_price = 450.0

    mock_conn = _build_mock_conn([alert], current_price)

    with (
        patch("backend.workers.price_alert_check.psycopg.AsyncConnection.connect", return_value=mock_conn),
        patch("backend.workers.price_alert_check.RESEND_API_KEY", "test-key"),
        patch("backend.workers.price_alert_check.DATABASE_URL", "postgresql://fake"),
        patch("backend.workers.price_alert_check.send_email", new_callable=AsyncMock) as mock_send,
    ):
        mock_send.return_value = False  # email failed
        checked, triggered = await check_price_alerts()

    assert triggered == 0
    # Only 2 execute calls: alerts query + price query (no UPDATE)
    assert mock_conn.execute.call_count == 2
    mock_conn.commit.assert_not_called()


@pytest.mark.asyncio
async def test_skips_alert_with_no_price_data():
    """When latest_prices returns no row for paddle, alert is skipped."""
    alert = _make_alert_row(paddle_id=99)

    mock_conn = _build_mock_conn([alert], price_value=None)

    with (
        patch("backend.workers.price_alert_check.psycopg.AsyncConnection.connect", return_value=mock_conn),
        patch("backend.workers.price_alert_check.RESEND_API_KEY", "test-key"),
        patch("backend.workers.price_alert_check.DATABASE_URL", "postgresql://fake"),
        patch("backend.workers.price_alert_check.send_email", new_callable=AsyncMock) as mock_send,
    ):
        checked, triggered = await check_price_alerts()

    assert checked == 1
    assert triggered == 0
    mock_send.assert_not_called()


@pytest.mark.asyncio
async def test_multiple_alerts_independent():
    """Multiple alerts processed independently — only qualifying ones trigger."""
    alerts = [
        _make_alert_row(alert_id=1, price_target=Decimal("500.00"), email="a@a.com"),
        _make_alert_row(alert_id=2, price_target=Decimal("300.00"), email="b@b.com"),
    ]
    # First alert: price 450 <= 500 → triggers
    # Second alert: price 450 > 300 → skips

    price_cursor_1 = AsyncMock()
    price_cursor_1.fetchone = AsyncMock(return_value=_make_price_row(450.0))
    price_cursor_2 = AsyncMock()
    price_cursor_2.fetchone = AsyncMock(return_value=_make_price_row(450.0))

    alerts_cursor = AsyncMock()
    alerts_cursor.fetchall = AsyncMock(return_value=alerts)

    conn = AsyncMock()
    conn.execute = AsyncMock(side_effect=[alerts_cursor, price_cursor_1, price_cursor_2])
    conn.commit = AsyncMock()
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("backend.workers.price_alert_check.psycopg.AsyncConnection.connect", return_value=conn),
        patch("backend.workers.price_alert_check.RESEND_API_KEY", "test-key"),
        patch("backend.workers.price_alert_check.DATABASE_URL", "postgresql://fake"),
        patch("backend.workers.price_alert_check.send_email", new_callable=AsyncMock) as mock_send,
    ):
        mock_send.return_value = True
        checked, triggered = await check_price_alerts()

    assert checked == 2
    assert triggered == 1


@pytest.mark.asyncio
async def test_raises_without_database_url():
    with patch.dict("os.environ", {}, clear=True):
        with patch("backend.workers.price_alert_check.DATABASE_URL", None):
            with patch("backend.workers.price_alert_check.RESEND_API_KEY", "key"):
                with pytest.raises(RuntimeError, match="DATABASE_URL"):
                    await check_price_alerts()


@pytest.mark.asyncio
async def test_raises_without_resend_api_key():
    with patch("backend.workers.price_alert_check.DATABASE_URL", "postgresql://fake"):
        with patch("backend.workers.price_alert_check.RESEND_API_KEY", None):
            with pytest.raises(RuntimeError, match="RESEND_API_KEY"):
                await check_price_alerts()
