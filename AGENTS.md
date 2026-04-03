# PickleIQ — Project Knowledge Base

 A Pickleball paddle intelligence platform for the Brazilian market. Scrapes prices/specs from BR retailers, runs a RAG AI agent for personalized recommendations, and monetizes via affiliate links.

 
**Generated:** 2026-04-03
**Version:** 1.3.0.1
**Stack:** Python 3.12 + FastAPI (backend) | Next.js 14 App Router (frontend) | PostgreSQL + pgvector (DB)

## Structure

```
picklepicker/
├── backend/          # FastAPI + RAG agent (Python)
│   ├── app/
│   │   ├── main.py       # FastAPI entrypoint
│   │   ├── api/         # REST endpoints (paddles, chat, health, price_history, admin)
│   │   ├── agents/     # RAG agent (semantic search) + eval gate (LLM selection)
│   │   ├── middleware/ # Telegram alerting with rate limiting
│   │   ├── routers/   # affiliate tracking, webhooks
│   │   ├── db.py       # Async connection pool (psycopg)
│   │   ├── schemas.py  # Pydantic response models
│   │   ├── prompts.py  # Prompt templates + metric translation (PT-BR)
│   │   └── cache.py     # Caching layer
│   ├── workers/         # Background workers (price alerts)
│   ├── tests/           # pytest-asyncio, mock DB pool, conftest fixtures
│   └── pyproject.toml
├── frontend/         # Next.js 14 App Router (TypeScript)
│   ├── src/
│   │   ├── app/         # Pages: /, /paddles, /chat, /admin, /blog, /api/
│   │   ├── components/  # UI: layout, chat, quiz, products, admin, ui (12)
│   │   ├── lib/        # API client, auth (Clerk), tracking, SEO, admin API
│   │   ├── types/      # TypeScript types (paddle.ts)
│   │   ├── hooks/      # Custom hooks (use-announcer)
│   │   ├── tests/      # Vitest unit tests
│   │   └── middleware.ts # Clerk middleware
│   └── package.json
├── pipeline/          # Scraping + data pipeline (Python)
│   ├── crawlers/       # Brazil Store, Dropshot Brasil, Mercado Livre
│   ├── db/            # Schema, connection pool, dead letter queue, quality metrics
│   ├── dedup/          # Spec matching (RapidFuzz), normalization
│   ├── embeddings/     # OpenAI embeddings for pgvector
│   ├── alerts/         # Price alert notifications
│   ├── utils/          # Shared utilities
│   ├── tests/          # pytest-asyncio, mock responses, fixtures
│   └── pyproject.toml
├── .github/workflows/  # CI/CD: deploy, test, scrape, lighthouse, price-alerts, NPS survey
├── prisma/            # Database migrations (legacy)
├── scripts/          # Utility scripts (SQL seeds, image extraction, NPS surveys)
├── docker-compose.yml # Local Postgres (pgvector image)
├── Makefile            # Dev orchestration (setup, db-up, dev, test)
├── CLAUDE.md           # AI assistant config — READ THIS
├── DESIGN.md          # Design system v2.0 — follow strictly
├── TODOS.md            # 7 deferred items from eng review
├── VERSION             # Current version
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new API endpoint | `backend/app/api/` + `backend/app/routers/` | Follow FastAPI router pattern |
| Modify chat/RAG logic | `backend/app/agents/rag_agent.py` | Uses pgvector semantic search |
| Change DB schema | `pipeline/db/schema.sql` | SQL-based, no ORM |
| Add new scraper | `pipeline/crawlers/` | Use tenacity retry + Firecrawl |
| Fix UI component | `frontend/src/components/` | Read DESIGN.md first |
| Change page/route | `frontend/src/app/` | App Router convention |
| Debug deploy | `.github/workflows/deploy.yml` | Railway (backend) + Vercel (frontend) |
| Run tests locally | `make test-backend` / `make test-frontend` | pytest + vitest |

## DATA FLOW

```
Scrapers (pipeline/crawlers/)
  → price_snapshots (append-only)
  → latest_prices (materialized view)
  → paddles API (backend/app/api/paddles.py)
  → Frontend (frontend/src/lib/api.ts)

Scrapers → paddle_embeddings (pgvector)
  → RAG Agent (backend/app/agents/rag_agent.py)
  → /chat SSE endpoint (backend/app/api/chat.py)
  → Frontend chat widget
