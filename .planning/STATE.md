# STATE.md — PickleIQ

## Current Position

Phase: v1.6 — UI Redesign (planning)
Plan: TBD
Status: v1.4.0 complete. Design review completed (9 variants, 3 screens). v1.6.0 milestone created. Ready for /gsd:plan-phase 16.
Last activity: 2026-04-05 — Design review complete, v1.6.0 milestone planned

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-05)

**Core value:** Users can confidently choose the right pickleball paddle through AI-powered recommendations backed by real-time pricing and technical specs
**Current focus:** v1.6 UI Redesign — implement winning design variants from design review

## Accumulated Context

### Shipped Milestones

| Milestone | Version | Phases | Status |
|-----------|---------|--------|--------|
| MVP | v1.0.0 | 1–6 | ✅ Complete |
| Scraper & E2E | v1.1.0 | 7–9 | ✅ Complete |
| Core Web Vitals | v1.2.0 | 11 | ✅ Complete |
| Hybrid UI Redesign | v1.3.0 | 13 | ✅ Complete |
| Launch Readiness | v1.4.0 | 14 | ✅ Complete |
| Design Review | — | — | ✅ Complete (9 variants, 3 screens, approved combo saved) |

### Design Review Summary (2026-04-05)

**Experts consulted:** Oracle (conversion + coherence), Metis (constraint analysis), Designer-eye (plan-design-review principles)
**Visual inspection:** Playwright browser, 1440x900 viewport, 9 full-page screenshots taken and evaluated
**Approved combination:**
- Home: C (Quiz-Forward) + data stats from A — score 8/10
- Catalog: A (Comparison Table) + product images from B + grid toggle — score 8/10
- Chat: B (Sidebar Companion) + card responses from C — score 8/10

**6 DESIGN.md changes proposed:**
1. Allow full-dark sections for immersive flows
2. Add Chat UI section
3. Add semantic level colors
4. Relax border radius for conversational elements
5. Add interactive widget patterns
6. Widen max-width for data-dense layouts

**Files:**
- `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/approved.json`
- `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/design-review-report.md`
- 9 screenshots in same directory

### Test Results (Phase 14 Verification)

- **Backend:** 174 passed, 2 pre-existing failures (Jina/HuggingFace API 401 — not Phase 14 related)
- **Frontend:** 161/161 passed

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
- Design review HTML mockups at `picklepicker/designs/variant-*.html` (9 files) + `picklepicker/designs/board-*.html` (3 comparison boards).

---
*State updated: 2026-04-05 — v1.6.0 UI Redesign milestone ready for planning*
