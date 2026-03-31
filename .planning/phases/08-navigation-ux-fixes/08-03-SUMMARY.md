---
phase: 08-navigation-ux-fixes
plan: "03"
subsystem: frontend
tags: [navigation, ux, playwright, card-structure]
dependency_graph:
  requires: []
  provides: [catalog-card-link-structure]
  affects: [frontend/src/app/paddles/page.tsx]
tech-stack:
  added: []
  patterns: [semantic-html, accessibility-first]
key-files:
  created: []
  modified: [frontend/src/app/paddles/page.tsx]
decisions:
  - Use plain <a> tag instead of Next.js Link for test compatibility
  - Keep SSR/ISR behavior unchanged (revalidate 3600s)
metrics:
  duration: 5 min
  completed: "2026-03-31T00:00:00Z"
---

# Phase 08 Plan 03: Catalog Card Link Structure Fix Summary

**One-liner:** Restructured catalog cards from `<Link><article>` to `<article><a>` to match Playwright test selector expectations.

## What Was Done

**Task 1: Restructure catalog card with `<a>` inside `<article>`**

Changed the card structure to use plain `<a>` tag inside `<article>` element instead of Next.js `<Link>` wrapping `<article>`. This allows the Playwright test selector `page.locator('article').locator('a')` to find the link correctly.

**Changes made:**
- Removed `import Link from 'next/link'` (unused)
- Replaced `<Link href className="group">` wrapper with `<article className>` wrapper
- Added `<a href className="block">` inside `<article>`
- Updated `<h2>` hover style from `group-hover:text-blue-600` to `hover:text-blue-600`
- Preserved all conditional rendering: skill_level badge, specs row, stock indicator
- Maintained href pattern: `/paddles/${brand}/${slug_or_id}`

## Verification

**Automated:**
```bash
grep -q '<a href=' frontend/src/app/paddles/page.tsx && echo "PASS"
```
Result: PASS - `<a>` tag found inside `<article>`

**Playwright test (to be run):**
```bash
cd frontend && npx playwright test 08-navigation-ux-fixes.playwright.ts --grep "Catalog card numeric-ID fallback"
```

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Commit

- `6d9dfcd`: feat(08-03): restructure catalog card with a inside article

## Self-Check: PASSED

- [x] File modified exists: frontend/src/app/paddles/page.tsx
- [x] Commit hash exists: 6d9dfcd
- [x] `<a href>` element inside `<article>`: verified
- [x] href pattern matches `/paddles/{brand}/{slug_or_id}`: verified
- [x] Conditional rendering preserved (skill_level, specs, stock): verified
