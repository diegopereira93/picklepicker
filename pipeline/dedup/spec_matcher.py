"""RapidFuzz-based tier-3 fuzzy matching for paddle deduplication."""

import logging
from rapidfuzz import fuzz
from pipeline.db.connection import get_connection
from pipeline.dedup.normalizer import normalize_title

logger = logging.getLogger(__name__)

FUZZY_MATCH_THRESHOLD = 0.85


async def fuzzy_match_paddles(title: str, threshold: float = FUZZY_MATCH_THRESHOLD) -> tuple[int | None, float]:
    """Find best matching paddle by fuzzy title matching using RapidFuzz.

    Uses token_set_ratio for robust matching that handles word reordering.

    Args:
        title: Paddle product title to match
        threshold: RapidFuzz score threshold (0.0-1.0). Default 0.85.

    Returns:
        Tuple of (paddle_id, score) if match found and score >= threshold, else (None, best_score)
    """
    normalized_input = normalize_title(title)

    if not normalized_input:
        return None, 0.0

    async with get_connection() as conn:
        # Get all paddle titles for fuzzy matching
        result = await conn.execute(
            "SELECT id, name FROM paddles ORDER BY id"
        )
        rows = await result.fetchall()

    best_match_id = None
    best_score = 0.0

    for paddle_id, paddle_title in rows:
        normalized_paddle = normalize_title(paddle_title)

        # Calculate fuzzy match score using token_set_ratio
        # This handles word reordering and is more robust than simple ratio
        score = fuzz.token_set_ratio(normalized_input, normalized_paddle) / 100.0

        if score > best_score:
            best_score = score
            best_match_id = paddle_id if score >= threshold else None

    return best_match_id, best_score


async def evaluate_fuzzy_match(title: str, candidate_paddle_id: int, threshold: float = FUZZY_MATCH_THRESHOLD) -> dict:
    """Evaluate if a candidate paddle is a fuzzy match.

    Returns detailed match info for logging and decision making.

    Args:
        title: Source product title
        candidate_paddle_id: Paddle ID to evaluate against
        threshold: Match threshold (default 0.85)

    Returns:
        Dict with:
        - is_match: bool (score >= threshold)
        - score: float (0.0-1.0)
        - source_title: str
        - candidate_title: str
    """
    async with get_connection() as conn:
        result = await conn.execute(
            "SELECT name FROM paddles WHERE id = %(id)s",
            {"id": candidate_paddle_id}
        )
        row = await result.fetchone()

    if not row:
        return {
            "is_match": False,
            "score": 0.0,
            "source_title": title,
            "candidate_title": None,
        }

    candidate_title = row[0]
    normalized_input = normalize_title(title)
    normalized_candidate = normalize_title(candidate_title)

    score = fuzz.token_set_ratio(normalized_input, normalized_candidate) / 100.0

    return {
        "is_match": score >= threshold,
        "score": score,
        "source_title": title,
        "candidate_title": candidate_title,
        "threshold": threshold,
    }
