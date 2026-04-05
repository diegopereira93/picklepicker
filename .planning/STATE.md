# STATE.md — PickleIQ

## Current Position

Phase: v1.6 — UI Redesign — ALL PHASES COMPLETE
Status: Phase 16 ✅, Phase 17 ✅, Phase 18 ✅, Phase 19 ✅
Last activity: 2026-04-05 — All 4 phases implemented, build passes, 161/161 tests pass.

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-05)

**Core value:** Users can confidently choose the right pickleball paddle through AI-powered recommendations backed by real-time pricing and technical specs
**Current focus:** v1.6 UI Redesign — COMPLETE

## Accumulated Context

### Shipped Milestones

| Milestone | Version | Phases | Status |
|-----------|---------|--------|--------|
| MVP | v1.0.0 | 1–6 | ✅ Complete |
| Scraper & E2E | v1.1.0 | 7–9 | ✅ Complete |
| Core Web Vitals | v1.2.0 | 11 | ✅ Complete |
| Hybrid UI Redesign | v1.3.0 | 13 | ✅ Complete |
| Launch Readiness | v1.4.0 | 14 | ✅ Complete |
| Design Review | — | — | ✅ Complete |
| DESIGN.md v3.0 + Foundation | v1.6.0 | 16 | ✅ Complete |
| Home-C Quiz-Forward | v1.6.0 | 17 | ✅ Complete |
| Chat-B Sidebar Companion | v1.6.0 | 18 | ✅ Complete |
| Catalog-A Comparison Table | v1.6.0 | 19 | ✅ Complete |

### Phase 18 Implementation Summary

**Files created:**
- `frontend/src/components/chat/sidebar-product-card.tsx` — Large product display with image, specs, score badge, CTA
- `frontend/src/components/chat/related-paddles.tsx` — Horizontal row of smaller product cards
- `frontend/src/components/chat/comparison-card.tsx` — Mini-table comparing 2+ paddles with green highlights
- `frontend/src/components/chat/tip-card.tsx` — Amber-bordered informational card
- `frontend/src/components/chat/suggested-questions.tsx` — Clickable prompt pills

**Files modified:**
- `frontend/src/app/chat/page.tsx` — Split-panel layout (55%/45%), sidebar + chat
- `frontend/src/components/chat/chat-widget.tsx` — v3.0 styling, onRecommendations callback, SuggestedQuestions
- `frontend/src/components/chat/message-bubble.tsx` — v3.0 styling (8px radius, lime border, transparent AI bg)

**Verification:** Build passes ✅, 161/161 tests pass ✅

### Phase 19 Implementation Summary (complete)

**Files created:**
- `frontend/src/components/catalog/filter-bar.tsx` — Brand/level filter chips, sort dropdown, view toggle
- `frontend/src/components/catalog/selection-bar.tsx` — Fixed bottom bar for comparison selection
- `frontend/src/components/catalog/comparison-table.tsx` — Sortable table with score badges
- `frontend/src/components/catalog/product-grid.tsx` — 3-col card grid with selection checkboxes
- `frontend/src/components/catalog/catalog-client.tsx` — Client component assembling catalog

**Files modified:**
- `frontend/src/app/paddles/page.tsx` — Server component wrapper with CatalogClient

**Verification:** Build passes ✅, 161/161 tests pass ✅

### Design Review Summary (2026-04-05)

**Experts consulted:** Oracle (conversion + coherence), Metis (constraint analysis), Designer-eye (plan-design-review principles)
**Visual inspection:** Playwright browser, 1440x900 viewport, 9 full-page screenshots taken and evaluated
**Approved combination:**
- Home: C (Quiz-Forward) + data stats from A — score 8/10
- Catalog: A (Comparison Table) + product images from B + grid toggle — score 8/10
- Chat: B (Sidebar Companion) + card responses from C — score 8/10

### Test Results

- **Backend:** 174 passed, 2 pre-existing failures (Jina/HuggingFace API 401 — not Phase 14 related)
- **Frontend:** 161/161 passed (verified after Phase 18 + Phase 19)

### Key Technical Notes

- Backend uses raw SQL (no ORM). Column names must match `pipeline/db/schema.sql`.
- Two separate Python venvs: `backend/venv/` and `pipeline/.venv/`.
- Frontend uses native `<img>` via `SafeImage` component (not next/image) for retailer CDN compat.
- Chat proxy at `frontend/src/app/api/chat/route.ts` transforms Vercel AI SDK format → FastAPI format.
- Embeddings: Jina AI (primary) + Hugging Face (fallback). OpenAI removed.
- LLM: Groq (Mixtral 8x7B). Anthropic removed.

---
*State updated: 2026-04-05 — v1.6.0 UI Redesign milestone COMPLETE*
