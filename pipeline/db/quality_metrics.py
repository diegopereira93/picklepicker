"""Data quality metrics tracking module.

Tracks validation failures, null rates, and data quality issues for pipeline monitoring.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from pipeline.db.connection import get_connection


class ValidationFailure(BaseModel):
    """Represents a validation failure for a data field.

    Attributes:
        source: The crawler/data source that produced the failure
        field: The field that failed validation
        reason: Why the validation failed (e.g., 'missing_or_zero', 'invalid_format')
        raw_value: The raw value that failed (optional)
        created_at: When the failure was recorded
    """

    source: str
    field: str
    reason: str
    raw_value: Optional[str] = None
    created_at: datetime = datetime.utcnow()


class NullRateMetric(BaseModel):
    """Represents null rate metrics for a field.

    Attributes:
        source: The data source
        field: The field being measured
        total_records: Total number of records checked
        null_count: Number of null/empty values
        null_rate_pct: Percentage of null values (0-100)
        checked_at: When the metric was calculated
    """

    source: str
    field: str
    total_records: int
    null_count: int
    null_rate_pct: float
    checked_at: datetime = datetime.utcnow()


async def record_validation_failure(
    source: str,
    field: str,
    reason: str,
    raw_value: Optional[str] = None,
) -> None:
    """Record a validation failure for later analysis.

    Args:
        source: Name of the crawler or data source
        field: Field that failed validation
        reason: Reason for the failure (e.g., 'missing_or_zero', 'invalid_format')
        raw_value: Optional raw value that caused the failure
    """
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO data_quality_checks
                (source, field, reason, raw_value, created_at)
            VALUES (%(source)s, %(field)s, %(reason)s, %(raw_value)s, NOW())
            """,
            {
                "source": source,
                "field": field,
                "reason": reason,
                "raw_value": raw_value,
            },
        )
        await conn.commit()


async def get_null_rate_metrics(
    source: str,
    table: str,
    fields: list[str],
) -> list[NullRateMetric]:
    """Calculate null rate metrics for specified fields.

    Args:
        source: Data source name
        table: Database table to query
        fields: List of field names to check for nulls

    Returns:
        List of NullRateMetric objects with null rates for each field
    """
    async with get_connection() as conn:
        results = []
        for field in fields:
            result = await conn.execute(
                f"""
                SELECT
                    COUNT(*) as total_records,
                    COUNT(*) FILTER (WHERE {field} IS NULL OR {field} = '') as null_count
                FROM {table}
                WHERE retailer_id = (
                    SELECT id FROM retailers WHERE name = %(source)s
                )
                """,
                {"source": source},
            )
            row = await result.fetchone()
            if row:
                total = row[0] or 0
                nulls = row[1] or 0
                null_rate = (nulls / total * 100) if total > 0 else 0.0
                results.append(
                    NullRateMetric(
                        source=source,
                        field=field,
                        total_records=total,
                        null_count=nulls,
                        null_rate_pct=round(null_rate, 2),
                    )
                )
        return results


async def get_validation_summary(
    source: str,
    hours: int = 24,
) -> list[dict]:
    """Get aggregated validation failures by source and field.

    Args:
        source: Data source to summarize
        hours: Lookback window in hours (default: 24)

    Returns:
        List of dicts with source, field, and failure_count
    """
    async with get_connection() as conn:
        result = await conn.execute(
            """
            SELECT
                source,
                field,
                COUNT(*) as failure_count
            FROM data_quality_checks
            WHERE source = %(source)s
              AND created_at > NOW() - INTERVAL '%(hours)s hours'
            GROUP BY source, field
            ORDER BY failure_count DESC
            """,
            {"source": source, "hours": hours},
        )
        rows = await result.fetchall()
        return [
            {
                "source": row[0],
                "field": row[1],
                "failure_count": row[2],
            }
            for row in rows
        ]
