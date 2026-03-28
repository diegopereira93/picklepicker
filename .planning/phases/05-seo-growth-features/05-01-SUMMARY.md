---
phase: 05-seo-growth-features
plan: 01
subsystem: auth
tags: [clerk, nextjs, resend, email, authentication, session-migration]

requires:
  - phase: 04-frontend-ui
    provides: "Next.js app router layout, lib/profile.ts localStorage helpers, API route patterns"

provides:
  - "Clerk v5 middleware with clerkMiddleware() protecting all routes globally"
  - "ClerkProvider wrapping root layout for auth context throughout app"
  - "getUserId() and requireUserId() server helpers in lib/clerk.ts"
  - "POST /api/price-alerts — auth-protected endpoint returning 401 anon / 201 auth"
  - "sendPriceAlert() in lib/resend.ts with RFC 8058 List-Unsubscribe headers"
  - "POST /api/users/migrate — reconciles anon UUID to Clerk user_id"
  - "migrateProfileOnLogin() client helper clears anon localStorage, sets pickleiq:user_id"

affects:
  - 05-02-seo-pages
  - 05-03-price-alert-ui
  - 05-04-affiliate-tracking

tech-stack:
  added:
    - "@clerk/nextjs (Clerk v5 — installed with --legacy-peer-deps)"
    - "resend (transactional email SDK)"
  patterns:
    - "requireUserId() throws Unauthorized — caller gets 401 via try/catch or direct check"
    - "Route Handlers call auth() from @clerk/nextjs/server for userId"
    - "Resend client instantiated lazily (inside function) for testability with vi.mock"
    - "vi.hoisted() + plain function constructor for mocking class-based SDK in vitest"

key-files:
  created:
    - "frontend/src/middleware.ts — clerkMiddleware() with Next.js 15 compatible matcher"
    - "frontend/src/lib/clerk.ts — getUserId() and requireUserId() helpers"
    - "frontend/src/lib/resend.ts — sendPriceAlert() with RFC 8058 unsubscribe headers"
    - "frontend/src/app/api/price-alerts/route.ts — POST protected endpoint"
    - "frontend/src/app/api/users/migrate/route.ts — anon-to-auth migration endpoint"
    - "frontend/src/tests/unit/clerk-middleware.test.ts — 5 tests"
    - "frontend/src/tests/unit/price-alerts.test.ts — 6 tests"
    - "frontend/src/tests/unit/session-upgrade.test.ts — 6 tests"
  modified:
    - "frontend/src/app/layout.tsx — wrapped with ClerkProvider"
    - "frontend/src/lib/profile.ts — added migrateProfileOnLogin()"
    - "frontend/package.json — added @clerk/nextjs, resend"

key-decisions:
  - "Clerk installed with --legacy-peer-deps due to peer dependency conflict with existing packages"
  - "Resend client instantiated lazily (inside getResendClient()) not at module level — required for vitest mocking"
  - "vi.hoisted() + plain function constructor used to mock Resend class before module instantiation"
  - "migrateProfileOnLogin() added to existing lib/profile.ts rather than a new file — keeps localStorage logic co-located"
  - ".env.local gitignored — Clerk keys stored there, RESEND_API_KEY left empty pending domain verification"

patterns-established:
  - "Auth check pattern: const { userId } = await auth(); if (!userId) return 401"
  - "Backend proxy pattern: Route Handler authenticates via Clerk, then forwards with user_id to FastAPI"
  - "TDD with vi.hoisted(): declare mock refs before vi.mock() factory for class-based SDKs"

requirements-completed: [R5.2]

duration: 25min
completed: 2026-03-28
---

# Phase 05 Plan 01: Clerk Auth & Email Integration Summary

**Clerk v5 middleware + ClerkProvider wired into Next.js app router, price-alert endpoint auth-gated (401/201), Resend email with RFC 8058 unsubscribe headers, and anon-to-auth localStorage migration**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-03-28T01:18:00Z
- **Completed:** 2026-03-28T01:23:00Z
- **Tasks:** 3/3
- **Files modified:** 10

## Accomplishments

