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

### Active

- [ ] T1: Provision Supabase/Railway production infrastructure
- [ ] T2: Eval gate as monthly CI job (currently mock scores)
- [ ] T3: Legal assessment of scraping BR retailer data
- [ ] T5: Load test /chat endpoint (P95 < 3s target)
- [ ] T6: Zero-paddle alert in crawler GitHub Actions
- [ ] Embedding provider reliability (local fallback for Jina/HuggingFace outages)

### Out of Scope

- New features or UX changes — this milestone is bug-fix only
- Performance optimization (addressed in v1.2)
- Data pipeline quality improvements (addressed in v1.1)
- TODOS T1-T7 from eng review (deferred, not launch-blocking)

## Context

**Current state (v1.4.0):** All launch-blocking bugs fixed. Core flows work without errors. 174 backend + 161 frontend tests passing. v1.5 (Production Readiness) planned but not started. v1.6 (UI Redesign) next — based on 9-variant design review completed 2026-04-05.

## Constraints

- **Tech stack:** Python 3.12 + FastAPI (backend) | Next.js 14 App Router (frontend) | PostgreSQL + pgvector
- **No ORM:** Raw psycopg with parameterized queries — must validate column names against `pipeline/db/schema.sql`
- **Tests:** pytest-asyncio (backend) + Vitest (frontend) — must not introduce regressions
- **Locale:** PT-BR for all user-facing text
- **Design system:** Follow DESIGN.md (updating to v3.0 this milestone based on design review)
- **Design review:** Follow approved.json decisions from `all-screens-20260405/`

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Raw SQL (no ORM) | Simpler stack, full control | ⚠️ Column name mismatches cause silent bugs |
| Groq over Claude | Cost optimization | ✓ Working for chat |
| Jina AI over OpenAI | Free embeddings | ✓ Working for RAG |
| placehold.co for seed data | Quick prototyping | ⚠️ Causes image errors in production |
| Quiz-Forward (Home-C) | Max funnel conversion (score 9/10) | 🆕 v1.6 — approved variant |
| Sidebar Companion (Chat-B) | Buy button always visible (score 9/10) | 🆕 v1.6 — approved variant |
| Comparison Table (Catalog-A) | Data density for analytical persona (score 9/10) | 🆕 v1.6 — approved variant |
| DESIGN.md v3.0 updates | 6 changes from design review (Metis analysis) | 🆕 v1.6 — planned |

## Current Milestone: v1.6 UI Redesign

**Goal:** Implement the winning design variants from the 9-variant design review (2026-04-05). Redesign Home, Catalog, and Chat screens to maximize funnel conversion and cross-screen coherence.

**Design review source:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/`

**Winning combination:**
- **Home**: C (Quiz-Forward) + data stats from A — quiz above-the-fold captures intent immediately
- **Catalog**: A (Comparison Table) + product images from B + grid toggle — sortable data for analytical persona
- **Chat**: B (Sidebar Companion) + card responses from C — split-panel keeps buy button accessible

**Target features:**
- DESIGN.md v3.0 with 6 proposed updates (chat UI, semantic colors, border radius, widgets, max-width, full-dark sections)
- Home page redesigned with quiz widget above-the-fold
- Chat redesigned with sidebar companion layout + card-structured AI responses
- Catalog redesigned with comparison table + visual grid toggle
- Cross-screen coherence (consistent visual language, shared components)

**Implementation order:** DESIGN.md → Home-C → Chat-B → Catalog-A → Polish

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
*Last updated: 2026-04-05 — v1.6.0 UI Redesign milestone created from design review*
