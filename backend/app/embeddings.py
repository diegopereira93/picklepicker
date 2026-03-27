"""Embeddings service for similarity search."""

import logging
from typing import List
from pipeline.db.connection import get_connection

logger = logging.getLogger(__name__)


async def get_similar_paddles(
    query_embedding: List[float],
    top_k: int = 5,
    threshold: float = 0.65
) -> List[int]:
    """
    Find paddles similar to the query embedding using pgvector cosine similarity.

    Args:
        query_embedding: Query embedding vector (1536 dimensions)
        top_k: Number of results to return
        threshold: Similarity threshold (0.65 for cosine similarity)

    Returns:
        List of paddle IDs sorted by similarity
    """
    try:
        async with get_connection() as conn:
            # Query using pgvector cosine distance operator
            # cosine distance = 1 - cosine similarity
            # So we use <= (1 - threshold) to filter
            query = """
            SELECT paddle_id, (embedding <-> $1::vector) AS distance
            FROM paddle_embeddings
            WHERE (embedding <-> $1::vector) <= (1 - $2)
            ORDER BY distance
            LIMIT $3
            """

            result = await conn.execute(query, [query_embedding, threshold, top_k])
            rows = await result.fetchall()

            paddle_ids = [row[0] for row in rows] if rows else []
            logger.info(f"Found {len(paddle_ids)} similar paddles with threshold {threshold}")

            return paddle_ids

    except Exception as e:
        logger.error(f"Similarity search failed: {e}", exc_info=True)
        raise
