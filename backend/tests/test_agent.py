"""Tests for RAG Agent."""

import pytest

from backend.app.agents.rag_agent import (
    RAGAgent,
    UserProfile,
    RecommendationResult,
)


@pytest.fixture
def rag_agent():
    """Create a RAG Agent instance."""
    return RAGAgent(model_name="mixtral-8x7b-32768")


@pytest.fixture
def beginner_profile():
    """Create a beginner user profile."""
    return UserProfile(
        skill_level="beginner",
        budget_max_brl=500.0,
        style="control",
        in_stock_only=True,
    )


@pytest.mark.asyncio
async def test_search_paddles_cosine_similarity(rag_agent, beginner_profile):
    """Test that pgvector search respects cosine similarity threshold (0.65)."""
    results = await rag_agent.search_by_profile(beginner_profile)

    # All results should have similarity >= 0.65
    for result in results:
        assert result.similarity_score is not None
        assert result.similarity_score >= 0.65


@pytest.mark.asyncio
async def test_filter_by_skill_level(rag_agent):
    """Test filtering by user skill level (applicable_levels)."""
    beginner_profile = UserProfile(
        skill_level="beginner",
        budget_max_brl=500.0,
        in_stock_only=True,
    )

    results = await rag_agent.search_by_profile(beginner_profile)
    # Should return recommendations suitable for beginner
    assert len(results) > 0


@pytest.mark.asyncio
async def test_filter_by_budget_excludes_expensive(rag_agent):
    """Test that filtering by budget_brl excludes expensive paddles."""
    tight_budget_profile = UserProfile(
        skill_level="beginner",
        budget_max_brl=400.0,  # Should exclude paddles > 400
        in_stock_only=True,
    )

    results = await rag_agent.search_by_profile(tight_budget_profile)

    # All results should be <= budget
    for result in results:
        assert result.price_min_brl <= 400.0


@pytest.mark.asyncio
async def test_filter_by_in_stock(rag_agent):
    """Test that in_stock constraint is enforced."""
    profile = UserProfile(
        skill_level="beginner",
        budget_max_brl=1000.0,
        in_stock_only=True,
    )

    results = await rag_agent.search_by_profile(profile)

    # All results should be in stock (mock paddle 5 is out of stock and should be excluded)
    paddle_ids = [r.paddle_id for r in results]
    assert 5 not in paddle_ids  # Out of stock paddle should not appear


@pytest.mark.asyncio
async def test_build_affiliate_urls_server_side(rag_agent, beginner_profile):
    """Test that affiliate URLs are built server-side and included."""
    results = await rag_agent.search_by_profile(beginner_profile)

    # All results should have affiliate URLs
    for result in results:
        assert result.affiliate_url is not None
        assert result.affiliate_url.startswith("https://")
        assert "session=" in result.affiliate_url or "affiliate" in result.affiliate_url


@pytest.mark.asyncio
async def test_apply_reranking_top_3(rag_agent, beginner_profile):
    """Test that reranking returns top-3 recommendations."""
    results = await rag_agent.search_by_profile(beginner_profile, limit=3)

    # Should return at most 3 results
    assert len(results) <= 3
    # Results should be sorted by similarity (descending)
    for i in range(len(results) - 1):
        assert results[i].similarity_score >= results[i + 1].similarity_score


def test_recommendation_result__schema_valid():
    """Test RecommendationResult Pydantic schema validates correctly."""
    result = RecommendationResult(
        paddle_id=1,
        name="Control Pro",
        brand="Selkirk",
        reasoning="Good for beginners",
        price_min_brl=450.0,
        affiliate_url="https://affiliate.selkirk.com/control-pro?session=abc123",
        similarity_score=0.85,
    )

    assert result.paddle_id == 1
    assert result.name == "Control Pro"
    assert result.price_min_brl == 450.0
    assert result.affiliate_url is not None


@pytest.mark.asyncio
async def test_degraded_mode__returns_by_price(rag_agent):
    """Test degraded mode fallback returns top-3 by price proximity."""
    budget = 500.0
    results = await rag_agent.get_top_by_price(budget_max_brl=budget, limit=3)

    # Should return results sorted by price proximity to budget
    assert len(results) <= 3
    for result in results:
        assert result.price_min_brl <= budget
        assert result.affiliate_url is not None
        # In degraded mode, similarity_score should be None
        assert result.similarity_score is None


@pytest.mark.asyncio
async def test_degraded_mode__respects_budget(rag_agent):
    """Test degraded mode respects budget constraint."""
    budget = 350.0
    results = await rag_agent.get_top_by_price(budget_max_brl=budget)

    for result in results:
        assert result.price_min_brl <= budget
