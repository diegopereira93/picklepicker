# Phase 4: Frontend Chat & Product UI

## Phase Brief

**Goal**: Complete web interface for PickleIQ with conversational chat, paddle comparison, and admin tooling.

**Depends on**: Phase 3 (RAG Agent & AI Core)

**Type**: Multi-plan frontend + integration layer

**Wave Structure**: 5 waves (likely sequential for frontend iterations)

---

## Requirements Checklist

- [x] R4.1: Next.js 14 App Router with Tailwind CSS + shadcn/ui component library
- [x] R4.2: Quiz onboarding (3 steps: skill level → play style → budget) + chat widget with inline product cards
- [x] R4.3: Paddle comparison page with search/autocomplete, side-by-side table, radar chart visualization
- [x] R4.4: Affiliate tracking (keepalive fetch, Edge Route Handler logging, UTM preservation)
- [x] R4.5: Admin panel (/admin/queue for review queue, /admin/catalog for CRUD) protected by ADMIN_SECRET

---

## Success Criteria (Must be TRUE)

1. **Next.js 14 scaffolding**: App Router deployed on Vercel preview with Tailwind + shadcn/ui
2. **Quiz onboarding (3 steps)**: Nível → estilo → orçamento → chat widget funcional com product cards inline
3. **Comparison page**: Search/autocomplete, table side-by-side, RadarChart (ssr: false)
4. **Affiliate tracking**: keepalive fetch + Edge Route Handler logging
5. **Admin panel**: /admin/queue + /admin/catalog protegido por ADMIN_SECRET

---

## Plan Structure

5 planned tasks (each task = 1 plan file):

1. **04-01: Next.js 14 scaffolding** — App Router + Tailwind + shadcn/ui + layout base (anônimo-first, sem auth)
2. **04-02: Quiz onboarding + Chat widget** — Route Handler proxy → FastAPI, useChat, SSE transform, product cards inline
3. **04-03: Paddle comparison page** — search/autocomplete, tabela side-by-side, RadarChart Recharts (ssr: false)
4. **04-04: Affiliate tracking** — fetch keepalive, Edge Route Handler logging, UTM params preservados
5. **04-05: Admin panel** — /admin/queue (review queue) + /admin/catalog (CRUD paddles) protegido por ADMIN_SECRET

---

## Upstream Contracts

**From Phase 3 (RAG Agent)**:
- POST /chat endpoint returns SSE with top-3 recommendations
- Streaming response format: `data: {type, content, metadata}`
- Degraded mode: returns top-3 by price if LLM timeout

**From Phase 2 (Data Pipeline)**:
- GET /paddles returns full catalog with embeddings
- GET /paddles/{id}/latest-prices returns current pricing
- Comparison-friendly fields: swingweight, twistweight, core, face material

---

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS + shadcn/ui
- **Charts**: Recharts (RadarChart)
- **API communication**: fetch + Edge Route Handlers
- **Deployment**: Vercel (preview + production)
- **Auth**: Admin panel protected by ADMIN_SECRET env var (no full auth yet)

---

## Testing Strategy

- **Route handler testing**: Mocking FastAPI responses, testing SSE streaming
- **Component testing**: Quiz flow, comparison page search, chart rendering
- **E2E testing**: Chat widget → response → product card clicks
- **Affiliate tracking**: Verify keepalive fetch logs, UTM params preserved

---

## Known Constraints

- **No user auth yet** (Phase 5 adds Clerk)
- **Comparison page** must have `ssr: false` for RadarChart (Recharts hydration issue)
- **Admin panel**: Minimal security (ADMIN_SECRET only, no role-based access yet)
- **Quiz data**: Stored in URL params or session (no DB persistence yet)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| SSE streaming complexity | Use `useChat()` hook from `ai/react`, handle error states |
| RadarChart hydration mismatch | Mark component `ssr: false`, test on mobile viewports |
| Affiliate tracking data loss | Use fetch keepalive + immediate Edge Route logging, test in DevTools throttle |
| Admin panel security | Add IP whitelist or temp auth token, document ADMIN_SECRET setup |

---

## Definition of Done

- ✅ All 5 plan tasks completed and merged
- ✅ Vercel preview deployment working
- ✅ Chat widget streams responses from Phase 3 /chat endpoint
- ✅ Comparison page renders all required fields + charts
- ✅ Affiliate clicks logged to analytics (edge logs)
- ✅ Admin panel accessible at /admin/queue and /admin/catalog
- ✅ No console errors on mobile (iOS/Android)
- ✅ Lighthouse score ≥ 90 (performance + accessibility)
- ✅ Test coverage ≥ 70% for critical paths

---

## Blocking Dependencies

- ✅ Phase 3 must be complete (RAG Agent with /chat endpoint)
- ✅ Frontend environment: Next.js project scaffolded in `/frontend`
- ✅ API proxy URL environment variable configured

---

## Questions for Planning

1. Should the admin panel have a login form (temporary password) or just ADMIN_SECRET env var?
2. Quiz results: persist in URL params, localStorage, or session cookie?
3. Comparison page: max 5 paddles to compare, or unlimited?
4. Affiliate link behavior: open in new tab, or same tab with tracking pixel?
