# Changelog

All notable changes to this project will be documented in this file.

## [0.2.2.0] - 2026-03-28

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
