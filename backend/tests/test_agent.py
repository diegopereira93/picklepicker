"""Tests for RAG Agent."""

import os
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from app.agents.rag_agent import RAGAgent, UserProfile


@pytest.fixture
def rag_agent():
    with patch.dict("os.environ", {}, clear=["DATABASE_URL"]):
        agent = RAGAgent()
        agent._use_real_db = False
        return agent


@pytest.fixture
def beginner_profile():
    return UserProfile(
        skill_level="beginner",
        budget_max_brl=500.0,
        in_stock_only=True,
    )


@pytest.mark.asyncio
async def test_search_paddles_cosine_similarity(rag_agent, beginner_profile):
    results = await rag_agent.search_by_profile(beginner_profile, user_message="raquete leve")
    assert len(results) > 0
    for result in results:
        assert result.paddle_id is not None


        assert result.name is not None


        assert result.brand is not None
        assert result.price_min_brl is not None


@pytest.mark.asyncio
async def test_filter_by_skill_level(rag_agent):
    beginner_profile = UserProfile(
        skill_level="beginner",
        budget_max_brl=500.0,
        in_stock_only=True,
    )
    with patch.object(
        RAGAgent, "_get_similar_paddle_ids",
        new_callable=AsyncMock,
        return_value=[1, 2, 3]
    ), patch.object(
        RAGAgent, "_get_paddle_details",
        new_callable=AsyncMock,
        return_value=[
            {"id": 1, "name": "Control Pro", "brand": "Selkirk", "price": 450.0, "affiliate_url": "https://example.com/cp", "in_stock": True},
            {"id": 2, "name": "Power Plus", "brand": "Selkirk", "price": 650.0, "affiliate_url": "https://example.com/pp", "in_stock": True},
            {"id": 3, "name": "Pro Tour", "brand": "Selkirk", "price": 950.0, "affiliate_url": "https://example.com/pt", "in_stock": True},
        ]
    ):
        results = await rag_agent.search_by_profile(beginner_profile, user_message="raquete leve para iniciante")
        assert len(results) > 0
        for r in results:
            assert r.paddle_id is not None
            assert r.name is not None
            assert r.brand is not None
            assert r.price_min_brl is not None


@pytest.mark.asyncio
async def test_filter_by_budget_excludes_expensive(rag_agent):
    tight_budget_profile = UserProfile(
        skill_level="beginner",
        budget_max_brl=400.0,
        in_stock_only=True,
    )
    results = await rag_agent.search_by_profile(tight_budget_profile, user_message="barate")
    for result in results:
        assert result.price_min_brl <= 400.0


@pytest.mark.asyncio
async def test_filter_by_in_stock(rag_agent):
    profile = UserProfile(
        skill_level="beginner",
        budget_max_brl=1000.0,
        in_stock_only=True,
    )
    results = await rag_agent.search_by_profile(profile, user_message="raquete")
    paddle_ids = [r.paddle_id for r in results]
    assert 5 not in paddle_ids


@pytest.mark.asyncio
async def test_degraded_mode__returns_by_price(rag_agent):
    budget = 500.0
    results = await rag_agent.get_top_by_price(budget_max_brl=budget, limit=3)
    assert len(results) <= 3
    for result in results:
        assert result.price_min_brl <= budget
        assert result.affiliate_url is not None
        assert result.similarity_score is None


@pytest.mark.asyncio
async def test_degraded_mode__respects_budget(rag_agent):
    budget = 350.0
    results = await rag_agent.get_top_by_price(budget_max_brl=budget)
    for result in results:
        assert result.price_min_brl <= budget
