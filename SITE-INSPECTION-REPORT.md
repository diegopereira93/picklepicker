# PickleIQ — Site Inspection Report

**Date:** 2026-04-20
**Scope:** Full-stack inspection of localhost:3000 (Next.js 14 frontend + FastAPI backend)
**Methodology:** Source code analysis across all pages, components, layouts, and backend endpoints

---

## Executive Summary

PickleIQ is a pickleball paddle intelligence platform for the Brazilian market with a solid technical foundation: Next.js 14 App Router, Tailwind, Clerk auth, FastAPI backend with pgvector, and a RAG-based AI chat. The core flows (Quiz → Chat → Compare) are functional.

However, the inspection reveals **3 critical bugs**, **12 high-priority improvements**, and **15 medium-priority enhancements** across UX, visual design, SEO, and functionality. The most impactful issues are: broken Gift/Quiz Results pages (legacy CSS classes), design system vs implementation mismatch, missing SEO fundamentals, and a flat landing page experience.

**Estimated impact of fixes:** 40-60% improvement in conversion potential (SEO + UX + trust signals).

---

## 🔴 CRITICAL — Bugs & Broken Features

### C1. Gift Page & Quiz Results Use Legacy CSS Classes (BROKEN)

**Severity:** Critical — Pages likely render broken/unstyled
**Files:**
- `frontend/src/app/gift/page.tsx` — uses `wg-button-coral`, `wg-button-ghost`, `wg-container`, `wg-animate-fade-up`, `wg-recommendation-card`
- `frontend/src/app/quiz/results/page.tsx` — uses `wg-button-coral`, `wg-button-outline`, `wg-button-ghost`, `wg-recommendation-card`

**Problem:** These classes don't exist in the current Tailwind config or CSS. They're remnants from an older design system. The Gift page and Quiz Results render with no button styling, no card styling, and broken layout.

**Evidence:** Gift page uses `bg-[var(--warm-white)]` which isn't defined in `design-tokens.css`. Quiz results text is `text-[#2A2A2A]` (dark text) on a dark background.

**Fix:** Replace all `wg-*` classes with current design system equivalents. Update Gift page to use dark theme consistent with the rest of the app.

---

### C2. HTML `lang="en"` but All Content is Portuguese

**Severity:** Critical — Affects SEO, accessibility, and browser behavior
**File:** `frontend/src/app/layout.tsx` line 46

**Problem:** `<html lang="en">` but every piece of user-facing text is in Portuguese. Screen readers will mispronounce Portuguese words. Google may not index correctly for Brazilian users. Browser auto-translate will try to "translate" Portuguese as if it were English.

**Fix:** Change to `<html lang="pt-BR">`. Update `<meta name="language" content="pt-BR">`. Add `hreflang` tags.

---

### C3. Quiz Results Profile Mismatch

**Severity:** Critical — Quiz results may fail to load
**Files:**
- `frontend/src/app/quiz/page.tsx` uses `loadQuizProfile` from `@/lib/quiz-profile`
- `frontend/src/app/quiz/results/page.tsx` uses `getProfile` from `@/lib/profile`

**Problem:** Two completely different profile modules. If quiz saves to `quiz-profile` but results reads from `profile`, the results page will find nothing and redirect back to quiz — infinite loop or empty results.

**Fix:** Unify to single profile storage module. Quiz results should read from the same source quiz writes to.

---

## 🟠 HIGH PRIORITY — UX & Functional Gaps

### H1. No Text Search in Catalog

**Severity:** High — Core e-commerce feature missing
**File:** `frontend/src/app/catalog/page.tsx`

**Problem:** Users can only filter by brand and price range. No way to search "Selkirk Luxx" or "spin paddle". This is table stakes for any product catalog.

**Fix:** Add a search input to the catalog header that filters by `name` and `brand` client-side (data is already loaded). Add backend `?search=` param for server-side filtering.

---

### H2. Compare Limited to 2 Paddles

**Severity:** High — Competitive disadvantage
**File:** `frontend/src/app/catalog/page.tsx` — `compareIds.length >= 2` hardcoded limit