```

## CONVENTIONS

- **Database**: Raw psycopg (no ORM). Pool via `psycopg_pool.AsyncConnectionPool`. SQL migrations in `pipeline/db/schema.sql`.
- **Python packaging**: Two separate `pyproject.toml` files (backend + pipeline). No requirements.txt.
 Install with `pip install -e .`
- **Async tests**: pytest-asyncio with `asyncio_mode = "auto"`. Mock DB pool via autouse conftest fixture.
 `DATABASE_URL` env var required.
 Coverage threshold: 80%.
- **Frontend testing**: Vitest with jsdom. Setup in `frontend/src/tests/setup.ts`.
- **Retry logic**: All crawlers use tenacity with `@retry` decorator. Exponential backoff, 3 attempts max.
 Params vary per crawler (1-10s vs 5-120s).
- **Error alerting**: Telegram via `backend/app/middleware/alerts.py`. Rate limited to 1 alert per type per 60s.
 No spam.
- **Auth**: Clerk for frontend. Admin endpoints use Bearer token via `ADMIN_SECRET` env var.
- **Logging**: structlog for backend. Configured in `app/logging_config.py`.
- **Locale**: PT-BR for frontend. Portuguese comments and prompts in backend.
- **Design system**: Read DESIGN.md before ANY UI change. Hybrid Modern Sports Tech aesthetic. Lime (#84CC16) on dark only. Green (#76b900) for data elements.

## ANTI-PATTERNS (THIS PROJECT)

- **No .editorconfig or .pre-commit-config** — No formatting consistency enforcement. Consider adding.
- **No ORM** — Raw SQL in `paddles.py`. Parameterized queries via string concatenation. Safe but requires careful review.
 Column references are not validated at compile time.
 See `pipeline/db/schema.sql` for exact column names.
 
- **Duplicate pipeline concept** — `backend/pipeline/` appears in some worktree references AND `pipeline/` exists at root. The root-level `pipeline/` is the actual source.
 The `backend/pipeline/` reference may be stale.
- **RAG agent uses mock data** — `rag_agent.py` currently returns hardcoded mock paddles, not real DB data. The comment says "In production, this would hold db_pool" — integration is incomplete.
- **Eval gate is mock** — `eval_gate.py` returns hardcoded scores arrays. Not testing real LLMs.
- **No LangChain** — Despite being a "RAG" agent, there's no LangChain usage. Direct API calls to Claude/OpenAI. This is intentional (simpler stack).
- **chat.py has mock LLM** — Reasoning is hardcoded string, not from actual LLM call. Timeout check uses `asyncio.sleep(0.1)`.
- **Crawlers lack consistent `__main__` guards** — Only `mercado Livre` has `if __name__ == "__main__"`. `Brazil Store` and `Dropshot Brasil` are library-only modules.
 They're invoked via GitHub Actions workflows.
 
- **vercel.json security headers** — Root `vercel.json` has extensive security headers. `frontend/vercel.json` has a minimal subset. Duplicate purpose.

## COMMANDS

```bash
# Development
make setup                    # Install all deps
make db-up                     # Start PostgreSQL
make dev                      # Start DB + backend + frontend
make dev-backend               # Backend only (uvicorn :8000)
make dev-frontend              # Frontend only (npm run dev :3000)

# Testing
make test                      # All tests
make test-backend              # pytest (backend)
make test-frontend             # vitest (frontend)
make test-e2e                # E2E scraper tests (requires DB)
make test-backend-cov          # pytest with coverage report

# Database
make db-up                     # Start PostgreSQL
make db-down                   # Stop PostgreSQL
make db-shell                   # Open psql shell
make db-clean                   # Remove all data (destructive!)

# CI/CD (GitHub Actions)
# .github/workflows/deploy.yml        — Deploy to Railway + Vercel
# .github/workflows/test.yml          — Test + coverage + lint
# .github/workflows/scrape.yml       — Scheduled scraping (cron)
# .github/workflows/scraper.yml      — Individual crawler runs
# .github/workflows/lighthouse.yml   — Frontend performance
# .github/workflows/price-alerts-check.yml — Price alert worker
# .github/workflows/nps-survey.yml   — NPS survey distribution
# .github/workflows/validate-production.yml — Playwright production validation
```

## NOTES

- `pipeline/` is the real scraping/data pipeline. `backend/` has its own `pipeline/` reference in some worktrees — may be stale.
- `prisma/` directory exists but unclear if actively used. Schema is SQL-based via `pipeline/db/schema.sql`.
- Docker Compose only provides Postgres. Backend + frontend run outside containers locally.
 Deploy target: Railway (backend) + Vercel (frontend) + Supabase (DB in production).
- Two separate Python virtual environments: `backend/venv/` and `pipeline/.venv/`. Dependencies are NOT shared.
 Each has its own `pyproject.toml`.
- `scripts/` contains one-off utilities: SQL seeds, image extraction, NPS surveys, production validation (Playwright). These are NOT production code.
 
- `DESIGN.md` is the source of truth for all visual decisions. Read it BEFORE touching any UI code.
 AI slop checklist at DESIGN.md appendix — verify before shipping.
