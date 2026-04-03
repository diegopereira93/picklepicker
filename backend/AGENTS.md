# Backend — AGENTS.md

FastAPI backend with RAG agent, SSE chat, and raw SQL via psycopg. PT-BR locale.

## Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI entry, lifespan, global error handler, logging middleware
│   ├── api/
│   │   ├── paddles.py    # Paddle CRUD + price endpoints (raw SQL)
│   │   ├── chat.py       # SSE streaming chat (mock LLM, degraded fallback)
│   │   ├── health.py     # Health check
│   │   ├── price_history.py  # Price history + P20 percentile
│   │   └── admin.py      # Admin endpoints (Bearer token)
│   ├── agents/
│   │   ├── rag_agent.py  # RAG agent (MOCK data, pgvector search)
│   │   └── eval_gate.py  # Model eval gate (MOCK scores)
│   ├── middleware/alerts.py   # Telegram alerting (60s rate limit)
│   ├── routers/          # affiliate.py, webhooks.py
│   ├── db.py             # AsyncConnectionPool (psycopg_pool)
│   ├── schemas.py        # Pydantic: PaddleResponse, SpecsResponse, PriceSnapshot
│   ├── prompts.py        # SYSTEM_PROMPT (PT-BR), translate_metrics()
│   ├── embeddings.py     # pgvector similarity search
│   └── logging_config.py # structlog
├── workers/              # price_alert_check.py
├── tests/                # 16 files, autouse mock_db_pool
├── Dockerfile            # Python 3.12-slim, uvicorn
└── pyproject.toml        # fastapi==0.135.2, psycopg, structlog
```

## Where to Look

| Task | File |
|------|------|
| Add/modify endpoint | `app/api/*.py` or `app/routers/*.py` |
| Change RAG logic | `app/agents/rag_agent.py` |
| Change prompt/response | `app/prompts.py`, `app/schemas.py` |
| DB connection config | `app/db.py` (pool min=2, max=10) |
| Error alerting | `app/middleware/alerts.py` (Telegram) |
| Logging setup | `app/logging_config.py` (structlog) |
| Tests | `tests/` — conftest.py has autouse mock_db_pool |

## Conventions

- **No ORM** — raw psycopg with parameterized SQL. Column names from `pipeline/db/schema.sql`.
- **Portuguese** — prompts, comments, and metric translations in PT-BR.
- **Async everywhere** — `asyncio_mode = "auto"` in pytest. All endpoints async.
- **Mock RAG** — `rag_agent.py` returns hardcoded paddles. `eval_gate.py` returns hardcoded scores.
- **chat.py** — reasoning is hardcoded string. Timeout check uses `asyncio.sleep(0.1)`. Not real LLM calls.
- **Telegram alerts** — rate limited to 1 per error type per 60s. `asyncio.create_task` fire-and-forget.

## Anti-Patterns

- Do NOT introduce SQLAlchemy/ORM — project uses raw SQL intentionally.
- Do NOT add real LLM calls without updating mock tests first.
- Do NOT bypass `get_connection()` — always use the pool context manager.
- Do NOT hardcode column names — reference `pipeline/db/schema.sql` for exact names.
