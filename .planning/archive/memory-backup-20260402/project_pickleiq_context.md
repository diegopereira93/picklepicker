---
name: PickleIQ Project Context
description: v1.0 + v1.1 + v1.2 + v1.3 (Phase 13) COMPLETE. 12 phases. Hybrid design system implemented.
type: project
---

PickleIQ is a pickleball paddle recommendation platform for the **Brazilian market** combining daily price tracking (Firecrawl scraping of BR retailers) with a conversational AI agent (RAG + Groq Llama 3.3 70B).

**Why:** Founder (Diego) experienced the problem personally. Has a professional trainer partner who validated the concept and wants to distribute to students.

**Design doc location:** `~/.gstack/projects/picklepicker/diego-master-design-20260326-004316.md`

---

## Execution Status (v1.0 + v1.1 + v1.2 — ALL SHIPPED)

### Phase 1 — Foundation & Data Infrastructure ✅ COMPLETE
- Completed: 2026-03-26
- 4 plans, 11 tests passing
- Monorepo, PostgreSQL schema, Brazil Pickleball Store crawler, Mercado Livre integration

### Phase 2 — Full Data Pipeline ✅ COMPLETE
- Completed: 2026-03-27
- 5 plans (2 waves), 56+ tests passing
- All BR retailers, SKU dedup 3-tier, pgvector embeddings, FastAPI 5 endpoints, GH Actions schedule

### Phase 3 — RAG Agent & AI Core ✅ COMPLETE
- Completed: 2026-03-27
- 5 waves, 103 tests passing
- **Groq Llama 3.3 70B selected** (eval gate ≥4.0 on PT-BR queries)
- POST /chat with SSE streaming, Redis cache, Langfuse, degraded mode (8s timeout)

### Phase 4 — Frontend: Chat & Product UI ✅ COMPLETE
- Completed: 2026-03-27
- 5 sub-plans in parallel, 61 tests passing
- Next.js 14, Tailwind, shadcn/ui, quiz onboarding, comparison tool, admin panel

### Phase 5 — SEO & Growth Features ✅ COMPLETE
- Completed: 2026-03-28
- 4 plans, 127 tests passing
- Clerk v5 auth + price alerts (Resend), price history charts, blog pillar page

### Phase 6 — Launch & Deploy ✅ COMPLETE
- Completed: 2026-03-28
- Production infra, CI/CD, observability, 50-user beta

### Phase 7 — E2E Testing & Scraper Validation ✅ COMPLETE 2026-03-29
- 1 plan, 101 new tests, 90% combined coverage
- All 3 scrapers validated (Brazil 80%, Drop Shot 93%, ML 94%)
- Firecrawl `/extract` error modes documented

### Phase 8 — Navigation UX Fixes ✅ COMPLETE 2026-03-29
- 1 plan, 4 tasks
- Removed /compare links (404), Chat IA nav item
- Added numeric ID fallback in fetchProductData
- Enriched catalog cards (skill_level, specs, stock indicator)

### Phase 9 — Image Extraction ✅ COMPLETE 2026-03-31
- 1 plan, scraper enhanced for Selkirk product images
- Two-phase extraction (category + product pages) for lazy-loaded images
- mitiendanube URL transform (-1024-1024 → -480-0) for optimized size
- Brazil Store scraper now captures product images from Nube CDN

### Phase 10 — Performance & UX Polish ✅ COMPLETE 2026-04-01
- 3 sub-plans (P02, P03, P10.1), 12 tasks total
- Dark/light theme toggle with ThemeProvider (localStorage key: pickleiq-theme)
- Price formatting with R$ prefix and Brazilian locale (pt-BR)
- Price history chart dynamic import with time-range selector (1M/3M/6M/1Y/ALL)
- CSS motion system with prefers-reduced-motion support
- Loading skeletons and Suspense boundaries for async content

### Phase 11 — Core Web Vitals Optimization ✅ COMPLETE 2026-04-01
- 4 plans, 25/25 must-haves verified
- **LCP < 2.5s** — next/image with priority loading, WebP/AVIF, responsive sizes
- **CLS < 0.1** — skeleton placeholders, min-height containers, font swap
- **WCAG 2.1 AA** — focus indicators, aria labels, useAnnouncer, skip link
- Vercel Speed Insights with dynamic import (zero initial load)
- Lighthouse CI with performance budgets (LCP ≤ 2500ms, CLS ≤ 0.1)
- Bundle analyzer with size-limit (150KB chunks, 50KB _app.js)

