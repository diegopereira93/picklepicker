"""Batch embedding service using free providers (Jina AI / Hugging Face)."""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx

from pipeline.embeddings.document_generator import generate_paddle_document
from pipeline.db.connection import get_connection

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSIONS = 768


async def _generate_embedding(text: str) -> list[float]:
    """Generate embedding using free providers with fallback chain: Jina → HF → zero vector."""
    headers_base = {"Content-Type": "application/json"}
    jina_key = os.environ.get("JINA_API_KEY")
    if jina_key:
        headers_base["Authorization"] = f"Bearer {jina_key}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.jina.ai/v1/embeddings",
                json={"model": "jina-embeddings-v2-base-en", "input": [text]},
                headers=headers_base,
            )
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    emb = data["data"][0]["embedding"]
                    if len(emb) < EMBEDDING_DIMENSIONS:
                        return emb + [0.0] * (EMBEDDING_DIMENSIONS - len(emb))
                    return emb[:EMBEDDING_DIMENSIONS]
    except Exception as e:
        logger.warning(f"Jina AI failed: {e}")

    hf_headers = {}
    hf_key = os.environ.get("HUGGINGFACE_API_KEY")
    if hf_key:
        hf_headers["Authorization"] = f"Bearer {hf_key}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2",
                json={"inputs": text},
                headers=hf_headers,
            )
            if response.status_code == 200:
                embeddings = response.json()
                if isinstance(embeddings, list) and len(embeddings) > 0:
                    emb = embeddings[0] if isinstance(embeddings[0], list) else embeddings
                    if len(emb) < EMBEDDING_DIMENSIONS:
                        return emb + [0.0] * (EMBEDDING_DIMENSIONS - len(emb))
                    return emb[:EMBEDDING_DIMENSIONS]
    except Exception as e:
        logger.warning(f"Hugging Face failed: {e}")

    logger.warning("All embedding providers failed, returning zero vector")
    return [0.0] * EMBEDDING_DIMENSIONS


async def batch_embed_paddles(
    paddle_ids: Optional[list[int]] = None,
    batch_size: int = 5,
    db_pool=None,
) -> dict:
    """Batch embed paddles using free embedding providers (Jina → HF → zero vector)."""
    total_embedded = 0

    try:
        async with get_connection() as conn:
            if paddle_ids is None:
                result = await conn.execute(
                    "SELECT id FROM paddles "
                    "WHERE NOT EXISTS (SELECT 1 FROM paddle_embeddings WHERE paddle_embeddings.paddle_id = paddles.id) "
                    "LIMIT 1000"
                )
                rows = await result.fetchall()
                paddle_ids = [row[0] for row in rows] if rows else []

            if not paddle_ids:
                logger.info("No paddles to embed")
                return {"status": "success", "total_embedded": 0}

            logger.info(f"Embedding {len(paddle_ids)} paddles in batches of {batch_size}")

            for paddle_id in paddle_ids:
                result = await conn.execute(
                    """SELECT p.id, p.name, p.brand, p.price_min_brl,
                              ps.swingweight, ps.twistweight, ps.weight_oz,
                              ps.core_thickness_mm, ps.face_material
                       FROM paddles p
                       LEFT JOIN paddle_specs ps ON p.id = ps.paddle_id
                       WHERE p.id = $1""",
                    [paddle_id],
                )
                row = await result.fetchone()
                if not row:
                    continue

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
                        "face_material": row[8],
                    },
                }
                doc = generate_paddle_document(paddle_dict)
                embedding = await _generate_embedding(doc)

                now = datetime.now(timezone.utc)
                await conn.execute(
                    """INSERT INTO paddle_embeddings (paddle_id, embedding, updated_at)
                       VALUES ($1, $2::vector, $3)
                       ON CONFLICT (paddle_id) DO UPDATE SET embedding = $2::vector, updated_at = $3""",
                    [paddle_id, str(embedding), now],
                )
                total_embedded += 1
                logger.info(f"Embedded paddle {paddle_id} ({total_embedded}/{len(paddle_ids)})")

                if total_embedded % batch_size == 0:
                    await asyncio.sleep(0.5)

        result = {"status": "success", "total_embedded": total_embedded}
        logger.info(f"Embedding complete: {result}")
        return result

    except Exception as e:
        logger.error(f"Batch embedding failed: {e}", exc_info=True)
        raise


async def re_embed_flagged_paddles(db_pool=None) -> dict:
    """Re-embed paddles that have needs_reembed=true flag."""
    logger.info("Starting re-embedding of flagged paddles")

    try:
        async with get_connection() as conn:
            result = await conn.execute(
                "SELECT id FROM paddles WHERE needs_reembed = true LIMIT 1000"
            )
            rows = await result.fetchall()
            paddle_ids = [row[0] for row in rows] if rows else []

            if not paddle_ids:
                logger.info("No flagged paddles to re-embed")
                return {"status": "success", "total_re_embedded": 0}

            logger.info(f"Re-embedding {len(paddle_ids)} flagged paddles")
            embed_result = await batch_embed_paddles(paddle_ids, batch_size=5, db_pool=db_pool)

            if embed_result["total_embedded"] > 0:
                await conn.execute(
                    "UPDATE paddles SET needs_reembed = false WHERE id = ANY($1::int[])",
                    [paddle_ids],
                )
                logger.info(f"Reset needs_reembed flag for {len(paddle_ids)} paddles")

            return {
                "status": "success",
                "total_re_embedded": embed_result.get("total_embedded", 0),
            }

    except Exception as e:
        logger.error(f"Re-embedding failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(batch_embed_paddles())
