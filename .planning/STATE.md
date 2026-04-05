# STATE.md — PickleIQ

## Current Position

Phase: v1.5 — Production Readiness (planning)
Plan: TBD
Status: Phase 14 complete. Oracle assessed. v1.5 requirements gathering.
Last activity: 2026-04-05 — Doc debt cleanup + Oracle assessment

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-05)

**Core value:** Users can confidently choose the right pickleball paddle through AI-powered recommendations backed by real-time pricing and technical specs
**Current focus:** v1.5 Production Readiness — infrastructure, legal, reliability

## Accumulated Context

### Shipped Milestones

| Milestone | Version | Phases | Status |
|-----------|---------|--------|--------|
| MVP | v1.0.0 | 1–6 | ✅ Complete |
| Scraper & E2E | v1.1.0 | 7–9 | ✅ Complete |
| Core Web Vitals | v1.2.0 | 11 | ✅ Complete |
| Hybrid UI Redesign | v1.3.0 | 13 | ✅ Complete |
| Launch Readiness | v1.4.0 | 14 | ✅ Complete |

### Phase 14 Completion Summary

All 10 tasks verified:

| Task | Description | Status |
|------|-------------|--------|
| 14.1 | Backend model_slug filter | ✅ In code |
| 14.2a | Schema sync (schema.sql) | ✅ In code |
| 14.2b | Image migration script | ✅ In code |
| 14.2c | Seed data cleanup (NULL images) | ✅ In code |
| 14.3 | Frontend slug match verification | ✅ In code |
| 14.4 | Catalog SafeImage component | ✅ In code |
| 14.5 | Detail SafeImage component | ✅ In code |
| 14.6 | Chat proxy edge cases | ✅ In code |
| 14.7 | Product card verification | ✅ No change needed |
| 14.8 | Backend regression tests (4 tests) | ✅ In code |
| 14.9 | Frontend regression tests (7 tests) | ✅ In code |
| 14.10 | Full verification | ✅ Passed |

### Test Results (Phase 14 Verification)

- **Backend:** 174 passed, 2 pre-existing failures (Jina/HuggingFace API 401 — not Phase 14 related)
- **Frontend:** 161/161 passed
- **Fabricated images:** Zero in source code (legacy scripts with unsplash URLs deleted)

### Oracle Assessment (2026-04-05)

**Verdict:** v1.4.0 technically shippable, 3 operational risks before full production launch.

**v1.5 Priorities (Oracle recommended):**
1. T1: Provision Supabase/Railway production infrastructure
2. T3: Legal assessment of BR retailer scraping
3. T2: Eval gate as monthly CI job
4. Local embedding fallback (SentenceTransformers) for Jina/HuggingFace outages
5. Basic uptime/error monitoring for /chat + scrapers
6. T5: Load test /chat (after infra stable)
7. T7: Firecrawl self-hosted runbook (upgrade to P2)

**Top 3 Risks (30 days):**
1. Embedding API outages (Jina/HuggingFace 401s)
2. Legal/compliance exposure (unvetted scraping)
3. Infrastructure gaps (no production DB/hosting)

### Pending TODOS (from TODOS.md)

| TODO | Priority | Status |
|------|----------|--------|
| T1 | P1 | ⏳ Pending — v1.5 scope |
| T2 | P1 | ⏳ Pending — v1.5 scope |
| T3 | P1 | ⏳ Pending — v1.5 scope |
| T4 | P2 | ⏳ Deferred |
| T5 | P1 | ⏳ Pending — v1.5 scope (after infra) |
| T6 | P2 | ⏳ Pending — v1.5 scope |
| T7 | P3 → P2 | ⏳ Pending — v1.5 scope |

### Key Technical Notes

- Backend uses raw SQL (no ORM). Column names must match `pipeline/db/schema.sql`.
- Two separate Python venvs: `backend/venv/` and `pipeline/.venv/`.
- Frontend uses native `<img>` via `SafeImage` component (not next/image) for retailer CDN compat.
- Chat proxy at `frontend/src/app/api/chat/route.ts` transforms Vercel AI SDK format → FastAPI format.
- Embeddings: Jina AI (primary) + Hugging Face (fallback). OpenAI removed.
- LLM: Groq (Mixtral 8x7B). Anthropic removed.

---
*State updated: 2026-04-05*