### Phase 13 — Hybrid UI Redesign ✅ COMPLETE 2026-04-02
- 8 plans (4 original + 4 gap closure), 12/12 must-haves verified
- **Design System:** Hybrid Modern Sports Tech (see DESIGN.md v2.0)
- **Typography:** Google Fonts CDN (Instrument Sans, Inter, JetBrains Mono)
- **Color:** Lime (#84CC16) for primary actions, Green (#76b900) for data elements
- **Class Migration:** Complete nv-* → hy-* migration with CSS aliases
- **Components:** Button variants, card components, navigation with lime "IQ" accent
- Requirements HY-01 through HY-12 satisfied

---

## Settled Architecture Decisions

Confirmed during /plan-eng-review (2026-03-26) AND validated through Phase 11:

- **pgvector on PostgreSQL** — 500 paddles doesn't justify separate vector service
- **Groq Llama 3.3 70B** — selected via eval gate (≥4.0 on 10 PT-BR queries)
- **Anonymous-first** through Phase 4 — Clerk auth added Phase 5
- **Brazil retailers:** Brazil Pickleball Store, Franklin Pickleball Brasil, Head Brasil, JOOLA Brasil, Drop Shot Brasil, Mercado Livre
- **US/international sites** — spec enrichment only (no price scraping)
- **Mercado Livre Afiliados** — primary affiliate program
- **SSE streaming** for chat; 8s timeout → degraded mode (price-based fallback)
- **Next.js Route Handler proxy** for chat (FastAPI → Vercel AI SDK)
- **GitHub Actions schedule** for pipeline orchestration (not Prefect)
- **Entity named `paddles`** (not `products`)
- **Supabase** for PostgreSQL + pgvector
- **Railway for API staging** — zero cold starts, CLI fluidity

### Phase 11 CWV Decisions (2026-04-01)

- **next/image mandatory** — no raw `<img>` tags; explicit width/height required
- **Font loading** — Inter with `display: 'swap'`, `adjustFontFallback: true`, preconnect hints
- **Third-party scripts** — dynamic import with `ssr: false` defers loading (SpeedInsights)
- **Bundle analysis** — `ANALYZE=true npm run build` triggers @next/bundle-analyzer
- **Lighthouse CI** — runs on every push; fails build if Performance < 90 or Accessibility < 90
- **Focus indicators** — 2px solid outline with 2px offset using primary color
- **Screen reader** — `useAnnouncer` hook with `aria-live="polite"` for dynamic content

---

## Execution Workflow Preferences (Confirmed 2026-03-27 to 2026-04-01)

**GSD Phase Execution:**
- **Wave 1 Checkpoint Mode** for multi-plan phases — execute first wave, show summary, pause for verification
- **Auto-mode** (`--auto` flag) works well — /plan-phase → /execute-phase → /ship
- **/ship fully automated** — version bump, CHANGELOG, PR creation with comprehensive body
- **/gsd:next routing** — effective for rapid context switches; detects phase state automatically

**Shipping with /ship:**
- Version auto-decided (PATCH: 50-7171 lines)
- CHANGELOG from git diff
- TODOS.md auto-updated
- Pre-landing review catches issues pre-PR
- PR body includes: test coverage, review findings, verification results

---

## Feature Decisions (from /plan-eng-review 2026-03-26)

- **Pre-chat quiz** — 3-step (nível → estilo → orçamento) before chat opens
- **OSS model eval gate** — Groq Llama 3.3 70B vs Claude Sonnet → Groq selected
- **Admin Panel** — /admin/queue (review) + /admin/catalog (CRUD)
- **Spec enrichment matching** — RapidFuzz ≥0.85 threshold, no match → review_queue
- **Crawler failure alerts** — Telegram after 3 Firecrawl retries

---

## Known Issues & Debugging Patterns

### Catalog 404 Bug (2026-03-30)

**Symptom:** `/paddles` page returning 404, showing "Nenhuma raquete encontrada"

**Root causes found:**
1. Wrong API endpoint in `frontend/src/lib/seo.ts` — `/paddles` instead of `/api/v1/paddles`
2. Missing `NEXT_PUBLIC_FASTAPI_URL` in `frontend/.env.local`
3. Next.js dev server on port 3001 (not 3000) due to port conflict

**Fix applied:**
- Corrected endpoint: `${FASTAPI_URL}/api/v1/paddles`
- Added env var: `NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000`
- Debug logging added to fetchPaddlesList and PaddlesPage

**Lesson:** Frontend API calls must match backend route prefix (`/api/v1/`). Environment variables for API URLs must be in `.env.local` (not just `.env`).

---

## Revenue Model

Affiliate commissions (10-40%). Click tracking via `/go/{paddle_id}/{retailer}` redirect. URLs generated server-side — LLM never constructs affiliate URLs directly.

## Distribution

- Primary: Trainer partner → students (WhatsApp groups, immediate)
- Secondary: SEO organic (6-12 month maturation, started Phase 5)

---

## ROADMAP Summary

| Milestone | Phases | Status | Completed |
|-----------|--------|--------|-----------|
| v1.0 | 1-6 | ✅ SHIPPED | 2026-03-28 |
| v1.1 | 7-8 | ✅ SHIPPED | 2026-03-29 |
| v1.2 | 9-11 | ✅ SHIPPED | 2026-04-01 |
| v1.3 | 13 | ✅ Phase 13 COMPLETE | 2026-04-02 |

**Design System:** Hybrid Modern Sports Tech (DESIGN.md v2.0) — lime accent, green data, JetBrains Mono specs, 2px radius, dark/light alternation

**Next:** v1.3 milestone completion or continue planning
