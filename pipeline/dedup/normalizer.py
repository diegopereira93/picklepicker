"""Title normalization and tier-1/2 deduplication matching."""

import hashlib
import re
import logging
from pipeline.db.connection import get_connection

logger = logging.getLogger(__name__)


def normalize_title(title: str) -> str:
    r"""Normalize paddle title for comparison.

    Steps:
    1. Convert to lowercase
    2. Strip leading/trailing whitespace
    3. Remove all punctuation (regex: [^\w\s])
    4. Replace multiple spaces with single space

    Examples:
        "Selkirk Vanguard Power Air™" → "selkirk vanguard power air"
        "JOOLA Ben-Johns Hyperion" → "joola ben johns hyperion"
    """
    normalized = title.lower().strip()
    # Remove all punctuation except word characters and spaces
    normalized = re.sub(r"[^\w\s]", "", normalized)
    # Replace multiple spaces with single space
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def title_hash(title: str) -> str:
    """Compute SHA256 hash of normalized title.

    Used for fast tier-2 deduplication (exact match after normalization).
    """
    normalized = normalize_title(title)
    return hashlib.sha256(normalized.encode()).hexdigest()


async def tier1_match(sku: str, retailer_id: int) -> int | None:
    """Tier 1: Match by manufacturer SKU exact match.

    Args:
        sku: Manufacturer SKU from product
        retailer_id: Retailer ID where product was found

    Returns:
        paddle_id if found, None otherwise
    """
    if not sku or not sku.strip():
        return None

    async with get_connection() as conn:
        result = await conn.execute(
            "SELECT id FROM paddles WHERE manufacturer_sku = %(sku)s",
            {"sku": sku.strip()},
        )
        row = await result.fetchone()
        return row[0] if row else None


async def tier2_match(title: str) -> int | None:
    """Tier 2: Match by title hash (normalized title exact match).

    Args:
        title: Paddle product title

    Returns:
        paddle_id if found, None otherwise
    """
    if not title or not title.strip():
        return None

    hash_value = title_hash(title)

    async with get_connection() as conn:
        result = await conn.execute(
            "SELECT id FROM paddles WHERE title_hash = %(hash)s",
            {"hash": hash_value},
        )
        row = await result.fetchone()
        return row[0] if row else None


async def get_or_create_paddle(title: str, brand: str = "", specs: dict | None = None) -> int:
    """Get existing paddle by title hash or create new one.

    Args:
        title: Paddle product title
        brand: Brand name (optional)
        specs: Technical specifications JSONB (optional)

    Returns:
        paddle_id of existing or newly created paddle
    """
    if specs is None:
        specs = {}

    hash_value = title_hash(title)

    async with get_connection() as conn:
        # Try to find by hash first
        result = await conn.execute(
            "SELECT id FROM paddles WHERE title_hash = %(hash)s",
            {"hash": hash_value},
        )
        row = await result.fetchone()
        if row:
            return row[0]

        # Create new paddle
        result = await conn.execute(
            """
            INSERT INTO paddles (name, brand, title_hash, specs)
            VALUES (%(name)s, %(brand)s, %(title_hash)s, %(specs)s)
            RETURNING id
            """,
            {
                "name": title,
                "brand": brand or "",
                "title_hash": hash_value,
                "specs": specs or {},
            },
        )
        row = await result.fetchone()
        await conn.commit()
        return row[0] if row else None
