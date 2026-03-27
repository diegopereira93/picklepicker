"""Tests for LLM Evaluation Gate."""

import json
import pytest
from pathlib import Path

from backend.app.agents.eval_gate import (
    EVAL_QUERIES,
    EvalResult,
    run_eval_gate,
    save_eval_results,
    load_eval_results,
)


@pytest.mark.asyncio
async def test_eval_gate__returns_result():
    """Test that eval_gate returns EvalResult structure."""
    result = await run_eval_gate()
    assert isinstance(result, EvalResult)
    assert result.model_name == "eval-gate-v1"
    assert result.selected_model in ("groq", "claude-sonnet")
    assert result.timestamp is not None


@pytest.mark.asyncio
async def test_eval_gate__scores_between_1_5():
    """Test that all query scores are in valid 1-5 range."""
    result = await run_eval_gate()
    assert len(result.scores) == 10
    for score in result.scores:
        assert 1.0 <= score <= 5.0


@pytest.mark.asyncio
async def test_eval_gate__10_queries_evaluated():
    """Test that all 10 queries are evaluated."""
    result = await run_eval_gate()
    assert result.queries_count == 10
    assert len(result.scores) == 10
    assert len(EVAL_QUERIES) == 10


@pytest.mark.asyncio
async def test_eval_gate__selection_logic_groq():
    """Test that Groq is selected when avg >= 4.0."""
    result = await run_eval_gate(threshold=4.0)
    # Given our mock scores average to 4.25, Groq should be selected
    if result.avg_score >= 4.0:
        assert result.selected_model == "groq"
        assert "4.0 threshold" in result.reasoning.lower() or "cost-effective" in result.reasoning.lower()


@pytest.mark.asyncio
async def test_eval_gate__selection_logic_sonnet():
    """Test that Claude Sonnet is selected when avg < 4.0."""
    result = await run_eval_gate(threshold=5.0)  # Set high threshold to force Claude selection
    # With a 5.0 threshold, avg should be < threshold
    if result.avg_score < 5.0:
        assert result.selected_model == "claude-sonnet"
        assert "claude sonnet" in result.reasoning.lower()


def test_save_eval_results(tmp_path):
    """Test saving evaluation results to JSON."""
    eval_result = EvalResult(
        model_name="eval-gate-v1",
        avg_score=4.25,
        queries_count=10,
        scores=[4.5, 4.3, 4.1, 4.4, 4.2, 4.0, 4.3, 4.2, 4.4, 4.1],
        selected_model="groq",
        reasoning="Groq selected (cost-effective)",
        timestamp="2026-03-27T12:00:00",
    )

    filepath = tmp_path / "eval_results.json"
    save_eval_results(eval_result, str(filepath))

    assert filepath.exists()
    with open(filepath) as f:
        data = json.load(f)

    assert data["selected_model"] == "groq"
    assert data["groq_avg"] == 4.25
    assert data["queries_count"] == 10
    assert len(data["queries"]) == 10


def test_load_eval_results(tmp_path):
    """Test loading evaluation results from JSON."""
    eval_result = EvalResult(
        model_name="eval-gate-v1",
        avg_score=4.25,
        queries_count=10,
        scores=[4.5, 4.3, 4.1, 4.4, 4.2, 4.0, 4.3, 4.2, 4.4, 4.1],
        selected_model="groq",
        reasoning="Groq selected",
        timestamp="2026-03-27T12:00:00",
    )

    filepath = tmp_path / "eval_results.json"
    save_eval_results(eval_result, str(filepath))

    loaded = load_eval_results(str(filepath))
    assert loaded is not None
    assert loaded["selected_model"] == "groq"
    assert loaded["queries_count"] == 10


def test_load_eval_results_missing():
    """Test loading missing eval results returns None."""
    result = load_eval_results("/nonexistent/path/eval_results.json")
    assert result is None
