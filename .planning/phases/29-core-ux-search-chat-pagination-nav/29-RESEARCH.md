# Phase 29: Core UX — Search, Chat, Pagination, Nav — Research

**Phase:** 29
**Date:** 2026-04-20
**Discovery Level:** 1 — Quick Verification

## Standard Stack

| Layer | Tech | Notes |
|-------|------|-------|
| Frontend | Next.js 14 App Router | Client components with `'use client'` |
| UI | Tailwind CSS + shadcn/ui | Dark theme tokens: base=#0a0a0a, surface=#141414 |
| State | React useState + URL params | `useSearchParams` + `useRouter` from `next/navigation` |
| API | FastAPI backend | `/api/v1/paddles` supports `limit`, `offset`, `brand`, `price_min`, `price_max` |

## Existing Patterns Found

### Catalog Page (`frontend/src/app/catalog/page.tsx`)
- **Already has URL sync:** `useSearchParams` for `price_min`, `price_max`, `brand`, `sort`
- **Already has `total` state** from API response — just not displayed
- **`loadProducts()`** hardcodes `limit: 200, offset: 0` — needs pagination
- **`updateUrl()`** builds `URLSearchParams` — extendable for `?q=` and `?page=`
- **Filter UI** is desktop sidebar + mobile bottom sheet — search input fits naturally in header area
- **Suspense boundary already present** (wraps `CatalogPageContent`)

### Chat Page (`frontend/src/app/chat/page.tsx`)
- **Hard quiz gate:** `if (!profile) return (...)` redirects to quiz
- **Profile loaded via:** `loadQuizProfile()` from `@/lib/quiz-profile`
- **ChatWidget expects `UserProfile`:** `{ level: string, style: string, budget_max: number }`
- **Profile mapping in chat page:** converts `QuizProfile` → `UserProfile` with level/style/budget transforms
- **Generic profile needed:** `{ level: 'intermediate', style: 'all-court', budget_max: 2000 }` as fallback

### Header Navigation (`frontend/src/components/layout/header.tsx`)
- **navLinks array:** `[{ href: "/", label: "HOME" }, { href: "/quiz", label: "QUIZ" }, { href: "/catalog", label: "CATÁLOGO" }]`
- **Desktop nav:** hidden `md:flex` with Link components
- **Mobile nav:** Sheet (drawer) with same links
- **Gift page exists** at `/gift` (confirmed via `frontend/src/app/gift/page.tsx`)
- **Blog directory exists** at `frontend/src/app/blog/`

### API Client (`frontend/src/lib/api.ts`)
- `fetchPaddles` accepts `{ brand, price_min, price_max, in_stock, limit, offset }`
- Returns `PaddleListResponse { items: Paddle[], total: number, limit: number, offset: number }`
- Backend `list_paddles` endpoint supports all these params + returns `total`

## Architecture Decisions

### Search: Client-side filtering
- All paddles already loaded (currently `limit: 200`)
- With pagination (24/page), search should still be client-side for instant feedback
- Filter by `paddle.name.toLowerCase().includes(q)` and `paddle.brand.toLowerCase().includes(q)`
- URL sync: `?q=selkirk` for shareable links
- Search applies BEFORE pagination (filters reduce set, then paginate the result)

### Pagination: Server-side via existing API
- Backend already supports `limit` and `offset` params
- 24 items per page (industry standard for product grids)
- URL sync: `?page=2`
- Previous/Next navigation (no infinite scroll — explicit control)
- Search filters + pagination compose naturally: search reduces set, API returns filtered+paginated results

### Chat without quiz: Generic profile
- When no quiz profile in localStorage, use hardcoded "all-purpose" profile:
  `{ level: 'intermediate', style: 'all-court', budget_max: 2000 }`
- Show suggestion card/banner: "Complete o quiz para recomendações personalizadas"
- Profile sidebar hidden when using generic profile (no real data to show)

## Common Pitfalls

1. **useSearchParams requires Suspense** — catalog page already has it, but changes to URL param reading must stay inside the Suspense boundary
2. **Search + pagination interaction** — when search changes, reset page to 1
3. **URL param encoding** — search query may contain special chars; use `encodeURIComponent`
4. **Chat generic profile** — ChatWidget sends profile to `/api/chat` which passes to RAG agent; generic profile must be a valid `UserProfile` shape
5. **Blog page** — `/blog` directory exists but may not have a page.tsx yet; nav link should still be added (404 is acceptable, page will be built in Phase 30)

## What NOT to Hand-roll

- URL param sync: Use existing `URLSearchParams` pattern from catalog page
- Chat profile: Reuse existing `loadQuizProfile()` and `UserProfile` types
- Navigation: Just extend existing `navLinks` array
- API calls: Reuse `fetchPaddles` — it already supports pagination params
