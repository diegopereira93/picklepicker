# Development Guide — PickleIQ

Development workflows, conventions, and patterns for contributors.

## Project Structure

```
picklepicker/
├── backend/              # FastAPI + RAG agent (Python 3.12)
│   ├── app/
│   │   ├── main.py       # FastAPI entrypoint, router registration
│   │   ├── api/          # REST endpoints (paddles, chat, health, price_alerts, affiliate_clicks, admin)
│   │   ├── agents/       # RAG agent (pgvector semantic search) + eval gate
│   │   ├── services/     # Embedding service (Jina AI + HF fallback)
│   │   ├── middleware/    # Telegram alerting with rate limiting
│   │   ├── routers/      # Affiliate tracking, webhooks
│   │   ├── db.py         # Async connection pool (psycopg)
│   │   ├── schemas.py    # Pydantic response models
│   │   ├── prompts.py    # Prompt templates (PT-BR)
│   │   └── cache.py      # Caching layer
│   ├── workers/          # Background workers (price alerts)
│   ├── tests/            # pytest-asyncio
│   └── pyproject.toml
├── frontend/             # Next.js 14 App Router (TypeScript)
│   ├── src/
│   │   ├── app/          # Pages: /, /paddles, /chat, /admin, /blog, /quiz, /catalog, /compare
│   │   ├── components/   # UI components (layout, chat, quiz, products, admin, ui)
│   │   ├── lib/          # API client, auth (Clerk), tracking, SEO
│   │   ├── types/        # TypeScript types (paddle.ts)
│   │   ├── hooks/        # Custom hooks
│   │   └── tests/        # Vitest unit tests
│   ├── e2e/              # Playwright E2E tests
│   └── package.json
├── pipeline/             # Scraping + data pipeline (Python 3.12)
│   ├── crawlers/         # Brazil Store, Dropshot Brasil, Mercado Livre
│   ├── db/               # Schema, connection pool, dead letter queue
│   ├── dedup/            # Spec matching (RapidFuzz), normalization
│   ├── embeddings/       # Jina AI embeddings for pgvector
│   ├── alerts/           # Price alert notifications
│   └── pyproject.toml
├── .github/workflows/    # CI/CD
├── scripts/              # Utility scripts (SQL seeds, image extraction)
├── docker-compose.yml    # Local PostgreSQL (pgvector)
└── Makefile              # Dev orchestration
```

## Development Commands

### Daily Workflow

```bash
make dev          # Start everything (DB + backend + frontend)
make stop         # Stop all services
make test         # Run all tests before committing
```

### Backend

```bash
make dev-backend           # Start backend only (uvicorn --reload :8000)
make test-backend          # Run pytest
make test-backend-cov      # pytest with HTML coverage report
```

Backend runs at http://localhost:8000 with auto-reload. API docs at http://localhost:8000/docs.

### Frontend

```bash
make dev-frontend          # Start frontend only (npm run dev :3000)
make test-frontend         # Run vitest
cd frontend && npx playwright test   # Run E2E tests
```

Frontend runs at http://localhost:3000 with hot reload.

### Database

```bash
make db-up       # Start PostgreSQL (health check, 30s wait)
make db-down     # Stop PostgreSQL
make db-shell    # Open psql shell
make db-logs     # Tail PostgreSQL logs
make db-clean    # Remove all data (destructive!)
```

Schema is in `pipeline/db/schema.sql`. No ORM — raw SQL with parameterized queries via psycopg.

## Conventions

### Backend (Python)

- **No ORM** — Raw psycopg with `AsyncConnectionPool`. Parameterized queries only.
- **Async everywhere** — All DB operations and API handlers are `async def`.
- **Logging** — structlog configured in `app/logging_config.py`. Use `structlog.get_logger()`.
- **Error alerting** — Telegram via `middleware/alerts.py`. Rate limited to 1 per type per 60s.
- **Pydantic models** — Request/response schemas in `schemas.py`.
- **Tests** — pytest-asyncio with `asyncio_mode = "auto"`. Mock DB pool via autouse conftest fixture.
- **Two separate venvs** — `backend/venv/` and `pipeline/.venv/`. Dependencies NOT shared.

### Frontend (TypeScript/Next.js)

- **App Router** — All pages use Next.js 14 App Router convention.
- **Design system** — Read `DESIGN.md` BEFORE touching any UI. Dark-only, lime (#84CC16) accent.
- **Clerk auth** — `middleware.ts` handles auth redirects.
- **Tailwind CSS** — Utility-first. Follow existing component patterns.
- **Tests** — Vitest with jsdom for unit tests, Playwright for E2E.
- **Locale** — PT-BR for all user-facing text.

### Pipeline (Python)

- **Crawlers** — Use Firecrawl API via `app.scrape()` (not `app.extract()`). Markdown parsing.
- **Retry** — All crawlers use tenacity with `@retry` decorator. Exponential backoff, 3 attempts.
- **Dedup** — RapidFuzz for spec matching. Threshold: 0.85.
- **Embeddings** — Jina AI v2-base (768d) with Hugging Face fallback.

## Adding a New Backend Endpoint

1. Create the route file in `backend/app/api/` (e.g., `price_alerts.py`)
2. Define Pydantic schemas in `backend/app/schemas.py`
3. Add DB schema to `pipeline/db/schema.sql` if needed
4. Register the router in `backend/app/main.py`
5. Write tests in `backend/tests/`
6. Run `make test-backend` to verify

Pattern:

```python
from fastapi import APIRouter, status
from psycopg.rows import dict_row
from app.schemas import MyCreate, MyResponse
from app.db import get_connection

router = APIRouter(prefix="/my-resource", tags=["my-resource"])

@router.post("", response_model=MyResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: MyCreate):
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO my_table (field) VALUES (%s) RETURNING id, field",
                [item.field]
            )
            row = await cur.fetchone()
            return MyResponse(**dict(row))
```

## Adding a New Frontend Page

1. Create directory under `frontend/src/app/` (e.g., `my-page/page.tsx`)
2. Follow App Router convention (default export)
3. Use components from `frontend/src/components/ui/`
4. Follow DESIGN.md for all visual decisions
5. Add API calls via `frontend/src/lib/api.ts`
6. Write unit tests in `frontend/src/tests/`

## Adding a New Scraper

1. Create crawler in `pipeline/crawlers/` (e.g., `my_store.py`)
2. Use tenacity `@retry` decorator with exponential backoff
3. Use Firecrawl API via `app.scrape()` for web extraction
4. Parse markdown output for product data
5. Add retailer to `pipeline/db/schema.sql`
6. Write tests in `pipeline/tests/`
7. Add GitHub Actions workflow in `.github/workflows/`

## Common Workflows

### Run a single scraper locally

```bash
cd pipeline
.venv/bin/python -m crawlers.mercado_livre
```

### Seed the database

```bash
make db-shell < scripts/seed.sql
```

### Check production health

```bash
curl https://pickleiq-api.up.railway.app/health
```

### Generate embeddings

```bash
cd pipeline
.venv/bin/python -m embeddings.generate
```

## Debugging

### Backend not starting

Check `backend/.env` has all required vars. Run `make env-check`.

### Database connection errors

```bash
make db-up      # Ensure DB is running
make db-shell   # Test connection
```

### Embedding failures

Jina AI is primary, Hugging Face is fallback. If both fail, check API keys in `.env`.

### Chat not responding

Requires `GROQ_API_KEY`. Check backend logs for `groq_api_error`.

### Frontend not connecting to backend

Verify backend is on port 8000. Check `frontend/src/lib/api.ts` for the base URL.
