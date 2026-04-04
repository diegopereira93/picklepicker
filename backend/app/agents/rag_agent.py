"""RAG Agent for paddle recommendations.

Implements semantic search via pgvector with profile-based filtering (skill level, budget, in-stock).
Includes degraded mode fallback for LLM timeout scenarios.
"""

import logging
import os
from typing import Optional

from pydantic import BaseModel

from app.db import get_connection
from app.services.embedding import EmbeddingManager

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSIONS = 768


class RecommendationResult(BaseModel):
    paddle_id: int
    name: str
    brand: str
    reasoning: str
    price_min_brl: float
    affiliate_url: str
    similarity_score: Optional[float] = None


class UserProfile(BaseModel):
    skill_level: str
    budget_max_brl: float
    style: Optional[str] = None
    in_stock_only: bool = True


async def generate_query_embedding(query_text: str) -> list[float]:
    """Generate embedding using EmbeddingManager with free providers.

    Uses Gemini → Jina AI → Hugging Face → zero vector fallback chain.
    """
    manager = EmbeddingManager()
    return await manager.get_embedding(query_text)


class RAGAgent:
    """RAG Agent for paddle recommendations via pgvector search."""

    def __init__(self):
        self._embedding_manager = EmbeddingManager()
        self._use_real_db = bool(os.environ.get("DATABASE_URL"))

    async def _get_similar_paddle_ids(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        threshold: float = 0.2,
    ) -> list[int]:
        try:
            async with get_connection() as conn:
                query = """
                SELECT pe.paddle_id, (pe.embedding <-> %s::vector) AS distance
                FROM paddle_embeddings pe
                INNER JOIN latest_prices lp ON pe.paddle_id = lp.paddle_id
                WHERE (pe.embedding <-> %s::vector) <= (1 - %s)
                ORDER BY distance
                LIMIT %s
                """
                result = await conn.execute(query, (query_embedding, query_embedding, threshold, top_k))
                rows = await result.fetchall()
                paddle_ids = [row[0] for row in rows] if rows else []
                logger.info(f"Found {len(paddle_ids)} similar paddles")
                return paddle_ids
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    async def _get_paddle_details(
        self,
        paddle_ids: list[int],
        budget_max: float,
        in_stock_only: bool = True,
    ) -> list[dict]:
        if not paddle_ids:
            return []

        try:
            async with get_connection() as conn:
                query = """
                SELECT
                    p.id,
                    p.name,
                    p.brand,
                    lp.price_brl,
                    lp.affiliate_url,
                    lp.in_stock
                FROM paddles p
                JOIN latest_prices lp ON p.id = lp.paddle_id
                WHERE p.id = ANY(%s)
                  AND lp.price_brl <= %s
                  AND (%s = FALSE OR lp.in_stock = TRUE)
                ORDER BY lp.price_brl DESC
                """
                result = await conn.execute(query, (paddle_ids, budget_max, in_stock_only))
                rows = await result.fetchall()

                paddles = []
                for row in rows:
                    paddles.append({
                        "id": row[0],
                        "name": row[1],
                        "brand": row[2],
                        "price": float(row[3]),
                        "affiliate_url": row[4],
                        "in_stock": row[5],
                    })
                return paddles
        except Exception as e:
            logger.error(f"Failed to fetch paddle details: {e}")
            return []

    async def search_by_profile(
        self,
        profile: UserProfile,
        user_message: str = "",
        limit: int = 3,
    ) -> list[RecommendationResult]:
        if not self._use_real_db:
            logger.warning("DATABASE_URL not set, using mock data")
            return await self._search_mock(profile, limit)

        try:
            query_text = f"{user_message} {profile.skill_level} player budget {profile.budget_max_brl} BRL"
            query_embedding = await self._embedding_manager.get_embedding(query_text)

            similar_ids = await self._get_similar_paddle_ids(
                query_embedding,
                top_k=limit * 2,
            )

            paddles = await self._get_paddle_details(
                similar_ids,
                profile.budget_max_brl,
                profile.in_stock_only,
            )

            recommendations = []
            for paddle in paddles[:limit]:
                recommendation = RecommendationResult(
                    paddle_id=paddle["id"],
                    name=paddle["name"],
                    brand=paddle["brand"],
                    reasoning=f"Recommended for {profile.skill_level} players with excellent value at R${paddle['price']:.0f}.",
                    price_min_brl=paddle["price"],
                    affiliate_url=paddle["affiliate_url"],
                    similarity_score=None,
                )
                recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return await self._search_mock(profile, limit)

    async def _search_mock(
        self,
        profile: UserProfile,
        limit: int = 3,
    ) -> list[RecommendationResult]:
        mock_paddles = [
            {"id": 1, "name": "Control Pro", "brand": "Selkirk", "price": 450.0, "in_stock": True, "similarity": 0.85, "affiliate_url": "https://example.com/control-pro"},
            {"id": 2, "name": "Power Plus", "brand": "Selkirk", "price": 650.0, "in_stock": True, "similarity": 0.78, "affiliate_url": "https://example.com/power-plus"},
            {"id": 3, "name": "Pro Tour", "brand": "Selkirk", "price": 950.0, "in_stock": True, "similarity": 0.72, "affiliate_url": "https://example.com/pro-tour"},
        ]

        recommendations = []
        for paddle in mock_paddles[:limit]:
            if profile.in_stock_only and not paddle["in_stock"]:
                continue
            if paddle["price"] > profile.budget_max_brl:
                continue

            recommendation = RecommendationResult(
                paddle_id=paddle["id"],
                name=paddle["name"],
                brand=paddle["brand"],
                reasoning=f"Recommended for {profile.skill_level} players.",
                price_min_brl=paddle["price"],
                affiliate_url=paddle["affiliate_url"],
                similarity_score=paddle["similarity"],
            )
            recommendations.append(recommendation)

        return recommendations

    async def get_top_by_price(
        self,
        budget_max_brl: float,
        limit: int = 3,
        in_stock_only: bool = True,
    ) -> list[RecommendationResult]:
        try:
            async with get_connection() as conn:
                query = """
                SELECT
                    p.id,
                    p.name,
                    p.brand,
                    lp.price_brl,
                    lp.affiliate_url
                FROM paddles p
                JOIN latest_prices lp ON p.id = lp.paddle_id
                WHERE lp.price_brl <= %s
                  AND (%s = FALSE OR lp.in_stock = TRUE)
                ORDER BY lp.price_brl DESC
                LIMIT %s
                """
                result = await conn.execute(query, (budget_max_brl, in_stock_only, limit))
                rows = await result.fetchall()

                recommendations = []
                for row in rows:
                    recommendations.append(
                        RecommendationResult(
                            paddle_id=row[0],
                            name=row[1],
                            brand=row[2],
                            reasoning=f"Top option by price (R${float(row[3]):.0f})",
                            price_min_brl=float(row[3]),
                            affiliate_url=row[4],
                            similarity_score=None,
                        )
                    )
                return recommendations
        except Exception as e:
            logger.error(f"Price-based search failed: {e}")
            return await self._get_top_by_price_mock(budget_max_brl, limit, in_stock_only)

    async def _get_top_by_price_mock(
        self,
        budget_max_brl: float,
        limit: int = 3,
        in_stock_only: bool = True,
    ) -> list[RecommendationResult]:
        mock_paddles = [
            {"id": 1, "name": "Budget", "brand": "Generic", "price": 300.0, "in_stock": True},
            {"id": 2, "name": "Mid", "brand": "Selkirk", "price": 650.0, "in_stock": True},
            {"id": 3, "name": "Premium", "brand": "Selkirk", "price": 950.0, "in_stock": True},
        ]

        candidates = []
        for paddle in mock_paddles:
            if in_stock_only and not paddle["in_stock"]:
                continue
            if paddle["price"] > budget_max_brl:
                continue
            candidates.append(
                RecommendationResult(
                    paddle_id=paddle["id"],
                    name=paddle["name"],
                    brand=paddle["brand"],
                    reasoning=f"Top option by price (R${paddle['price']:.0f})",
                    price_min_brl=paddle["price"],
                    affiliate_url="https://example.com",
                    similarity_score=None,
                )
            )

        candidates.sort(key=lambda r: budget_max_brl - r.price_min_brl, reverse=True)
        return candidates[:limit]
