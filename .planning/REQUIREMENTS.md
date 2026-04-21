# Requirements: v2.4.0 — Site Quality & UX Polish

*Created: 2026-04-20*
*Source: SITE-INSPECTION-REPORT.md — Full-stack inspection of localhost:3000*

## Overview

Comprehensive site quality milestone addressing 27 issues identified during full inspection. Fixes critical bugs (broken pages), closes UX gaps (no search, forced quiz flow), improves conversion (landing page, SEO), and polishes remaining rough edges.

**Goal:** Transform the site from "functional beta" to "polished, trustworthy product" ready for organic traffic growth.

---

## Functional Requirements

### FR-01: Fix Broken Gift & Quiz Results Pages
**Priority:** P0 (Critical)
**Source:** SITE-INSPECTION C1

Gift page (`/gift`) and Quiz Results (`/quiz/results`) use legacy CSS classes (`wg-button-coral`, `wg-button-ghost`, `wg-recommendation-card`, `wg-animate-fade-up`) that don't exist in the current Tailwind config. Pages render with no button styling, no card styling, broken layout.

**Acceptance:**
- Gift page renders with current design system (dark theme, brand colors)
- Quiz results page renders with current design system
- All `wg-*` classes replaced with Tailwind/shadcn equivalents
- Gift page uses `bg-base`/`bg-surface` instead of `var(--warm-white)`

### FR-02: Fix HTML Language Attribute
**Priority:** P0 (Critical)
**Source:** SITE-INSPECTION C2

`<html lang="en">` but all content is PT-BR. Screen readers mispronounce, SEO wrong locale, browsers auto-translate incorrectly.

**Acceptance:**
- `<html lang="pt-BR">` in root layout
- All metadata descriptions in Portuguese
- `hreflang` consideration for future i18n

### FR-03: Fix Quiz Profile Storage Mismatch
**Priority:** P0 (Critical)
**Source:** SITE-INSPECTION C3

Quiz page saves to `@/lib/quiz-profile` but Results page reads from `@/lib/profile`. Different modules → potential infinite redirect or empty results.

**Acceptance:**
- Single source of truth for quiz profile (one module)
- Quiz saves → Results reads from same storage
- No redirect loops

### FR-04: Catalog Text Search
**Priority:** P1
**Source:** SITE-INSPECTION H1

No way to search for paddle names or brands by text. Only brand/price filters exist.

**Acceptance:**
- Search input in catalog header
- Filters by `name` and `brand` (client-side, data already loaded)
- Optional: backend `?search=` param for server-side filtering
- Clear button to reset search
- URL sync: `?q=selkirk`

### FR-05: Allow Chat Without Quiz
**Priority:** P1
**Source:** SITE-INSPECTION H12

Chat requires completed quiz profile. New users who just want to ask "which paddle for beginners?" must complete 7-step quiz first.

**Acceptance:**
- Chat accessible without quiz
- Generic "all-purpose" profile used when no quiz completed
- Suggestion card: "Complete o quiz para recomendações personalizadas"
- No redirect to quiz

### FR-06: Filter Result Count
**Priority:** P1
**Source:** SITE-INSPECTION H11

No indication of how many results match current filters.

**Acceptance:**
- "Mostrando X de Y raquetes" header above grid
- Updates dynamically with filter changes

### FR-07: Catalog Pagination
**Priority:** P1
**Source:** SITE-INSPECTION H9

Loads all 200 products at once (`limit: 200`). No pagination, infinite scroll, or "load more".

**Acceptance:**
- 24 products per page
- Page-based pagination with URL sync (`?page=2`)
- Previous/Next navigation
- Total count visible

### FR-08: Add Gift & Blog to Navigation
**Priority:** P1
**Source:** SITE-INSPECTION H5

Gift finder and Blog pillar page exist but aren't in header navigation.

**Acceptance:**
- "Presente" link in header nav
- "Blog" link in header nav
- Both visible on desktop and mobile nav

### FR-09: Landing Page Visual Overhaul
**Priority:** P1
**Source:** SITE-INSPECTION H3

Landing page is visually flat: all sections same dark background, no scroll animations, fake stats, ALL CAPS buttons, no social proof, no product images.

**Acceptance:**
- Section background alternation (base/surface/elevated)
- Scroll-triggered fade-in animations (IntersectionObserver, staggered delays)
- Real stats from API (paddle count from `/api/v1/paddles`)
- Sentence-case buttons (not ALL CAPS)
- At least one testimonial or trust signal section
- Hero section with pickleball imagery

