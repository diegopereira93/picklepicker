# Roadmap: PickleIQ

## Milestones

- ✅ **v1.6.0** — UI Redesign (Phases 16-19) — shipped 2026-04-05
- ✅ **v1.7.0** — Backend API (Phases 20-23) — shipped 2026-04-13
- ✅ **v2.2.0** — Launch Readiness (Phases 24-27) — shipped 2026-04-13
- ✅ **v2.4.0** — Site Quality & UX Polish (Phases 28-31) — shipped 2026-04-20
- ✅ **v2.5.0** — Backend Hardening & RAG Reliability (Phases 32-34) — shipped 2026-04-24
- ✅ **v2.6.0** — Pipeline & Infra Hardening (Phases 35-37) — shipped 2026-04-24
- ✅ **v2.7.0** — Build & Test Quality (Phases 38-39) — shipped 2026-04-24
- ✅ **v2.8.0** — E2E Critical Fixes (Phases 40-43) — shipped 2026-04-25
- 📋 **v1.5.0** — Production Infrastructure (Phase 15) — deferred

## Current Focus

**v2.8.0 — E2E Critical Fixes ✅ COMPLETE (2026-04-25)**

Full Playwright E2E analysis found 2 site-breaking + 4 high-priority issues + quiz→chat flow broken. All issues fixed.

| Phase | Goal | Status |
|-------|------|--------|
| 40 | Critical Frontend Fixes (Clerk + Docker) | ✅ Complete |
| 41 | API & Route Fixes (Slugs + Similar + Auth + Routes) | ✅ Complete |
| 42 | Data Quality & E2E Verification | ✅ Complete |
| 43 | Quiz → Chat Auto-Recommendation Fix | ✅ Complete |

---

## Milestone v2.8.0 — E2E Critical Fixes

*Created: 2026-04-25*
*Source: Playwright E2E Analysis — 15 frontend routes + 17 backend API endpoints tested*
*Goal: Restore full site functionality. All 15 routes must render content, all user flows must work end-to-end.*

**Requirements:** See `.planning/REQUIREMENTS.md` (E2E-CR1, E2E-CR2, E2E-H1–H4, E2E-M1, E2E-L1–L2)

### Phase 40: Critical Frontend Fixes (Clerk + Docker Networking)

**Goal:** Fix the two issues that make the entire site non-functional.

**Root causes:**
1. `ClerkWrapper` renders `<>{children}</>` without `ClerkProvider` when `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is absent. `ClerkAuthButtons` calls `useAuth()` outside provider → throws → `NotFoundErrorBoundary` catches → page body = EMPTY.
2. Frontend Docker container uses `FASTAPI_URL=http://localhost:8000` (container's own loopback), not `http://backend:8000` (Docker service name). Chat proxy returns 503.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 40.1 | `frontend/src/components/layout/clerk-available-provider.tsx`, `frontend/src/components/layout/clerk-auth-buttons.tsx` | Create a `useClerkAvailable()` hook that checks if ClerkProvider is active. Make `ClerkAuthButtons` and `MobileClerkAuth` return `null` when Clerk is unavailable. No `useAuth()` call outside provider. |
| 40.2 | `frontend/src/components/clerk-provider.tsx` | Verify `ClerkWrapper` properly signals availability to children (context or global flag). |
| 40.3 | `docker-compose.yml` | Set `FASTAPI_URL=http://backend:8000` for frontend service. Verify `NEXT_PUBLIC_FASTAPI_URL` for client-side calls (may need to remain `http://localhost:8000` for browser access). |
| 40.4 | `frontend/src/app/api/chat/route.ts` | Verify `FASTAPI_URL` env var is read correctly from Docker env. Add fallback logic for Docker vs local dev. |
| 40.5 | All pages | Manual E2E: all 15 routes render content. Chat proxy returns 200. Zero `pageerror` events. |

**Success criteria:**
1. All 15 frontend routes render content (body text length > 0) after 3s
2. Chat proxy returns 200 with SSE stream (not 503)
3. Zero `@clerk/nextjs: useAuth can only be used within ClerkProvider` errors
4. Docker Compose `make dev` produces a fully functional site

**Plans:** 2 plans (Wave 1 — all parallel)

Plans:
- [ ] 40-01-PLAN.md — Fix ClerkAuthButtons Rules of Hooks violation + tests (E2E-CR1)
- [ ] 40-02-PLAN.md — Verify Docker networking + chat proxy env var tests (E2E-CR2)

---

### Phase 41: API & Route Fixes

**Goal:** Fix paddle slugs, similar paddles, admin auth, and price history route mismatch.

**Root causes:**
1. Most paddles have `model_slug: null` — detail route `/paddles/[brand]/[model-slug]` fails.
2. Similar paddles endpoint finds no matches — returns 404 instead of 200 + empty array.
3. Admin endpoints have no auth dependency despite docstring claims.
4. Frontend calls wrong path for price history data.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 41.1 | `scripts/` or SQL migration | Generate `model_slug` for all paddles: `LOWER(REPLACE(REPLACE(REPLACE(name, ' ', '-'), '--', '-'), '"', ''))`. Update all rows where `model_slug IS NULL`. |
| 41.2 | `backend/app/api/paddles.py` | Change similar paddles endpoint: return 200 + `[]` when no matches found (not 404). Add `min_similarity` parameter (default 0.5, lower than current threshold). |
| 41.3 | `backend/app/api/admin.py` | Add `Depends(require_admin)` dependency to all admin endpoints. Extract `require_admin` function from existing pattern in other modules. |
| 41.4 | `frontend/src/components/price-history-chart.tsx` (or relevant file) | Fix price history API call to use correct backend route `GET /paddles/{id}/price-history`. |
| 41.5 | `backend/tests/` | Add tests: (a) similar paddles returns 200 + `[]` for paddle with no matches, (b) admin endpoints return 401 without auth, (c) price history route works. |

**Success criteria:**
1. `GET /api/v1/paddles/{id}/similar` returns 200 (not 404) for all paddles
2. Paddle detail pages resolve via brand + slug (not 404)
3. Admin endpoints return 401 without `Authorization: Bearer` header
4. Price history chart loads real data on paddle detail page
5. All existing tests pass

---

### Phase 42: Data Quality & E2E Verification

**Goal:** Fix remaining low-priority issues and run comprehensive E2E verification to prove everything works.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 42.1 | `frontend/src/app/blog/pillar-page/page.tsx` | Update blog title from "2025" to "2026". |
| 42.2 | `frontend/.env` or `docker-compose.yml` | Ensure all env vars documented. Verify `frontend/.env.example` matches actual needs. |
| 42.3 | Docker Compose | Run full E2E Playwright test suite against `make dev`. All 15 routes must render. All user flows must complete. |
| 42.4 | Backend | Run full API smoke test: health, paddles, chat, similar, price-history, admin auth. |
| 42.5 | Tests | Run full test suites: backend (pytest), frontend (vitest), pipeline (pytest). No regressions. |

**Success criteria:**
1. E2E smoke test passes for all 15 routes (see REQUIREMENTS.md verification table)
2. Backend API smoke test passes for all critical endpoints
3. Chat flow works end-to-end: type message → receive SSE response
4. Quiz flow works: step 1 → step 7 → results
5. All existing test suites pass (170 frontend, 208+ backend)
6. Blog title updated to 2026

---

## Milestone v1.5.0 — Core Infrastructure & Production Deploy

