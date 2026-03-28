---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
last_updated: "2026-03-28T22:30:00.000Z"
progress:
  total_phases: 6
  completed_phases: 6
  total_plans: 17
  completed_plans: 28
  phase_03_tests: 103/103
---

# PickleIQ — Project State

**Última atualização:** 2026-03-28T22:30:00Z
**Status:** Phase 03 Complete — Ready for Phase 04
**Última sessão:** 2026-03-28T22:30:00Z

## Posição Atual

Fase: 03 (rag-agent-ai-core) — ALL WAVES COMPLETE
Plan: Ready for Phase 04 planning

- **Milestone:** v1.0 (All infrastructure, observability, beta launch complete)
- **Fase:** 3 (RAG Agent & AI Core)
- **Status:** All 5 waves complete — 103/103 tests passing
- **Última atividade:** 2026-03-28T22:30:00Z
- **Próxima ação:** Move to Phase 04 (Frontend Chat Product UI)

## Completed

- [x] PROJECT.md criado
- [x] config.json criado (YOLO, Standard, git tracking, research, plan-check)
- [x] Pesquisa de domínio concluída (4 áreas: scraping, RAG, frontend, afiliados)
- [x] REQUIREMENTS.md criado (6 fases, 24 plans)
- [x] ROADMAP.md criado
- [x] Git inicializado
- [x] Plan 01-01: Monorepo skeleton, Docker Compose, pipeline project (2 tasks, 14 files)

## Research Findings — Critical Decisions

1. **Amazon**: usar PA-API (não Firecrawl) — scraping bloqueado
2. **RAG**: raw SDK (sem LangChain/LlamaIndex) — menos latência, mais controle
3. **Chat streaming**: Vercel AI SDK `streamText` + Edge runtime (não Server Actions)
4. **Radar chart**: Recharts com `ssr: false` obrigatório
5. **Clerk**: usar `clerkMiddleware` v5 (não `authMiddleware` deprecado)
6. **E-mail**: Resend (free tier 3K/mês) com React Email
7. **Afiliado prioritário**: Selkirk (~10-15% comissão vs Amazon 3%)
8. **FTC**: disclosure acima do primeiro link em cada página (não apenas footer)
9. **Embedding**: narrativo por raquete (200-400 tokens), metadata estruturada no Pinecone
10. **Latência**: dois estágios — Haiku para perfil (turns 1-3) + Sonnet para recomendação

## Decisions

