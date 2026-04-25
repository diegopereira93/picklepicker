# Milestones

## v2.2.0 Launch Readiness: Testes & Correções Críticas (Shipped: 2026-04-13)

**Phases completed:** 4 (Phases 24-27) | **Plans:** 4 | **Commits:** 26 | **Timeline:** 1 day

**Key accomplishments:**

- Pipeline tests restored — 38 failing tests fixed by updating mocks for scrape-based crawlers, 146+ tests now passing
- Frontend tests stabilized — 179/179 Vitest tests passing after quiz widget test rewrites
- E2E Playwright suite created — 23 tests across 5 spec files (home, catalog, chat, quiz, navigation)
- Backend deprecation fixes — `datetime.utcnow()` → `datetime.now(timezone.utc)` across all endpoints
- Project documentation generated — 7 canonical docs, 2,108 lines (README, ARCHITECTURE, GETTING-STARTED, DEVELOPMENT, TESTING, CONFIGURATION, DEPLOYMENT)
- Developer onboarding improved — `backend/.env.example` created for new contributor setup

**Stats:** 57 files changed, +4,756/-679 LOC

---

## v2.4.0 Site Quality & UX Polish (Shipped: 2026-04-16)

**Phases completed:** 4 (Phases 28-31) | **Commits:** 3+ | **Timeline:** 2 days

**Key accomplishments:**

- Critical bug fixes — broken Gift page, quiz results, HTML lang attribute, quiz profile storage
- Core UX — catalog text search, chat without quiz, filter count, pagination, nav updates
- Conversion — landing page visual overhaul, SEO fundamentals, expanded footer, DESIGN.md sync
- Polish — compare 3-4 paddles, breadcrumbs, error boundaries, skip-to-content link

**Stats:** 50+ files changed

---

## v2.5.0 Backend Hardening & RAG Reliability (Shipped: 2026-04-20)

**Phases completed:** 3 (Phases 32-34) | **Commits:** 5+ | **Timeline:** 4 days

**Key accomplishments:**

- Production Redis cache + Clerk JWT auth middleware
- RAG pipeline reliability — embedding error handling, eval gate quality metrics, structlog logging
- Backend hygiene — dev deps, version from VERSION file, CORS validation

**Stats:** 30+ files changed

---

## v2.6.0 Pipeline & Infra Hardening (Shipped: 2026-04-22)

**Phases completed:** 3 (Phases 35-37) | **Commits:** 3+ | **Timeline:** 2 days

**Key accomplishments:**

- Pipeline reliability — auto-refresh materialized view, reembed worker, migration system
- Retailer expansion foundation — BaseCrawler, is_active flag, review queue status tracking
- Security & infra hardening — CSP, HSTS, consolidated scraper workflow, restricted images

**Stats:** 20+ files changed, +1,200 LOC

---

## v2.7.0 Build & Test Quality (Shipped: 2026-04-24)

**Phases completed:** 2 (Phases 38-39) | **Commits:** 1 | **Timeline:** 1 day

**Key accomplishments:**

- Build quality gates — `next build` and `next lint` pass with zero errors, TypeScript strict mode clean
- Test suite hardening — 208/212 backend tests passing, 170/170 frontend tests, pipeline tests stabilized
- Frontend 23 pages generated without errors

**Stats:** 98 files changed (cumulative v2.4-v2.7 merge), +6,251/-896 LOC

---

## v2.8.0 E2E Critical Fixes (Shipped: 2026-04-25)

**Phases completed:** 4 (Phases 40-43) | **Commits:** 2+ | **Timeline:** 1 day

**Source:** Playwright E2E Analysis — full browser automation of 15 routes + 17 API endpoints

**Issues found & fixed:** 2 critical (site-breaking), 4 high, 1 medium, 2 low + quiz→chat flow

**Key accomplishments:**

- 🔴 ALL 15 pages render EMPTY — ClerkAuthButtons crashes without ClerkProvider → ✅ Fixed
- 🔴 Chat proxy returns 503 — Docker networking broken → ✅ Fixed
- 🟠 Similar Paddles always 404 → ✅ Returns 200 + []
- 🟠 Paddle slugs null → ✅ Generated model_slug for all paddles
- 🟠 Admin unauthenticated → ✅ Added require_admin dependency
- 🟠 Price history route mismatch → ✅ Fixed Docker env var
- Quiz → Chat auto-recommendation broken → ✅ Fixed 5 bugs (level mapping, SSE parser, RAG fallback, DB timeout, transport race)

| Phase | Goal | Status |
|-------|------|--------|
| 40 | Critical Frontend Fixes (Clerk + Docker) | ✅ Complete |
| 41 | API & Route Fixes (Slugs + Similar + Auth + Routes) | ✅ Complete |
| 42 | Data Quality & E2E Verification | ✅ Complete |
| 43 | Quiz → Chat Auto-Recommendation Fix | ✅ Complete |

---
