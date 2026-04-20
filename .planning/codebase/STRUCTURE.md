# Codebase Structure

**Analysis Date:** 2026-04-20

## Directory Layout

```
picklepicker/
├── backend/                    # FastAPI application (Python)
├── frontend/                   # Next.js 14 application (TypeScript)
├── pipeline/                  # Scraping & data pipeline (Python)
├── .github/workflows/        # CI/CD pipelines
├── scripts/                  # One-off utilities
├── docs/                     # Project documentation
├── docker-compose.yml         # Local PostgreSQL
├── Makefile                  # Development orchestration
├── CLAUDE.md                 # AI assistant config
├── DESIGN.md                # Design system
└── README.md               # Project overview
```

## Directory Purposes

### `backend/` — FastAPI Application

**Purpose:** REST API and RAG agent for paddle recommendations

**Key Structure:**
```
backend/
├── app/
│   ├── main.py              # FastAPI entrypoint, middleware, exception handlers
│   ├── db.py               # AsyncConnectionPool (psycopg)
│   ├── schemas.py           # Pydantic response models
│   ├── prompts.py           # PT-BR prompt templates
│   ├── cache.py            # Caching layer
│   ├── embeddings.py        # Embedding generation (Jina AI)
│   ├── observability.py    # Health checks, metrics
│   ├── logging_config.py   # structlog configuration
│   ├── langfuse_handler.py # LLM observability
│   │
│   ├── api/               # REST endpoints
│   │   ├── paddles.py      # GET /paddles, /paddles/{id}, /paddles/{id}/similar
│   │   ├── chat.py        # POST /chat (SSE streaming)
│   │   ├── health.py      # GET /health
│   │   ├── price_history.py # GET /price-history/{id}
│   │   ├── embeddings.py # POST /embeddings
│   │   ├── users.py     # POST /users
│   │   ├── price_alerts.py # POST /price-alerts
│   │   ├── affiliate_clicks.py # POST /affiliate-clicks
│   │   └── admin.py     # Admin endpoints (Bearer auth)
│   │
│   ├── agents/             # AI agents
│   │   ├── rag_agent.py  # RAG with pgvector semantic search
│   │   └── eval_gate.py # LLM selection (mock)
│   │
│   ├── middleware/        # HTTP middleware
│   │   └── alerts.py    # Telegram alerting with rate limiting
│   │
│   ├── routers/           # Additional routers
│   │   ├── affiliate.py # Affiliate link generation
│   │   └── webhooks.py # External webhooks
│   │
│   └── services/          # Business logic
│       ├── search.py    # Search service
│       └── embedding.py # Embedding service
│
├── workers/               # Background workers
│   └── price_alert_check.py # Price alert processor
│
├── tests/                # pytest-asyncio tests
│   ├── conftest.py      # Test fixtures (mock DB pool)
│   └── test_*.py      # Test modules
│
└── pyproject.toml        # Python dependencies
```

**Entry Point:** `backend/app/main.py`
- Initializes FastAPI app with lifespan context manager
- Registers all routers
- Adds CORS middleware
- Adds logging middleware
- Registers global exception handler

---

### `frontend/` — Next.js 14 Application

**Purpose:** User-facing web application with quiz and catalog

