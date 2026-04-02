---
gsd_state_version: 1.0
milestone: v1.3
milestone_name: — Next Milestone
status: verifying
stopped_at: Completed 13-08-PLAN.md
last_updated: "2026-04-02T16:43:36.808Z"
last_activity: 2026-04-02 - Completed quick task 260402-ntf: Fix chat page components to match DESIGN.md v2.0
progress:
  total_phases: 2
  completed_phases: 2
  total_plans: 12
  completed_plans: 12
---

# PickleIQ — Project State

**Última atualização:** 2026-04-01
**Status:** Phase 13 verified — PR #10 updated with UAT
**Last session:** 2026-04-02T14:14:29.534Z

## Current Position

Phase: 13
Plan: Not started

- **Last session:** 2026-04-01T16:30:00.000Z
- **Stopped at:** Completed 13-08-PLAN.md

- **Milestone:** v1.2 Core Web Vitals Optimization — COMPLETED
- **Status:** All 4 plans complete (11.1-11.4), milestone archived
- **Last activity:** 2026-04-02
- **Next action:** Run `/gsd:new-milestone` to start v1.3 planning

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-01)

**Core value:** Real-time pickleball paddle recommendations with transparent pricing
**Current focus:** Phase 13 — nvidia-ui-redesign

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
- [Phase 09-01]: Two-phase extraction (category page + product pages) to capture lazy-loaded images from Brazil Store
- [Phase 09-01]: Transform mitiendanube URLs from -1024-1024 to -480-0 for optimized image size
- [Phase 10-10]: Custom ThemeProvider instead of next-themes package for zero dependencies; localStorage key pickleiq-theme; motion system uses CSS animations (no JS library); all animations respect prefers-reduced-motion
- [Phase 11.1]: next/image migration complete; all images now use explicit dimensions, responsive sizes, priority loading for hero; automatic WebP/AVIF via Next.js
- [Phase 11.3]: Skeleton placeholders with Suspense for dynamic content; min-height containers prevent CLS; no ad components exist in codebase
- [Phase 11.4]: Vercel Speed Insights with dynamic import for zero initial load impact; Lighthouse CI with strict budgets (LCP < 2500ms, CLS < 0.1); Bundle analyzer with ANALYZE env var; size-limit 150KB budget; WCAG 2.1 AA focus indicators using primary color with offset; useAnnouncer hook with polite aria-live region
- [Phase 11.2]: Font already optimized with display: 'swap', adjustFontFallback: true, preconnect hints, and system font fallback; SpeedInsights uses dynamic import pattern (ssr: false) which is equivalent to lazyOnload for component-level deferring
- [Phase 12-03]: MAX_ITEMS=1000 prevents unbounded memory growth from fetch_all=True pagination
- [Phase 12-03]: Atomic upsert with ON CONFLICT DO UPDATE ... RETURNING eliminates TOCTOU race; requires UNIQUE constraint on paddles.name
- [Phase 12-04]: Staggered cron schedules (5-min intervals) combined with random sleep jitter for thundering herd prevention
- [Phase 12-04]: TDD for database modules - write failing tests first, then implementation (17 tests total: 7 quality metrics + 10 DLQ)
- [Phase 12-04]: Pydantic models for database entities with proper typing and validation
- [Phase 12-04]: DLQ status management via Enum (pending/processing/resolved/failed) with retry_count tracking
- [Phase 13]: Used cdnjs Font Awesome 6 Free CDN (no kit ID) in layout.tsx
- [Phase 13]: Shadcn HSL shims retained in :root mapping NVIDIA black/white palette so bg-background/text-foreground Tailwind classes remain valid
- [Phase 13]: Google Fonts CDN (not next/font) for Hybrid typography - matches DESIGN.md v2.0 requirement
- [Phase 13]: Removed inline NVIDIA-EMEA font-family to allow CSS variables from globals.css to cascade
- [Phase 13]: Logo lime accent implemented via nested span structure; all nv-* classes migrated to hy-* prefix in header.tsx
- [Phase 13]: Added hy-section-heading, hy-subheading, hy-caption-small CSS classes to globals.css before class migration

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
| Phase 05 P02 | 4 min | 2 tasks | 9 files |
| Phase 05 P01 | 25min | 3 tasks | 10 files |
| Phase 08 P04 | 45min | 3 tasks | 3 files |
| Phase 09 P01 | 15min | 4 tasks | 2 files |
| Phase 10 P10 | 15min | 4/4 | 7 files |
| Phase 10-performance-ux-polish P02 | 5min | 2 tasks | 2 files |
| Phase 10-performance-ux-polish P10.1 | 5 min | 3 tasks | 3 files |
| Phase 11 P11.1 | 10 min | 3 tasks | 2 files |
| Phase 11 P11.2 | 15 min | 4 tasks | 3 files |
| Phase 11 P11.4 | 15 min | 5 tasks | 8 files |
| Phase 12 P01 | 18 | 3 tasks | 6 files |
| Phase 12 P03 | 15 min | 3 tasks | 2 files |
| Phase 12 P02 | 15 | 3 tasks | 4 files |
| Phase 12 P04 | 35 min | 4 tasks | 7 files |
| Phase 13 P01 | 1 min | 2 tasks | 2 files |
| Phase 13 P06 | 2 min | 1 tasks | 1 files |
| Phase 13 P05 | 2min | 1 tasks | 1 files |
| Phase 13 P07 | 2 min | 1 tasks | 1 files |
| Phase 13 P08 | 4 min | 4 tasks | 5 files |

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260402-ntf | Fix chat page components to match DESIGN.md v2.0 | 2026-04-02 | 2607bdd | [260402-ntf-fix-chat-page-components-to-match-design](./quick/260402-ntf-fix-chat-page-components-to-match-design/) |

## Open Questions (não bloqueantes para Phase 1)

- [ ] Confirmar Fromuth affiliate program details
- [ ] Confirmar Selkirk affiliate network (Impact Radius vs ShareASale)
- [ ] Verificar keyword volumes (Ahrefs/Semrush) — antes Phase 5
- [ ] Pricing Firecrawl `/extract` por call — verificar antes Phase 2
- [ ] Amazon PA-API: cobertura de SKUs do catálogo target