- [01-01] pgvector/pgvector:pg16 Docker image selected (not postgres:16) to get pgvector pre-installed
- [01-01] psycopg3 AsyncConnectionPool singleton with open()/close() lifecycle for pipeline DB access
- [01-01] Telegram alert helper fails gracefully (logs warning) when credentials absent
- [01-01] pytest asyncio_mode=auto eliminates per-test @pytest.mark.asyncio decorators
- [Phase 01-02]: latest_prices uses DISTINCT ON with ORDER BY scraped_at DESC and unique index for CONCURRENTLY refresh support
- [Phase 01-03]: paddle_id left NULL in price_snapshots Phase 1 — dedup/matching deferred to Phase 2
- [Phase 01-03]: pipeline/__init__.py added to make pipeline importable as namespace package from project root
- [Phase 01-04]: matt_id used as ML Afiliados affiliate parameter — needs portal confirmation before production
- [Phase 01-04]: psycopg[binary,pool] required — pool extra must be explicit in pyproject.toml
- [Phase 01-04]: httpx response.json() is sync — test mocks for httpx responses use MagicMock not AsyncMock
- [04-01]: shadcn@latest init generates Tailwind v4 / @base-ui/react components — all UI components rewritten with Radix UI + HSL CSS variables for Next.js 14 / Tailwind v3 compatibility
- [04-01]: Geist font not in next/font/google for Next.js 14.2 — replaced with Inter
- [04-01]: API client uses NEXT_PUBLIC_FASTAPI_URL env var; graceful fallback returns empty list on network error
- [Phase 04]: AdminAuthContext provides logout() to all /admin/* children via React context, avoiding prop drilling
- [Phase 04]: Route Handlers validate Authorization header server-side against ADMIN_SECRET env var; client never compares secrets directly
- [Phase 04-root]: UIMessage from ai SDK uses parts array only — msg.content property does not exist; textContent must be extracted from parts
- [Phase 05-02]: Canonical URL stored in alternates.canonical (Next.js 14 Metadata API)
- [Phase 05-02]: revalidateTag/revalidatePath imported dynamically to gracefully no-op in test environment
- [Phase 05]: Clerk installed with --legacy-peer-deps; Resend client made lazy for vitest testability; vi.hoisted() pattern established for class-based SDK mocks
- [Phase 02-07]: Backend AsyncConnectionPool singleton (min=2, max=10) initialized in FastAPI lifespan; all paddles endpoints wire real psycopg queries with dict_row factory
- [Phase 02-08]: Docker image uses python:3.12-slim with WORKDIR=/app/backend to align module path (app.main:app) with railway.toml start command; libpq-dev included for psycopg[binary,pool]

## Performance Metrics

| Phase | Plan | Duration | Tasks | Files | Tests |
|-------|------|----------|-------|-------|-------|
| 01    | 01   | 4 min    | 2/2   | 14    | 22 |
| Phase 01 P02 | 1 min | 2 tasks | 1 files | 8 |
| Phase 01 P03 | 6 min | 1 tasks | 5 files | 12 |
| Phase 01 P04 | 7 min | 1 tasks | 4 files | 10 |
| 04    | 01   | 14 min   | 2/2   | 29    | 38 |
| Phase 04 P05 | 25 min | 2 tasks | 15 files | 35 |
| Phase 04 Proot | 15 min | 1 tasks | 3 files | 12 |
| Phase 05 P02 | 4 min | 2 tasks | 9 files | 18 |
| Phase 05 P01 | 25 min | 3 tasks | 10 files | 28 |
| Phase 05 P03 | 8 min | 4 micro-tasks | 11 files | 57 |
| Phase 05 P04 | 6 min | 3 micro-tasks | 7 files | 25 |
| Phase 02 P07 | 15 min | 2 tasks | 4 files | 0 |
| Phase 03 W1 | 15 min | 2 tasks | 6 files | 17 ✅ |
| Phase 03 W2-5 | 45 min | 6 tasks | 13 files | 86 ✅ |
| Phase 03 Total | 60 min | 8 tasks | 13 new + 6 modified | 103 ✅ |

## Phase 03 Completion Summary (RAG Agent & AI Core)

**Execution Date:** 2026-03-28T22:30:00Z
**Duration:** ~60 minutes
**Final Commit:** a6c5cca
**Tests:** 103/103 passing ✅

**Deliverables:**
- ✅ Eval gate: 10 Portuguese queries scored, Groq selected (4.25 avg)
- ✅ RAG agent: pgvector search, top-3 filtering, degraded mode
- ✅ POST /chat SSE endpoint: streaming recommendations, <3s P95 latency
- ✅ Redis cache: 3600s TTL, deterministic keys, graceful degradation
- ✅ Langfuse observability: traces, cost tracking, latency monitoring
- ✅ E2E tests: full pipeline, timeout handling, regression checks

**Key Decisions (Phase 03):**
- [03-01] Groq selected as primary LLM (4.25 avg score >= 4.0 threshold, cost-effective)
- [03-02] Portuguese metric translation handles NULL specs gracefully
- [03-03] SSE events properly JSON-serialized (fixed in commit e805611)
- [03-04] Redis cache compatible with any async-capable library (no hard redis dependency)
- [03-05] Langfuse v3 API used for production-ready observability

## Open Questions (não bloqueantes para Phase 1)

- [ ] Confirmar Fromuth affiliate program details
- [ ] Confirmar Selkirk affiliate network (Impact Radius vs ShareASale)
- [ ] Verificar keyword volumes (Ahrefs/Semrush) — antes Phase 5
- [ ] Pricing Firecrawl `/extract` por call — verificar antes Phase 2
- [ ] Amazon PA-API: cobertura de SKUs do catálogo target
