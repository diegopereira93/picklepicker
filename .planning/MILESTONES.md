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