**Key Structure:**
```
frontend/src/
├── app/                    # Pages (App Router)
│   ├── page.tsx            # Homepage
│   ├── layout.tsx           # Root layout
│   ├── globals.css         # Global styles
│   ├── design-tokens.css   # Design system tokens
│   │
│   ├── quiz/               # Quiz flow
│   │   ├── page.tsx        # Quiz entry
│   │   └── results/        # Quiz results
│   │
│   ├── chat/               # Chat interface
│   │   └── page.tsx        # Chat page (forced dark mode)
│   │
│   ├── paddles/             # Paddle catalog
│   │   ├── page.tsx        # Catalog listing
│   │   └── [brand]/[model-slug]/page.tsx # Paddle detail
│   │
│   ├── compare/            # Comparison tool
│   │   └── page.tsx        # Compare page
│   │
│   ├── catalog/            # Alternative catalog URLs
│   │   └── [slug]/page.tsx
│   │
│   ├── admin/             # Admin dashboard
│   │   ├── layout.tsx      # Admin layout
│   │   ├── page.tsx        # Dashboard
│   │   ├── catalog/page.tsx # Catalog management
│   │   └── queue/page.tsx # Review queue
│   │
│   ├── blog/              # Content pages
│   │   ├── layout.tsx
│   │   └── pillar-page/
│   │
│   ├── gift/              # Gift quiz flow
│   │   ├── page.tsx
│   │   └── results/
│   │
│   └── api/               # API routes (Next.js API)
│       ├── chat/route.ts           # Chat proxy
│       ├── price-alerts/route.ts   # Price alerts
│       ├── track/route.ts         # Affiliate tracking
│       ├── webhooks/revalidate/route.ts # On-demand revalidation
│       └── admin/                 # Admin API proxy
│           ├── queue/route.ts
│           ├── catalog/route.ts
│           └── queue/[id]/resolve/route.ts
│
├── components/
│   ├── layout/            # Layout components
│   │   ├── header.tsx      # Navigation header
│   │   └── footer.tsx     # Site footer
│   │
│   ├── chat/              # Chat components
│   │   ├── chat-widget.tsx      # Main chat widget
│   │   ├── message-bubble.tsx   # Chat bubbles
│   │   ├── typing-indicator.tsx # AI typing animation
│   │   ├── recommendation-rail.tsx # Paddle carousel
│   │   └── sidebar-product-card.tsx # Product in sidebar
│   │
│   ├── quiz/              # Quiz components
│   │   ├── quiz-widget.tsx      # Quiz container
│   │   ├── quiz-step-*.tsx     # Individual quiz steps
│   │   ├── recommendation-card.tsx # Results card
│   │   └── quiz-analyzing.tsx  # Loading state
│   │
│   ├── products/          # Product components
│   │   ├── product-card.tsx    # Catalog card
│   │   ├── product-table.tsx   # Comparison table
│   │   └── inline-paddle-card.tsx # Chat inline card
│   │
│   ├── admin/             # Admin components
│   │   └── admin-panel.tsx
│   │
│   ├── ui/               # Reusable UI components
│   │   ├── button.tsx, input.tsx, select.tsx, dialog.tsx
│   │   ├── card.tsx, badge.tsx, label.tsx
│   │   ├── price-tag.tsx, price-chart.tsx, price-alert-modal.tsx
│   │   ├── safe-image.tsx # Image with error handling
│   │   ├── radar-chart.tsx # Spec comparison chart
│   │   └── quiz-option-card.tsx quiz-progress-bar.tsx
│   │
│   ├── home/              # Homepage components
│   │   ├── landing-client.tsx
│   │   ├── feature-steps.tsx
│   │   └── data-stats-section.tsx
│   │
│   ├── shared/            # Shared components
│   │   └── affiliate-link.tsx
│   │
���   └── theme-provider.tsx, theme-toggle.tsx # Dark/light mode
│
├── lib/                  # Utilities
│   ├── api.ts            # Backend API client
│   ├── admin-api.ts      # Admin API client
│   ├── tracking.ts       # Affiliate tracking
│   ├── affiliate.ts     # Affiliate link utils
│   ├── seo.ts          # SEO metadata
│   ├── clerk.ts        # Clerk auth utilities
│   ├── profile.ts       # User profile management
│   ├── quiz-profile.ts   # Quiz profile state
│   ├── price-history.ts  # Price history chart data
│   └── content.ts       # Static content
│
├── types/               # TypeScript types
│   └── paddle.ts         # Paddle types
│
├── hooks/               # Custom hooks
│   └── use-announcer.ts  # Accessibility announcer
│
├── middleware.ts        # Clerk middleware (route protection)
│
└── tests/              # Vitest tests
    ├── setup.ts       # Test setup
    └── unit/         # Unit tests
```

**Entry Points:**
- Homepage: `frontend/src/app/page.tsx`
- Quiz: `frontend/src/app/quiz/page.tsx`
- Chat: `frontend/src/app/chat/page.tsx`
- Catalog: `frontend/src/app/paddles/page.tsx`

---

### `pipeline/` — Scraping & Data Pipeline

**Purpose:** Data collection, processing, and vectorization