- Clerk v5 middleware and ClerkProvider installed — anonymous users access app freely, authenticated users have userId available in all Route Handlers
- POST /api/price-alerts protected endpoint: 401 for anon, 201 for auth, forwards user_id to FastAPI backend
- sendPriceAlert() email function with RFC 8058 List-Unsubscribe + List-Unsubscribe-Post headers and PT-BR template
- POST /api/users/migrate + migrateProfileOnLogin() enable seamless anon-to-auth profile handoff with no data loss

## Task Commits

1. **Task 1: Clerk middleware and root layout** - `e610ccc` (feat)
2. **Task 2: Protected price-alert endpoint + Resend email** - `dc76b06` (feat)
3. **Task 3: Anon-to-auth migration endpoint** - `d0ca1b7` (feat)

## Files Created/Modified

- `frontend/src/middleware.ts` — clerkMiddleware() with matcher for all routes + API
- `frontend/src/lib/clerk.ts` — getUserId() returns null for anon, requireUserId() throws Unauthorized
- `frontend/src/lib/resend.ts` — sendPriceAlert() with RFC 8058 headers, PT-BR email template
- `frontend/src/app/api/price-alerts/route.ts` — POST protected, proxies to FastAPI /price-alerts
- `frontend/src/app/api/users/migrate/route.ts` — POST migration, proxies to FastAPI /users/migrate
- `frontend/src/app/layout.tsx` — ClerkProvider added as outermost wrapper
- `frontend/src/lib/profile.ts` — migrateProfileOnLogin() appended
- `frontend/src/tests/unit/clerk-middleware.test.ts` — 5 tests (auth context, matcher config)
- `frontend/src/tests/unit/price-alerts.test.ts` — 6 tests (401/201/500, RFC 8058 headers)
- `frontend/src/tests/unit/session-upgrade.test.ts` — 6 tests (401/200/500, localStorage ops)

## Decisions Made

- Clerk installed with `--legacy-peer-deps` due to peer dependency conflict with existing packages (no breaking changes observed)
- Resend client made lazy (factory function) to enable vitest mocking — module-level `new Resend()` cannot be mocked after import
- `vi.hoisted()` + plain function constructor pattern established for class-based SDK mocks in vitest
- RESEND_API_KEY left empty in .env.local — domain verification at alerts@pickleiq.com required before email sends work in production

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed vitest mock hoisting for Resend constructor**
- **Found during:** Task 2 (price-alerts tests)
- **Issue:** `vi.fn().mockImplementation()` inside `vi.mock()` factory failed because `vi.fn` not available at hoist time; `new Resend()` at module level ran before mock took effect
- **Fix:** Made Resend client lazy via `getResendClient()` factory function; used `vi.hoisted()` + plain function constructor in test
- **Files modified:** `frontend/src/lib/resend.ts`, `frontend/src/tests/unit/price-alerts.test.ts`
- **Verification:** 6/6 price-alerts tests pass
- **Committed in:** `dc76b06`

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug in test mock strategy)
**Impact on plan:** Fix improved testability of resend.ts with no behavior change to production code.

## Known Stubs

- `RESEND_API_KEY` is empty in `.env.local` — `sendPriceAlert()` will fail at runtime until Resend domain (alerts@pickleiq.com) is verified and key added. The function itself is fully implemented; this is an environment configuration gap.

## Issues Encountered

- npm peer dependency conflict when installing `@clerk/nextjs` — resolved with `--legacy-peer-deps` (no breakage)
- `vi.fn().mockImplementation()` not valid inside `vi.mock()` factory — standard vitest limitation; resolved with `vi.hoisted()` pattern

## Next Phase Readiness

- Auth context available globally via ClerkProvider — price alert UI (Plan 05-03) can use `useUser()` hook directly
- Protected endpoints ready — no backend changes needed for auth flow (backend receives user_id from Route Handler)
- RESEND_API_KEY must be added to .env.local before email sending works end-to-end
- Backend FastAPI endpoints `/price-alerts` and `/users/migrate` assumed to exist from Phase 2 — verify before integration testing

---
*Phase: 05-seo-growth-features*
*Completed: 2026-03-28*
