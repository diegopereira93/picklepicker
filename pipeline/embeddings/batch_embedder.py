"""Batch embedding service using configurable providers.

Provider priority (based on EMBEDDING_PROVIDER env var):
- When EMBEDDING_PROVIDER=gemini and GEMINI_API_KEY is set: use Gemini → Jina → HF → zero vector
- When EMBEDDING_PROVIDER=jina or not set: use Jina → HF → zero vector (DEFAULT behavior)
"""

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


async def _try_gemini(text: str) -> list[float]:
    """Generate embedding via Gemini API (requires GEMINI_API_KEY)."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY not configured")

    payload = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [{"text": text}]
        },
        "taskType": "RETRIEVAL_DOCUMENT",  # Using DOCUMENT for embedding storage
        "outputDimensionality": EMBEDDING_DIMENSIONS,
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": gemini_key
    }

    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        if "embedding" not in data or "values" not in data["embedding"]:
            raise RuntimeError("Invalid Gemini response: no embedding")

        embedding = data["embedding"]["values"]

        if len(embedding) != EMBEDDING_DIMENSIONS:
            raise RuntimeError(
                f"Unexpected dimension: {len(embedding)}, expected: {EMBEDDING_DIMENSIONS}"
            )

        return embedding


async def _generate_embedding(text: str) -> list[float]:
    """Generate embedding using configurable providers with fallback chain.
    
    Provider priority (based on EMBEDDING_PROVIDER env var):
    - When EMBEDDING_PROVIDER=gemini and GEMINI_API_KEY is set: use Gemini → Jina → HF → zero vector
    - When EMBEDDING_PROVIDER=jina or not set: use Jina → HF → zero vector (DEFAULT behavior)
    """
    provider = os.environ.get("EMBEDDING_PROVIDER", "jina").lower()
    
    logger.info(f"Embedding with provider: {provider}")
    
    # Provider selection based on EMBEDDING_PROVIDER env var
    if provider == "gemini":
        # When EMBEDDING_PROVIDER=gemini and GEMINI_API_KEY is set: use Gemini API
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                embedding = await _try_gemini(text)
                logger.info(f"embedding_provider: gemini, dimensions: {EMBEDDING_DIMENSIONS}")
                return embedding
            except Exception as e:
                logger.warning(f"gemini_failed: {str(e)}, falling_back: jina")
    
    # Default behavior: Jina → HF → zero vector
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
        logger.warning(f"jina_failed: {str(e)}, falling_back: huggingface")

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
        logger.error(f"huggingface_failed: {str(e)}")

    logger.warning("embedding_fallback_zero_vector")
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
                provider = os.environ.get("EMBEDDING_PROVIDER", "jina").lower()
                logger.info(f"Embedded paddle {paddle_id} with provider {provider} ({total_embedded}/{len(paddle_ids)})")

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
    import argparse
    import json
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Batch embedding service for paddle embeddings"
    )
    parser.add_argument(
        "--reembed",
        action="store_true",
        help="Re-embed paddles flagged with needs_reembed=true",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of paddles to process per batch (default: 50)",
    )
    args = parser.parse_args()

    async def _main():
        if args.reembed:
            result = await re_embed_flagged_paddles()
        else:
            result = await batch_embed_paddles(batch_size=args.batch_size)
        return result

    try:
        result = asyncio.run(_main())
        print(json.dumps(result))
    except Exception as e:
        logger.error(f"CLI failed: {e}", exc_info=True)
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
