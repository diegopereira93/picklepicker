from typing import List, Dict, Any
from app.db import get_connection
from app.services.embedding import EmbeddingManager
import structlog

logger = structlog.get_logger()


async def semantic_search(
    query_text: str,
    top_k: int = 10,
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    embedding_manager = EmbeddingManager()
    query_embedding = await embedding_manager.get_embedding(query_text)

    async with get_connection() as conn:
        query = """
            SELECT p.id, p.name, lp.price_brl,
                   1 - (pe.embedding <=> %s::vector) AS similarity
            FROM paddles p
            JOIN paddle_embeddings pe ON p.id = pe.paddle_id
            JOIN latest_prices lp ON p.id = lp.paddle_id
            WHERE pe.embedding IS NOT NULL
            ORDER BY pe.embedding <=> %s::vector
            LIMIT %s
        """

        result = await conn.execute(query, (str(query_embedding), str(query_embedding), top_k))
        rows = await result.fetchall()

        results = []
        for row in rows:
            similarity = float(row[3])
            if similarity >= threshold:
                results.append({
                    "id": row[0],
                    "name": row[1],
                    "price": float(row[2]) if row[2] else None,
                    "similarity": similarity
                })

        logger.info("semantic_search", query=query_text[:50], results=len(results))
        return results
