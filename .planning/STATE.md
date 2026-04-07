# STATE.md — PickleIQ

## Current Position

Milestone: v1.7.0 — Backend API for Frontend Redesign
Phase: 21 — Price Alerts CRUD (in planning)
Status: Planning complete, awaiting `/gsd/plan-phase 20` to begin execution
Last activity: 2026-04-07 — Phase 20 committed, Phase 21 planning complete

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-07)

**Core value:** Users can confidently choose the right pickleball paddle through AI-powered recommendations backed by real-time pricing and technical specs
**Current focus:** v1.7.0 Backend API — endpoint additions for frontend redesign v2.1.0

## Context

Frontend redesign v2.1.0 shipped successfully (PR #18 merged). The new UI features require 4 backend endpoints:

1. **Similar Paddles** (`GET /paddles/{id}/similar`) — Product detail pages need similar paddle recommendations
2. **Price Alerts** (`POST /price-alerts`) — Price alerts modal needs backend persistence
3. **Affiliate Tracking** (`POST /api/affiliate-clicks`) — Analytics requires DB logging instead of console.log
4. **Quiz Profile** (`POST/GET /quiz/profile`) — Cross-device profile persistence (optional)

**Implementation priority:** Similar Paddles → Price Alerts → Affiliate Tracking → Quiz Profile
**Estimated effort:** ~4.5 hours total

## Prerequisites (Complete ✅)

- [x] Frontend redesign v2.1.0 shipped (PR #18 merged)
- [x] 182/182 frontend tests passing
- [x] 174+ backend tests passing (2 pre-existing Jina/HF API 401 failures)
- [x] Build passes (0 errors, 21/21 pages)
- [x] Token audit clean (23 files verified)
- [x] Oracle APPROVED (v1.7 redesign complete)
- [x] Backend analyzed for integration points (4 gaps identified)

## Accumulated Context

### Shipped Milestones

| Milestone | Version | Phases | Status |
|-----------|---------|--------|--------|
| MVP | v1.0.0 | 1–6 | ✅ Complete |
| Scraper & E2E | v1.1.0 | 7–9 | ✅ Complete |
| Core Web Vitals | v1.2.0 | 11 | ✅ Complete |
| Hybrid UI Redesign | v1.3.0 | 13 | ✅ Complete |
| Launch Readiness | v1.4.0 | 14 | ✅ Complete |
| UI Redesign | v1.6.0 | 16–19 | ✅ Complete |
| Frontend Redesign v2.1.0 | v2.1.0 | — | ✅ Complete |
| **Backend API Updates** | **v1.7.0** | **20–23** | **⏳ Planning** |

### Key Files for v1.7.0 Implementation

| File | Purpose | Phase |
|------|---------|-------|
| `backend/app/api/paddles.py` | Add `GET /paddles/{id}/similar` endpoint | 20 |
| `backend/app/agents/rag_agent.py` | Contains `_get_similar_paddle_ids()` — reference for endpoint | 20 |
| `pipeline/db/schema.sql` | Add `price_alerts`, `affiliate_clicks`, `quiz_profiles` tables | 21-23 |
| `backend/app/api/price_alerts.py` | New file for POST endpoint | 21 |
| `backend/app/routers/affiliate.py` | Add POST tracking endpoint | 22 |
| `backend/app/api/quiz.py` | New file for profile endpoints | 23 |
| `backend/app/schemas.py` | Add Pydantic models for all new endpoints | 20-23 |

### Backend Analysis Summary

**Similar Paddles:**
- RAG Agent has `_get_similar_paddle_ids()` method ready to expose
- Need to add endpoint to existing `paddles.py` router
- Return full paddle objects, not just IDs

**Price Alerts:**
- New table required (`price_alerts`)
- Worker `price_alert_check.py` exists but has no data
- Email validation via Pydantic `EmailStr`

**Affiliate Tracking:**
- New table required (`affiliate_clicks`)
- Add POST to existing `affiliate.py` router (GET already exists)
- Optional fields for analytics: session_id, user_agent

**Quiz Profile:**
- New table required (`quiz_profiles`)
- New file `quiz.py` for endpoints
- UUID profile_id for cross-device persistence

### Key Technical Notes

- **No ORM:** Raw psycopg with parameterized queries — validate column names against `pipeline/db/schema.sql`
- **Async:** All DB queries via `psycopg_pool.AsyncConnectionPool`
- **Tests:** pytest-asyncio, 80%+ coverage required
- **Locale:** PT-BR for user-facing error messages
- **Frontend:** Already shipped — 56 files changed in v2.1.0
- **DB migrations:** Run `schema.sql` updates against PostgreSQL

### Active Deferred Items (T1-T7)

From eng review (TODOS.md):
- T1: Provision Supabase/Railway production infrastructure → v1.5.0
- T2: Eval gate as monthly CI job → v1.5.1
- T3: Legal assessment of scraping BR retailer data → v1.5.2
- T5: Load test /chat endpoint (P95 < 3s) → v1.5.1
- T6: Zero-paddle alert in crawler GitHub Actions → v1.5.0
- T7: Embedding provider reliability (local fallback) → v1.5.0 (Phase 15.5-15.6)

---
*State updated: 2026-04-07 — v1.7.0 Backend API Updates milestone ready to start*