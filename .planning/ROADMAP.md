# PickleIQ — Roadmap

## Milestones

- ✅ **v1.0 MVP** — Phases 1-6 (shipped 2026-03-28)
- ✅ **v1.1 Scraper Validation & E2E Testing** — Phases 7-9 (shipped 2026-04-01)
- ✅ **v1.2 Core Web Vitals Optimization** — Phase 11 (shipped 2026-04-01)
- 📋 **v1.3** — Next milestone (planning)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-6) — SHIPPED 2026-03-28</summary>

- [x] Phase 1: Foundation & Data Infrastructure — completed 2026-03-26
- [x] Phase 2: Full Data Pipeline — completed 2026-03-27
- [x] Phase 3: RAG Agent & AI Core — completed 2026-03-27
- [x] Phase 4: Frontend Chat & Product UI — completed 2026-03-28
- [x] Phase 5: SEO & Growth Features — completed 2026-03-28
- [x] Phase 6: Launch & Deploy — completed 2026-03-28

</details>

<details>
<summary>✅ v1.1 Scraper Validation & E2E Testing (Phases 7-9) — SHIPPED 2026-04-01</summary>

- [x] Phase 7: E2E Testing & Scraper Validation — completed 2026-04-01
- [x] Phase 8: Navigation UX Fixes — completed 2026-04-01
- [x] Phase 9: Image Extraction — completed 2026-04-01

</details>

<details>
<summary>✅ v1.2 Core Web Vitals Optimization (Phase 11) — SHIPPED 2026-04-01</summary>

- [x] Phase 11: Core Web Vitals Optimization — completed 2026-04-01

**Key achievements:**
- Image optimization with next/Image, responsive sizes, priority loading
- Font optimization with display swap and adjustFontFallback
- Layout stability with skeleton placeholders and Suspense
- Vercel Speed Insights with dynamic import
- Lighthouse CI with performance budgets (LCP < 2500ms, CLS < 0.1)
- WCAG 2.1 AA compliance with focus indicators and screen reader support

</details>

### 📋 v1.3 — Next Milestone (Planning)

#### Phase 13: Hybrid UI Redesign

**Goal:** Restyle the PickleIQ frontend with the Hybrid Modern Sports Tech design system — lime (#84CC16) accent on dark, green (#76b900) for data, JetBrains Mono for specs, 2px border radius, dark/light alternation, responsive grid.

**Requirements:** HY-01 through HY-12

**Plans:**
8/8 plans complete
- [x] 13-01-PLAN.md — Design Tokens & Typography Foundation (HY-01–HY-04, HY-11)
- [x] 13-02-PLAN.md — Button & Link Components (HY-05, HY-07)
- [x] 13-03-PLAN.md — Navigation & Layout Shell (HY-06, HY-08, HY-09)
- [x] 13-04-PLAN.md — Pages & Product Cards (HY-05, HY-08, HY-09, HY-12)
- [x] 13-05-PLAN.md — Gap Closure: Typography System (HY-01) — Google Fonts CDN
- [x] 13-06-PLAN.md — Gap Closure: Button Border Color (HY-04) — Lime borders
- [x] 13-07-PLAN.md — Gap Closure: Navigation Logo Accent (HY-06, HY-11) — IQ highlight + header classes
- [x] 13-08-PLAN.md — Gap Closure: Class Migration (HY-11) — Footer, pages, card components

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1 | v1.0 | 2/2 | Complete | 2026-03-26 |
| 2 | v1.0 | 2/2 | Complete | 2026-03-27 |
| 3 | v1.0 | 3/3 | Complete | 2026-03-27 |
| 4 | v1.0 | 2/2 | Complete | 2026-03-28 |
| 5 | v1.0 | 4/4 | Complete | 2026-03-28 |
| 6 | v1.0 | 2/2 | Complete | 2026-03-28 |
| 7 | v1.1 | 2/2 | Complete | 2026-04-01 |
| 8 | v1.1 | 2/2 | Complete | 2026-04-01 |
| 9 | v1.1 | 1/1 | Complete | 2026-04-01 |
| 10 | v1.1 | 2/2 | Complete | 2026-04-01 |
| 11 | v1.2 | 4/4 | Complete | 2026-04-01 |
| 12 | v1.3 | 4/4 | Complete    | 2026-04-01 |

### Phase 12: Data Pipeline Quality & Reliability

**Goal:** Fix production-critical operational issues identified in engineering review — race conditions, API key exposure, transaction safety, and observability.

**Requirements:** PIPE-01 through PIPE-12

**Plans:**
4/4 plans complete
- [x] 12-01-P1-schema-foundation-PLAN.md — Schema fixes, NOT NULL constraints
- [x] 12-02-P1-transactions-and-retry-PLAN.md — Transaction rollback, ML retry logic
- [x] 12-03-P1-memory-and-concurrency-PLAN.md — Memory limits, atomic upsert
- [x] 12-04-P2-observability-infrastructure-PLAN.md — Metrics, DLQ, freshness alerts

---

*For detailed milestone archives, see `.planning/milestones/`*