### FR-10: SEO Fundamentals
**Priority:** P1
**Source:** SITE-INSPECTION H6

Missing JSON-LD, OG images, sitemap, robots.txt, canonical URLs.

**Acceptance:**
- JSON-LD Product schema on product detail pages
- JSON-LD Organization schema on homepage
- OG images (use `next/og` ImageResponse API or static images)
- `app/sitemap.ts` with all routes
- `app/robots.ts`
- `<link rel="canonical">` on all pages

### FR-11: Expand Footer
**Priority:** P1
**Source:** SITE-INSPECTION H8

Footer has only 3 links, no social media, no blog, no contact info.

**Acceptance:**
- 4 columns: Product, Content, Legal, Social
- Links to: Quiz, Catalog, Compare, Gift, Blog, Privacy
- Social media links (Instagram, YouTube placeholder)
- Affiliate disclosure retained

### FR-12: Update DESIGN.md to Match Implementation
**Priority:** P1
**Source:** SITE-INSPECTION H7

DESIGN.md says "light-first" but app is all dark. Says "Inter" but uses Source Sans 3. Says "Sentence case" but buttons are ALL CAPS.

**Acceptance:**
- DESIGN.md reflects current dark-theme implementation
- Font references match (Bebas Neue, Source Sans 3, JetBrains Mono)
- Color palette matches Tailwind config
- Component specs match actual implementation
- Remove references to "warm-white" and "light-first"

### FR-13: Complete Price Alerts Frontend Flow
**Priority:** P1
**Source:** SITE-INSPECTION H10

Price alerts backend exists, Bell icon exists, modal component exists, but flow appears disconnected.

**Acceptance:**
- Bell icon on product cards opens price alert modal
- Modal creates alert via `POST /api/v1/price-alerts`
- Success/error feedback via toast
- User can see active alerts (in profile or dedicated page)

### FR-14: Fix English Button Text
**Priority:** P1
**Source:** SITE-INSPECTION H4

"Details" button on product cards is English. Everything else is Portuguese.

**Acceptance:**
- "Details" → "Detalhes"
- Scan all components for remaining English text

### FR-15: Allow 3-4 Paddle Comparison
**Priority:** P2
**Source:** SITE-INSPECTION H2

Compare limited to 2 paddles. Market standard is 3-4.

**Acceptance:**
- Allow up to 4 paddles in comparison
- Responsive layout: 2-col mobile, 3-col tablet, 4-col desktop
- CompareRow supports N columns
- URL sync: `?a=1&b=2&c=3`

---

## Non-Functional Requirements

### NFR-01: Design System Compliance
All changes must follow DESIGN.md (after it's updated per FR-12). No `wg-*` legacy classes. No hardcoded colors outside Tailwind tokens.

### NFR-02: Test Coverage
No regressions in existing tests:
- Frontend: 179/179 Vitest
- Backend: 196+/198 pytest
- E2E: 23/23 Playwright

New tests for:
- Catalog search functionality
- Chat without quiz flow
- Pagination

### NFR-03: Performance
- Lighthouse Performance ≥ 85
- No increase in bundle size > 10KB
- Catalog page loads first 24 products in < 2s

### NFR-04: Accessibility
- `lang="pt-BR"` on all pages
- Skip-to-content link in root layout
- ARIA labels on interactive elements
- `prefers-reduced-motion` respected

### NFR-05: Locale
All user-facing text in PT-BR. No English strings in UI.

---

## Out of Scope

- Production infrastructure (T1 — deferred)
- Legal/compliance (T3 — deferred)
- Performance load testing (T5 — deferred)
- Backend architecture changes
- New backend endpoints (unless needed for search)
- Mobile app / PWA
- Internationalization (i18n)
- Payment integration
- Admin dashboard improvements

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Broken pages | 2 (Gift, Quiz Results) | 0 |
| `lang` attribute | `en` | `pt-BR` |
| Catalog search | None | Text search with filters |
| Landing page sections | All same bg | Alternating backgrounds |
| SEO structured data | None | JSON-LD on all pages |
| Footer links | 3 | 12+ |
| Navigation links | 4 | 6 |
| ALL CAPS buttons | 2 (landing CTAs) | 0 |
| English text in UI | "Details" button | None |
| Profile storage modules | 2 (mismatched) | 1 (unified) |
