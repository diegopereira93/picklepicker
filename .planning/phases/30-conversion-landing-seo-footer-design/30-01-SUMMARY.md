---
phase: 30-conversion-landing-seo-footer-design
plan: 01
status: completed
date: 2026-04-20
---

# Phase 30-01 Summary: SEO Infrastructure + DESIGN.md Rewrite

## What Was Done

### Task 1: sitemap.ts ✅
- Created `frontend/src/app/sitemap.ts` using Next.js 14 `MetadataRoute.Sitemap`
- Static routes: /, /catalog, /quiz, /chat, /gift, /compare, /blog
- Dynamic routes: fetches up to 500 paddles via `fetchPaddles`, generates `/catalog/[model_slug]` entries
- Graceful fallback: if API fails, static routes still returned
- Priority: 1.0 (home), 0.9 (catalog), 0.7-0.8 (quiz/chat/compare), 0.5-0.6 (gift/blog)

### Task 2: robots.ts ✅
- Created `frontend/src/app/robots.ts` using `MetadataRoute.Robots`
- Allows all crawlers on /
- Disallows /admin/ and /api/
- Points to https://pickleiq.com/sitemap.xml

### Task 3: DESIGN.md Rewrite ✅
- Complete rewrite from v4.0 (Warm Guide) to v5.0 (Dark Premium Sports Analytics)
- All contradictions fixed:
  - "light-first" → dark-only (bg-base #0a0a0a)
  - "Inter" → Source Sans 3
  - "warm-white/cream/charcoal" → base/surface/elevated dark hierarchy
  - Product cards #ffffff → bg-surface #141414
  - Button coral → brand-primary #84CC16 (lime)
  - Font loading via `<link>` → next/font/google with CSS variables
  - Removed "When to Use Dark Mode" table entirely
- Retained sections: Spacing System, Border Radius, Quiz Specification, Accessibility, AI Slop Checklist, Decisions Log
- Added: Box Shadows section, Tailwind Animations table, accurate contrast ratios

## Verification Results

| Check | Result |
|-------|--------|
| `npm run build` | ✅ Passes (23 static pages generated, /robots.txt + /sitemap.xml visible) |
| sitemap.ts contains MetadataRoute.Sitemap | ✅ |
| robots.ts contains MetadataRoute.Robots | ✅ |
| DESIGN.md "light-first" (non-changelog) | ✅ 0 matches |
| DESIGN.md "warm-white" (non-changelog) | ✅ 0 matches |
| DESIGN.md "Source Sans 3" | ✅ Multiple matches |
| DESIGN.md "Bebas Neue" | ✅ Multiple matches |
| DESIGN.md "#0a0a0a" | ✅ Multiple matches |
| Pre-existing TS errors only | ✅ use-announcer.ts (not modified) |

## Files Modified

| File | Action |
|------|--------|
| `frontend/src/app/sitemap.ts` | Created |
| `frontend/src/app/robots.ts` | Created |
| `DESIGN.md` | Complete rewrite (v4.0 → v5.0) |
