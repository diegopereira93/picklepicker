---
phase: 13-nvidia-ui-redesign
plan: 06
subsystem: frontend/ui
tags: [button, border-color, hybrid-design, gap-closure]
requires: [HY-04]
provides: [correct-lime-borders]
affects: [button-variants]
key_files:
  created: []
  modified:
    - frontend/src/components/ui/button.tsx
tech_stack:
  added: []
  patterns: [Hybrid Design System, CSS color tokens]
duration: 2 min
completed: 2026-04-02
---

# Phase 13 Plan 06: Button Border Color Fix Summary

## One-liner

Fixed button border colors to use lime (#84CC16) instead of data-green (#76b900) per HY-04 specification, preserving data-green for link text and light variant hover states.

## What Changed

Updated `frontend/src/components/ui/button.tsx` to correct the border color across all button variants:

| Variant | Before | After | Notes |
|---------|--------|-------|-------|
| default | `border-[#76b900]` | `border-[#84CC16]` | Primary action button |
| secondary | `border-[#76b900]` | `border-[#84CC16]` | Secondary action button |
| light | `border-[#76b900]` | `border-[#84CC16]` | Hover bg remains `#76b900` |
| compact | `border-[#76b900]` | `border-[#84CC16]` | Compact variant |
| outline | `border-[#76b900]` | `border-[#84CC16]` | Outline variant |

**Preserved (correct):**
- `link` variant: `text-[#76b900]` — data-green for link text color
- `light` variant: `hover:bg-[#76b900]` — data-green hover background on light backgrounds

## Verification Results

```bash
# Border colors updated
$ grep -c 'border-\[#84CC16\]' button.tsx
5  # All 5 variants with borders

# No data-green borders remain
$ grep -c 'border-\[#76b900\]' button.tsx
0  # Zero remaining

# Link text color preserved
$ grep -c 'text-\[#76b900\]' button.tsx
1  # Link variant only

# Light hover preserved
$ grep -c 'hover:bg-\[#76b900\]' button.tsx
1  # Light variant only
```

## Deviations from Plan

None — plan executed exactly as specified.

## Files Modified

- `frontend/src/components/ui/button.tsx` — 5 border color replacements across 5 button variants

## Commit

`d6d15c3` — fix(13-06): use lime (#84CC16) for button borders per HY-04

## Task Completion

| Task | Name | Status | Commit |
|------|------|--------|--------|
| 1 | Replace #76b900 with #84CC16 in button variants | Complete | d6d15c3 |

## Self-Check

- [x] Created file exists: `frontend/src/components/ui/button.tsx` (modified)
- [x] Commit exists: `d6d15c3`
- [x] All acceptance criteria verified via grep