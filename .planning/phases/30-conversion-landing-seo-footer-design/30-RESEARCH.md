# Phase 30: Conversion — Landing, SEO, Footer, Design System — Research

**Phase:** 30
**Date:** 2026-04-20
**Discovery Level:** 2 — Detailed Analysis (from 3 explore agents)

## Standard Stack

| Layer | Tech | Notes |
|-------|------|-------|
| Frontend | Next.js 14.2.35 App Router | Client + Server components |
| UI | Tailwind CSS + shadcn/ui | Dark theme tokens: base=#0a0a0a, surface=#141414, elevated=#1a1a1a |
| Fonts | Bebas Neue (display), Source Sans 3 (body), JetBrains Mono (data) | Configured via next/font |
| API | FastAPI backend | `/api/v1/paddles`, `/api/v1/price-alerts` |
| Auth | Clerk | For user authentication |

## Existing Patterns Found

### Landing Page (`frontend/src/components/home/landing-client.tsx`)
- **5 sections:** Hero (bg-base), How It Works (bg-surface), Stats (bg-base), Features (bg-base), CTA (bg-base)
- **Problem:** 4 of 5 sections use bg-base → visually flat
- **IntersectionObserver:** Only used for stats counter animation (lines 22-60), threshold 0.1
- **Stats:** Hardcoded [500, 180, 2847] — fake numbers
- **Buttons:** "ENCONTRAR MINHA RAQUETE" — ALL CAPS
- **No social proof, testimonials, or trust signals**

### Footer (`frontend/src/components/layout/footer.tsx`)
- **4-column grid** (md:grid-cols-4) but only 3 columns actually used
- **Only 3 links:** Privacy, Chat, Catalog
- **No social links** (Instagram, YouTube, etc.)
- **No Gift, Blog, or legal links**
- **Affiliate disclosure present** at top

### Catalog Detail Page (`frontend/src/app/catalog/[slug]/page.tsx`)
- **generateMetadata** exists (lines 17-47) with title, description, canonical, openGraph
- **No JSON-LD** structured data
- **Product data available for JSON-LD:** brand, name, description, image_url, price_brl, price_min_brl, in_stock, specs (swingweight, twistweight, weight_oz, grip_size, core_thickness_mm, face_material), skill_level, rating, review_count

### Homepage (`frontend/src/app/page.tsx`)
- **Static metadata** (lines 4-17)
- **No Organization schema**
- **Renders LandingClient component**

### Root Layout (`frontend/src/app/layout.tsx`)
- **Basic metadata** (lines 31-35)
- **lang="pt-BR"** (fixed in Phase 28)
- **No JSON-LD**

### Sitemap/Robots
- **Neither exist** — need to create `app/sitemap.ts` and `app/robots.ts`

### Blog Directory
- **Exists** at `frontend/src/app/blog/` with layout.tsx and pillar-page/page.tsx

### Price Alert Modal (`frontend/src/components/ui/price-alert-modal.tsx`)
- **Modal exists** with form fields
- **API integration exists** but flow is disconnected from product cards
- **Bell icon exists** in product-card.tsx but not wired to modal

### Product Card (`frontend/src/components/ui/product-card.tsx`)
- **Has Bell icon** present but not connected to price alert flow
- **"Detalhes" button** (fixed in Phase 28)
- **Card structure:** image, brand, name, price, specs, buttons

### API Client (`frontend/src/lib/api.ts`)
- **Price alert endpoints exist** in API client

### DESIGN.md
- **Exists at project root**
- **Contradictions:** Says "light-first" but app is dark, says "Inter" but uses Source Sans 3, says "Sentence case" but buttons are ALL CAPS
- **Has "warm-white" references** that should be removed
- **Font references wrong:** Should be Bebas Neue, Source Sans 3, JetBrains Mono

## Architecture Decisions

### Landing Overhaul: Extend existing IntersectionObserver pattern
- Already have IO pattern in stats section → reuse for staggered fade-in on all sections
- Add section background alternation: base → surface → base → elevated → base
- Fetch real paddle count from `/api/v1/paddles` for stats

### SEO: Next.js App Router metadata API
- Use `generateMetadata` for dynamic JSON-LD injection (already pattern exists in catalog detail)
- `app/sitemap.ts` and `app/robots.ts` follow Next.js conventions (no extra deps)
- JSON-LD via `<script type="application/ld+json">` in page components

### Footer: Extend existing 4-column grid
- Already has grid-cols-4, just needs content filled in all columns
- Add: Quiz, Catalog, Compare, Gift, Blog links + social icons

### Price Alerts: Wire existing components
- Bell icon in product-card → onClick opens price-alert-modal
- Modal → POST /api/v1/price-alerts → toast feedback
- No new components needed, just wiring

### DESIGN.md: Full rewrite to match reality
- Dark theme, correct fonts, correct color tokens
- Remove all "light-first" and "warm-white" references
- Match actual component implementations

## Common Pitfalls

1. **JSON-LD in Next.js App Router:** Must use `dangerouslySetInnerHTML` or script tags, cannot use React components
2. **Sitemap in Next.js 14:** Export default function from `app/sitemap.ts` that returns `MetadataRoute.Sitemap`
3. **IntersectionObserver:** Must cleanup observers on unmount, respect `prefers-reduced-motion`
4. **Landing animations:** Stagger delays must be subtle (100-200ms) to feel polished, not distracting
5. **Footer links:** Use Next.js Link component, not anchor tags for internal routes
6. **Price alerts modal:** Must handle unauthenticated state (redirect to sign in or show auth prompt)

## What NOT to Hand-roll
- JSON-LD generation — use structured data templates
- Sitemap generation — use Next.js built-in `MetadataRoute.Sitemap`
- Animation library — use CSS transitions + IntersectionObserver (no new deps)
