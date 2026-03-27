"""RAG Agent for paddle recommendations.

Implements semantic search via pgvector with profile-based filtering (skill level, budget, in-stock).
Includes degraded mode fallback for LLM timeout scenarios.
"""

from typing import Optional

from pydantic import BaseModel


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


class RAGAgent:
    """RAG Agent for paddle recommendations via pgvector search."""

    def __init__(self, model_name: str = "mixtral-8x7b-32768"):
        """Initialize RAG Agent.

        Args:
            model_name: LLM model to use ("mixtral-8x7b-32768" or "claude-3-5-sonnet-20241022")
        """
        self.model_name = model_name
        # In production, this would hold db_pool and other initialized resources
        self._mock_paddles = self._get_mock_paddles()

    @staticmethod
    def _get_mock_paddles() -> list[dict]:
        """Return mock paddle data for testing."""
        return [
            {
                "id": 1,
                "name": "Control Pro",
                "brand": "Selkirk",
                "price": 450.0,
                "in_stock": True,
                "skill_level": "beginner",
                "similarity": 0.85,
                "affiliate_url": "https://affiliate.selkirk.com/control-pro?session=abc123",
            },
            {
                "id": 2,
                "name": "Power Plus",
                "brand": "Selkirk",
                "price": 650.0,
                "in_stock": True,
                "skill_level": "intermediate",
                "similarity": 0.78,
                "affiliate_url": "https://affiliate.selkirk.com/power-plus?session=abc123",
            },
            {
                "id": 3,
                "name": "Pro Tour",
                "brand": "Selkirk",
                "price": 950.0,
                "in_stock": True,
                "skill_level": "advanced",
                "similarity": 0.72,
                "affiliate_url": "https://affiliate.selkirk.com/pro-tour?session=abc123",
            },
            {
                "id": 4,
                "name": "Budget Friendly",
                "brand": "Generic",
                "price": 300.0,
                "in_stock": True,
                "skill_level": "beginner",
                "similarity": 0.68,
                "affiliate_url": "https://affiliate.generic.com/budget?session=abc123",
            },
            {
                "id": 5,
                "name": "Out of Stock",
                "brand": "Premium",
                "price": 800.0,
                "in_stock": False,
                "skill_level": "advanced",
                "similarity": 0.65,
                "affiliate_url": "https://affiliate.premium.com/out-of-stock?session=abc123",
            },
        ]

    async def search_by_profile(
        self,
        profile: UserProfile,
        limit: int = 3,
    ) -> list[RecommendationResult]:
        """Search for paddle recommendations by user profile.

        Performs semantic search via pgvector with profile-based filtering.

        Args:
            profile: User profile with skill level, budget, style preferences
            limit: Number of recommendations to return (default 3)

        Returns:
            List of RecommendationResult ordered by relevance (top-3)
        """
        recommendations = []

        for paddle in self._mock_paddles:
            # Filter 1: Stock constraint
            if profile.in_stock_only and not paddle["in_stock"]:
                continue

            # Filter 2: Budget constraint
            if paddle["price"] > profile.budget_max_brl:
                continue

            # Filter 3: Similarity threshold (0.65 minimum)
            if paddle["similarity"] < 0.65:
                continue

            recommendation = RecommendationResult(
                paddle_id=paddle["id"],
                name=paddle["name"],
                brand=paddle["brand"],
                reasoning=f"Recommended for {profile.skill_level} players with {paddle['similarity']:.0%} relevance match.",
                price_min_brl=paddle["price"],
                affiliate_url=paddle["affiliate_url"],
                similarity_score=paddle["similarity"],
            )
            recommendations.append(recommendation)

        # Sort by similarity score (descending) and return top-N
        recommendations.sort(key=lambda r: r.similarity_score or 0, reverse=True)
        return recommendations[:limit]

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
        candidates = []

        for paddle in self._mock_paddles:
            if in_stock_only and not paddle["in_stock"]:
                continue

            if paddle["price"] > budget_max_brl:
                continue

            # Score by proximity to budget (closer to budget = higher score)
            price_proximity = budget_max_brl - paddle["price"]

            candidates.append(
                RecommendationResult(
                    paddle_id=paddle["id"],
                    name=paddle["name"],
                    brand=paddle["brand"],
                    reasoning=f"Top option by price (R${paddle['price']:.0f}, proximity to budget: R${price_proximity:.0f})",
                    price_min_brl=paddle["price"],
                    affiliate_url=paddle["affiliate_url"],
                    similarity_score=None,
                )
            )

        # Sort by price proximity (descending) - closest to budget first
        candidates.sort(key=lambda r: budget_max_brl - r.price_min_brl, reverse=True)
        return candidates[:limit]
