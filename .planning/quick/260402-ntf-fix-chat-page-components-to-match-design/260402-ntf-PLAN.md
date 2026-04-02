---
gsd_version: 1.0
type: quick
status: executing
created: 2026-04-02
---

# Quick Task: Fix Chat Page Components to Match Design

**Objective:** Align chat components with DESIGN.md specifications

## Context

Chat components (ProductCard, MessageBubble, ChatWidget) have drifted from DESIGN.md:
- ProductCard missing "Por que essa raquete?" section, wrong CTA text
- MessageBubble missing PickleIQ avatar for assistant messages
- ChatWidget error handling doesn't match DESIGN.md inline retry pattern

## Tasks

### Task 1: Fix ProductCard CTA and layout
- [ ] Change button text from "Comprar" to "VER NO SITE →"
- [ ] Update aria-label to "Ver {name} no site"
- [ ] Add "Por que essa raquete?" section with fallback reason
- [ ] Commit: `fix(chat): ProductCard CTA matches DESIGN.md`

### Task 2: Add PickleIQ avatar to MessageBubble
- [ ] Add avatar for assistant messages (left-aligned)
- [ ] Use circular avatar with "PI" initials or icon
- [ ] Commit: `feat(chat): add PickleIQ avatar to assistant messages`

### Task 3: Fix ChatWidget error handling
- [ ] Change error message to match DESIGN.md: "⚠️ Erro ao carregar. [Tentar novamente]"
- [ ] Add inline retry button
- [ ] Commit: `fix(chat): error handling with inline retry per DESIGN.md`

### Task 4: Update ChatPage welcome message
- [ ] Add avatar to initial welcome message
- [ ] Commit: `fix(chat): welcome message with avatar`

## Verification

- Visual comparison against DESIGN.md Chat Widget spec
- All components render correctly
- Accessibility: aria-labels present