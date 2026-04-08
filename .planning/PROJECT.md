# PickleIQ

## What This Is

Pickleball paddle intelligence platform for the Brazilian market. Scrapes prices/specs from BR retailers, runs a RAG AI agent for personalized recommendations, and monetizes via affiliate links.

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

### Active

- [ ] T1: Provision Supabase/Railway production infrastructure
- [ ] T2: Eval gate as monthly CI job (currently mock scores)
- [ ] T3: Legal assessment of scraping BR retailer data
- [ ] T5: Load test /chat endpoint (P95 < 3s target)
- [ ] T6: Zero-paddle alert in crawler GitHub Actions
- [ ] Embedding provider reliability (local fallback for Jina/HuggingFace outages)

### Out of Scope

- Frontend changes (complete in v2.1.0)
- Performance optimization (addressed in v1.2)
- Data pipeline quality improvements (addressed in v1.1)
- Production deployment (v1.5.0)
- TODOS T1-T7 from eng review (deferred, not launch-blocking)

## Context

**Current state (v2.1.0):** Frontend redesign shipped (PR #18). Dark-only Premium Sports Analytics design system complete. Backend needs 4 new endpoints to support new frontend features: similar paddles, price alerts, affiliate tracking, and quiz profile persistence.

## Constraints

- **Tech stack:** Python 3.12 + FastAPI (backend) | Next.js 14 App Router (frontend) | PostgreSQL + pgvector
- **No ORM:** Raw psycopg with parameterized queries — must validate column names against `pipeline/db/schema.sql`
- **Tests:** pytest-asyncio (backend) + Vitest (frontend) — must not introduce regressions
- **Locale:** PT-BR for all user-facing text
- **Design system:** Follow DESIGN.md v5.0 (Premium Sports Analytics, dark-only)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Raw SQL (no ORM) | Simpler stack, full control | ⚠️ Column name mismatches cause silent bugs |
| Groq over Claude | Cost optimization | ✓ Working for chat |
| Jina AI over OpenAI | Free embeddings | ✓ Working for RAG |
| placehold.co for seed data | Quick prototyping | ⚠️ Causes image errors in production |
| Similar paddles via pgvector | Already have `_get_similar_paddle_ids()` in RAG Agent | ✓ Minimal code needed |
| Price alerts table | New DB table, simple CRUD | 🆕 v1.7 — planned |
| Affiliate tracking via POST | Replace console.log with DB insert | 🆕 v1.7 — planned |

## Current Milestone: v1.7.0 Backend API Updates

**Goal:** Add 4 backend endpoints required by the frontend redesign (v2.1.0). Support similar paddles on product detail, price alerts modal, affiliate click tracking, and quiz profile persistence.

**Target features:**
1. `GET /paddles/{id}/similar` — Product detail shows similar paddles (currently placeholder)
2. `POST /price-alerts` — Price alerts modal posts to backend (currently 404)
3. `POST /api/affiliate-clicks` — Affiliate tracking logs to DB (currently console.log only)
4. `POST/GET /quiz/profile` — Quiz profile persistence across devices (optional)

**Implementation order:** Similar Paddles → Price Alerts → Affiliate Tracking → Quiz Persistence

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
*Last updated: 2026-04-07 — v1.7.0 Backend API Updates milestone created from frontend redesign integration needs*