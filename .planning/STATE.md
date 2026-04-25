---
gsd_state_version: 1.0
milestone: v2.8.0
milestone_name: E2E Critical Fixes
status: Complete
last_updated: "2026-04-25"
last_activity: 2026-04-25
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 0
  completed_plans: 0
---

# STATE.md — PickleIQ

## Current Position

Milestone: v2.8.0 — E2E Critical Fixes
Status: ✅ Complete
Last activity: 2026-04-25

**All 4 phases executed. All E2E findings addressed. Phase 43 (Quiz→Chat Fix) complete.**

## Milestone Overview

| Phase | Goal | Status |
|-------|------|--------|
| 40 | Critical Frontend Fixes (Clerk + Docker Networking) | ✅ Complete |
| 41 | API & Route Fixes (Slugs + Similar + Auth + Routes) | ✅ Complete |
| 42 | Data Quality & Verification | ✅ Complete |
| 43 | Quiz → Chat Auto-Recommendation Fix | ✅ Complete |

## E2E Finding Resolution

### 🔴 Critical (Site-breaking) — FIXED

| ID | Finding | Fix |
|----|---------|-----|
| E2E-1 | ClerkAuthButtons crashes without ClerkProvider | ✅ Added `ClerkAvailableContext` + `useClerkAvailable()` hook, components return null when Clerk unavailable |
| E2E-2 | Frontend Docker container can't reach backend | ✅ Fixed all 10 server-side API routes to prefer `FASTAPI_INTERNAL_URL` (Docker) with fallback |

### 🟠 High (Feature-breaking) — FIXED

| ID | Finding | Fix |
|----|---------|-----|
| E2E-3 | Similar Paddles endpoint returns 404 | ✅ Returns 200 + empty array, added `min_similarity` param |
| E2E-4 | Paddle detail pages 404 (null model_slug) | ✅ Created `scripts/generate_model_slugs.sql` migration |
| E2E-5 | Admin API endpoints unauthenticated | ✅ Added `require_admin` dependency to all 6 endpoints |
| E2E-6 | Price History route mismatch | ✅ Fixed by Docker networking fix (env var was wrong, not route) |

### 🟡 Medium — FIXED

| ID | Finding | Fix |
|----|---------|-----|
| E2E-7 | React setState-during-render in ClerkAuthButtons | ✅ Fixed by early return pattern |

### 🟢 Low — FIXED

| ID | Finding | Fix |
|----|---------|-----|
| E2E-8 | Blog title says "2025" | ✅ Updated to 2026 |

## Files Changed (29 files)

**Phase 43 — Quiz → Chat Auto-Recommendation Fix (7 files):**
- `frontend/src/app/chat/page.tsx` — Added `buildQuizInitialMessage()` with PT-BR label maps, passes `initialMessage` to ChatWidget
- `frontend/src/components/chat/chat-widget.tsx` — Added `initialMessage` prop, `initialSentRef`, auto-send `useEffect`, `requestAnimationFrame` transport fix, `isSendingInitial` loading state
- `frontend/src/app/api/chat/route.ts` — Replaced `VALID_LEVELS` with `LEVEL_MAP` (competitive→advanced), refactored SSE parser to use `\n\n` buffer
- `backend/app/api/chat.py` — Added `_SKILL_LEVEL_MAP` dict, updated `validate_skill_level` to normalize competitive→advanced
- `backend/app/agents/rag_agent.py` — Two-stage fallback in `search_by_profile`, fixed `_search_mock` iteration
- `backend/app/db.py` — Added `_POOL_TIMEOUT=30.0` to pool and connection calls

**Frontend (13 files — Phases 40-42):**
- `frontend/src/components/clerk-provider.tsx` — Added ClerkAvailableContext + useClerkAvailable hook
- `frontend/src/components/layout/clerk-auth-buttons.tsx` — Early return when Clerk unavailable
- `frontend/src/app/api/chat/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/api/price-alerts/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/api/paddles/[id]/price-history/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/api/admin/queue/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/api/admin/queue/[id]/resolve/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/api/admin/queue/[id]/dismiss/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/api/admin/catalog/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/api/admin/catalog/[id]/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/api/users/migrate/route.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/lib/seo.ts` — FASTAPI_INTERNAL_URL fallback
- `frontend/src/app/blog/pillar-page/page.tsx` — 2025→2026

**Backend (3 files):**
- `backend/app/api/paddles.py` — Similar paddles returns 200 + [], min_similarity param
- `backend/app/api/admin.py` — Added require_admin auth dependency to all endpoints
- `backend/tests/test_admin_endpoints.py` — Updated tests for admin auth, added 401 tests
- `backend/tests/test_paddles_endpoints.py` — Updated similar paddles tests (404→200)

**Scripts (2 files):**
- `scripts/generate_model_slugs.sql` — Migration to generate model_slug for NULL slugs
- `scripts/generate_model_slugs.sh` — Runner script for the migration

## Test Status

| Suite | Status | Details |
|-------|--------|---------|
| Frontend (vitest) | ✅ 170/170 pass | 19 suites, 0 regressions |
| Frontend (next build) | ✅ 0 errors | 23 pages generated |
| Backend (pytest) | ✅ 208/214 pass | 6 pre-existing failures (embedding keys, review_queue mock, price_history mock) |
| E2E (Playwright) | ⏳ Needs Docker retest | All code fixes applied |

## Pre-existing Failures (not introduced by this milestone)

1. `test_get_review_queue_items__filters_correctly` — IndexError in review_queue.py (mock tuple mismatch)
2. `test_get_embedding_raises_when_both_fail` — Embedding API keys unavailable in test env
3. `test_both_providers_fail_raises_error` — Embedding integration test
4. `test_get_paddles__limit_max` — FastAPI Query validation difference
5. `test_price_history_response_shape` — Stale mock attribute `db_fetch_all`
6. `test_price_history_paddle_not_found_returns_empty` — Same stale mock

## Project Reference

See: .planning/PROJECT.md
Requirements: .planning/REQUIREMENTS.md
Source: E2E Playwright analysis (2026-04-25)

---
*State updated: 2026-04-25 — v2.8.0 milestone complete (all 4 phases executed including Phase 43 Quiz→Chat fix)*
