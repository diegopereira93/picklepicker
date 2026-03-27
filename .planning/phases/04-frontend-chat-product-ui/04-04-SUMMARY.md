---
phase: 04-frontend-chat-product-ui
plan: 04-04
subsystem: frontend/affiliate-tracking
tags: [affiliate, tracking, edge-runtime, utm, ftc-disclosure, tdd]
dependency_graph:
  requires: ["04-01"]
  provides: ["affiliate-tracking", "utm-preservation", "ftc-disclosure"]
  affects: ["product-cards", "comparison-table"]
tech_stack:
  added: ["Edge Runtime route (POST /api/track)"]
  patterns: ["keepalive fetch", "fire-and-forget tracking", "UTM parameter propagation"]
key_files:
  created:
    - frontend/src/lib/tracking.ts
    - frontend/src/app/api/track/route.ts
    - frontend/src/components/shared/affiliate-link.tsx
    - frontend/src/tests/unit/affiliate.test.ts
  modified: []
decisions:
  - "trackAffiliateClick is fire-and-forget (no await) — errors console.warn only, never block navigation"
  - "appendUtmParams skips params already on affiliate URL (affiliate URL wins to avoid duplicate attribution)"
  - "getOrCreateUserId uses localStorage with crypto.randomUUID for anonymous session tracking"
  - "Edge runtime chosen for /api/track — lowest latency, no cold starts, works globally"
  - "FTC disclosure text in Portuguese per Brazilian market requirements"
metrics:
  duration: "~15 minutes"
  completed: "2026-03-27"
  tasks_completed: 1
  tasks_total: 1
  files_created: 4
  files_modified: 0
  tests_added: 9
  tests_passing: 9
---

# Phase 04 Plan 04: Affiliate Tracking System Summary

**One-liner:** Keepalive fetch affiliate tracking with Edge Route Handler structured logging, UTM preservation, and FTC disclosure component.

## What Was Built

Reusable affiliate tracking system with three layers:

1. **`frontend/src/lib/tracking.ts`** — Client-side utility:
   - `trackAffiliateClick`: fire-and-forget `fetch` with `keepalive: true` to `/api/track`. Extracts UTM params from current page URL, attaches anonymous `user_id` from localStorage, sends `paddle_id`, `retailer`, `timestamp`.
   - `appendUtmParams`: reads UTM keys from `window.location.search`, appends to affiliate URL only if not already present.
   - `extractRetailer`: derives retailer name from affiliate URL hostname.
   - `getOrCreateUserId`: persists anonymous UUID in localStorage.

2. **`frontend/src/app/api/track/route.ts`** — Edge Route Handler:
   - `export const runtime = 'edge'`
   - POST accepts `TrackPayload`, validates `paddle_id` and `retailer` (400 if missing).
   - Logs `{ event: 'affiliate_click', ...payload }` as structured JSON to stdout (Vercel Edge logs).
   - Returns 204 No Content.

3. **`frontend/src/components/shared/affiliate-link.tsx`** — UI components:
   - `AffiliateLink`: renders `<a target="_blank" rel="noopener noreferrer">`, calls `trackAffiliateClick` on click, applies `appendUtmParams` to href.
   - `FtcDisclosure`: renders required Portuguese affiliate disclosure text with info icon.

## Test Results

All 9 TDD tests pass:

| # | Test | Result |
|---|------|--------|
| 1 | trackAffiliateClick fires fetch with keepalive:true | PASS |
| 2 | sends paddle_id, retailer, timestamp, utm_params, user_id | PASS |
| 3 | appendUtmParams preserves UTM params from page URL | PASS |
| 4 | appendUtmParams does not duplicate existing UTM params | PASS |
| 5 | POST /api/track returns 204 on valid payload | PASS |
| 6 | POST /api/track returns 400 on missing paddle_id | PASS |
| 7 | AffiliateLink renders target=_blank rel=noopener noreferrer | PASS |
| 8 | AffiliateLink onClick calls trackAffiliateClick | PASS |
| 9 | FtcDisclosure renders disclosure text | PASS |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed unused `afterEach` import in test file**
- **Found during:** Build lint check
- **Issue:** `afterEach` imported but never used caused ESLint `no-unused-vars` error blocking build
- **Fix:** Removed from import statement
- **Files modified:** `frontend/src/tests/unit/affiliate.test.ts`
- **Commit:** 52d4f7a

### Out-of-Scope Pre-existing Issues (logged to deferred-items.md)

- `frontend/src/app/chat/page.tsx` references `@/components/chat/chat-widget` which does not yet exist (04-02 scaffold). Causes `npm run build` to fail. Will be resolved by plan 04-02.

## Known Stubs

None. All tracking logic is fully wired. `getOrCreateUserId` is self-contained in tracking.ts (not dependent on an external profile.ts that didn't exist).

## Self-Check: PASSED

Files exist:
- FOUND: frontend/src/lib/tracking.ts
- FOUND: frontend/src/app/api/track/route.ts
- FOUND: frontend/src/components/shared/affiliate-link.tsx
- FOUND: frontend/src/tests/unit/affiliate.test.ts

Commit exists: 52d4f7a — feat(04-04): implement affiliate tracking system
