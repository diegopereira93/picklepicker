# Phase 31: Polish — Compare 3-4, Breadcrumbs, Error Boundaries

**Research Date:** 2026-04-22
**Status:** Complete

## Standard Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js App Router | 14.2.35 |
| React | React | 18.x |
| Styling | Tailwind CSS | 3.4.1 |
| Language | TypeScript | 5.x |
| Fonts | Bebas Neue (display), Source Sans 3 (body), JetBrains Mono (data) | next/font/google |
| Icons | lucide-react | latest |

## Task 31.1 — Compare 3-4 Paddles

### Current Implementation
- **File:** `frontend/src/app/compare/page.tsx` (409 lines)
- Uses `useSearchParams()` with `?a=ID&b=ID` for 2 paddles
- `CompareRow` component takes `valueA`/`valueB` (hardcoded for 2 columns)
- `RadarChart` component hardcoded with `valueA`/`valueB`
- `CompareVerdict` only works with 2 paddles
- Grid: `grid-cols-1 md:grid-cols-2`
- Buy CTAs: 2-column grid

### Required Changes
- Extend URL params: `?a=1&b=2&c=3&d=4` (2-4 paddles)
- Responsive grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`
- `CompareRow` must render N columns (not just A/B)
- `RadarChart` needs N data series (or hide for >2 paddles)
- `CompareVerdict` only for 2 paddles; for 3-4, hide or show summary
- Buy CTA grid: dynamic columns matching paddle count

### Key Pattern
```tsx
const paddleIds = ['a', 'b', 'c', 'd']
  .map(key => searchParams.get(key))
  .filter(Boolean)
  .map(Number)

const paddles = await Promise.all(paddleIds.map(id => fetchPaddle(id)))
```

### CompareRow Extension
Current `CompareRowProps` has `valueA` and `valueB`. Needs refactoring to accept `values: (string|number|null)[]` and `winners: ('a'|'b'|'c'|'d'|'tie'|null)[]`.

## Task 31.2 — Breadcrumbs with JSON-LD

### Pages to Add Breadcrumbs
1. `frontend/src/app/catalog/[slug]/page.tsx` — Product detail: `Início > Catálogo > {Brand} {Name}`
2. `frontend/src/app/compare/page.tsx` — Compare: `Início > Comparar Raquetes`

### JSON-LD BreadcrumbList Schema
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Início", "item": "https://pickleiq.com" },
    { "@type": "ListItem", "position": 2, "name": "Catálogo", "item": "https://pickleiq.com/catalog" },
    { "@type": "ListItem", "position": 3, "name": "{Paddle Name}", "item": "https://pickleiq.com/catalog/{slug}" }
  ]
}
```

### Component Design
- Create reusable `<Breadcrumb>` component in `frontend/src/components/ui/breadcrumb.tsx`
- Props: `items: Array<{ label: string; href?: string }>`
- Visual: chevron separators, muted text, last item bold
- Use `Home` icon from lucide-react for first item

## Task 31.3 — Error and 404 Pages

### Next.js 14 App Router Convention
- `frontend/src/app/error.tsx` — Must be a Client Component (`'use client'`)
  - Props: `{ error: Error; reset: () => void }`
  - Catches runtime errors in route segments
- `frontend/src/app/not-found.tsx` — Can be Server Component
  - Shown when `notFound()` is called or no route matches

### Design Specs
- Dark theme matching site design (bg-base, text-text-primary)
- Brand lime CTA: "Voltar ao catálogo"
- Error page: error message + "Tentar novamente" button (calls `reset()`)
- 404 page: illustration/icon + "Página não encontrada" + link to catalog
- Use `AlertTriangle` icon for error, `SearchX` icon for 404

## Task 31.4 — Alternating Row Backgrounds in Specs Table

### Current Implementation
```tsx
// catalog/[slug]/page.tsx — specs table has no alternating backgrounds
<div className={cn('grid grid-cols-2 gap-4', 'px-4 py-3')}>
```

### Required Change
Add `bg-surface`/`bg-elevated` alternating using `index % 2 === 0`:
```tsx
<div className={cn(
  'grid grid-cols-2 gap-4 px-4 py-3',
  index % 2 === 0 ? 'bg-surface' : 'bg-elevated'
)}>
```

## Task 31.5 — Skip-to-Content Link

### Accessibility Pattern
```tsx
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-brand-primary focus:text-base focus:rounded focus:font-semibold">
  Pular para o conteúdo
</a>
```

### Implementation
- Add to `frontend/src/app/layout.tsx` as first child of `<body>`
- Add `id="main-content"` to `<main>` element
- Visible only on keyboard focus (Tab from URL bar)
- Global — works on every page

## Architecture Patterns

### Existing Conventions
- All UI components use `@/components/ui/` directory
- Tailwind classes: `bg-base`, `bg-surface`, `bg-elevated`, `text-text-primary`, `text-text-secondary`, `text-text-muted`
- Brand primary: `bg-brand-primary` (#84CC16), secondary: `bg-brand-secondary` (#F97316)
- Font classes: `font-display` (Bebas Neue), `font-sans` (Source Sans 3), `font-mono` (JetBrains Mono)
- Button variants: `default`, `ghost`, `outline`
- Design tokens from tailwind.config.ts (not arbitrary values)

### Testing
- Vitest in `frontend/src/tests/`
- No component-level tests currently exist for compare/catalog pages
- Tests should verify rendering, accessibility attributes, URL param handling

## Validation Architecture

### Dimension Coverage
| Dimension | Test Strategy |
|-----------|--------------|
| 1 — Compiles | `npm run build` passes |
| 2 — Unit | Vitest tests for Breadcrumb, CompareRow, skip link |
| 3 — Integration | URL params → correct paddle count on compare page |
| 4 — Visual | Manual: compare 2/3/4 paddles, error page, 404 |
| 5 — Accessibility | Skip link focusable, breadcrumbs structured data |
| 6 — Performance | No regressions (page weight within 10%) |
| 7 — Security | No new attack surface (client-side only changes) |
| 8 — Edge Cases | 0 paddles, 1 paddle, 5 paddles (reject), invalid IDs |

## Out of Scope
- Server-side error logging (no Sentry/DD integration)
- Custom error page per route segment
- Breadcrumb schema for chat/admin pages
- Compare page redesign (just extending existing layout)
