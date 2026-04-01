# Phase 10: Performance & UX Polish

## Goal

Improve perceived performance, accessibility, and user experience across the PickleIQ platform. Focus on Core Web Vitals, animation system implementation, and dark mode completion.

## Success Criteria

- [ ] LCP < 2.5s, CLS < 0.1, FID < 100ms on all key pages
- [ ] Motion system implemented (chat messages, quiz transitions, product cards)
- [ ] Dark mode fully functional with brand colors preserved
- [ ] Accessibility audit: WCAG 2.1 AA compliance
- [ ] Design system v1.1 fully implemented in code

## Context

- DESIGN.md v1.1 defines motion system and dark mode brand colors
- globals.css has dark mode variables but they need verification
- No animation library currently in use
- Core Web Vitals not yet measured

## Tasks

### Task 1: Core Web Vitals Optimization
**Scope:** Implement performance monitoring and optimizations
**UAT:**
- [ ] Lighthouse score ≥ 90 on /, /chat, /paddles
- [ ] Images use next/image with proper sizing
- [ ] Fonts use next/font with display: swap
- [ ] Critical CSS inlined

### Task 2: Motion System Implementation
**Scope:** Implement DESIGN.md motion system
**UAT:**
- [ ] Chat messages animate in with message-enter keyframes
- [ ] Quiz cards have selection transitions
- [ ] Product cards have hover lift effect
- [ ] All animations respect prefers-reduced-motion

### Task 3: Dark Mode Completion
**Scope:** Verify and fix dark mode implementation
**UAT:**
- [ ] Dark mode toggle works across all pages
- [ ] Lime brand color visible in dark mode
- [ ] No color contrast issues in dark mode
- [ ] Toggle state persisted in localStorage

### Task 4: Accessibility Audit
**Scope:** WCAG 2.1 AA compliance pass
**UAT:**
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible
- [ ] Color contrast passes everywhere
- [ ] Screen reader labels on all icons
- [ ] axe-core tests pass in CI

## Verification

Run `npm run lighthouse` and verify all thresholds met.
Test dark mode toggle on every page.
Tab through entire user flow keyboard-only.

## Files to Modify

- frontend/src/app/globals.css
- frontend/src/components/chat/message-bubble.tsx
- frontend/src/components/quiz/*.tsx
- frontend/src/components/chat/product-card.tsx
- frontend/tailwind.config.ts (add animation utilities)

## Blockers

None — this phase is self-contained.

## Notes

Design system v1.1 already documents all requirements. This phase is about implementation and verification.
