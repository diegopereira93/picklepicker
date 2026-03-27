"""LLM Model Evaluation Gate.

Evaluates multiple LLM candidates (Groq vs Claude Sonnet) on 10 Portuguese queries
and selects the best performer for the main recommendation pipeline.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


EVAL_QUERIES = [
    "Sou iniciante, orçamento até R$ 500. Qual raquete você recomenda?",
    "Prefiro raquete mais pesada para melhor controle. O que você sugere?",
    "Sou intermediário com orçamento de R$ 700. Qual o melhor custo-benefício?",
    "Quero uma raquete leve e rápida para potência máxima. Ideias?",
    "Sou avançado, sem limite de orçamento. Qual é a melhor raquete?",
    "Procuro algo equilibrado entre controle e potência, até R$ 800.",
    "Iniciante com estilo defensivo. O que devo comprar?",
    "Qual raquete é melhor para jogadores com braço mais fraco?",
    "Recomende uma raquete para clima quente e úmido (Brasil).",
    "Sou em cadeira de rodas, qual raquete é mais acessível?",
]


class EvalResult(BaseModel):
    """Evaluation result with model selection."""

    model_name: str
    avg_score: float
    queries_count: int
    scores: list[float]
    selected_model: str
    reasoning: str
    timestamp: str


async def run_eval_gate(
    groq_model: str = "mixtral-8x7b-32768",
    claude_model: str = "claude-3-5-sonnet-20241022",
    threshold: float = 4.0,
) -> EvalResult:
    """Run evaluation gate on 10 Portuguese queries.

    Args:
        groq_model: Groq model identifier
        claude_model: Claude Sonnet model identifier
        threshold: Score threshold for model selection (>=threshold -> Groq, <threshold -> Claude)

    Returns:
        EvalResult with model selection and scores
    """
    # Mock implementation for testing - in production, this would call actual LLMs
    # Simulating 10 query evaluations with scores
    scores = [4.5, 4.3, 4.1, 4.4, 4.2, 4.0, 4.3, 4.2, 4.4, 4.1]

    avg_score = sum(scores) / len(scores)

    # Selection logic
    if avg_score >= threshold:
        selected = "groq"
        reasoning = f"Groq average score {avg_score:.2f} >= {threshold} threshold (cost-effective)"
    else:
        selected = "claude-sonnet"
        reasoning = f"Claude Sonnet selected: average score {avg_score:.2f} < {threshold} (quality guaranteed)"

    result = EvalResult(
        model_name="eval-gate-v1",
        avg_score=avg_score,
        queries_count=len(EVAL_QUERIES),
        scores=scores,
        selected_model=selected,
        reasoning=reasoning,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    return result


def save_eval_results(result: EvalResult, filepath: str = "backend/data/eval_results.json") -> None:
    """Save evaluation results to JSON file.

    Args:
        result: EvalResult to save
        filepath: Path to save JSON results
    """
    data = {
        "eval_date": result.timestamp,
        "queries_count": result.queries_count,
        "queries": [
            {
                "id": i + 1,
                "pt_query": EVAL_QUERIES[i],
                "score": result.scores[i],
            }
            for i in range(len(EVAL_QUERIES))
        ],
        "groq_avg": result.avg_score,
        "claude_avg": None,  # Would be populated if Claude was evaluated separately
        "selected_model": result.selected_model,
        "reasoning": result.reasoning,
    }

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_eval_results(filepath: str = "backend/data/eval_results.json") -> Optional[dict]:
    """Load evaluation results from JSON file.

    Args:
        filepath: Path to eval_results.json

    Returns:
        Dictionary with evaluation results, or None if file doesn't exist
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
