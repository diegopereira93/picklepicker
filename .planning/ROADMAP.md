# Roadmap: PickleIQ

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

## Milestone v1.6.0 — UI Redesign (Design Review Implementation)

**Goal:** Implement the winning design variants from the 9-variant design review (2026-04-05). Redesign Home, Catalog, and Chat screens to maximize funnel conversion.

**Design review source:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/`

**Winning combination:**
- Home: C (Quiz-Forward) + data stats from A
- Catalog: A (Comparison Table) + product images from B + grid toggle
- Chat: B (Sidebar Companion) + card responses from C

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 16 | DESIGN.md v3.0 + Foundation | Update design system with 6 proposed changes, add chat/widget sections | DS-01–05 | All new tokens defined, new sections documented |
| 17 | Home-C Quiz-Forward | Quiz widget above-the-fold, data stats, feature steps | HOME-01–05 | Quiz completes → recommendation card shows → "Ver detalhes" works |
| 18 | Chat-B Sidebar Companion | Split-panel layout, card responses, product sidebar | CHAT-01–06 | Buy button visible during chat, card responses render |
| 19 | Catalog-A Comparison Table | Sortable table, visual grid toggle, score badges | CAT-01–06, COH-01–04, QA-01–06 | Table sorts, toggle works, responsive passes |

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

## Milestone v1.7.0 — Backend API for Frontend Redesign

**Goal:** Add 4 backend endpoints required by frontend redesign v2.1.0. Support similar paddles on product detail, price alerts modal, affiliate click tracking, and quiz profile persistence.

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 20 | Similar Paddles Endpoint | Expose existing RAG `_get_similar_paddle_ids()` as API | SIM-01–03 | 3 |
| 21 | Price Alerts CRUD | Create price_alerts table + POST endpoint for modal | PRICE-01–04 | 4 |
| 22 | Affiliate Tracking | POST endpoint to log clicks to DB | AFF-01–03 | 3 |
| 23 | Quiz Profile Persistence | POST/GET endpoints for cross-device profile | QUIZ-01–03 | 3 |

### Phase 20: Similar Paddles Endpoint

**Goal:** Expose the existing RAG Agent method `_get_similar_paddle_ids()` as a REST API endpoint for product detail pages.

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
*Last updated: 2026-04-05 — v1.6.0 UI Redesign phases 16-19 added*
