---
phase: 13-nvidia-ui-redesign
plan: "01"
subsystem: frontend-design-tokens
tags: [css, design-tokens, typography, nvidia, fonts]
dependency_graph:
  requires: []
  provides: [css-custom-properties, nvidia-typography-scale, font-awesome-cdn, nvidia-font-stack]
  affects: [frontend/src/app/globals.css, frontend/src/app/layout.tsx]
tech_stack:
  added: [Font Awesome 6 CDN, NVIDIA-EMEA @font-face]
  patterns: [CSS custom properties on :root, shadcn compatibility shims]
key_files:
  created: []
  modified:
    - frontend/src/app/globals.css
    - frontend/src/app/layout.tsx
decisions:
  - Used cdnjs Font Awesome 6 Free CDN (no kit ID required) instead of kit.fontawesome.com
  - Kept shadcn compatibility shims (--background, --foreground, etc.) so existing Tailwind bg-background/text-foreground classes continue to work
  - @font-face uses local() sources only (Arial fallback) since NVIDIA-EMEA is not a hosted web font
  - Added explicit <head> element in RootLayout (Next.js App Router allows this alongside metadata export)
metrics:
  duration: "1 min"
  completed_date: "2026-04-02"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 2
---

# Phase 13 Plan 01: Design Tokens & Typography Foundation Summary

**One-liner:** NVIDIA brand CSS custom properties (20+ color vars, spacing scale, typography) plus Font Awesome 6 CDN and NVIDIA-EMEA font-family replacing Inter/lime palette.

## What Was Built

### Task 1 — NVIDIA design tokens in globals.css (commit 9334be4)

Replaced the shadcn HSL lime/amber `:root` block with the full NVIDIA token system:

- **20+ color vars:** `--color-green: #76b900`, neutrals, extended brand, semantics, decorative, interactive states
- **Typography:** 4-size scale (1.50rem/1.00rem/0.875rem/0.75rem), weights 400/700 only
- **Spacing:** `--space-xs` through `--space-4xl`, plus `--space-button-v: 11px` / `--space-button-h: 13px`
- **Border, shadow, layout:** `--radius-standard: 2px`, `--shadow-standard`, `--max-content-width: 1200px`
- **nv-* utility classes:** display, subheading, body, button-label, link, caption, section-label, container, dark/light section, image treatment
- **Focus rings:** overridden to `outline: 2px solid #000000` per NVIDIA WCAG spec
- **Shadcn shims:** `--background`, `--foreground`, etc. remapped to NVIDIA black/white palette so existing Tailwind classes continue working

### Task 2 — Font Awesome CDN and NVIDIA font in layout.tsx (commit 18597c8)

- Removed `Inter` next/font import and `inter.variable` class
- Added explicit `<head>` with Font Awesome 6 Free CDN (cdnjs.cloudflare.com)
- Applied `style={{ fontFamily: "'NVIDIA-EMEA', Arial, Helvetica, sans-serif" }}` to `<html>`
- Removed `font-sans` from body className

## Decisions Made

1. **cdnjs vs kit:** Used `cdnjs.cloudflare.com/libs/font-awesome/6.5.0/css/all.min.css` — no kit ID needed, reliably public.
2. **Shadcn shims retained:** `--background: 0 0% 0%` (black) and `--foreground: 0 0% 100%` (white) map to NVIDIA palette, keeping all downstream `bg-background`/`text-foreground` Tailwind classes valid without touching component files.
3. **@font-face local() only:** NVIDIA-EMEA is a brand font not distributed via CDN; `local()` references with Arial fallback give correct behavior when font is installed, graceful fallback otherwise.
4. **suppressHydrationWarning removed:** The original layout did not have it; not added.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — this plan only establishes CSS custom properties and font loading. No UI rendering involved.

## Self-Check: PASSED

- FOUND: frontend/src/app/globals.css
- FOUND: frontend/src/app/layout.tsx
- FOUND commit: 9334be4 (globals.css)
- FOUND commit: 18597c8 (layout.tsx)
