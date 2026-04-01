---
phase: 08-navigation-ux-fixes
plan: "01"
subsystem: frontend
tags: [navigation, ux, seo, catalog]
dependency_graph:
  requires: []
  provides: [fixed-nav-links, catalog-card-fallback, enriched-catalog-cards]
  affects: [frontend/src/components/layout/header.tsx, frontend/src/app/page.tsx, frontend/src/lib/seo.ts, frontend/src/app/paddles/page.tsx]
tech_stack:
  added: []
  patterns: [numeric-id-fallback, conditional-rendering, Portuguese-i18n-labels]
key_files:
  created: []
  modified:
    - frontend/src/components/layout/header.tsx
    - frontend/src/app/page.tsx
    - frontend/src/lib/seo.ts
    - frontend/src/app/paddles/page.tsx
decisions:
  - navLinks reduced to [Home, Catalogo] — Chat IA removed to enforce quiz-gate flow via Encontrar raquete CTA only
  - fetchProductData gracefully returns null on non-ok instead of throwing — prevents 404 crash for null model_slug
  - Numeric ID fallback added for paddles whose model_slug is a raw database ID
metrics:
  duration: 8 min
  completed: "2026-03-29"
  tasks: 4/4
  files_modified: 4
  reverified: "2026-03-31"
  reverified_by: gsd:execute-phase
---

# Phase 08 Plan 01: Navigation UX Fixes Summary

**One-liner:** Eliminated user-facing 404s by removing /compare links and Chat IA nav entry, adding numeric ID fallback in fetchProductData, and enriching catalog cards with skill_level badge, specs, and stock indicator.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Fix header navLinks — remove Chat IA, point Catalogo to /paddles | 0f360ea | frontend/src/components/layout/header.tsx |
| 2 | Fix home page hero CTA — point to /paddles with updated label | 6c83dd4 | frontend/src/app/page.tsx |
| 3 | Fix catalog card 404 — add numeric ID fallback in fetchProductData | 0667bb4 | frontend/src/lib/seo.ts |
| 4 | Add useful info to catalog cards — skill_level, specs, in_stock | 2788023 | frontend/src/app/paddles/page.tsx |

## What Was Built

- **Header nav:** 3-item array [Home, Comparar, Chat IA] replaced with 2-item [Home, Catalogo]. "Encontrar raquete" CTA button (pointing to /chat with quiz gate) preserved.
- **Home page CTA:** Secondary hero button changed from "Ver comparador" → /compare to "Ver catalogo" → /paddles. Primary "Comecar agora" and bottom "Falar com o PickleIQ" /chat links unchanged.
- **seo.ts fetchProductData:** Non-ok responses return null instead of throwing. After slug-based query, if paddle is null and modelSlug matches `/^\d+$/`, a fallback fetch to `/api/v1/paddles/{id}` is attempted. Also corrected base path from `/paddles` to `/api/v1/paddles`.
- **Catalog cards:** Each card now conditionally renders: skill_level badge (Iniciante/Intermediário/Avançado), specs row (SW: {swingweight} · Core: {core_thickness_mm}mm), and in_stock indicator (Em estoque in green / Fora de estoque in gray).

## Decisions Made

1. **navLinks = [Home, Catalogo]** — Chat IA removed from nav to enforce quiz-first flow. The "Encontrar raquete" button is the intended entry point to /chat.
2. **Graceful null return** — fetchProductData now returns null on error instead of throwing, which prevents SSR crashes for product pages with missing model_slug.
3. **Numeric ID fallback** — When model_slug is a raw integer (e.g., "42"), the direct `/api/v1/paddles/42` endpoint is tried as fallback. This matches how catalog card hrefs are generated when `paddle.model_slug` is null.

## Deviations from Plan

### Scope Discovery (not auto-fixed)

**1. [Out of Scope] Stale /compare links in footer and blog page**
- **Found during:** Overall verification
- **Files:** `frontend/src/components/layout/footer.tsx`, `frontend/src/app/blog/pillar-page/page.tsx`
- **Action:** Logged to deferred-items.md — pre-existing issues outside this plan's file scope
- **Fix:** These should be addressed in a follow-up task (footer /compare → /paddles, blog pillar page /compare → /paddles)

## Known Stubs

None — all new conditional rendering wires directly to live Paddle type fields (`skill_level`, `specs.swingweight`, `specs.core_thickness_mm`, `in_stock`) which are already defined and populated from the backend.

## Self-Check: PASSED

Files exist:
- FOUND: frontend/src/components/layout/header.tsx
- FOUND: frontend/src/app/page.tsx
- FOUND: frontend/src/lib/seo.ts
- FOUND: frontend/src/app/paddles/page.tsx

Commits exist:
- FOUND: 0f360ea (task 1)
- FOUND: 6c83dd4 (task 2)
- FOUND: 0667bb4 (task 3)
- FOUND: 2788023 (task 4)
