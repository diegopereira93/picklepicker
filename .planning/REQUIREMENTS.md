# Requirements: v2.8.0 — E2E Critical Fixes

*Created: 2026-04-25*
*Source: Playwright E2E Analysis — 15 frontend routes + 17 backend API endpoints*

## Overview

Critical fixes discovered during full Playwright E2E analysis of the Docker Compose environment. Two site-breaking issues render the entire frontend non-functional, plus four high-priority feature fixes.

**Goal:** Restore full site functionality in Docker Compose. All 15 frontend routes must render content. All user flows (catalog, quiz, chat, compare) must work end-to-end.

---

## Critical Requirements

### E2E-CR1: Fix ClerkAuthButtons Crash (ALL pages empty)
**Priority:** P0 (Critical)
**Source:** E2E-1

`ClerkWrapper` skips `ClerkProvider` when `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is missing, but `ClerkAuthButtons` calls `useAuth()` outside `ClerkProvider`, throwing `"@clerk/nextjs: useAuth can only be used within the <ClerkProvider /> component"`. Error propagates to `NotFoundErrorBoundary`, rendering all 15 pages with empty body.

**Root cause chain:**
```
No Clerk key → ClerkWrapper renders <>{children}</> without ClerkProvider
  → ClerkAuthButtons calls useAuth() outside provider
  → Error thrown → NotFoundErrorBoundary catches → page body = EMPTY
```

**Acceptance:**
- All 15 frontend routes render content when Clerk keys are absent
- `ClerkAuthButtons` gracefully degrades (no auth buttons shown, no crash)
- No `useAuth()` call outside `ClerkProvider`
- No `pageerror` events on any route
- `document.body.innerText.length > 0` on all pages after hydration

### E2E-CR2: Fix Docker Networking (Chat returns 503)
**Priority:** P0 (Critical)
**Source:** E2E-2

Frontend Docker container uses `FASTAPI_URL=http://localhost:8000` which points to the container's own loopback, not the backend container. Chat proxy returns `{"error":"FastAPI unreachable"}` with 503 status.

**Acceptance:**
- Frontend container can reach backend via Docker service name (`http://backend:8000`)
- Chat proxy returns 200 with SSE stream
- `NEXT_PUBLIC_FASTAPI_URL` still works for client-side API calls
- Both `FASTAPI_URL` (server-side) and `NEXT_PUBLIC_FASTAPI_URL` (client-side) configured correctly

---

## High Requirements

### E2E-H1: Fix Similar Paddles Endpoint (returns 404)
**Priority:** P1 (High)
**Source:** E2E-3

`GET /api/v1/paddles/{id}/similar` returns `{"detail":"No similar paddles found"}` for all paddles. Only 2 of ~60 paddles have `face_material` specs. Vector similarity search finds no matches.

**Acceptance:**
- Similar paddles returns 200 with results for paddles that have embeddings
- Returns empty array (not 404) when no similar paddles found
- At least 50% of paddles have usable embeddings after fix

### E2E-H2: Fix Paddle Detail Pages (model_slug null)
**Priority:** P1 (High)
**Source:** E2E-4

Most paddles have `model_slug: null` in the database. Route `/paddles/[brand]/[model-slug]` fails because no slug exists. `/paddles/3rdshot/3rdshot-oberon-mini` returns 404.

**Acceptance:**
- All paddles have a non-null `model_slug` generated from name
- Paddle detail pages resolve correctly via brand + slug
- Existing URL patterns continue to work

### E2E-H3: Fix Admin API Authentication
**Priority:** P1 (High)
**Source:** E2E-5

Admin endpoints (`/admin/queue/*`, `/admin/paddles/*`) docstrings claim "Protected by Authorization: Bearer {ADMIN_SECRET}" but no `Depends()` auth guard exists.

**Acceptance:**
- Admin endpoints require `Authorization: Bearer {ADMIN_SECRET}` header
- Unauthenticated requests return 401
- Health and public endpoints remain unprotected

### E2E-H4: Fix Price History Route Mismatch
**Priority:** P1 (High)
**Source:** E2E-6

Backend registers price history at `GET /paddles/{id}/price-history` but frontend expects `/api/v1/admin/price-history/{id}`. Price charts won't load data.

**Acceptance:**
- Frontend calls the correct backend route for price history
- Price history charts render with real data on paddle detail pages

---

## Medium Requirements

### E2E-M1: Fix React setState-During-Render Warning
**Priority:** P2 (Medium)
**Source:** E2E-7

`ClerkAuthButtons` triggers `Cannot update a component while rendering a different component` warning. React anti-pattern.

**Acceptance:**
- No setState-during-render warnings in console
- ClerkAuthButtons follows React best practices

---

## Low Requirements

### E2E-L1: Fix Blog Title Year
**Priority:** P3 (Low)
**Source:** E2E-8

Blog pillar page title says "Guia Completo 2025" but current year is 2026.

**Acceptance:**
- Blog title updated to current year

### E2E-L2: Add frontend/.env file
**Priority:** P3 (Low)
**Source:** E2E-9

`frontend/.env` doesn't exist. Relies on root `.env` and Docker Compose env vars.

**Acceptance:**
- `frontend/.env` exists with correct `NEXT_PUBLIC_FASTAPI_URL`
- Or documented that Docker Compose provides all needed env vars

---

## Verification Criteria

### E2E Smoke Test (MUST pass after all fixes)

| Route | Must Show | Must NOT Show |
|-------|-----------|---------------|
| `/` | Hero content, nav, CTA | Empty body |
| `/paddles` | Product listing | "Carregando..." stuck |
| `/paddles/{brand}/{slug}` | Paddle details, specs, price | 404 |
| `/catalog` | Product grid with cards | Empty body |
| `/catalog/{slug}` | Product detail | Empty body |
| `/chat` | Chat input, empty state | Missing input |
| `/quiz` | Quiz step 1 | Empty body |
| `/gift` | Gift finder flow | Empty body |
| `/compare?a=3&b=2` | Comparison table | Empty body |
| `/blog/pillar-page` | Blog content | Empty body |

### Backend API Smoke Test (MUST pass)

| Endpoint | Expected | Must NOT |
|----------|----------|----------|
| `GET /health` | 200 | Error |
| `GET /api/v1/paddles?limit=5` | 200 + items | Empty |
| `GET /api/v1/paddles/{id}/similar` | 200 + array | 404 |
| `POST /chat` (correct body) | 200 + SSE stream | 422/503 |
| `GET /paddles/{id}/price-history` | 200 + history | 404 |
| `GET /api/v1/admin/queue` (no auth) | 401 | 200 |

---
*Requirements created: 2026-04-25 — v2.8.0 (E2E Critical Fixes)*
