# PickleIQ — Project Knowledge Base

 A Pickleball paddle intelligence platform for the Brazilian market. Scrapes prices/specs from BR retailers, runs a RAG AI agent for personalized recommendations, and monetizes via affiliate links.

 
**Generated:** 2026-04-19
**Version:** 2.3.0
**Stack:** Python 3.12 + FastAPI (backend) | Next.js 14 App Router (frontend) | PostgreSQL + pgvector (DB) | Groq (LLM) | Jina AI (embeddings)

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
│   ├── crawlers/       # Brazil Store, Dropshot Brasil, JOOLA (Shopify JSON API)
│   ├── db/            # Schema, connection pool, migrations, dead letter queue, quality metrics
│   ├── dedup/          # Spec matching (RapidFuzz), normalization
│   ├── embeddings/     # Jina AI embeddings for pgvector
│   ├── alerts/         # Price alert notifications
│   ├── utils/          # Shared utilities (KNOWN_BRANDS, validation)
│   ├── tests/          # pytest-asyncio, mock responses, fixtures
│   └── pyproject.toml
├── .github/workflows/  # CI/CD: deploy, test, scrape, lighthouse, price-alerts, NPS survey
├── scripts/          # Utility scripts (SQL seeds, image extraction, NPS surveys)
├── docker-compose.yml # Local Postgres (pgvector image)
├── Makefile            # Dev orchestration (setup, db-up, dev, test, prod-local)
├── CLAUDE.md           # AI assistant config — READ THIS
├── DESIGN.md          # Design system v2.0 — follow strictly
├── .planning/          # GSD project planning (source of truth for architecture, conventions, concerns)
│   └── codebase/      # Structured codebase docs (ARCHITECTURE, STACK, TESTING, etc.)
├── VERSION             # Current version
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new API endpoint | `backend/app/api/` + `backend/app/routers/` | Follow FastAPI router pattern |
| Modify chat/RAG logic | `backend/app/agents/rag_agent.py` | Uses pgvector semantic search |
| Change DB schema | `pipeline/db/schema.sql` | SQL-based, no ORM |
| Add new scraper | `pipeline/crawlers/` | Use tenacity retry + Firecrawl. Shopify stores use native JSON API (see joola.py pattern) |
| Fix dedup/duplicate detection | `pipeline/dedup/` | tier2_match + fuzzy_match with RapidFuzz |
| Fix UI component | `frontend/src/components/` | Read DESIGN.md first |
| Change page/route | `frontend/src/app/` | App Router convention |
| Debug deploy | `.github/workflows/deploy.yml` | Railway (backend) + Vercel (frontend) |
| Run tests locally | `make test` | pytest + vitest |

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

