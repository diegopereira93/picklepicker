"""Tests for data quality metrics tracking module.

TDD RED phase: Write failing tests for data quality metrics.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from pipeline.db.quality_metrics import (
    ValidationFailure,
    NullRateMetric,
    record_validation_failure,
    get_null_rate_metrics,
    get_validation_summary,
)


class TestValidationFailure:
    """Test ValidationFailure Pydantic model."""

    def test_create_validation_failure(self):
        """Should create a validation failure with all fields."""
        failure = ValidationFailure(
            source="mercado_livre",
            field="price",
            reason="missing_or_zero",
            raw_value="0.00",
        )
        assert failure.source == "mercado_livre"
        assert failure.field == "price"
        assert failure.reason == "missing_or_zero"
        assert failure.raw_value == "0.00"
        assert isinstance(failure.created_at, datetime)

    def test_validation_failure_without_raw_value(self):
        """Should create validation failure without optional raw_value."""
        failure = ValidationFailure(
            source="dropshot_brasil",
            field="name",
            reason="null_value",
        )
        assert failure.raw_value is None


class TestNullRateMetric:
    """Test NullRateMetric Pydantic model."""

    def test_create_null_rate_metric(self):
        """Should create a null rate metric."""
        metric = NullRateMetric(
            source="brazil_pickleball_store",
            field="weight",
            total_records=100,
            null_count=5,
            null_rate_pct=5.0,
        )
        assert metric.source == "brazil_pickleball_store"
        assert metric.field == "weight"
        assert metric.total_records == 100
        assert metric.null_count == 5
        assert metric.null_rate_pct == 5.0


class TestRecordValidationFailure:
    """Test record_validation_failure function."""

    @pytest.mark.asyncio
    async def test_record_validation_failure_inserts_to_db(self):
        """Should insert validation failure into database."""
        mock_conn = AsyncMock()
        mock_result = AsyncMock()
        mock_conn.execute.return_value = mock_result

        with patch("pipeline.db.quality_metrics.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            await record_validation_failure(
                source="mercado_livre",
                field="price",
                reason="missing_or_zero",
                raw_value="0",
            )

            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args
            sql = call_args[0][0]
            params = call_args[0][1]
            assert "INSERT INTO data_quality_checks" in sql
            assert params["source"] == "mercado_livre"
            assert params["field"] == "price"

    @pytest.mark.asyncio
    async def test_record_validation_failure_without_raw_value(self):
        """Should handle missing raw_value gracefully."""
        mock_conn = AsyncMock()

        with patch("pipeline.db.quality_metrics.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            await record_validation_failure(
                source="dropshot_brasil",
                field="image_url",
                reason="empty_string",
            )

            mock_conn.execute.assert_called_once()


class TestGetNullRateMetrics:
    """Test get_null_rate_metrics function."""

    @pytest.mark.asyncio
    async def test_get_null_rate_metrics_returns_list(self):
        """Should return list of NullRateMetric objects."""
        mock_conn = AsyncMock()
        mock_result = AsyncMock()
        # psycopg returns rows as tuples, not dicts
        mock_row = (100, 5)  # total_records, null_count
        mock_result.fetchone.return_value = mock_row
        mock_conn.execute.return_value = mock_result

        with patch("pipeline.db.quality_metrics.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            metrics = await get_null_rate_metrics(
                source="brazil_pickleball_store",
                table="paddles",
                fields=["weight", "thickness"],
            )

            assert isinstance(metrics, list)
            assert len(metrics) == 2  # One metric per field
            assert isinstance(metrics[0], NullRateMetric)
            assert metrics[0].total_records == 100
            assert metrics[0].null_count == 5


class TestGetValidationSummary:
    """Test get_validation_summary function."""

    @pytest.mark.asyncio
    async def test_get_validation_summary_aggregates_failures(self):
        """Should aggregate validation failures by source and field."""
        mock_conn = AsyncMock()
        mock_result = AsyncMock()
        # psycopg returns rows as tuples: (source, field, failure_count)
        mock_row = ("mercado_livre", "price", 10)
        mock_result.fetchall.return_value = [mock_row]
        mock_conn.execute.return_value = mock_result

        with patch("pipeline.db.quality_metrics.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            summary = await get_validation_summary(source="mercado_livre")

            assert isinstance(summary, list)
            assert len(summary) == 1
            assert summary[0]["source"] == "mercado_livre"
            assert summary[0]["failure_count"] == 10
