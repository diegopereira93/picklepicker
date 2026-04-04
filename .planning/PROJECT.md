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

### Active

- [ ] FIX-01: All paddle images render correctly (no broken/placeholder errors)
- [ ] FIX-02: Paddle detail pages resolve by brand+model_slug (no 404s)
- [ ] FIX-03: Chat endpoint accepts all valid frontend payloads (no 422s)
- [ ] FIX-04: Zero console errors on core user flows (catalog, detail, chat)
- [ ] FIX-05: Existing tests pass + new regression tests for fixed bugs

### Out of Scope

- New features or UX changes — this milestone is bug-fix only
- Performance optimization (addressed in v1.2)
- Data pipeline quality improvements (addressed in v1.1)
- TODOS T1-T7 from eng review (deferred, not launch-blocking)

## Context

**Current state (v1.3.0.2):** CHANGELOG claims 3 bugs were fixed (paddle detail 404, chat 422, broken images), but local testing shows all 3 still reproducible. The fixes were superficial — response shape parsing and skill_level sanitization — without addressing root causes.

**Root causes identified:**
1. **Images:** DB seed (`scripts/populate_paddles.sql`) fills paddles with `placehold.co` URLs. Next.js Image optimizer cannot process placehold.co responses. The "Foto" fallback only triggers when `image_url` is NULL, but paddles have invalid (non-null) URLs.
2. **Paddle detail 404:** Backend `GET /api/v1/paddles` does NOT accept `model_slug` as a query parameter. The frontend sends `?brand=X&model_slug=Y` but the backend ignores `model_slug`, returning all paddles for the brand. `fetchProductData` takes `items[0]` which may not match the requested slug.
3. **Chat 422:** Edge cases in payload validation — `budget_max` of 0 bypasses `?? 600` fallback (0 is falsy but not null), empty/whitespace messages from the chat widget, or profile structure mismatch between quiz output and proxy expectations.

## Constraints

- **Tech stack:** Python 3.12 + FastAPI (backend) | Next.js 14 App Router (frontend) | PostgreSQL + pgvector
- **No ORM:** Raw psycopg with parameterized queries — must validate column names against `pipeline/db/schema.sql`
- **Tests:** pytest-asyncio (backend) + Vitest (frontend) — must not introduce regressions
- **Locale:** PT-BR for all user-facing text
- **Design system:** Follow DESIGN.md strictly

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Raw SQL (no ORM) | Simpler stack, full control | ⚠️ Column name mismatches cause silent bugs |
| Groq over Claude | Cost optimization | ✓ Working for chat |
| Jina AI over OpenAI | Free embeddings | ✓ Working for RAG |
| placehold.co for seed data | Quick prototyping | ⚠️ Causes image errors in production |

## Current Milestone: v1.4 Launch Readiness

**Goal:** Fix all launch-blocking bugs so core user flows (catalog browsing, paddle detail, AI chat) work without errors.

**Target features:**
- Working product images on catalog and detail pages
- Paddle detail pages resolving correctly by brand+model_slug
- Chat endpoint accepting all valid payloads from the quiz flow
- Zero console errors on core flows
- Regression tests preventing these bugs from recurring

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
*Last updated: 2026-04-04 after v1.4 milestone start*
