---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: planning
last_updated: "2026-03-28T03:00:51.601Z"
last_activity: 2026-03-28
progress:
  total_phases: 6
  completed_phases: 2
  total_plans: 9
  completed_plans: 14
---

# PickleIQ — Project State

**Última atualização:** 2026-03-27
**Status:** Ready to plan
**Last session:** 2026-03-28T02:58:03.079Z

## Current Position

Phase: 04 (frontend-chat-product-ui) — EXECUTING
Plan: Not started

- **Milestone:** v1.0 (MVP → Beta Launch)
- **Phase:** 5
- **Status:** Executing Phase 4
- **Last activity:** 2026-03-28
- **Next action:** Execute 04-02

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

## Performance Metrics

| Phase | Plan | Duration | Tasks | Files |
|-------|------|----------|-------|-------|
| 01    | 01   | 4 min    | 2/2   | 14    |
| Phase 01 P02 | 1 min | 2 tasks | 1 files |
| Phase 01 P03 | 6 min | 1 tasks | 5 files |
| Phase 01 P04 | 7 min | 1 tasks | 4 files |
| 04    | 01   | 14 min   | 2/2   | 29    |
| Phase 04 P05 | 25 min | 2 tasks | 15 files |
| Phase 04 Proot | 15 min | 1 tasks | 3 files |

## Open Questions (não bloqueantes para Phase 1)

- [ ] Confirmar Fromuth affiliate program details
- [ ] Confirmar Selkirk affiliate network (Impact Radius vs ShareASale)
- [ ] Verificar keyword volumes (Ahrefs/Semrush) — antes Phase 5
- [ ] Pricing Firecrawl `/extract` por call — verificar antes Phase 2
- [ ] Amazon PA-API: cobertura de SKUs do catálogo target