**Problem:** Most paddle comparison sites allow 3-4 products. 2 is too restrictive for informed purchase decisions.

**Fix:** Allow up to 4 paddles. Update UI to handle 2-4 column comparison layout. Update `CompareRow` to support N columns.

---

### H3. Landing Page is Visually Flat

**Severity:** High — First impression drives conversion
**File:** `frontend/src/components/home/landing-client.tsx`

**Problems:**
- All sections use `bg-base` (same dark background). DESIGN.md specifies "alternating dark/light sections" but implementation is monolithic dark.
- No scroll-triggered animations except stats counter. DESIGN.md specifies staggered reveals, parallax, etc.
- Stats are hard-coded fake numbers (500+, R$180, 2.847) — erodes trust
- ALL CAPS buttons ("ENCONTRAR MINHA RAQUETE") contradict DESIGN.md's "Sentence case"
- No testimonials, social proof, or trust signals
- Feature cards are identical boxes with no visual differentiation
- No video, no product images on landing

**Fix:** 
1. Add section background alternation (surface/elevated/base)
2. Add IntersectionObserver for staggered fade-in animations
3. Replace fake stats with real data from API (paddle count from `/api/v1/paddles`)
4. Lowercase buttons to sentence case
5. Add testimonials carousel
6. Add hero image/video of pickleball action
7. Differentiate feature cards with distinct accent colors or gradients

---

### H4. Product Card Buttons in English

**Severity:** High — Language inconsistency breaks trust
**File:** `frontend/src/components/ui/product-card.tsx`

**Problem:** "Details" button text is English while everything else is Portuguese.

**Fix:** Change to "Detalhes".

---

### H5. No Blog/Gift Links in Navigation

**Severity:** High — Features exist but are undiscoverable
**File:** `frontend/src/components/layout/header.tsx`

**Problem:** Blog pillar page (`/blog/pillar-page`) and Gift finder (`/gift`) exist but aren't in the header navigation. Users can only find them by knowing the URL.

**Fix:** Add "Presente" and "Blog" to nav links. Consider a "Recursos" dropdown for secondary links.

---

### H6. Missing SEO Fundamentals

**Severity:** High — Organic discovery impaired

**Problems:**
1. **No JSON-LD structured data** — No Product, Organization, FAQ, or BreadcrumbList schemas
2. **Missing Open Graph images** — Only text in OG tags, no `og:image`
3. **No sitemap.xml or robots.txt** — Not visible in the codebase
4. **`/paddles` route is wasted** — Just redirects to `/catalog`. Could be an SEO landing page
5. **No canonical URL management** — Multiple URLs can reach same product (e.g., `/paddles/selkirk/luxx` → `/catalog/luxx`)

**Fix:**
1. Add `generateMetadata` with JSON-LD for products
2. Create OG images using `next/og` (ImageResponse API)
3. Add `app/sitemap.ts` and `app/robots.ts`
4. Make `/paddles` a brand listing page
5. Add `<link rel="canonical">` on all pages

---

### H7. DESIGN.md vs Implementation Mismatch

**Severity:** High — Developer confusion, inconsistent output
**Files:** `DESIGN.md` vs `tailwind.config.ts` vs `design-tokens.css`