Dedup Pipeline: tier2_match (title_hash) → fuzzy_match (RapidFuzz ≥ 0.85) → review_queue (log only)
```

## CONVENTIONS

- **Database**: Raw psycopg (no ORM). Pool via `psycopg_pool.AsyncConnectionPool`. SQL migrations in `pipeline/db/schema.sql`.
- **Python packaging**: Two separate `pyproject.toml` files (backend + pipeline). No requirements.txt.
 Install with `pip install -e .`
- **Async tests**: pytest-asyncio with `asyncio_mode = "auto"`. Mock DB pool via autouse conftest fixture.
 `DATABASE_URL` env var required.
 Coverage threshold: 80%.
- **Frontend testing**: Vitest with jsdom. Setup in `frontend/src/tests/setup.ts`.
- **Scrapers**: Firecrawl structured extraction as primary (Shopify stores use native JSON API). Markdown parsing as fallback.
- **Dedup**: All crawlers run tier2_match (title hash) + fuzzy_match (RapidFuzz ≥ 0.85) before paddle INSERT. Conservative: duplicates logged to review_queue, not blocked.
- **Retry logic**: All crawlers use tenacity with `@retry` decorator. Exponential backoff, 3 attempts max.
  Brazil Store/Dropshot use Firecrawl. JOOLA uses httpx with Shopify JSON API.
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
- **Eval gate is mock** — `eval_gate.py` returns hardcoded scores arrays. Not testing real LLMs.
- **No LangChain** — Despite being a "RAG" agent, there's no LangChain usage. Direct API calls to Claude/OpenAI. This is intentional (simpler stack).
- **vercel.json security headers** — Root `vercel.json` has extensive security headers. `frontend/vercel.json` has a minimal subset. Duplicate purpose.

## COMPLETED FIXES (MVP + v1.4 Launch + v2.1 Redesign + v2.3.0 Pipeline Overhaul)

- ✅ **Phase 21-24** — Pipeline overhaul: JOOLA scraper (Shopify JSON API), spec parsing, dedup integration, backend API fixes, CI/CD Telegram notifications, data quality monitoring, catalog reliability (price freshness + retailer count)

## COMPLETED FIXES (MVP + v1.4 Launch + v2.1 Redesign)

- ✅ **RAG Agent** — Integrated with real pgvector (Jina AI embeddings + semantic search, OpenAI removed)
- ✅ **Chat LLM** — Integrated with Groq (Mixtral 8x7B, streaming SSE, real responses)
- ✅ **Backend Tests** — 174 passing (2 pre-existing Jina/HF API 401 failures)
- ✅ **Frontend Tests** — 182/182 passing (v2.1.0)
- ✅ **Dropshot Retailer** — Added to schema (id=3)
- ✅ **Scraper.yml** — Module paths corrected
- ✅ **Embeddings** — Jina AI (v2-base, 768d) + Hugging Face fallback (OpenAI removed)
- ✅ **Schema** — Migrated to vector(768) for Jina/HF compatibility
- ✅ **RAG Tests** — Embedding generation, vector search, price filtering validated
- ✅ **Phase 14** — Launch readiness: SafeImage component, model_slug filter, chat proxy edge cases, regression tests
- ✅ **Phase 16-19** — v2.1.0 Premium Sports Analytics redesign (DESIGN.md v5.0, Home, Chat, Catalog)
- ✅ **Phase 20** — Similar Paddles Endpoint (GET /paddles/{id}/similar)

## PENDING WORK

- 📋 **Phase 25** — Price Alerts (enhancement)
- 📋 **Phase 26** — Affiliate Click Tracking (enhancement)
- 📋 **Phase 27** — Quiz Profile Persistence (optional, cross-device)

## COMMANDS

```bash
# Setup
make setup                    # Install all deps (backend + frontend)
make setup-backend            # Install backend deps only
make setup-frontend           # Install frontend deps only
make env-check                # Validate environment (Docker, DB URL, API keys)

# Development
make dev                      # Start DB + backend + frontend (parallel, hot-reload)
make dev-backend              # Backend only (uvicorn --reload :8000)
make dev-frontend             # Frontend only (npm run dev :3000)

# Testing
make test                     # All tests (backend + frontend)
make test-backend             # pytest (backend)
make test-frontend            # vitest (frontend)
make test-e2e                 # E2E scraper tests (requires DB)
make test-backend-cov         # pytest with coverage report

# Database
make db-up                    # Start PostgreSQL (health check, max 30s wait)
make db-down                  # Stop PostgreSQL
make db-logs                  # Tail PostgreSQL logs
make db-shell                 # Open psql shell
make db-clean                 # Remove all data (destructive!)

# Control
make stop                     # Stop all services (DB + backend + frontend)
make clean                    # Remove venvs, node_modules, DB data

# Help
make help                     # List all commands
make help-full                # Grouped command reference

## NOTES

- `pipeline/` is the real scraping/data pipeline. `backend/` has its own `pipeline/` reference in some worktrees — may be stale.
- Docker Compose only provides Postgres. Backend + frontend run outside containers locally.
 Deploy target: Railway (backend) + Vercel (frontend) + Supabase (DB in production).
- Two separate Python virtual environments: `backend/venv/` and `pipeline/.venv/`. Dependencies are NOT shared.
 Each has its own `pyproject.toml`.
- `scripts/` contains one-off utilities: SQL seeds, image extraction, NPS surveys, production validation (Playwright). These are NOT production code.
 
- `DESIGN.md` is the source of truth for all visual decisions. Read it BEFORE touching any UI code.
 AI slop checklist at DESIGN.md appendix — verify before shipping.
