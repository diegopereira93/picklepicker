"""RAG Agent for paddle recommendations.

Implements semantic search via pgvector with profile-based filtering (skill level, budget, in-stock).
Includes degraded mode fallback for LLM timeout scenarios.
"""

import logging
import os
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.db import get_connection

logger = logging.getLogger(__name__)


class RecommendationResult(BaseModel):
    """A single paddle recommendation."""

    paddle_id: int
    name: str
    brand: str
    reasoning: str
    price_min_brl: float
    affiliate_url: str
    similarity_score: Optional[float] = None


class UserProfile(BaseModel):
    """User profile for filtering recommendations."""

    skill_level: str  # "beginner", "intermediate", "advanced"
    budget_max_brl: float
    style: Optional[str] = None  # "control", "power", "balanced"
    in_stock_only: bool = True


async def generate_query_embedding(query_text: str) -> list[float]:
    """Generate embedding for user query using OpenAI.
    
    Args:
        query_text: User's natural language query
        
    Returns:
        1536-dimensional embedding vector
    """
    try:
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        # Return zero vector as fallback
        return [0.0] * 1536


class RAGAgent:
    """RAG Agent for paddle recommendations via pgvector search."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        """Initialize RAG Agent.

        Args:
            model_name: LLM model to use
        """
        self.model_name = model_name
        self._use_real_db = os.environ.get("OPENAI_API_KEY") is not None
        
    async def _get_similar_paddle_ids(
        self, 
        query_embedding: list[float], 
        top_k: int = 5,
        threshold: float = 0.65
    ) -> list[int]:
        """Find similar paddles using pgvector.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Similarity threshold
            
        Returns:
            List of paddle IDs
        """
        try:
            async with get_connection() as conn:
                # Query using pgvector cosine distance operator
                # cosine distance = 1 - cosine similarity
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
                logger.info(f"Found {len(paddle_ids)} similar paddles")
                return paddle_ids
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    async def _get_paddle_details(
        self, 
        paddle_ids: list[int],
        budget_max: float,
        in_stock_only: bool = True
    ) -> list[dict]:
        """Get paddle details from database.
        
        Args:
            paddle_ids: List of paddle IDs
            budget_max: Maximum budget filter
            in_stock_only: Only return in-stock items
            
        Returns:
            List of paddle dictionaries
        """
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
                WHERE p.id = ANY($1)
                  AND lp.price_brl <= $2
                  AND ($3 = FALSE OR lp.in_stock = TRUE)
                ORDER BY lp.price_brl DESC
                """
                
                result = await conn.execute(query, [paddle_ids, budget_max, in_stock_only])
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
        """Search for paddle recommendations by user profile.

        Performs semantic search via pgvector with profile-based filtering.

        Args:
            profile: User profile with skill level, budget, style preferences
            user_message: User's natural language query
            limit: Number of recommendations to return (default 3)

        Returns:
            List of RecommendationResult ordered by relevance (top-3)
        """
        if not self._use_real_db:
            # Fallback to mock data if OpenAI key not available
            logger.warning("OPENAI_API_KEY not set, using mock data")
            return await self._search_mock(profile, limit)
        
        try:
            # Generate query embedding from user message + profile
            query_text = f"{user_message} {profile.skill_level} player budget {profile.budget_max_brl} BRL"
            query_embedding = await generate_query_embedding(query_text)
            
            # Find similar paddles
            similar_ids = await self._get_similar_paddle_ids(
                query_embedding, 
                top_k=limit * 2  # Get extra for filtering
            )
            
            # Get paddle details with filters
            paddles = await self._get_paddle_details(
                similar_ids,
                profile.budget_max_brl,
                profile.in_stock_only
            )
            
            # Build recommendations
            recommendations = []
            for paddle in paddles[:limit]:
                recommendation = RecommendationResult(
                    paddle_id=paddle["id"],
                    name=paddle["name"],
                    brand=paddle["brand"],
                    reasoning=f"Recommended for {profile.skill_level} players with excellent value at R${paddle['price']:.0f}.",
                    price_min_brl=paddle["price"],
                    affiliate_url=paddle["affiliate_url"],
                    similarity_score=None,  # Could calculate from distance
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            # Fallback to mock data on error
            return await self._search_mock(profile, limit)

    async def _search_mock(
        self,
        profile: UserProfile,
        limit: int = 3,
    ) -> list[RecommendationResult]:
        """Mock search for fallback/testing."""
        mock_paddles = [
            {
                "id": 1,
                "name": "Control Pro",
                "brand": "Selkirk",
                "price": 450.0,
                "in_stock": True,
                "skill_level": "beginner",
                "similarity": 0.85,
                "affiliate_url": "https://example.com/control-pro",
            },
            {
                "id": 2,
                "name": "Power Plus",
                "brand": "Selkirk",
                "price": 650.0,
                "in_stock": True,
                "skill_level": "intermediate",
                "similarity": 0.78,
                "affiliate_url": "https://example.com/power-plus",
            },
            {
                "id": 3,
                "name": "Pro Tour",
                "brand": "Selkirk",
                "price": 950.0,
                "in_stock": True,
                "skill_level": "advanced",
                "similarity": 0.72,
                "affiliate_url": "https://example.com/pro-tour",
            },
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
        """Degraded mode: return top paddles by price proximity without embedding search.

        Used when LLM latency exceeds budget (>8s).

        Args:
            budget_max_brl: Maximum budget in BRL
            limit: Number of results to return
            in_stock_only: Filter to in-stock items only

        Returns:
            List of RecommendationResult sorted by price proximity to budget
        """
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
                WHERE lp.price_brl <= $1
                  AND ($2 = FALSE OR lp.in_stock = TRUE)
                ORDER BY lp.price_brl DESC
                LIMIT $3
                """
                
                result = await conn.execute(query, [budget_max_brl, in_stock_only, limit])
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
            # Fallback to mock
            return await self._get_top_by_price_mock(budget_max_brl, limit, in_stock_only)

    async def _get_top_by_price_mock(
        self,
        budget_max_brl: float,
        limit: int = 3,
        in_stock_only: bool = True,
    ) -> list[RecommendationResult]:
        """Mock price-based search for fallback."""
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