**Goal:** Provision production infrastructure, deploy to Railway + Vercel + Supabase, and add resilience for embedding outages.

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 15 | Production Deploy | Provision infra, deploy, health checks, embedding fallback, zero-paddle alert | INFRA-01–05, EMB-01–03, ALERT-01, QA-01–03 | 5 |

### Phase 15: Production Infrastructure

**Goal:** Ship to production with working health checks, embedding fallback, and basic alerting.

**Root causes (from Metis pre-planning analysis):**

1. **No production infra** — Local Docker only. Supabase, Railway, Vercel not provisioned. All deploy targets exist but have never been connected.
2. **Embedding provider fragility** — Jina AI + HuggingFace are external dependencies with no local fallback. `backend/app/services/embedding.py` has dead code `_get_local_model()` (lines 23-34) that's never called. If both APIs fail, RAG is down.
3. **No scraper health monitoring** — Crawlers run via GitHub Actions cron but there's no alert when they return zero results. Price data goes stale silently.
4. **Railway cold starts** — Hobby tier sleeps after 30min inactivity. `/chat` SSE will disconnect during cold start (~15s), causing message duplication.

**Tasks (in execution order):**

#### Wave 1 — Infrastructure Provisioning

| Task | File(s) | Description |
|------|---------|-------------|
| 15.1 | Supabase dashboard, `backend/.env` | Provision Supabase project (sa-east-1 São Paulo for LGPD compliance). Free tier initially. Create `DATABASE_URL` with connection pooler. Verify pgvector extension enabled. |
| 15.2 | `scripts/migrate_to_supabase.py` (new), `pipeline/db/schema.sql` | Create migration script: dump local schema → apply to Supabase. Run `schema-updates.sql` for missing columns. Verify all tables exist. Seed with `populate_paddles.sql`. Run `migrate_real_images.py` for real images. |
| 15.3 | `backend/Dockerfile`, Railway dashboard | Deploy backend to Railway. Configure health check (`/health` endpoint, <5s response). Set env vars via Railway Secrets (not GitHub Secrets). Verify: `curl $RAILWAY_URL/health` → 200. |
| 15.4 | `frontend/vercel.json`, Vercel dashboard | Deploy frontend to Vercel. Configure `NEXT_PUBLIC_API_URL` env var pointing to Railway backend. Verify: homepage loads, /paddles renders, /chat accessible. |

#### Wave 2 — Resilience & Alerting (parallel, after Wave 1)

| Task | File(s) | Description |
|------|---------|-------------|
| 15.5 | `backend/app/services/embedding.py` | Implement embedding fallback chain: Jina AI → HuggingFace → SentenceTransformers (local). Integrate existing dead code `_get_local_model()`. Add dimension validation (384d model must NOT be used — pgvector expects 768d). Use `all-MiniLM-L6-v2` only if dimension matches. Add sticky fallback: once local is active, stay local for 5 minutes before retrying API. |
| 15.6 | `backend/tests/test_embedding_service.py` | Add tests: (a) Jina fails → HuggingFace used, (b) Both APIs fail → local SentenceTransformers used, (c) Dimension validation rejects wrong-size vectors, (d) Sticky fallback timer works, (e) All three providers succeed → Jina preferred. |
| 15.7 | `.github/workflows/scrape.yml` | Add zero-paddle alert step at end of scrape job. Query: `SELECT COUNT(*) FROM price_snapshots WHERE DATE(scraped_at) = CURRENT_DATE AND retailer_id = X`. If 0 for any retailer → Telegram alert via existing middleware. Add "3 consecutive zeros" logic with GitHub Actions cache to avoid false positives from transient network failures. |

#### Wave 3 — Verification & Cold Start Mitigation

| Task | File(s) | Description |
|------|---------|-------------|
| 15.8 | `.github/workflows/keepalive.yml` (new) | Add GitHub Actions cron (every 5 minutes) that `curl`s Railway health endpoint to prevent cold starts. Simple: `curl -sf $RAILWAY_URL/health || echo "unhealthy"`. Runs 24/7. |
| 15.9 | `backend/tests/`, `frontend/src/tests/` | Run full test suite against production: backend 174+ pass, frontend 161+ pass. Verify health endpoint. Verify embedding fallback. Verify scraper alert triggers on zero-paddle condition. |
| 15.10 | All | Production smoke test: (a) Homepage loads, (b) /paddles shows real images or "Foto" fallback, (c) Paddle detail resolves correctly, (d) Quiz completes, (e) /chat returns streaming response. |

**Success criteria:**
1. `curl $PROD_URL/health` returns `{"status":"ok"}` in <2s
2. Homepage loads at production URL with zero console errors
3. `/chat` responds within 5s (no cold start delay)
4. Embedding fallback works when Jina/HuggingFace are unreachable
5. Zero-paddle Telegram alert fires when scraper returns 0 results
6. All existing tests pass with no regressions

---

## Milestone v1.6.0 — UI Redesign (Design Review Implementation) ✅ COMPLETE

**Goal:** Implement the winning design variants from the 9-variant design review (2026-04-05). Redesign Home, Catalog, and Chat screens to maximize funnel conversion.

**Status:** Complete — All phases executed (2026-04-05)

