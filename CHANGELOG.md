# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0.1] - 2026-04-03

### Changed
- **Workflow Migration** — Migrated from GSD/gstack to native oh-my-openagent (omo) workflow. Updated CLAUDE.md with omo agent delegation, categories, and subagent configuration.
- **CLAUDE.md Rewritten** — Replaced all gstack/GSD references with omo-native workflow: project overview, agent delegation table, subagent descriptions, command table, design system section.

### Removed
- **GSD Planning Artifacts** — Deleted entire `.planning/` directory (100+ files across milestones, phases, research, archives, quick tasks, memory backups, optimization plans).
- **Old Tooling Directories** — Removed `.gstack/`, `.claire/`, `.clone/` directories.
- **Debug/Temp Files** — Removed `debug-catalog.mjs`, `debug-catalog.playwright.ts`, `debug-paddles.png`, `test_firecrawl.py`, `run-e2e-test.sh`, `conftest.py`, UAT screenshots.
- **Cache/Build Artifacts** — Removed `playwright_chromiumdev_profile-*`, `playwright-artifacts-*`, `tsx-1000/`, `v8-compile-cache-1000/`, `node-jiti/`, `__pycache__/`, `pickleiq_pipeline.egg-info/`, `test-results/`.
- **Orphan Playwright Configs** — Removed root-level and frontend-level debug `playwright.config.ts`.

### Fixed
- **`.gitignore` Rewritten** — Comprehensive patterns for Python, Node, testing, Playwright, build artifacts, GSD/planning, Claude/Omo configs, OS files, debug files.

---

## [1.3.0.0] - 2026-04-02