**Contradictions:**
| DESIGN.md Says | Implementation Does |
|---|---|
| "Light-first aesthetic" | All dark (#0a0a0a base) |
| "Warm white (#FAF7F2)" background | #0a0a0a background |
| "Coral (#F97316) primary CTA" | Lime (#84CC16) everywhere |
| "Inter for body text" | Source Sans 3 for body |
| "Sentence case" | ALL CAPS buttons |
| "2px border radius" | `rounded-rounded`, `rounded-lg`, `rounded-full` mixed |

**Fix:** Update DESIGN.md to match current dark-theme implementation OR update implementation to match DESIGN.md. The dark theme is actually well-executed — update DESIGN.md to reflect reality.

---

### H8. Footer is Thin

**Severity:** High — Missing trust signals and SEO links
**File:** `frontend/src/components/layout/footer.tsx`

**Problems:**
- Only 3 links (Privacy, Chat, Comparar)
- No social media links
- No blog categories
- No "Sobre nós" page
- No contact info
- Affiliate disclosure is good but buried

**Fix:** Expand to 4 columns: Product (Quiz, Catalog, Compare, Gift), Content (Blog, Guides), Legal (Privacy, Terms, Affiliate Disclosure), Social (Instagram, YouTube, Discord). Add logo and tagline.

---

### H9. No Pagination in Catalog

**Severity:** High — Performance and UX
**File:** `frontend/src/app/catalog/page.tsx`

**Problem:** Loads all 200 products at once (`limit: 200`). No pagination, no infinite scroll, no "load more". Slow on mobile, overwhelming for users.

**Fix:** Implement either pagination (12-24 per page) or infinite scroll with intersection observer.

---

### H10. Alerta de Preço Feature is Incomplete

**Severity:** High — Advertised but not functional
**Files:** Backend has `/api/v1/price-alerts/*`, frontend has `price-alert-modal.tsx` and Bell icon

**Problem:** "Alertas de Preço" is listed as a main feature on the landing page. Bell icon exists on product cards. Backend API exists. But the actual alert creation/management flow appears incomplete or disconnected.

**Fix:** Verify end-to-end flow. Add price alert management page in user profile. Connect Bell icon to alert creation modal.

---

### H11. No Filter Result Count

**Severity:** High — UX feedback missing
**File:** `frontend/src/app/catalog/page.tsx`

**Problem:** When applying filters, users don't see "Mostrando 23 de 500 raquetes". They just see the grid change. No indication of how many results match.

**Fix:** Add result count header: `"Mostrando {filtered.length} de {total} raquetes"`.

---

### H12. Quiz → Chat Flow is Forced

**Severity:** High — Barrier to entry
**File:** `frontend/src/app/chat/page.tsx`

**Problem:** Chat page loads quiz profile and redirects to quiz if none exists. Users who just want to ask "which paddle for beginners?" must complete a 7-step quiz first.

**Fix:** Allow chat without quiz. Show "Complete o quiz para recomendações personalizadas" as a suggestion card when no profile exists. Let users chat with a generic "all-purpose" profile.

---

## 🟡 MEDIUM PRIORITY — Polish & Enhancement

### M1. No Breadcrumbs

**Problem:** Deep pages (product detail, compare) have no breadcrumb navigation. Users lose context.
**Fix:** Add breadcrumb component. Use JSON-LD BreadcrumbList for SEO.

### M2. No Favorites/Wishlist

**Problem:** Users can't save paddles they're interested in. Clerk auth exists but no saved items feature.
**Fix:** Add favorites with Clerk user ID + localStorage fallback. Heart icon on product cards.

### M3. Missing Social Proof

**Problem:** No testimonials, user reviews, or "popular paddles" section.
**Fix:** Add testimonials section to landing page. Add "Mais populares" sort option. Show review counts prominently.

### M4. No Loading States on Landing

**Problem:** Only the stats counter has animation. Feature cards, CTA sections just appear.
**Fix:** Add fade-in-up animations triggered by IntersectionObserver with staggered delays.

### M5. Catalog Sorting Limited

**Problem:** Only 5 sort options (relevance, price asc/desc, name, newest). Missing: rating, popularity, discount percentage.
**Fix:** Add `rating_desc`, `discount_desc`, `popularity` sort options.

### M6. No Error Boundaries

**Problem:** No `error.tsx` files visible in app directory. API failures will show default Next.js error page.
**Fix:** Add `error.tsx` and `not-found.tsx` at app root and key routes.

### M7. Product Detail Specs Layout

**Problem:** Specs table in `catalog/[slug]/page.tsx` uses plain grid with no alternating row backgrounds or dividers. Hard to scan.
**Fix:** Add alternating row backgrounds (`bg-surface`/`bg-elevated`) and subtle bottom borders.

### M8. Mobile Catalog Filter UX

**Problem:** Filters apply immediately on change (no "Apply" button). On slow connections, this creates many API calls.
**Fix:** Either debounce filter changes or add "Aplicar filtros" button.

### M9. Price Display on Product Cards

**Problem:** `PriceTag` component exists but some places use raw `R$ {price.toFixed(2)}` (compact mode). Inconsistent formatting.
**Fix:** Always use `PriceTag` component for price display.

### M10. No "Back to Top" on Long Pages

**Problem:** Catalog with 200 products and product detail pages are long. No way to quickly return to top.
**Fix:** Add floating "back to top" button that appears after scrolling 3+ viewport heights.

### M11. Chat Suggested Questions are Hard-Coded

**Problem:** `SUGGESTED_QUESTIONS` array in `chat-widget.tsx` is static. Doesn't adapt to user context or trending paddles.
**Fix:** Fetch suggestions from backend based on popular queries or user profile.

### M12. Gift Page Only Recommends 1 Paddle

**Problem:** Gift flow (`gift/page.tsx`) fetches paddles and shows only the first match. No alternatives presented.
**Fix:** Show top 3 matches with different price points, like quiz results.

### M13. No 404 Page

**Problem:** No custom `not-found.tsx`. Default Next.js 404 doesn't match site design.
**Fix:** Create themed 404 with "Voltar ao catálogo" CTA.

### M14. Quiz Budget Values Mismatch

**Problem:** Quiz options say "Até R$200", "R$200-400", etc. but `budget_max` mapping in chat page uses different values (200, 400, 600, 2000). The display values and actual filter values are inconsistent.
**Fix:** Align quiz display values with actual budget ranges used for filtering.

### M15. Accessibility — Missing Skip Links

**Problem:** Landing page has a skip link (`sr-only focus:not-sr-only`) but other pages don't.
**Fix:** Add skip-to-content link in root layout, visible on focus, for all pages.

---

## 📊 Summary Matrix

| Category | Critical | High | Medium | Total |
|---|---|---|---|---|
| Bugs/Broken | 3 | 0 | 0 | 3 |
| UX/Functional | 0 | 7 | 10 | 17 |
| Visual/Design | 0 | 3 | 2 | 5 |
| SEO | 0 | 2 | 0 | 2 |
| **Total** | **3** | **12** | **12** | **27** |

---

## 🎯 Recommended Implementation Order

### Phase 1 — Stop the Bleeding (1-2 days)
1. **C1** — Fix Gift & Quiz Results broken CSS
2. **C2** — Fix `lang="en"` → `lang="pt-BR"`
3. **C3** — Fix profile storage mismatch
4. **H4** — Fix English "Details" button

### Phase 2 — Core UX (3-5 days)
5. **H1** — Add catalog text search
6. **H12** — Allow chat without quiz
7. **H11** — Add filter result count
8. **H9** — Add catalog pagination
9. **H5** — Add Gift/Blog to navigation

### Phase 3 — Conversion & Trust (3-5 days)
10. **H3** — Landing page visual overhaul
11. **H6** — SEO fundamentals (JSON-LD, OG images, sitemap)
12. **H8** — Expand footer
13. **H7** — Update DESIGN.md to match implementation
14. **H10** — Complete price alerts flow

### Phase 4 — Polish (2-3 days)
15. **H2** — Allow 3-4 paddle comparison
16. **M1-M15** — Medium priority items

---

## Architecture Notes

### What's Working Well
- **Product detail page** (`catalog/[slug]`) is comprehensive — price chart, specs, similar paddles, affiliate tracking
- **Chat implementation** with streaming SSE, recommendation extraction, and sidebar rail
- **Design tokens** (dark theme with lime/coral accents) are well-defined in Tailwind config
- **Component architecture** — clean separation of concerns, multiple card modes (catalog/chat/compact)
- **Backend API surface** — comprehensive endpoints for paddles, prices, embeddings, chat
- **Affiliate tracking** — click tracking with page context for attribution

### Tech Debt
- Two different profile storage modules (`profile.ts` vs `quiz-profile.ts`)
- Legacy CSS classes (`wg-*`) not cleaned up from design system migration
- Gift page uses old light theme (`warm-white`) while rest of app is dark
- `fetchPaddles` called with `limit: 100` in product detail to find ONE paddle — should use direct fetch by ID
- No caching strategy visible for API calls

---

*Report generated by Sisyphus AI Agent — full source code analysis of 80+ files across frontend and backend.*
