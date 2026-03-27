"""Batch embedding service using OpenAI text-embedding-3-small."""

import logging
import asyncio
import os
from typing import Optional
from datetime import datetime
from openai import AsyncOpenAI
from pipeline.embeddings.document_generator import generate_paddle_document
from pipeline.db.connection import get_connection

logger = logging.getLogger(__name__)


async def batch_embed_paddles(
    paddle_ids: Optional[list[int]] = None,
    batch_size: int = 5,
    db_pool=None
) -> dict:
    """
    Batch embed paddles using OpenAI text-embedding-3-small.

    Args:
        paddle_ids: List of paddle IDs to embed, or None for all unembedded
        batch_size: Number of paddles per OpenAI API call
        db_pool: Database connection pool (for compatibility, uses global pool)

    Returns:
        Dict with status, total_embedded, tokens, and estimated cost
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    total_embedded = 0
    total_tokens = 0
    cost_usd = 0.0

    try:
        async with get_connection() as conn:
            # Fetch paddle IDs if not provided
            if paddle_ids is None:
                result = await conn.execute(
                    "SELECT id FROM paddles WHERE NOT EXISTS (SELECT 1 FROM paddle_embeddings WHERE paddle_embeddings.paddle_id = paddles.id) LIMIT 1000"
                )
                rows = await result.fetchall()
                paddle_ids = [row[0] for row in rows] if rows else []

            if not paddle_ids:
                logger.info("No paddles to embed")
                return {
                    "status": "success",
                    "total_embedded": 0,
                    "tokens": 0,
                    "cost_usd": 0.0
                }

            logger.info(f"Embedding {len(paddle_ids)} paddles in batches of {batch_size}")

            # Fetch paddle documents
            paddle_docs = {}
            for paddle_id in paddle_ids:
                result = await conn.execute(
                    """SELECT p.id, p.name, p.brand, p.price_min_brl,
                              ps.swingweight, ps.twistweight, ps.weight_oz, ps.core_thickness_mm, ps.face_material
                       FROM paddles p
                       LEFT JOIN paddle_specs ps ON p.id = ps.paddle_id
                       WHERE p.id = $1""",
                    [paddle_id]
                )
                row = await result.fetchone()
                if row:
                    paddle_dict = {
                        "id": row[0],
                        "name": row[1],
                        "brand": row[2],
                        "price_min": row[3],
                        "specs": {
                            "swingweight": row[4],
                            "twistweight": row[5],
                            "weight_oz": row[6],
                            "core_thickness_mm": row[7],
                            "face_material": row[8]
                        }
                    }
                    doc = generate_paddle_document(paddle_dict)
                    paddle_docs[paddle_id] = doc

            # Process in batches
            for i in range(0, len(paddle_ids), batch_size):
                batch_ids = paddle_ids[i:i+batch_size]
                batch_docs = [paddle_docs.get(pid, "") for pid in batch_ids]

                if not batch_docs or all(d == "" for d in batch_docs):
                    continue

                # Call OpenAI embedding API
                logger.info(f"Calling OpenAI for batch {i//batch_size + 1} ({len(batch_docs)} docs)")
                response = await client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch_docs
                )

                # Store embeddings in DB
                for j, embed_obj in enumerate(response.data):
                    paddle_id = batch_ids[j]
                    embedding_vector = embed_obj.embedding

                    # INSERT or UPDATE paddle_embeddings
                    await conn.execute(
                        """INSERT INTO paddle_embeddings (paddle_id, embedding, updated_at)
                           VALUES ($1, $2::vector, $3)
                           ON CONFLICT (paddle_id) DO UPDATE SET embedding = $2::vector, updated_at = $3""",
                        [paddle_id, embedding_vector, datetime.utcnow()]
                    )
                    total_embedded += 1

                # Track tokens
                total_tokens += response.usage.total_tokens
                logger.info(f"Embedded {total_embedded} paddles, {total_tokens} tokens used so far")

                # Respect rate limits: small delay between batches
                if i + batch_size < len(paddle_ids):
                    await asyncio.sleep(0.5)

        cost_usd = (total_tokens / 1_000_000) * 0.02  # $0.02 per 1M tokens
        result = {
            "status": "success",
            "total_embedded": total_embedded,
            "tokens": total_tokens,
            "cost_usd": round(cost_usd, 6)
        }
        logger.info(f"Embedding complete: {result}")
        return result

    except Exception as e:
        logger.error(f"Batch embedding failed: {e}", exc_info=True)
        raise


async def re_embed_flagged_paddles(db_pool=None) -> dict:
    """
    Re-embed paddles that have needs_reembed=true flag.

    Args:
        db_pool: Database connection pool (for compatibility, uses global pool)

    Returns:
        Embedding result dict
    """
    logger.info("Starting re-embedding of flagged paddles")

    try:
        async with get_connection() as conn:
            # Fetch flagged paddle IDs
            result = await conn.execute(
                "SELECT id FROM paddles WHERE needs_reembed = true LIMIT 1000"
            )
            rows = await result.fetchall()
            paddle_ids = [row[0] for row in rows] if rows else []

            if not paddle_ids:
                logger.info("No flagged paddles to re-embed")
                return {
                    "status": "success",
                    "total_re_embedded": 0,
                    "tokens": 0,
                    "cost_usd": 0.0
                }

            logger.info(f"Re-embedding {len(paddle_ids)} flagged paddles")

            # Call batch_embed_paddles
            embed_result = await batch_embed_paddles(paddle_ids, batch_size=5, db_pool=db_pool)

            # Reset needs_reembed flag
            if embed_result["total_embedded"] > 0:
                await conn.execute(
                    "UPDATE paddles SET needs_reembed = false WHERE id = ANY($1::int[])",
                    [paddle_ids]
                )
                logger.info(f"Reset needs_reembed flag for {len(paddle_ids)} paddles")

            return {
                "status": "success",
                "total_re_embedded": embed_result.get("total_embedded", 0),
                "tokens": embed_result.get("tokens", 0),
                "cost_usd": embed_result.get("cost_usd", 0.0)
            }

    except Exception as e:
        logger.error(f"Re-embedding failed: {e}", exc_info=True)
        raise
