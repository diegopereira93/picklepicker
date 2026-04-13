# PickleIQ

## What This Is

Pickleball paddle intelligence platform for the Brazilian market. Scrapes prices/specs from BR retailers, runs a RAG AI agent for personalized recommendations, and monetizes via affiliate links. Now includes comprehensive test coverage (backend, frontend, pipeline, E2E) and full project documentation.

## Core Value

Users can confidently choose the right pickleball paddle through AI-powered recommendations backed by real-time pricing and technical specs — in Portuguese.

## Requirements

### Validated

- ✓ Price scraping from 3 BR retailers (Brazil Store, Drop Shot, Mercado Livre) — v1.0
- ✓ RAG agent with pgvector semantic search — v1.0
- ✓ Streaming chat with Groq LLM — v1.0
- ✓ Paddle catalog with prices, specs, skill levels — v1.0
- ✓ Hybrid Modern Sports Tech design system — v1.3
- ✓ 101 backend tests + 152 frontend tests passing — v1.1
- ✓ E2E scraper validation with 94% coverage — v1.1
- ✓ FIX-01: All paddle images render correctly (no broken/placeholder errors) — v1.4
- ✓ FIX-02: Paddle detail pages resolve by brand+model_slug (no 404s) — v1.4
- ✓ FIX-03: Chat endpoint accepts all valid frontend payloads (no 422s) — v1.4
- ✓ FIX-04: Zero console errors on core user flows (catalog, detail, chat) — v1.4
- ✓ FIX-05: Existing tests pass + new regression tests for fixed bugs — v1.4
- ✓ Frontend redesign v2.1.0 Premium Sports Analytics — dark-only design, 6 pages, 15 components — v2.1
- ✓ Similar paddles endpoint (GET /paddles/{id}/similar via pgvector) — v2.2
- ✓ Price alerts CRUD (POST /api/v1/price-alerts with 409 duplicate detection) — v2.2
- ✓ Affiliate click tracking (DB persistence replacing console.log) — v2.2
- ✓ Quiz profile persistence (already existed in users.py) — v2.2
- ✓ Pipeline test suite restored (146+ tests passing, mock updates for scrape-based crawlers) — v2.2
- ✓ Frontend test suite stabilized (179/179 Vitest tests passing) — v2.2
- ✓ Playwright E2E test suite (23 tests across 5 spec files) — v2.2
- ✓ Backend deprecation fixes (datetime.utcnow → datetime.now(timezone.utc)) — v2.2
- ✓ Project documentation (7 docs, 2,108 lines: README, ARCHITECTURE, GETTING-STARTED, DEVELOPMENT, TESTING, CONFIGURATION, DEPLOYMENT) — v2.2

### Active

- [ ] T1: Provision Supabase/Railway production infrastructure
- [ ] T2: Eval gate as monthly CI job (currently mock scores)
- [ ] T3: Legal assessment of scraping BR retailer data
- [ ] T5: Load test /chat endpoint (P95 < 3s target)
- [ ] T6: Zero-paddle alert in crawler GitHub Actions
- [ ] Embedding provider reliability (local fallback for Jina/HuggingFace outages)

### Out of Scope

- Performance optimization (addressed in v1.2)
- Data pipeline quality improvements (addressed in v1.1)
- TODOS T1-T7 from eng review (deferred, not launch-blocking)

## Context

**Current state (v2.2.0):** All backend endpoints implemented (similar paddles, price alerts, affiliate tracking, quiz persistence). Full test coverage: 198 backend, 179 frontend, 23 E2E Playwright, 146+ pipeline tests. Project documentation complete (7 docs, 2,108 lines). Launch readiness score improved from 5.0/10 to target range.

**Tech stack:** Python 3.12 + FastAPI | Next.js 14 App Router | PostgreSQL + pgvector | Groq (LLM) | Jina AI (embeddings)

**Known issues:**
- 2 pre-existing backend chat test failures (Jina/HF/Groq API keys not set in test env)
- 2 pre-existing pipeline embedding placeholder tests (require real DB)
- `vercel.json` security headers duplicated in root and `frontend/` — should reconcile

## Constraints

- **Tech stack:** Python 3.12 + FastAPI (backend) | Next.js 14 App Router (frontend) | PostgreSQL + pgvector
- **No ORM:** Raw psycopg with parameterized queries — must validate column names against `pipeline/db/schema.sql`
- **Tests:** pytest-asyncio (backend) + Vitest (frontend) + Playwright (E2E) — must not introduce regressions
- **Locale:** PT-BR for all user-facing text
- **Design system:** Follow DESIGN.md v5.0 (Premium Sports Analytics, dark-only)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Raw SQL (no ORM) | Simpler stack, full control | ⚠️ Column name mismatches cause silent bugs |
| Groq over Claude | Cost optimization | ✓ Working for chat |
| Jina AI over OpenAI | Free embeddings | ✓ Working for RAG |
| placehold.co for seed data | Quick prototyping | ⚠️ Causes image errors in production |
| Similar paddles via pgvector | Already have `_get_similar_paddle_ids()` in RAG Agent | ✓ Shipped in v2.2 |
| Price alerts table | New DB table, simple CRUD | ✓ Shipped in v2.2 |
| Affiliate tracking via POST | Replace console.log with DB insert | ✓ Shipped in v2.2 |
| Fix mocks (not crawlers) | Crawlers migrated to scrape(), tests still mocked extract() | ✓ 38 pipeline failures resolved |
| Playwright for E2E | Standard framework, good Next.js support | ✓ 23 E2E tests passing |
| Manual docs over gsd-doc-writer | Agents timed out on large codebase | ✓ 7 docs written (3 by agents, 4 manually) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-13 after v2.2.0 milestone completion*
