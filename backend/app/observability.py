"""Observability and latency tracking."""

import time
from collections import deque
from typing import Optional


class LatencyTracker:
    """Track request latencies and compute P95 percentile."""

    def __init__(self, window_size: int = 1000):
        """Initialize latency tracker.

        Args:
            window_size: Number of latencies to keep (default 1000)
        """
        self.latencies_ms = deque(maxlen=window_size)

    async def record(self, latency_ms: float) -> None:
        """Record a request latency.

        Args:
            latency_ms: Latency in milliseconds
        """
        self.latencies_ms.append(latency_ms)

    def p95_latency_ms(self) -> Optional[float]:
        """Calculate P95 latency from recorded measurements.

        Returns:
            95th percentile latency in milliseconds, or None if no data
        """
        if not self.latencies_ms:
            return None

        sorted_latencies = sorted(self.latencies_ms)
        p95_index = int(0.95 * len(sorted_latencies))
        return float(sorted_latencies[p95_index])

    async def check_budget(self, latency_ms: float, budget_ms: float = 3000.0) -> bool:
        """Check if latency is within budget.

        Args:
            latency_ms: Measured latency
            budget_ms: Budget threshold (default 3000ms = 3s)

        Returns:
            True if latency < budget_ms
        """
        return latency_ms < budget_ms

    def get_stats(self) -> dict:
        """Get latency statistics.

        Returns:
            Dict with min, max, mean, p95, count
        """
        if not self.latencies_ms:
            return {
                "min_ms": None,
                "max_ms": None,
                "mean_ms": None,
                "p95_ms": None,
                "count": 0,
            }

        lats = list(self.latencies_ms)
        sorted_lats = sorted(lats)
        p95_index = int(0.95 * len(sorted_lats))

        return {
            "min_ms": float(min(lats)),
            "max_ms": float(max(lats)),
            "mean_ms": float(sum(lats) / len(lats)),
            "p95_ms": float(sorted_lats[p95_index]),
            "count": len(lats),
        }
