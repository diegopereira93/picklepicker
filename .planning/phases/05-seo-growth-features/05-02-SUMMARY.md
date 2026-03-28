---
phase: 05-seo-growth-features
plan: 02
subsystem: frontend/seo
tags: [seo, metadata, schema-org, isr, next-js, product-pages]
dependency_graph:
  requires: []
  provides:
    - Product detail page with generateMetadata() and Schema.org/Product JSON-LD
    - Product listing page with ISR revalidate=3600
    - On-demand revalidation webhook endpoint
    - lib/seo.ts SEO helpers
  affects:
    - frontend/src/app/paddles/** (new routes)
    - frontend/src/types/paddle.ts (extended)
tech_stack:
  added:
    - next/dynamic (ssr:false for Recharts hydration prevention)
    - Schema.org/Product JSON-LD via dangerouslySetInnerHTML
    - Next.js ISR (revalidate export) + revalidateTag/revalidatePath
  patterns:
    - TDD (RED/GREEN) for all new modules
    - generateMetadata() async function pattern (Next.js App Router)
    - Graceful no-op for Next.js server APIs outside runtime (tests)
key_files:
  created:
    - frontend/src/lib/seo.ts
    - frontend/src/lib/revalidate.ts
    - frontend/src/components/schema/product-schema.tsx
    - frontend/src/app/paddles/[brand]/[model-slug]/page.tsx
    - frontend/src/app/paddles/page.tsx
    - frontend/src/app/api/webhooks/revalidate/route.ts
    - frontend/src/tests/unit/product-metadata.test.ts
    - frontend/src/tests/unit/product-schema.test.tsx
    - frontend/src/tests/unit/product-listing.test.ts
  modified:
    - frontend/src/types/paddle.ts (extended Paddle interface with SEO fields)
decisions:
  - "Canonical URL stored in alternates.canonical (Next.js 14 Metadata API) not top-level canonical"
  - "revalidateTag/revalidatePath imported dynamically in revalidate.ts to gracefully no-op in test environment"
  - "Existing Paddle type extended with optional SEO fields rather than creating a new interface"
  - "PriceHistoryChart imported with ssr:false via dynamic() to prevent Recharts hydration mismatch"
  - "fetchPaddlesList supports both paddles and items response keys for forward compatibility"
metrics:
  duration: "4 min"
  completed_date: "2026-03-28"
  tasks: 2/2
  files: 9
---

# Phase 05 Plan 02: Product Pages SEO — Summary

**One-liner:** Next.js product pages with generateMetadata(), Schema.org/Product JSON-LD, and ISR 3600s caching using TDD (28 new tests, all GREEN).

## What Was Built

### Task 1: Product detail page with generateMetadata() and Schema.org

- **`lib/seo.ts`** — `fetchProductData()` fetches a single paddle by brand+model_slug; `generateProductMetadata()` builds Next.js Metadata object with title, description, OG image from product image_url, canonical URL, and robots=index,follow.
- **`components/schema/product-schema.tsx`** — Renders `<script type="application/ld+json">` with Schema.org/Product structure: name, brand, description, image, offers (BRL price, InStock/OutOfStock), aggregateRating (when rating+review_count present), and URL.
- **`app/paddles/[brand]/[model-slug]/page.tsx`** — SSR product detail page (revalidate=false for freshness) with generateMetadata(), breadcrumb nav, ProductSchema as first child, and PriceHistoryChart imported with `ssr:false`.

### Task 2: Product listing page with ISR revalidation

- **`app/paddles/page.tsx`** — Listing page with `export const revalidate = 3600` (ISR 1 hour). Renders all paddles as a grid with links to detail pages. Includes generateMetadata() for listing SEO.
- **`lib/revalidate.ts`** — `revalidatePaddlePages(paddleId?)` for tag/path-scoped revalidation; `revalidateWebhook(req)` validates `Authorization: Bearer ${REVALIDATE_SECRET}` header and triggers revalidation. Both gracefully no-op outside Next.js runtime.
- **`app/api/webhooks/revalidate/route.ts`** — POST webhook handler for on-demand cache invalidation by price-check workers.

## Test Coverage

28 new tests across 3 files, all GREEN:

| File | Tests | Coverage |
|------|-------|----------|
| product-metadata.test.ts | 8 | fetchProductData(), generateProductMetadata() |
| product-schema.test.tsx | 10 | ProductSchema JSON-LD serialization |
| product-listing.test.ts | 10 | fetchPaddlesList(), revalidatePaddlePages(), revalidateWebhook() |

## Caching Strategy

| Route | Strategy | Timing |
|-------|----------|--------|
| `/paddles/[brand]/[model-slug]` | SSR (revalidate=false) | Always fresh |
| `/paddles` | ISR | Regenerates every 3600s |
| `/api/webhooks/revalidate` | On-demand | Triggered by price worker |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Renamed product-schema test from .ts to .tsx**
- **Found during:** Task 1 RED phase
- **Issue:** Test file used JSX syntax but had `.ts` extension — Vitest transform rejected it
- **Fix:** Renamed to `.product-schema.test.tsx`
- **Files modified:** frontend/src/tests/unit/product-schema.test.tsx
- **Commit:** 975f7dd

**2. [Rule 1 - Bug] Existing Paddle type missing SEO fields**
- **Found during:** Task 1 GREEN phase
- **Issue:** Backend interface in plan used `price_brl`, `model_slug`, `rating`, `review_count`, `in_stock`, `description` — none existed in frontend Paddle type
- **Fix:** Extended Paddle interface with optional SEO fields (backward-compatible)
- **Files modified:** frontend/src/types/paddle.ts
- **Commit:** 44b85da

**3. [Rule 2 - Missing critical] revalidate.ts uses dynamic import for next/cache**
- **Found during:** Task 2 GREEN phase
- **Issue:** `revalidateTag`/`revalidatePath` are Next.js server APIs that throw outside runtime — would break vitest
- **Fix:** Dynamic import with try/catch no-op to support both Next.js runtime and test environments
- **Files modified:** frontend/src/lib/revalidate.ts
- **Commit:** 8271021

## Known Stubs

None — all data flows wired to real API (NEXT_PUBLIC_FASTAPI_URL). PriceHistoryChart imported with `ssr:false` but component itself is a pre-existing component (not created here).

## Self-Check: PASSED

- [x] frontend/src/lib/seo.ts exists
- [x] frontend/src/lib/revalidate.ts exists
- [x] frontend/src/components/schema/product-schema.tsx exists
- [x] frontend/src/app/paddles/[brand]/[model-slug]/page.tsx exists
- [x] frontend/src/app/paddles/page.tsx exists
- [x] frontend/src/app/api/webhooks/revalidate/route.ts exists
- [x] Commit 975f7dd exists (RED tests Task 1)
- [x] Commit 44b85da exists (GREEN Task 1)
- [x] Commit 93de3a4 exists (RED tests Task 2)
- [x] Commit 8271021 exists (GREEN Task 2)
