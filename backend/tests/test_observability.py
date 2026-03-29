"""Tests for observability and latency tracking."""

import pytest
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.observability import LatencyTracker


@pytest.fixture
def tracker():
    """Create latency tracker for testing."""
    return LatencyTracker(window_size=100)


@pytest.mark.asyncio
async def test_latency_tracker__records_value(tracker):
    """Record a latency value."""
    await tracker.record(150.5)
    await tracker.record(200.0)
    await tracker.record(175.5)

    assert len(tracker.latencies_ms) == 3
    assert 150.5 in tracker.latencies_ms


@pytest.mark.asyncio
async def test_latency_tracker__p95_calculation(tracker):
    """Calculate P95 percentile correctly."""
    # Add 100 values: 1-100ms
    for i in range(1, 101):
        await tracker.record(float(i))

    p95 = tracker.p95_latency_ms()

    # P95 of 1-100 should be around 95-96ms
    assert p95 is not None
    assert 94 <= p95 <= 96


@pytest.mark.asyncio
async def test_latency_tracker__p95_with_few_samples(tracker):
    """P95 works with small sample sizes."""
    await tracker.record(100.0)
    await tracker.record(200.0)
    await tracker.record(300.0)

    p95 = tracker.p95_latency_ms()
    assert p95 is not None
    assert isinstance(p95, float)


@pytest.mark.asyncio
async def test_latency_tracker__p95_empty(tracker):
    """P95 returns None when no data."""
    p95 = tracker.p95_latency_ms()
    assert p95 is None


@pytest.mark.asyncio
async def test_budget_check__under_3s(tracker):
    """Latency under 3s passes budget check."""
    result = await tracker.check_budget(2500.0)
    assert result is True

    result = await tracker.check_budget(2999.0)
    assert result is True


@pytest.mark.asyncio
async def test_budget_check__over_3s(tracker):
    """Latency over 3s fails budget check."""
    result = await tracker.check_budget(3000.0)
    assert result is False

    result = await tracker.check_budget(3001.0)
    assert result is False


@pytest.mark.asyncio
async def test_budget_check__custom_threshold(tracker):
    """Custom budget threshold works."""
    # Budget 500ms
    result = await tracker.check_budget(400.0, budget_ms=500.0)
    assert result is True

    result = await tracker.check_budget(500.0, budget_ms=500.0)
    assert result is False


@pytest.mark.asyncio
async def test_latency_tracker__window_size_limit(tracker):
    """Tracker respects max window size."""
    # Add 150 values (max is 100)
    for i in range(150):
        await tracker.record(float(i))

    # Should only keep last 100
    assert len(tracker.latencies_ms) == 100


@pytest.mark.asyncio
async def test_latency_tracker__get_stats(tracker):
    """Get comprehensive statistics."""
    await tracker.record(100.0)
    await tracker.record(200.0)
    await tracker.record(300.0)

    stats = tracker.get_stats()

    assert stats["min_ms"] == 100.0
    assert stats["max_ms"] == 300.0
    assert stats["mean_ms"] == 200.0  # (100 + 200 + 300) / 3
    assert stats["p95_ms"] is not None
    assert stats["count"] == 3


@pytest.mark.asyncio
async def test_latency_tracker__get_stats_empty(tracker):
    """Get stats on empty tracker."""
    stats = tracker.get_stats()

    assert stats["min_ms"] is None
    assert stats["max_ms"] is None
    assert stats["mean_ms"] is None
    assert stats["p95_ms"] is None
    assert stats["count"] == 0
