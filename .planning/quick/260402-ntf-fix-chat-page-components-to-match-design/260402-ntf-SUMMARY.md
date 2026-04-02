---
gsd_version: 1.0
phase: quick
plan: 260402-ntf
status: complete
completed_date: 2026-04-02
---

# Quick Task: Fix Chat Page Components to Match Design - Summary

**Objective:** Align chat components with DESIGN.md specifications

## One-liner

Fixed ProductCard CTA, added PickleIQ avatar to messages, and implemented inline error retry per DESIGN.md spec.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | ProductCard CTA matches DESIGN.md | da4149a | product-card.tsx |
| 2 | Add PickleIQ avatar to assistant messages | 1948c79 | message-bubble.tsx |
| 3 | Error handling with inline retry | 99c135f | chat-widget.tsx |
| 4 | Welcome message with avatar | b181a6e | chat-widget.tsx |

## Changes Made

### ProductCard (`product-card.tsx`)
- Changed button text from "Comprar" to "VER NO SITE →"
- Updated aria-label to "Ver {name} no site"
- Added "Por que essa raquete?" section with fallback reason
- Image placeholder now 80x80 per DESIGN.md spec
- Combined brand + name on single line

### MessageBubble (`message-bubble.tsx`)
- Added circular avatar with "PI" initials for assistant messages
- Avatar appears left-aligned per DESIGN.md spec
- User messages remain right-aligned without avatar

### ChatWidget (`chat-widget.tsx`)
- Error message now shows "⚠️ Erro ao carregar. [Tentar novamente]" with inline retry button
- Added avatar to loading indicator for consistency
- Added avatar to welcome message
- Implemented retry functionality that resubmits last message

## Deviations from Plan

None - plan executed exactly as intended.

## Verification

- Visual comparison against DESIGN.md Chat Widget spec completed
- All components render correctly with avatar
- Accessibility: aria-labels present on all CTAs
- Error handling matches DESIGN.md pattern

## Files Modified

- `frontend/src/components/chat/product-card.tsx`
- `frontend/src/components/chat/message-bubble.tsx`
- `frontend/src/components/chat/chat-widget.tsx`