### Added
- **Phase 13: Hybrid UI Redesign** — Modern sports tech design system with lime accent, data credibility styling
- **Hybrid Design System** — Instrument Sans (display), Inter (body), JetBrains Mono (data/specs), 2px border radius, dark/light section alternation
- **Color System** — Lime (#84CC16) for primary actions on dark, Green (#76b900) for data elements, semantic colors
- **Typography via Google Fonts CDN** — Preconnect hints for performance, proper font stack cascade
- **Component Restyling** — Button variants with lime borders, card components with hy-* classes, navigation with lime "IQ" accent
- **Class Migration** — Complete nv-* → hy-* prefix migration with CSS aliases for backwards compatibility

### Changed
- **Button Borders** — Primary action borders now use lime (#84CC16) instead of data-green (#76b900)
- **Navigation Logo** — "PickleIQ" with lime accent on "IQ" portion
- **Typography Loading** — Google Fonts CDN replaces inline NVIDIA-EMEA font override
- **CSS Architecture** — hy-* class prefix throughout, nv-* aliases maintained for migration period
- **Lighthouse CI Configuration** — Added `startServerCommand` to properly start Next.js production server before audits
- **SSG Error Handling** — Added graceful fallbacks when backend is unavailable during static generation

### Fixed
- **HY-01** — Google Fonts loaded for Hybrid typography (Instrument Sans, Inter, JetBrains Mono)
- **HY-04** — Button borders use sport-primary lime, not data-green
- **HY-06** — Navigation logo has lime accent on "IQ" portion
- **HY-11** — All components use hy-* class prefix
- Lighthouse CI failing with CHROME_INTERSTITIAL_ERROR due to missing dev server startup
- SSG build failures when backend services are unavailable

---

## [1.2.0.0] - 2026-04-01

### Added
- **Phase 11: Core Web Vitals Optimization** — Performance and accessibility compliance
- **Image Optimization** — All images migrated to next/Image with responsive sizes, priority loading, WebP/AVIF
- **Font & Script Optimization** — Font loading optimized with display swap and adjustFontFallback
- **Layout Stability** — Skeleton placeholders with Suspense, min-height containers prevent CLS
- **RUM & A11Y** — Vercel Speed Insights with dynamic import, Lighthouse CI with strict budgets, WCAG 2.1 AA compliance

---

## [1.1.0.0] - 2026-04-01

### Added
- **Phase 12: Data Pipeline Quality** — Comprehensive data quality infrastructure for the paddle catalog pipeline
- **Data Quality Metrics Tracking** — Pipeline success rate, extraction coverage, price currency consistency, image availability, and store distribution analytics
- **Dead Letter Queue (DLQ)** — Failed extraction handling with retry logic, exponential backoff, and comprehensive logging
- **Data Freshness Monitoring** — Automated freshness checks, configurable TTL per store, alerting for stale data
- **Pipeline Observability** — Structured logging, performance metrics, and extraction telemetry

## [1.1.0.0] - 2026-04-01

### Added
- **Milestone v1.1 Complete** — Scraper Validation, Navigation UX Fixes, and Image Extraction
- **Phase 07: E2E Testing & Scraper Validation** — 101 tests covering all 3 scrapers (Brazil Pickleball Store, Drop Shot Brasil, Mercado Livre), 94% code coverage on ML scraper, Firecrawl error handling documented
- **Phase 08: Navigation UX Fixes** — Fixed /compare 404 links, removed Chat IA standalone nav, enforced quiz gate, mobile nav consistency, enriched paddle data with specs/skill_level/in_stock
- **Phase 09: Image Extraction** — Two-phase Brazil Store crawler extracting real product images from individual pages, URL transformation (1024→480px), 6% → 80% real image coverage

### Changed
- **Crawler infrastructure** — Added `extract_image_from_markdown()` and `scrape_product_page()` helpers to Brazil Store crawler
- **Catalog data** — Enriched 10+ paddles with technical specs, skill levels, and real images
- **Test framework** — Added pytest-asyncio, pytest-cov, RapidFuzz for E2E scraper validation

## [1.0.0.0] - 2026-03-31

### Added
- **MVP v1.0 Complete** — Full PickleIQ platform with 6 phases delivered
- **Phase 1: Foundation** — PostgreSQL + pgvector schema, Docker Compose, Supabase staging
- **Phase 2: Data Pipeline** — Firecrawl scrapers for Brazil Pickleball Store, Drop Shot, Mercado Livre; deduplication, embeddings
- **Phase 3: RAG Agent** — Claude Sonnet via Groq eval gate, streaming SSE chat, <3s P95 latency, Redis cache
- **Phase 4: Frontend** — Next.js 14, quiz onboarding, chat widget, paddle comparator, admin panel
- **Phase 5: SEO & Growth** — SSR product pages, Clerk auth, price alerts, Resend emails, price history graphs
- **Phase 6: Launch** — Vercel + Railway + Supabase production, CI/CD, Langfuse observability
- **Phase 7: E2E Testing** — 101 tests across 3 scrapers with ≥80% coverage
- **Phase 8: Navigation UX** — Fixed /compare 404s, enriched catalog cards with skill_level/specs/in_stock

### Changed
- Navigation: Header shows only Home + Catalogo + "Encontrar raquete" CTA; mobile matches desktop
- Catalog: Cards display skill level badges, swingweight/core specs, stock indicators
- Database: Enriched paddle data with 10+ paddles including specs

## [0.2.4.0] - 2026-03-29

### Fixed
- Navigation: removed dead `/compare` links from header, footer, and blog — all point to `/paddles`
- Navigation: removed "Chat IA" as a standalone header nav item (was bypassing quiz gate)
- Catalog cards: `fetchProductData` returns `null` on error instead of throwing; numeric ID fallback prevents 404 when `model_slug` is null
- Backend: registered `price_history` router in `main.py` (endpoint was implemented but not mounted)
- Backend: defensive `.get()` access on paddle dicts prevents 500 errors in test/mock environments
- Backend: `PaddleResponse.created_at` made Optional to match real DB nullability

### Added
- Catalog cards: skill level badge, SW/Core specs row, and in-stock indicator on `/paddles` page

### Changed
- Home page hero CTA now links to `/paddles` ("Ver catalogo") instead of dead `/compare`
- Test: `fetchProductData` test updated to expect `null` on error (not throw)
- Tests: price alert worker mock fixed to provide correct number of `side_effect` values

## [0.2.3.0] - 2026-03-28

### Added
- Phase 6 (Launch & Deploy): Production infrastructure, CI/CD pipelines, observability, and beta launch
- Vercel frontend deployment with Next.js 14, Clerk auth, and security headers
- Railway backend deployment with FastAPI, Redis cache, and Langfuse tracing
- GitHub Actions CI/CD workflows: test gate, automatic deployment to Railway and Vercel
- Comprehensive observability: structured logging, Telegram alerts, health endpoints
- Admin panel (/admin/queue for review queue, /admin/catalog for paddle CRUD) protected by ADMIN_SECRET
- 230 files added/modified: 45,716 insertions, full pipeline from phase 1-6

### Changed
- Frontend builds now require Clerk env vars in Vercel config
- .npmrc configured with legacy-peer-deps for Clerk+Next.js compatibility
- Environmental configuration standardized across Railway (backend) and Vercel (frontend)

### Fixed
- Clerk downgrade from v7 to v6.39.1 for Next.js 14 compatibility
- ESLint/TypeScript build errors resolved
- Vercel output configuration for production deployment


### Added
- **Phase 5: SEO & Growth Features** — Complete product discovery & monetization platform
- Clerk v5 authentication: Protected endpoints, anon→registered migration, profile upgrade flow
- Product pages with SEO: Server Components, dynamic metadata, Schema.org JSON-LD, ISR (3600s) + on-demand revalidation
- Price history & alerts: Percentile tracking (P20 daily), email notifications via Resend, price trend visualization with Recharts
- Blog system: Pillar pages, FTC affiliate disclosure, automated metadata generation, SEO-optimized content
- Admin panel: Review queue (duplicates, spec mismatches), inline catalog editing, FastAPI integration
- Frontend test suite: Vitest with 152 tests covering auth, API, components, integration flows
- E2E verification: 4/4 phase plans executed, comprehensive test coverage

### Changed
- Implemented Session Upgrade pattern (anon → registered user profile)
- Extended Paddle type with metadata, ratings, review counts
- Added product revalidation webhook for instant ISR updates
- Expanded admin API routes (proxy to FastAPI backend)
- Updated .planning/STATE.md and ROADMAP.md with Phase 5 completion

### Test Coverage
- Phase 5 total: 127 new tests across authentication, SEO, price tracking, and admin features
- All phases: 152 frontend tests passing, no regressions from Phase 2
- Coverage includes: Unit tests (45%), Integration tests (35%), End-to-end verification (20%)

## [0.2.1.0] - 2026-03-27

### Added
- **Phase 3: RAG Agent & AI Core** — Conversational pickleball paddle recommendations in Portuguese
- LLM evaluation gate: 10-query Portuguese evaluation selecting Groq (avg 4.25/5.0) vs Claude Sonnet fallback
- RAG agent skeleton with semantic search (pgvector cosine similarity), 3-tier filtering (stock/budget/skill_level), and top-3 recommendation ranking
- Conversational chat endpoint (POST /chat) with SSE streaming, input validation, and timeout handling (>8s degraded mode)
- Portuguese system prompt + metric translation (swingweight, twistweight → plain language) using metrics.py
- Redis caching layer (3600s TTL, deterministic MD5 key generation) with LatencyTracker for P95 <3s enforcement
- Langfuse observability integration: traces with model selection, cache hits, degraded mode flags, token counts, and latency percentiles
- End-to-end testing (E2E): happy path, cache hits, degraded mode, concurrent request handling
- Production readiness validation: error handling, input validation, header management, no Phase 2 regressions
- 89 new tests across 5 waves (eval_gate, rag_agent, prompts, chat endpoint, cache, observability, langfuse, E2E, production)

### Changed
- Updated backend/pyproject.toml with test dependencies (pytest-asyncio, httpx[http2])
- Extended backend/app/main.py with RAG chat router and Langfuse middleware
- Updated .planning/STATE.md with Phase 3 progress tracking
- Updated .planning/ROADMAP.md with Phase 3 completion and Phase 4 next

### Test Coverage
- 17 tests for Wave 1 (LLM eval gate + RAG agent skeleton)
- 8 tests for Wave 2 (prompts + metric translation)
- 11 tests for Wave 3 (chat endpoint + SSE)
- 17 tests for Wave 4 (cache + observability)
- 36 tests for Wave 5 (Langfuse integration, E2E, production)
- Phase 2 regression: 14 tests confirming no regressions
- **Total: 103 tests passing, 89 new**

## [0.1.0.0] - 2026-03-27

### Added
- Initial project setup with PickleIQ pipeline infrastructure
- Python project structure with pytest configuration
- Docker Compose setup for local development
- Environment configuration templates

### Changed
- Updated .gitignore to exclude .venv and .env files from version control


## [0.2.0.0] - 2026-03-27

### Added
- Full data pipeline crawlers: Drop Shot Brasil and Mercado Livre expansion via Firecrawl
- 3-tier SKU deduplication with RapidFuzz (title hash + fuzzy matching ≥0.85)
- Review queue system with admin API endpoints for manual dedup review
- GitHub Actions 24h schedule for crawler orchestration with exponential backoff and Telegram alerts
- Railway staging deployment with FastAPI + PostgreSQL
- pgvector embeddings (text-embedding-3-small, HNSW index) with async re-embedding pipeline
- 5 FastAPI GET endpoints: /paddles, /paddles/{id}, /paddles/{id}/prices, /paddles/{id}/latest-prices, /health
- Admin API endpoints: GET /admin/queue, PATCH /admin/resolve, PATCH /admin/dismiss
- .env.example configuration for Phase 2 environment variables
- Dockerfile.railway for containerized FastAPI deployment on Railway
- railway.toml configuration for Railway deployment

### Changed
- Updated .gitignore to exclude Railway and plan artifacts
- Extended backend schema with async re-embedding flag (needs_reembed)
- FastAPI main.py with admin and paddles routers

### Test Coverage
- 43 tests for crawlers and deduplication (Wave 1)
- 13 tests for embeddings and FastAPI endpoints (Wave 2)
- Total: 56+ tests passing with 100% coverage of new code paths
