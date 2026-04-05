# Requirements: PickleIQ v1.4 — Launch Readiness

**Defined:** 2026-04-04
**Core Value:** Users can confidently choose the right pickleball paddle through AI-powered recommendations backed by real-time pricing and technical specs

## v1.4 Requirements

Bug fixes for launch-blocking issues. Each maps to roadmap phases.

### Product Images

- [x] **IMG-01**: All paddles with `image_url` set display a valid image — no "not a valid image" console errors on `/paddles` catalog page
- [x] **IMG-02**: Paddle detail pages (`/paddles/[brand]/[model-slug]`) show either a real product image or a styled placeholder — never a broken image
- [x] **IMG-03**: `placehold.co` URLs are removed from the database seed and replaced with either real URLs or NULL (triggering the existing "Foto" fallback)
- [x] **IMG-04**: Chat product cards show a styled placeholder image instead of attempting to load external URLs

### Paddle Detail Routing

- [x] **RTE-01**: Backend `GET /api/v1/paddles` accepts `model_slug` as an optional query parameter and filters results by exact match
- [x] **RTE-02**: Frontend `fetchProductData(brand, modelSlug)` correctly resolves to the exact paddle matching both brand and model_slug — no 404 for valid paddles
- [x] **RTE-03**: Paddle detail page returns 404 only when the paddle genuinely does not exist in the database

### Chat Endpoint

- [x] **CHT-01**: Frontend chat proxy handles all edge cases in the payload — zero `budget_max`, empty messages, missing profile fields — without returning 422
- [x] **CHT-02**: Chat works end-to-end from quiz completion through AI response — no validation errors at any step
- [x] **CHT-03**: Error responses from the backend are surfaced to the user with a meaningful message (not a raw 422/500)

### Quality Assurance

- [x] **QA-01**: All existing tests pass (167 backend + 152 frontend) with no regressions
- [x] **QA-02**: New regression tests cover the 3 fixed bugs — paddle detail routing, chat payload validation, image fallback behavior
- [x] **QA-03**: Manual smoke test of core flows produces zero console errors: browse catalog → view detail → complete quiz → chat

## v2 Requirements

Deferred to future release. Not launch-blocking.

### Deferred TODOS (from TODOS.md)

- **T1**: Provisionar infra Supabase/Railway desde Phase 1
- **T2**: Eval gate de modelo como job mensal
- **T3**: Avaliação legal de scraping de specs internacionais
- **T4**: Monitorar volume do review_queue + SLA
- **T5**: Load test endpoint /chat
- **T6**: Zero-paddle alert no crawler
- **T7**: Runbook Firecrawl self-hosted

## Out of Scope

| Feature | Reason |
|---------|--------|
| New features or UX changes | This milestone is bug-fix only |
| Performance optimization | Already addressed in v1.2 |
| Real product images for all paddles | Requires re-running scrapers with image extraction — separate effort |
| Clerk auth flow fixes | Not in scope unless auth blocks a core flow |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| IMG-01 | Phase 14 | ✅ Complete |
| IMG-02 | Phase 14 | ✅ Complete |
| IMG-03 | Phase 14 | ✅ Complete |
| IMG-04 | Phase 14 | ✅ Complete |
| RTE-01 | Phase 14 | ✅ Complete |
| RTE-02 | Phase 14 | ✅ Complete |
| RTE-03 | Phase 14 | ✅ Complete |
| CHT-01 | Phase 14 | ✅ Complete |
| CHT-02 | Phase 14 | ✅ Complete |
| CHT-03 | Phase 14 | ✅ Complete |
| QA-01 | Phase 14 | ✅ Complete |
| QA-02 | Phase 14 | ✅ Complete |
| QA-03 | Phase 14 | ✅ Complete |

**Coverage:**
- v1.4 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-04*
*Last updated: 2026-04-05 — v1.4.0 all requirements validated*
