# Roadmap: PickleIQ

## Milestone v1.4 — Launch Readiness & Bug Fixes

**Goal:** Fix all launch-blocking bugs so core user flows work without errors.

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 14 | Launch Readiness | Fix images, routing, chat bugs + regression tests | IMG-01–04, RTE-01–03, CHT-01–03, QA-01–03 | 4 |

### Phase 14: Launch Readiness

**Goal:** Eliminate all console errors and broken flows across catalog, detail, and chat.

**Requirements:** IMG-01, IMG-02, IMG-03, IMG-04, RTE-01, RTE-02, RTE-03, CHT-01, CHT-02, CHT-03, QA-01, QA-02, QA-03

**Root causes (from investigation):**

1. **Images (IMG):** `next.config.mjs` already allows all hosts (`hostname: '**'`) — config is NOT the issue. DB seed (`scripts/populate_paddles.sql`) fills paddles with `placehold.co` URLs containing `?text=` query params that return responses the Image optimizer can't process. The "Foto" fallback only triggers on NULL/falsy `image_url`, but paddles have invalid (non-null) URLs. Fix: NULL out `image_url` in seed data + add `onError` handler on `<Image>` to catch future broken URLs.
2. **Routing (RTE):** Backend `GET /api/v1/paddles` does NOT accept `model_slug` as a query parameter. The frontend sends `?brand=X&model_slug=Y` but the backend ignores `model_slug`, returning all paddles for the brand. `fetchProductData` takes `items[0]` which may not match the requested slug → null → 404. Fix: add `model_slug` filter to backend WHERE clause + verify frontend matches slug in response.
3. **Chat (CHT):** Edge cases in payload validation — `budget_max` of 0 bypasses `?? 600` fallback (0 is falsy but not null), empty/whitespace messages from the chat widget, or `style` field being undefined (FastAPI Optional[str] accepts null but proxy may send undefined). Fix: use `Math.max()` for budget, trim messages, sanitize style field.

**Tasks (in execution order):**

#### Wave 1 — Backend Fixes (parallel)

| Task | File(s) | Description |
|------|---------|-------------|
| 14.1 | `backend/app/api/paddles.py` | Add `model_slug: Optional[str]` query param to `list_paddles()`. Add `AND p.model_slug = %s` to WHERE clause when provided. |
| 14.2 | `scripts/populate_paddles.sql`, `pipeline/db/schema.sql` | Replace all `placehold.co` URLs with NULL in seed data. Update `schema.sql` to add missing `image_url TEXT` column (schema is out of sync with actual DB). |

#### Wave 2 — Frontend Fixes (parallel, after Wave 1)

| Task | File(s) | Description |
|------|---------|-------------|
| 14.3 | `frontend/src/lib/seo.ts` | In `fetchProductData`, verify `items[0].model_slug` matches the requested `modelSlug`. If not, find the matching item in the array. If no match, return null. |
| 14.4 | `frontend/src/app/paddles/page.tsx` | Add `onError` handler to `<Image>` that hides the image and shows the "Foto" fallback div when loading fails (catches broken URLs at runtime, not just null checks). |
| 14.5 | `frontend/src/app/paddles/[brand]/[model-slug]/page.tsx` | Add `onError` handler to `<Image>` matching catalog page pattern. Same runtime fallback for broken images. |
| 14.6 | `frontend/src/app/api/chat/route.ts` | Fix `budget_brl` to use `Math.max(profile?.budget_max ?? 600, 1)` instead of `profile?.budget_max ?? 600`. Add `message.trim()` validation before sending to backend. Add `style` field handling for undefined values. |
| 14.7 | `frontend/src/components/chat/product-card.tsx` | Keep the existing "Foto" placeholder (already correct — no external image loading). |

#### Wave 3 — Tests & Verification

| Task | File(s) | Description |
|------|---------|-------------|
| 14.8 | `backend/tests/` | Add test: `GET /api/v1/paddles?brand=selkirk&model_slug=vanguard-control` returns only matching paddle. Add test: query without model_slug returns all brand paddles. |
| 14.9 | `frontend/src/tests/` | Add test: `fetchProductData` returns correct paddle when multiple brand paddles exist. Add test: returns null when no match. Add test: chat proxy handles budget_max=0 gracefully. |
| 14.10 | All | Run full test suite: `make test`. Verify 167 backend + 152 frontend tests pass. Run manual smoke: catalog → detail → quiz → chat. |

**Success criteria:**
1. `/paddles` catalog page loads with zero "not a valid image" console errors
2. `/paddles/selkirk/vanguard-control` returns 200 with correct paddle data (not 404)
3. `/chat` returns streaming response with 200 status after quiz completion (not 422)
4. `make test` passes all tests with no regressions
5. New regression tests cover the 3 bug categories

---
*Roadmap created: 2026-04-04*
*Last updated: 2026-04-04 after v1.4 milestone start*
