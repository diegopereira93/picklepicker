# v1.2 Requirements

## Milestone Overview

**Name:** Polish & Performance
**Theme:** Incremental improvements to UX, performance, and accessibility
**Duration:** ~2 weeks
**Successor:** v1.3 (Feature Expansion — TBD)

## Problem Statement

v1.1 delivered core functionality with E2E testing and scraper validation. However, several UX rough edges remain:
- No animation/motion system implemented
- Dark mode partially implemented but incomplete
- Core Web Vitals not optimized
- Accessibility not formally audited
- Design system v1.1 (motion, spacing) not implemented in code

## Goals

1. **Performance:** Achieve "Good" Core Web Vitals across all key pages
2. **Motion:** Implement DESIGN.md v1.1 motion system for polished interactions
3. **Dark Mode:** Complete dark mode with brand color preservation
4. **Accessibility:** WCAG 2.1 AA compliance

## Out of Scope

- New features (price alerts, notifications)
- Backend changes
- New scrapers
- Marketing/SEO features

## Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| Lighthouse Performance | ≥ 90 | Not measured |
| LCP | < 2.5s | Unknown |
| CLS | < 0.1 | Unknown |
| axe-core violations | 0 | Unknown |
| Dark mode coverage | 100% | ~50% |

## Phases

### Phase 10: Performance & UX Polish
- Core Web Vitals optimization
- Motion system implementation
- Dark mode completion
- Accessibility audit

## Acceptance Criteria

- [ ] User can toggle dark mode and see brand colors (lime) preserved
- [ ] Chat messages animate smoothly on arrival
- [ ] Quiz transitions feel polished
- [ ] All pages pass Lighthouse performance audit
- [ ] Keyboard navigation works throughout app
- [ ] Screen reader announces chat messages correctly

## Decisions Needed

None — requirements are clear from DESIGN.md v1.1

## References

- DESIGN.md v1.1 (motion system, dark mode colors)
- globals.css (existing dark mode variables)
- Current pages: /, /chat, /paddles, /compare, /admin/*