**Design review source:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/`

**Winning combination:**
- Home: C (Quiz-Forward) + data stats from A
- Catalog: A (Comparison Table) + product images from B + grid toggle
- Chat: B (Sidebar Companion) + card responses from C

| # | Phase | Goal | Requirements | Status |
|---|---|-------|------|--------------|
| 16 | DESIGN.md v3.0 + Foundation | Update design system with 6 proposed changes, add chat/widget sections | DS-01–05 | ✅ Complete |
| 17 | Home-C Quiz-Forward | Quiz widget above-the-fold, data stats, feature steps | HOME-01–05 | ✅ Complete |
| 18 | Chat-B Sidebar Companion | Split-panel layout, card responses, product sidebar | CHAT-01–06 | ✅ Complete |
| 19 | Catalog-A Comparison Table | Sortable table, visual grid toggle, score badges | CAT-01–06, COH-01–04, QA-01–06 | ✅ Complete |

**Commit:** 6853154 — Phases 16-19 implemented together

### Phase 16: DESIGN.md v3.0 + Foundation

**Goal:** Update the design system to support all 3 winning variants. This phase is the foundation — all subsequent phases depend on it.

**Root causes (from Metis constraint analysis):**

1. **No chat UI patterns** — DESIGN.md has minimal chat guidance. 3 of 9 variants are chat-based but DESIGN.md provides no message bubble, card response, or input area patterns.
2. **No semantic color system** — Catalog C's segmented discovery needs level-based color coding. No beginner/intermediate/advanced/professional colors defined.
3. **2px border radius too strict** — Conversational elements (chat bubbles, tip cards) need softer edges. Current rule makes chat feel robotic.
4. **No widget patterns** — Quiz cards, carousels, progress indicators, toggle switches all lack guidance.
5. **1200px max-width constrains data** — Comparison tables and split-panels need 1440px.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 16.1 | `DESIGN.md` | Update to v3.0 header. Add "Chat Components" section (message bubbles, card responses, typing indicator, input area, streaming animation patterns). Add "Interactive Widgets" section (quiz cards with selected state, carousel arrows/dots, progress indicators, toggle switches). Add semantic level colors (--level-beginner, --level-intermediate, --level-advanced, --level-professional). |
| 16.2 | `DESIGN.md` | Add "Full-Dark Sections" exception to layout rules: "Default: alternate dark/light. Exception: allow continuous dark for chat, dashboards, terminal aesthetics." Add `--max-width-data: 1440px` token for data-dense layouts. Add `--radius-conversational: 8px` for chat bubbles and tip cards. |
| 16.3 | `frontend/src/app/globals.css` | Add new CSS custom properties for all v3.0 tokens (semantic levels, conversational radius, data max-width). Add base chat component styles (.chat-bubble, .chat-card, .chat-input, .typing-indicator). Add widget base styles (.quiz-pill, .carousel-arrow, .progress-dot, .toggle-switch). |
| 16.4 | `frontend/src/app/globals.css` | Update motion system: add chat-message-enter keyframe, quiz-card-selection ripple, carousel-snap easing, card-response-enter animation. |
| 16.5 | Design system | Verify all new DESIGN.md tokens are documented. Verify no contradictions between v2.0 and v3.0 rules. Verify existing components (nav, footer, buttons, product cards) still comply. |

**Success criteria:**
1. DESIGN.md has "Chat Components" and "Interactive Widgets" sections with complete patterns
2. All 6 new CSS custom properties defined in globals.css
3. New motion patterns documented in DESIGN.md
4. No contradictions with existing design system

---

### Phase 17: Home-C Quiz-Forward

**Goal:** Redesign the homepage with an interactive quiz widget above-the-fold that captures user intent immediately.

**Root causes:**
1. Current homepage has generic 3-column feature grid (AI slop pattern per previous audit).
2. Quiz CTA is buried — users don't see it until scrolling past the fold.
3. No data credibility signals on homepage — analytical users don't trust the platform immediately.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 17.1 | `frontend/src/app/page.tsx` | Redesign hero section: dark background, centered H1 "Encontre a raquete ideal para o seu jogo" with lime underline, interactive quiz widget with pill toggle buttons (Nível: Iniciante/Intermediário/Avançado, Orçamento: <R$300/<R$500/>R$500+, Estilo de jogo: Potência/Controle/Equilíbrio). "Começar Quiz →" CTA button. Recommendation card preview below quiz. |
| 17.2 | `frontend/src/components/quiz/` (new components) | Create QuizWidget component: pill toggle buttons with selected state (lime border + box-shadow glow), 2-col layout on tablet+, full-width on mobile. Create RecommendationCard component: image placeholder, paddle name (Instrument Sans 600), price (JetBrains Mono, data-green), key specs, "Ver detalhes" CTA. |
| 17.3 | `frontend/src/app/page.tsx` | Add data credibility stats section (dark #1a1a1a background): 3 stat cards — "147 raquetes analisadas", "3 varejistas monitorados", "Preços atualizados diariamente". JetBrains Mono for values, data-green accent. |
| 17.4 | `frontend/src/app/page.tsx` | Add feature steps section (light #ffffff background): numbered circles (1-2-3) with connecting lines, step titles + descriptions. Step 1: "Responda o quiz", Step 2: "Análise com IA", Step 3: "Compare preços". |
| 17.5 | `frontend/src/components/quiz/` | Returning visitor logic: check localStorage for completed quiz, show "Continue where you left off" or recent recommendations for returning users. Use `useEffect` + localStorage key `pickleiq_quiz_completed`. |

**Success criteria:**
1. Quiz widget renders above-the-fold on desktop and mobile
2. Quiz completes with 3 selections → recommendation card preview appears
3. Data stats display with JetBrains Mono values in data-green
4. Feature steps show numbered progression with connecting lines
5. Returning users see alternative content (not the quiz again)

---

### Phase 18: Chat-B Sidebar Companion

**Goal:** Redesign the chat screen with a split-panel layout that keeps product details visible during conversation.

**Root causes:**
1. Current chat is full-width — product information is not visible while chatting.
2. Buy button is only accessible by scrolling through conversation history.
3. AI responses are plain text — no structured product cards or comparison tables.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 18.1 | `frontend/src/app/chat/page.tsx` | Redesign chat page layout: 55%/45% split-panel. Left panel (white #ffffff): product card with image, name, brand (Inter 12px, uppercase), price (JetBrains Mono 20px, data-green), specs grid, score badge, "Comprar na loja" CTA button, related paddles row. Right panel (dark #1a1a1a): chat header, messages, input. |
| 18.2 | `frontend/src/components/chat/` | Create SidebarProductCard component: image container (180px height), paddle name (Instrument Sans 600, 20px), brand, price (JetBrains Mono, data-green), specs table, score badge with color, CTA button. Create RelatedPaddles component: horizontal row of smaller cards with name, price, brand. |
| 18.3 | `frontend/src/components/chat/chat-widget.tsx` | Add card-structured AI responses: ProductCard (image + specs + CTA embedded in message), ComparisonCard (mini-table with 2-3 paddles, green highlights), TipCard (amber accent left border, informational content). Limit to 1 card type per AI response. |
| 18.4 | `frontend/src/components/chat/chat-widget.tsx` | Update message styling: user messages right-aligned with lime (#84CC16) left border (2px radius), dark background (#111). AI messages left-aligned, transparent background. Max width 80% of chat container. |
| 18.5 | `frontend/src/components/chat/` | Add suggested questions component: clickable prompt pills below chat messages. "Qual a diferença entre 13mm e 16mm?", "Melhor raquete para iniciante?", "Raquete com melhor custo-benefício". |
| 18.6 | `frontend/src/app/chat/page.tsx` | Responsive: below 1024px, stack panels vertically (50% height each). Mobile: product panel on top, chat panel below. Full height on both. |

**Success criteria:**
1. Split-panel renders correctly at 1440px and stacks at 768px
2. Product card shows image, name, brand, price, specs, score, and CTA
3. Card-structured AI responses render as product cards, comparison tables, or tip cards
4. "Comprar na loja" button is always visible (no scrolling needed)
5. Related paddles row shows 3+ smaller product cards

---

### Phase 19: Catalog-A Comparison Table + Polish

**Goal:** Redesign the catalog with a sortable data table and visual grid toggle, then polish cross-screen coherence.

**Root causes:**
1. Current catalog uses basic product cards — no comparison capability.
2. Analytical persona needs sortable, scannable data — not just visual cards.
3. No way to compare paddles side-by-side on mobile.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 19.1 | `frontend/src/app/paddles/page.tsx` | Redesign catalog: sticky filter bar with chip filters (MARCA, NÍVEL, PREÇO) with active lime highlight. Results count display. Sort dropdown. Table/card toggle. Sticky bottom selection bar. |
| 19.2 | `frontend/src/components/catalog/` (new components) | Create FilterBar component: filter groups with labels, chip buttons with selected state, sort dropdown, view toggle (Tabela/Cards), results count. Create ComparisonTable component: sortable 9-column table with product thumbnail, name, brand, price (JetBrains Mono), specs, score badges. Alternating row colors (white/#1a1a1a). |
| 19.3 | `frontend/src/components/catalog/` | Create ProductGrid component (from Catalog-B): 3-col grid of polished cards with image container, hover-reveal specs overlay, compare checkbox. Used when grid toggle is active. Create SelectionBar component: sticky bottom bar showing selected count + "Comparar N raquetes" CTA. |
| 19.4 | `frontend/src/app/paddles/page.tsx` | Score badges: color-coded — high (#76b900 bg, white text), medium (#FDE047 bg, black text), low (#B91C1C bg, white text). Product image thumbnails in first column. Row selection via checkbox. Selection state persisted to state. |
| 19.5 | Cross-screen | Verify consistent navigation across Home/Chat/Catalog. Verify CTA styles match. Verify funnel paths work: Home → Quiz → Chat → Catalog AND Home → Catalog → Chat. Verify responsive at 375px, 768px, 1440px. |
| 19.19.6 | `frontend/src/tests/` | New component tests: quiz widget, comparison table, sidebar chat, card responses. Integration tests: quiz completion flow, chat with sidebar, table sort. |
| 19.7 | Quality | Run full test suite: backend 174+ pass, frontend 161+ pass. Run AI slop audit on all 3 screens. Manual smoke test: quiz → recommendation → chat → compare → affiliate click. Verify responsive at 3 breakpoints. |

**Success criteria:**
1. Comparison table sorts by any column (price, score, name)
2. Table/card toggle switches views without page reload
3. Score badges color-coded correctly
4. Bottom selection bar appears on selection with correct count
5. All 3 funnel paths work end-to-end
6. All existing tests pass + new tests pass
7. AI slop checklist passes on all screens

---

<details>
<summary>✅ v1.7.0 — Backend API for Frontend Redesign (Phases 20-23) — SHIPPED 2026-04-13</summary>

## Milestone v1.7.0 — Backend API for Frontend Redesign ✅ COMPLETE

**Goal:** Add 4 backend endpoints required by frontend redesign v2.1.0.

| # | Phase | Goal | Requirements | Status |
|---|-------|------|--------------|--------|
| 20 | Similar Paddles Endpoint | Expose existing RAG `_get_similar_paddle_ids()` as API | SIM-01–03 | ✅ Complete |
| 21 | Price Alerts CRUD | Create price_alerts table + POST endpoint for modal | PRICE-01–04 | ✅ Complete |
| 22 | Affiliate Tracking | POST endpoint to log clicks to DB | AFF-01–03 | ✅ Complete |
| 23 | Quiz Profile Persistence | POST/GET endpoints for cross-device profile | QUIZ-01–03 | ✅ Complete |

### Phase 20: Similar Paddles Endpoint ✅ COMPLETE

**Goal:** Expose the existing RAG Agent method `_get_similar_paddle_ids()` as a REST API endpoint for product detail pages.

**Status:** Complete — 2026-04-07  
**Commit:** ccfd7c7

**Root causes:**
1. Frontend product detail page shows "Similar Paddles" placeholder — data exists in RAG agent but not exposed via API.
2. RAG Agent already has `_get_similar_paddle_ids()` method that returns paddle IDs for semantic similarity.
3. No endpoint exists at `/paddles/{id}/similar` despite frontend calling it.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 20.1 | `backend/app/api/paddles.py` | Add `GET /paddles/{id}/similar` endpoint. Accept `limit` query param (default 5, max 10). Call `rag_agent._get_similar_paddle_ids()` with paddle ID. Return JSON array of paddle objects (not just IDs — full paddle data including price, specs, image). |
| 20.2 | `backend/tests/test_paddles_api.py` | Add tests: (a) Existing paddle returns 200 with similar paddles array, (b) Non-existent paddle returns 404, (c) Limit param works, (d) Similar paddles have required fields (name, brand, price, specs, image_url, affiliate_url). |
| 20.3 | `backend/app/schemas.py` | Verify `PaddleSimilarResponse` schema exists (or create if missing). Must include all fields returned by endpoint. |

**Success criteria:**
1. `GET /paddles/123/similar?limit=5` returns 200 with array of paddle objects
2. Similar paddles exclude the queried paddle (no self-reference)
3. All tests pass (backend 174+)

---

### Phase 21: Price Alerts CRUD

**Goal:** Create database table and POST endpoint for price alerts modal. Users can subscribe to price drop notifications.

**Root causes:**
1. Frontend has price alerts modal UI — posts to `/price-alerts` but backend returns 404.
2. Worker `price_alert_check.py` exists but has no data to process (no alerts table).
3. No persistence mechanism for user alert subscriptions.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 21.1 | `pipeline/db/schema.sql` | Add `price_alerts` table: `id SERIAL PRIMARY KEY`, `paddle_id INT REFERENCES paddles(id)`, `target_price DECIMAL(10,2)`, `email VARCHAR(255)`, `created_at TIMESTAMP DEFAULT NOW()`, `notified_at TIMESTAMP NULL`. Add index on `paddle_id, target_price`. |
| 21.2 | `backend/app/api/price_alerts.py` (new) | Create `POST /price-alerts` endpoint. Accept JSON body: `{paddle_id, target_price, email}`. Validate email format, paddle exists, target_price > 0. Insert into `price_alerts` table. Return 201 with alert object. |
| 21.3 | `backend/app/schemas.py` | Add `PriceAlertCreate` and `PriceAlertResponse` schemas. |
| 21.4 | `backend/tests/test_price_alerts_api.py` (new) | Add tests: (a) Valid alert creates successfully, (b) Invalid email returns 422, (c) Non-existent paddle returns 404, (d) Duplicate alert (same email + paddle + price) returns 409 Conflict. |
| 21.5 | `backend/app/main.py` | Register `/price-alerts` router. |

**Success criteria:**
1. `POST /price-alerts` creates alert and returns 201
2. Duplicate alerts return 409 Conflict (not duplicate insert)
3. Worker can query table: `SELECT * FROM price_alerts WHERE notified_at IS NULL`
4. All tests pass (backend 174+)

---

### Phase 22: Affiliate Click Tracking

**Goal:** Replace frontend console.log affiliate tracking with database persistence for analytics.

**Root causes:**
1. Frontend logs affiliate clicks to console — no server-side tracking.
2. No analytics on which retailers/paddles generate most clicks.
3. Affiliate revenue optimization requires click data.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 22.1 | `pipeline/db/schema.sql` | Add `affiliate_clicks` table: `id SERIAL PRIMARY KEY`, `paddle_id INT REFERENCES paddles(id)`, `retailer_id INT REFERENCES retailers(id)`, `clicked_at TIMESTAMP DEFAULT NOW()`, `session_id VARCHAR(255)`, `user_agent TEXT`. Add index on `paddle_id, clicked_at`. |
| 22.2 | `backend/app/routers/affiliate.py` | Add `POST /api/affiliate-clicks` endpoint. Accept JSON body: `{paddle_id, retailer_id, session_id?, user_agent?}`. Insert into `affiliate_clicks`. Return 204 No Content. |
| 22.3 | `backend/tests/test_affiliate_api.py` | Add tests: (a) Valid click logs successfully, (b) Optional fields accepted, (c) Non-existent paddle returns 404, (d) Non-existent retailer returns 404. |

**Success criteria:**
1. `POST /api/affiliate-clicks` logs click to database
2. Clicks can be queried for analytics: `SELECT paddle_id, COUNT(*) FROM affiliate_clicks GROUP BY paddle_id`
3. All tests pass (backend 174+)

---

### Phase 23: Quiz Profile Persistence (Optional)

**Goal:** Persist quiz answers across devices/sessions via POST/GET endpoints.

**Root causes:**
1. Quiz answers stored in localStorage — lost on device switch.
2. No cross-device profile for returning users.
3. Chat endpoint accepts `user_profile` but frontend has no way to persist it server-side.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 23.1 | `pipeline/db/schema.sql` | Add `quiz_profiles` table: `id SERIAL PRIMARY KEY`, `profile_id VARCHAR(255) UNIQUE`, `skill_level VARCHAR(50)`, `budget_brl DECIMAL(10,2)`, `style VARCHAR(50)`, `created_at TIMESTAMP DEFAULT NOW()`, `updated_at TIMESTAMP DEFAULT NOW()`. Add index on `profile_id`. |
| 23.2 | `backend/app/api/quiz.py` (new) | Create `POST /quiz/profile` endpoint (create/update) and `GET /quiz/profile/{profile_id}` endpoint (read). Accept/return JSON body matching `{skill_level, budget_brl, style}`. Return 200 with profile object. |
| 23.3 | `backend/app/schemas.py` | Add `QuizProfileRequest` and `QuizProfileResponse` schemas. |
| 23.4 | `backend/tests/test_quiz_api.py` (new) | Add tests: (a) POST creates new profile, (b) POST updates existing profile, (c) GET returns profile or 404, (d) Invalid skill_level returns 422. |
| 23.5 | `backend/app/main.py` | Register `/quiz` router. |

**Success criteria:**
1. `POST /quiz/profile` creates/updates profile and returns 200
2. `GET /quiz/profile/{profile_id}` returns profile or 404
3. Profile persists across sessions/devices
4. All tests pass (backend 174+)

---

</details>

<details>
<summary>✅ v2.2.0 — Launch Readiness: Testes & Correções Críticas (Phases 24-27) — SHIPPED 2026-04-13</summary>

## Milestone v2.2.0 — Launch Readiness: Testes & Correções Críticas ✅ COMPLETE

**Goal:** Corrigir todos os problemas críticos de qualidade identificados no relatório de launch readiness de 12/04/2026.

**Status:** ✅ Complete — Branch: `feat/v2.2.0-launch-readiness`

| # | Phase | Goal | Priority | Est. Effort |
|---|-------|------|----------|-------------|
| 24 | Fix Pipeline Tests | 2/2 | ⏳ Executing |
| 25 | Fix Frontend Test Failures | Corrigir quiz imports + session upgrade mocks | ✅ Complete | 2026-04-12 |
| 26 | Playwright E2E Tests | Configurar Playwright + specs para fluxos críticos | ⏳ Executing | 2026-04-12 |
| 27 | Backend Deprecation Fixes | Corrigir `datetime.utcnow()` + small cleanups | ✅ Complete | 2026-04-12 |

### Phase 24: Fix Pipeline Tests — Recriar Fixtures

**Goal:** Restaurar diretório `pipeline/tests/fixtures/mock_responses/` com arquivos JSON válidos para desbloquear todos os 130 testes do pipeline de scraping.

**Root causes:**
1. O pull do master removeu os arquivos de mock responses (`brazil_store_response.json`, `dropshot_brasil_response.json`, `mercado_livre_response.json`) e o diretório `pipeline/tests/fixtures/`.
2. `test_data_integrity.py` faz `load_mock_response("brazil_store_response.json")` no module-level, causando `FileNotFoundError` que bloqueia a coleção de TODOS os 130 testes.
3. Sem pipeline tests, zero visibilidade na integridade dos crawlers (Brazil Store, Dropshot Brasil, Mercado Livre).

**Plans:** 2/2 plans complete

Plans:
- [x] 24-01-PLAN.md — Create 3 mock response fixture JSON files (Brazil Store, Dropshot, Mercado Livre)
- [x] 24-02-PLAN.md — Create staging_config.yaml + validate full test suite collects and passes

**Success criteria:**
1. `cd pipeline && pytest --co -q` coleta 130 testes sem erros
2. Todos os testes passam (ou falhas são bugs reais, não problemas de fixture)
3. Coverage de crawlers ≥ 80%

---

### Phase 25: Fix Frontend Test Failures

**Goal:** Corrigir as 3 falhas de teste do frontend: suite de quiz quebrada (imports de componentes inexistentes) + session upgrade (Clerk auth mock).

**Root causes:**
1. `quiz-flow.tsx` importa `./step-level`, `./step-style`, `./step-budget` — estes componentes foram deletados no redesign v2.1.0 mas o import ficou.
2. `session-upgrade.test.ts` não faz mock de `getAuthToken()` do Clerk, causando "Not authenticated" onde deveria testar a migração.
3. O build do Next.js passa porque o tree-shaking remove imports não utilizados, mas vitest carrega tudo.

**Plans:** 1 plan

Plans:
- [ ] 25-01-PLAN.md — Fix quiz suite (dead code removal + test rewrite) + session-upgrade auth mock

**Success criteria:**
1. `npx vitest run` — 19 suites, 0 falhas
2. Quiz suite carrega e executa testes
3. Session upgrade tests passam com Clerk auth mockado
4. Build continua passando (`next build` sem erros)

---

### Phase 26: Playwright E2E Tests — Fluxos Críticos

**Goal:** Configurar Playwright e implementar testes E2E para os fluxos de usuário mais críticos do produto. Zero → cobertura básica de navegação.

**Root causes:**
1. Zero testes E2E existem — `@playwright/test` v1.58.2 instalado mas sem config nem specs.
2. Browsers Playwright instalados (chromium-1208) mas sem utilização.
3. Sem validação de fluxos reais: navegação, chat, quiz, catálogo, comparação, afiliados.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 26.1 | `frontend/playwright.config.ts` (novo) | Configurar Playwright: baseURL localhost:3000, chromium only, timeout 30s, retries 0, screenshot on failure |
| 26.2 | `frontend/e2e/navigation.spec.ts` (novo) | Testar navegação entre páginas: Home → Catalog → Product Detail → Chat → Quiz → Compare |
| 26.3 | `frontend/e2e/catalog.spec.ts` (novo) | Testar catálogo: página carrega, filtros funcionam, ordenação funciona, grid/table toggle funciona |
| 26.4 | `frontend/e2e/quiz.spec.ts` (novo) | Testar quiz: seleção de opções, progresso, resultado de recomendação |
| 26.5 | `frontend/e2e/chat.spec.ts` (novo) | Testar chat: envio de mensagem, resposta streaming, cards de produto |
| 26.6 | `frontend/package.json` | Adicionar script `"test:e2e": "playwright test"` |
| 26.7 | `frontend/` | Executar testes E2E contra `npm run dev` e validar que todos passam |

**Success criteria:**
1. `playwright.config.ts` configurado e funcional
2. ≥ 5 spec files com ≥ 15 testes E2E
3. Fluxos críticos testados: navegação, catálogo, quiz, chat
4. Todos os testes E2E passam contra dev server
5. Adicionar `test:e2e` ao CI (opcional para esta phase)

---

### Phase 27: Backend Deprecation Fixes & Cleanup

**Goal:** Corrigir warnings de deprecation e pequenos cleanups no backend.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 27.1 | `backend/app/api/health.py` | Substituir `datetime.utcnow()` por `datetime.now(timezone.utc)` |
| 27.2 | `backend/` | Validar que 183/183 testes passam sem warnings |

**Success criteria:**
1. Zero deprecation warnings no pytest output
2. 183/183 backend tests passando

---

**Launch Readiness Scorecard (pós-milestone target):**

| Dimensão | Score Atual | Meta |
|----------|-------------|------|
| Backend Stability | 9/10 | 9/10 |
| Frontend Stability | 6/10 | 9/10 |
| Pipeline Health | 0/10 | 8/10 |
| E2E Coverage | 0/10 | 7/10 |
| Build Integrity | 10/10 | 10/10 |
| Production Readiness | 5/10 | 8/10 |
| **Média** | **5.0/10** | **8.5/10** |

</details>

---

## Milestone v2.4.0 — Site Quality & UX Polish ✅ COMPLETE

*Created: 2026-04-20*
*Source: SITE-INSPECTION-REPORT.md — 27 findings across 80+ files*

**Goal:** Transform site from "functional beta" to "polished, trustworthy product." Fix 3 critical bugs, close 12 high-priority UX gaps, implement SEO fundamentals, and polish landing page for organic traffic.

**Requirements:** See `.planning/REQUIREMENTS.md`

### Phase 28: Critical Bug Fixes & Language Fix

**Goal:** Fix all broken pages and the lang attribute. Stop the bleeding.

| Task | File(s) | Description |
|------|---------|-------------|
| 28.1 | `frontend/src/app/gift/page.tsx`, `frontend/src/app/quiz/results/page.tsx` | Replace all `wg-*` legacy CSS classes with current Tailwind/shadcn equivalents. Update Gift page to use dark theme. |
| 28.2 | `frontend/src/app/layout.tsx` | Change `<html lang="en">` to `<html lang="pt-BR">`. Update all metadata to Portuguese. |
| 28.3 | `frontend/src/lib/quiz-profile.ts`, `frontend/src/lib/profile.ts` | Unify to single profile storage module. Update quiz and results pages to use same source. |
| 28.4 | `frontend/src/components/ui/product-card.tsx` | Change "Details" → "Detalhes". Scan all components for remaining English strings. |

**Success criteria:**
1. Gift page renders correctly with dark theme styling
2. Quiz results page renders correctly with dark theme styling
3. `<html lang="pt-BR">` confirmed via browser devtools
4. Quiz → Results flow works end-to-end without redirect loop
5. Zero English strings in user-facing UI
6. All existing tests still pass (179 frontend, 23 E2E)

**Plans:** 3 plans (Wave 1 — all parallel)

Plans:
- [ ] 28-01-PLAN.md — Fix Gift pages dark theme migration (FR-01)
- [ ] 28-02-PLAN.md — Fix Quiz Results + Layout lang + Profile storage (FR-01, FR-02, FR-03)
- [ ] 28-03-PLAN.md — Fix English strings in UI (FR-14)

---

### Phase 29: Core UX — Search, Chat, Pagination, Nav

**Goal:** Close the most impactful UX gaps that block users from finding and comparing paddles.

| Task | File(s) | Description |
|------|---------|-------------|
| 29.1 | `frontend/src/app/catalog/page.tsx` | Add search input to catalog header. Client-side filtering by name + brand. URL sync `?q=`. Clear button. |
| 29.2 | `frontend/src/app/chat/page.tsx` | Allow chat without quiz. Use generic "all-purpose" profile when no quiz completed. Show quiz suggestion card. Remove quiz redirect. |
| 29.3 | `frontend/src/app/catalog/page.tsx` | Add "Mostrando X de Y raquetes" result count above grid. Dynamic updates. |
| 29.4 | `frontend/src/app/catalog/page.tsx` | Replace `limit: 200` with pagination: 24 per page, page-based, URL sync `?page=`. |
| 29.5 | `frontend/src/components/layout/header.tsx` | Add "Presente" and "Blog" to nav links array. Verify mobile nav shows them. |

**Plans:** 2 plans

Plans:
- [ ] 29-01-PLAN.md — Add search, result count, and pagination to catalog page (FR-04, FR-06, FR-07)
- [ ] 29-02-PLAN.md — Allow chat without quiz + add Presente/Blog to nav (FR-05, FR-08)

**Success criteria:**
1. User can search "Selkirk" in catalog and see filtered results
2. User can open `/chat` without completing quiz first
3. Result count visible and updates with filters
4. Catalog paginated at 24 per page with Previous/Next
5. "Presente" and "Blog" visible in header nav

---

### Phase 30: Conversion — Landing, SEO, Footer, Design System

**Goal:** Improve first impression, search engine discoverability, and trust signals.

| Task | File(s) | Description |
|------|---------|-------------|
| 30.1 | `frontend/src/components/home/landing-client.tsx` | Overhaul: alternating section backgrounds (base/surface/elevated), scroll-triggered fade-in animations via IntersectionObserver, real stats from API, sentence-case buttons. |
| 30.2 | `frontend/src/app/catalog/[slug]/page.tsx`, `frontend/src/app/page.tsx` | Add JSON-LD Product schema on detail pages, Organization schema on homepage. |
| 30.3 | `frontend/src/app/sitemap.ts` (new), `frontend/src/app/robots.ts` (new) | Create sitemap.xml and robots.txt via Next.js App Router conventions. |
| 30.4 | `frontend/src/components/layout/footer.tsx` | Expand to 4 columns: Product, Content, Legal, Social. Add Gift, Blog, social links. |
| 30.5 | `DESIGN.md` | Update to match current dark-theme implementation. Fix font references, color palette, component specs. Remove "light-first" references. |
| 30.6 | `frontend/src/components/ui/price-alert-modal.tsx`, product cards | Connect Bell icon to price alert modal. Ensure modal creates alert via POST /api/v1/price-alerts. Toast feedback. |

**Success criteria:**
1. Landing page has ≥3 distinct section backgrounds
2. Scroll animations fire on sections entering viewport
3. Stats show real paddle count from API
4. Buttons use sentence case (not ALL CAPS)
5. JSON-LD validates via Google Rich Results Test
6. `/sitemap.xml` returns valid XML with all routes
7. Footer has 12+ links in 4 columns
8. DESIGN.md matches implementation with zero contradictions
9. Price alert Bell icon opens working modal

---

### Phase 31: Polish — Compare 3-4, Breadcrumbs, Error Boundaries

**Goal:** Final polish pass for production-quality feel.

| Task | File(s) | Description |
|------|---------|-------------|
| 31.1 | `frontend/src/app/compare/page.tsx`, `frontend/src/components/ui/compare-row.tsx` | Allow up to 4 paddles. Responsive layout (2/3/4 col). URL sync `?a=1&b=2&c=3`. |
| 31.2 | `frontend/src/app/catalog/[slug]/page.tsx`, compare page | Add breadcrumb navigation. Use JSON-LD BreadcrumbList. |
| 31.3 | `frontend/src/app/error.tsx` (new), `frontend/src/app/not-found.tsx` (new) | Custom error and 404 pages matching site design. "Voltar ao catálogo" CTAs. |
| 31.4 | `frontend/src/app/catalog/[slug]/page.tsx` | Alternating row backgrounds in specs table. Better visual scanning. |
| 31.5 | `frontend/src/app/layout.tsx` | Add skip-to-content link visible on focus. Global, not just landing page. |

**Success criteria:**
1. Compare page supports 2-4 paddles
2. Breadcrumbs visible on product detail and compare pages
3. Custom 404 page renders with site design
4. Error boundary catches and displays friendly message
5. Skip link visible on Tab focus from any page

**Plans:** 3 plans (Wave 1→2)

Plans:
- [ ] 31-01-PLAN.md — Compare 3-4 paddles refactor
- [ ] 31-02-PLAN.md — Breadcrumbs + alternating rows
- [ ] 31-03-PLAN.md — Error pages + skip link

---

## Planned Milestones (from INSPECTION-REPORT.md)

*Source: INSPECTION-REPORT.md — Deep architectural inspection (22 Abr 2026)*
*These milestones address findings NOT covered by v2.4.0 (which focused on visual/UX issues from SITE-INSPECTION-REPORT.md)*

### v2.5.0 — Backend Hardening & RAG Reliability

*Created: 2026-04-22*
*Goal: Fix critical production risks — fake cache, zero auth, fragile RAG pipeline. Make backend production-grade.*

| Phase | Goal | Findings | Status |
|-------|------|----------|--------|
| 32 | Production Cache & Backend Auth | B1 🔴, B2 🔴 | ✅ Complete |
| 33 | RAG Pipeline Reliability | B3 🟡, B4 🟡, B5 🟡 | ✅ Complete |
| 34 | Backend Hygiene & Config Cleanup | B6 🟡, B7 🟡, B8 🟢 | ✅ Complete |

### Phase 33: RAG Pipeline Reliability

**Goal:** Fix the 3 issues that can silently degrade or break AI recommendations.

**Root causes:**
1. `eval_gate.py` returns hardcoded scores `[4.5, 4.3, 4.1...]` — no actual LLM evaluation happens. Quality of AI responses is unmeasured.
2. If both Jina AI and HuggingFace fail, `EmbeddingManager` returns a 768-dimensional zero vector. pgvector cosine similarity with zero vectors returns arbitrary results.
3. Groq LLM timeout is 8 seconds — prompts with 3+ paddle recommendations + user profile can exceed this, causing degraded template responses.

**Plans:** 2 plans (Wave 1→2)

Plans:
- [x] 33-01-PLAN.md — Fix embedding fallback (raise error, not zero vector) + increase LLM timeout to 15s (B4, B5) ✅
- [x] 33-02-PLAN.md — Replace eval_gate mock with real quality metrics + RAG response logging (B3) ✅

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 33.1 | `backend/app/agents/eval_gate.py` | Replace hardcoded scores with real evaluation: log prompt + response pairs, compute basic quality metrics (response length, has_price_mention, has_brand_mention). Store results in `eval_results` table. Not a full LLM-as-judge — that's v1.5.1. |
| 33.2 | `backend/app/services/embedding.py` (or equivalent) | Replace zero-vector fallback with explicit error handling: if all embedding providers fail, return HTTP 503 from chat endpoint with message "Serviço temporariamente indisponível". Never silently return garbage results. |
| 33.3 | `backend/app/agents/rag_agent.py` | Increase LLM timeout from 8s to 15s. Add streaming-aware timeout (Groq streams tokens — first token timeout vs total timeout). Log timeout events to Telegram via existing alert middleware. |
| 33.4 | `backend/app/agents/rag_agent.py` | Add response quality logging: log prompt length, response length, paddle IDs returned, latency_ms. Feed into eval_gate metrics. |
| 33.5 | `backend/tests/` | Add tests: (a) Embedding failure returns 503 not zero vector, (b) LLM timeout triggers degraded response (not crash), (c) eval_gate logs real metrics, (d) Timeout increased to 15s verified. |

**Success criteria:**
1. Zero vector never returned from embedding service
2. Embedding failure → 503 response, not random results
3. LLM timeout is 15s with streaming awareness
4. eval_gate logs actual quality metrics (not hardcoded)
5. All existing tests pass

---

### Phase 34: Backend Hygiene & Config Cleanup

**Goal:** Fix medium/low backend hygiene issues that accumulate tech debt.

**Plans:** 1 plan (Wave 1)

Plans:
- [ ] 34-01-PLAN.md — Move pytest-asyncio to dev extras, fix version from VERSION file, add CORS validation (B6, B7, B8)

**Success criteria:**
1. `pytest-asyncio` not in production dependencies
2. FastAPI version matches `VERSION` file
3. CORS config validated on startup
4. All existing tests pass

---

### v2.6.0 — Pipeline & Infra Hardening

*Created: 2026-04-22*
*Goal: Make data pipeline reliable and infrastructure secure. Auto-refresh MV, expand retailers, harden security headers.*

| Phase | Goal | Findings | Status |
|-------|------|----------|--------|
| 35 | Pipeline Reliability | P1 🟡, P3 🟡, P4 🟡 | ✅ Complete |
| 36 | Retailer Expansion Foundation | P2 🟡, P5 🟢 | ✅ Complete |
| 37 | Security & Infra Hardening | I1 🟡, I2 🟡, I3 🟡, F7 🟡 | ✅ Complete |

### Phase 35: Pipeline Reliability

**Goal:** Auto-refresh materialized view, process `needs_reembed` flag, add versioned migrations.

**Root causes:**
1. `latest_prices` materialized view requires manual `REFRESH` after every crawler run. If forgotten, product pages show stale prices.
2. `paddles.needs_reembed` column exists but no worker reads it. Changed paddles never get re-embedded.
3. All schema changes go in a single `schema.sql` file. No migration history, no rollback capability.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 35.1 | `.github/workflows/scraper.yml` | Add `REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices` as final step after all crawlers complete. Single step, runs after the 3 sequential crawlers. |
| 35.2 | `pipeline/` or `backend/workers/` | Create `reembed_worker.py`: query `SELECT id FROM paddles WHERE needs_reembed = TRUE LIMIT 50`, generate embeddings via Jina/HF, update `paddle_embeddings`, set `needs_reembed = FALSE`. Add as manual-trigger GitHub Actions workflow (not cron — run on-demand). |
| 35.3 | `pipeline/db/` | Create `migrations/` directory with numbered SQL files (`001_initial.sql`, `002_price_alerts.sql`, etc.). Extract existing schema.sql into initial migration. Create `run_migrations.py` script that applies pending migrations with a `schema_migrations` tracking table. |
| 35.4 | `pipeline/tests/` | Add tests: (a) MV refresh completes without error, (b) reembed worker processes flagged paddles, (c) migration runner applies pending migrations, (d) migration runner skips already-applied migrations. |

**Success criteria:**
1. `latest_prices` MV auto-refreshes after every crawler run
2. `needs_reembed` flag has a consumer that processes flagged paddles
3. Schema changes tracked in numbered migrations
4. All existing pipeline tests pass

---

### Phase 36: Retailer Expansion Foundation

**Goal:** Prepare pipeline for additional Brazilian retailers beyond the current 3.

**Root causes:**
1. Only Brazil Store, Dropshot, and JOOLA are scraped. Brazilian pickleball market has dozens of retailers.
2. `review_queue` only logs uncertain duplicates — never blocks them. Conservative but risks duplicate paddles in catalog.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 36.1 | `pipeline/crawlers/` | Create crawler template/abstract base class with shared logic: retry with tenacity, dedup integration, price snapshot insert, error logging. Make existing 3 crawlers use it. |
| 36.2 | `pipeline/db/schema.sql` | Add `retailers.is_active` column. Document process for adding new retailers (INSERT into retailers table + create crawler class). |
| 36.3 | `pipeline/dedup/` | Improve review_queue handling: add `review_status` column (pending/auto-approved/manually-reviewed). Add CLI command `python -m pipeline.dedup.review` to list pending items. Keep conservative (don't auto-block). |
| 36.4 | `pipeline/tests/` | Add tests: (a) New crawler can be added by extending base class, (b) Review queue tracks status correctly, (c) `is_active` flag filters inactive retailers. |

**Success criteria:**
1. Crawler base class abstracts shared retry/dedup/insert logic
2. New retailer = extend base class + INSERT into retailers table
3. Review queue has status tracking (not just log-only)
4. All existing pipeline tests pass

---

### Phase 37: Security & Infra Hardening

**Goal:** Fix security headers, consolidate CI workflows, clean up docker-compose.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 37.1 | `frontend/vercel.json` (or root `vercel.json`) | Add security headers: Content-Security-Policy (strict for pickleiq.com), Strict-Transport-Security (max-age=31536000; includeSubDomains), Permissions-Policy (camera=(), microphone=(), geolocation=()), X-XSS-Protection. |
| 37.2 | `.github/workflows/scraper.yml` | Consolidate 3 separate cron triggers (02:00, 02:05, 02:10) into single workflow with sequential steps: crawl Brazil Store → crawl Dropshot → crawl JOOLA → refresh MV. |
| 37.3 | `docker-compose.yml` | Separate dev compose from production reference. Keep current as `docker-compose.dev.yml`. Add `docker-compose.prod.yml` with production-like configs (resource limits, health checks, restart policies). |
| 37.4 | `frontend/next.config.mjs` | Restrict `remotePatterns` from `**` wildcard to specific domains: `pickleiq.com`, `railway.app`, `supabase.co`, and retailer CDN domains. |
| 37.5 | Tests | Verify security headers present via `curl -I`. Verify scraper workflow runs as single job. Verify image loading still works with restricted domains. |

**Success criteria:**
1. Security headers include CSP, HSTS, Permissions-Policy
2. Single scraper workflow with 3 sequential steps
3. Docker compose files separated (dev vs prod reference)
4. Image remotePatterns restricted to known domains
5. All existing tests pass

---

### v2.7.0 — Build & Test Quality ✅ COMPLETE

*Created: 2026-04-22*
*Shipped: 2026-04-24*
*Goal: Make build a real quality gate. Fix test anti-patterns. Enforce coverage.*

| Phase | Goal | Findings | Status |
|-------|------|----------|--------|
| 38 | Build Quality Gates | F6 🟡, F8 🟡, F9 🟢, F3 🟡 | ✅ Complete |
| 39 | Test Suite Hardening | T1 🟡, T2 🟡, T3 🟡, T4 🟡, T5 🟢 | ✅ Complete |

### Phase 38: Build Quality Gates

**Goal:** Remove build safety nets that hide errors. Fix TypeScript/ESLint bypasses.

**Root causes:**
1. `next.config.mjs` has `ignoreBuildErrors: true` — TypeScript errors pass silently into production.
2. `next.config.mjs` has `eslint: ignoreDuringBuilds: true` — lint issues never caught in CI.
3. `tailwind.config.ts` has `darkMode: ["class"]` but app is dark-only — unnecessary config.
4. Almost all pages are CSR — only `/catalog/[slug]` is SSR. SEO impact on landing, quiz, chat pages.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 38.1 | `frontend/next.config.mjs` | Remove `ignoreBuildErrors: true`. Fix all TypeScript errors that surface. Run `next build` and fix each error. |
| 38.2 | `frontend/next.config.mjs` | Remove `eslint: ignoreDuringBuilds: true`. Fix all ESLint errors that surface. |
| 38.3 | `frontend/tailwind.config.ts` | Remove `darkMode: ["class"]` since theme is dark-only. If dark mode toggle is planned for future, keep but document. |
| 38.4 | `frontend/src/app/page.tsx`, `frontend/src/app/catalog/page.tsx` | Evaluate SSR migration for landing page and catalog listing. At minimum: add `generateMetadata()` for SEO. Full SSR is stretch goal. |
| 38.5 | `frontend/` | Run `next build` and `next lint` — both must pass with zero errors. |
| 38.6 | `frontend/src/tests/` | Add tests for any new components created during TS/lint fixes. |

**Success criteria:**
1. `next build` passes with zero TypeScript errors (no `ignoreBuildErrors`)
2. `next lint` passes with zero errors (no `ignoreDuringBuilds`)
3. `darkMode` config matches actual usage (dark-only or documented toggle plan)
4. Landing page has `generateMetadata()` for SEO at minimum
5. All existing frontend tests pass

---

### Phase 39: Test Suite Hardening

**Goal:** Fix test anti-patterns — fake E2E, ambiguous assertions, mock-only eval tests, conftest conflicts.

**Tasks:**

| Task | File(s) | Description |
|------|---------|-------------|
| 39.1 | `backend/tests/test_e2e_embeddings.py` | Rename to `test_embeddings_integration.py` (not E2E). Document that it uses mocked httpx, not real APIs. Add real E2E embedding test as separate file (optional, needs API keys). |
| 39.2 | `backend/tests/` | Search for `assert response.status_code in [200, 404]` patterns. Replace with explicit assertions: if both are valid, test both paths separately. If 404 is expected, assert 404 only. |
| 39.3 | `backend/tests/test_price_alerts.py` | Remove standalone conftest.py that conflicts with global `backend/tests/conftest.py`. Use autouse fixtures from global conftest. |
| 39.4 | `backend/tests/test_eval_gate.py` | Update tests to validate actual eval metrics (after Phase 33 changes), not hardcoded score serialization. |
| 39.5 | `backend/pyproject.toml` | Add `fail_under = 80` to `[tool.pytest.ini_options]` or `[tool.coverage.run]`. Enforce 80% coverage threshold in CI. |
| 39.6 | `backend/tests/` | Run full test suite: all pass, zero ambiguous assertions, zero conftest conflicts. |

**Success criteria:**
1. No test file named `test_e2e_*` that uses only mocks
2. Zero `status_code in [200, 404]` patterns
3. Single conftest.py per test directory (no conflicting fixtures)
4. eval_gate tests validate real metrics
5. Coverage threshold enforced (`fail_under = 80`)
6. All tests pass

---

## Deferred Milestones (Planned, Not Started)

### v1.5.0 — Production Readiness

**Goal:** Provision production infrastructure, deploy to Railway + Vercel + Supabase.

| # | Phase | Goal |
|---|-------|------|
| 15 | Production Deploy | Provision infra, deploy, health checks, embedding fallback |

See existing v1.5 roadmap for full details.

### v1.5.1 — Monitoring & Resilience

| Task | Description | Priority |
|------|-------------|----------|
| T5 | Load test /chat with k6 (50 concurrent, p95 <2s) | P1 |
| T2 | Eval gate as monthly CI job (real LLM calls, results DB) | P1 |
| Enhanced embedding fallback | Sticky sessions, performance tuning, dimension monitoring | P1 |
| Grafana/scrape dashboard | Scrape success rates, embedding latency, error rates | P2 |
| T7 | Firecrawl self-hosted runbook (document decision, may punt) | P2 |

### v1.5.2 — Legal & Compliance

| Task | Description | Priority |
|------|-------------|----------|
| T3 | Legal review of BR retailer scraping | P1 (external) |
| LGPD compliance audit | Data residency, privacy policy, cookie consent | P1 (external) |
| Privacy policy + Terms | Legal docs for BR market | P1 (external) |
| Affiliate disclosure | Required by BR consumer law | P1 (external) |

---
*Roadmap created: 2026-04-05*
*Last updated: 2026-04-24 — v2.7.0 shipped (Phases 38-39 complete)*
