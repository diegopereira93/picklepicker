---
phase: 08-navigation-ux-fixes
plan: GAP-02
type: gap_closure
subsystem: frontend
key_files:
  modified:
    - frontend/src/app/paddles/page.tsx
must_haves:
  truths:
    - "Catalog cards have proper <a> links with href attribute"
    - "Test selectors can find card links via data-testid"
---

# Phase 08 Gap Closure GAP-02: Catalog Card Link Structure Fix

## Summary

Fixed catalog card link structure to ensure test selectors can find and interact with paddle cards. The `<a>` element now has proper `data-testid="paddle-card-link"` attribute for reliable test targeting.

## Changes Made

### Modified Files

| File | Change |
|------|--------|
| `frontend/src/app/paddles/page.tsx` | Added `data-testid="paddle-card-link"` to card links, moved padding to `<a>` element, added `overflow-hidden` to `<article>` |

### Code Changes

**Before:**
```tsx
<article
  key={paddle.id}
  className="border rounded-lg p-4 hover:shadow-md transition-shadow"
>
  <a
    href={`/paddles/...`}
    className="block"
  >
```

**After:**
```tsx
<article
  key={paddle.id}
  className="border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
>
  <a
    href={`/paddles/...`}
    className="block p-4"
    data-testid="paddle-card-link"
  >
```

## Key Improvements

1. **Test Selector Support**: Added `data-testid="paddle-card-link"` for reliable Playwright test targeting
2. **Better Click Target**: Moved padding from `<article>` to `<a>` so the entire card area is clickable
3. **Visual Polish**: Added `overflow-hidden` to `<article>` for proper border-radius clipping

## Verification

- [x] `data-testid="paddle-card-link"` attribute present on card links
- [x] `<a>` element has proper `href` pointing to `/paddles/{brand}/{slug}`
- [x] All card content (image, name, brand, badges) remains inside the `<a>` tag
- [x] CSS classes properly distributed between `<article>` and `<a>`

## Commit

- **Hash:** `9ab1f06`
- **Message:** `fix(08-GAP-02): add data-testid to paddle card links for test selectors`

## Deviations

None - plan executed exactly as written.