**Key Structure:**
```
pipeline/
├── crawlers/              # Retailer scrapers
│   ├── brazil_store.py   # Brazil Pickleball Store (Firecrawl)
│   ├── dropshot_brasil.py # Drop Shot Brasil (Firecrawl)
│   ├── joola.py        # JOOLA (Shopify JSON API)
│   ├── utils.py        # Shared crawler utilities
│   ├── validation.py   # Data validation
│   └── __init__.py
│
├── db/                   # Database operations
│   ├── connection.py  # AsyncConnectionPool (psycopg)
│   ├── schema.sql      # Full schema definition
│   ├── schema-updates.sql # Schema migrations
│   ├── migrations/    # Data migrations
│   ├── quality_metrics.py # Scraping quality tracking
│   ├── dead_letter_queue.py # Failed extraction storage
│   └── __init__.py
│
├── dedup/                # Deduplication
│   ├── spec_matcher.py # RapidFuzz spec matching
│   ├── normalizer.py  # Product name normalization
│   ├── review_queue.py # Manual review queue
│   └── __init__.py
│
├── embeddings/            # Vector embeddings
│   ├── batch_embedder.py # Batch embedding generation
│   ├── document_generator.py # Context document generation
│   └── __init__.py
│
├── alerts/               # Price alert notifications
│   └── (notification logic)
│
├── utils/                # Shared utilities
│   ├── security.py    # Input sanitization
│   └── __init__.py
│
├── tests/                # pytest tests
│   ├── conftest.py   # Test fixtures
│   ├── fixtures/    # Mock responses
│   │   └── mock_responses/
│   └── test_*.py   # Test modules
│
└── pyproject.toml    # Python dependencies
```

**Scraper Pattern:**
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def crawl_retailer():
    # Fetch HTML via Firecrawl
    # Extract product data
    # Return structured data
```

---

### `docs/` — Project Documentation

**Purpose:** Project knowledge and guides

```
docs/
├── ARCHITECTURE.md    # This file — system architecture
├── DESIGN.md         # Design system v4.0
├── TESTING.md        # Testing patterns
├── DEVELOPMENT.md    # Development guide
├── DEPLOYMENT.md    # Deployment guide
├── CONFIGURATION.md # Environment configuration
���── GETTING-STARTED.md # Quick start
```

---

### `.github/workflows/` — CI/CD Pipelines

**Purpose:** Automated workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy.yml` | Push to main | Deploy backend + frontend |
| `test.yml` | Push to any | Run pytest + vitest |
| `scrape.yml` | Cron (daily) | Run all scrapers |
| `lighthouse.yml` | Cron (weekly) | Performance auditing |
| `price-alerts.yml` | Cron (hourly) | Check and send alerts |
| `nps-survey.yml` | Cron (monthly) | NPS survey workflow |

---

### `scripts/` — Utility Scripts

**Purpose:** One-off maintenance and analysis scripts

```
scripts/
└── catalog_cleanup/
    ├── 1_analyze_catalog.py
    ├── 2_backup_data.py
    ├── 3_cleanup_catalog.py
    ├── 4_maintenance_check.py
    ├── 5_verify_cleanup.py
    ├── 6_rollback_emergency.py
    └── PLAYBOOK_DE_LIMPEZA.md
```

---

## Config Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local PostgreSQL with pgvector |
| `Makefile` | Dev orchestration (setup, dev, test, db-*) |
| `CLAUDE.md` | AI assistant configuration |
| `DESIGN.md` | Design system v4.0 |
| `README.md` | Project overview |
| `railway.toml` | Railway deployment config |

## Where to Add New Code

### New API Endpoint
- **Implementation:** `backend/app/api/<feature>.py`
- **Registration:** Import and include in `backend/app/main.py`

### New Scraper
- **Implementation:** `pipeline/crawlers/<retailer>.py`
- **Config:** Add to `retailers` table in `pipeline/db/schema.sql`

### New Frontend Page
- **Implementation:** `frontend/src/app/<route>/page.tsx`
- **Components:** `frontend/src/components/<category>/`

### New Component
- **UI Components:** `frontend/src/components/ui/<component>.tsx`
- **Business Logic:** `frontend/src/components/<category>/`

### Database Changes
- **Schema:** `pipeline/db/schema.sql`
- **Migrations:** `pipeline/db/schema-updates.sql`

### Tests
- **Backend:** `backend/tests/test_<feature>.py`
- **Frontend:** `frontend/src/tests/unit/<feature>.test.tsx`

---

## Special Directories

| Directory | Purpose | Generated | Committed |
|-----------|---------|-----------|-----------|
| `backend/venv/` | Python venv for backend | Yes | No |
| `pipeline/.venv/` | Python venv for pipeline | Yes | No |
| `frontend/node_modules/` | npm dependencies | Yes | No |
| `.pytest_cache/` | pytest cache | Yes | No |
| `__pycache__/` | Python bytecode | Yes | No |

---

*Structure analysis: 2026-04-20*