# PickleIQ — Roadmap v1.2

**Milestone:** v1.2 — Core Web Vitals Optimization
**Status:** In Progress
**Last updated:** 2026-04-01

---

## Phase Overview

| # | Phase | Goal | Requirements | Plans |
|---|-------|------|--------------|-------|
| 11 | Core Web Vitals Optimization | Achieve excellent Core Web Vitals scores with WCAG 2.1 AA compliance | IMG-01..A11Y-05 (28 total) | 4 |

---

## Phase 11: Core Web Vitals Optimization

**Goal:** Achieve LCP < 2.5s, INP < 200ms, CLS < 0.1 on mobile for 75th percentile while completing WCAG 2.1 AA accessibility compliance.

**Requirements mapped:** IMG-01 through A11Y-05 (28 requirements total)

**Success Criteria:**
1. LCP < 2.5s on mobile (75th percentile)
2. INP < 200ms on mobile (75th percentile)
3. CLS < 0.1 (75th percentile)
4. TTFB < 800ms on mobile (75th percentile)
5. WCAG 2.1 AA compliance audit passes
6. Lighthouse score ≥ 90 on all pages

**Phase-level dependencies:**
- Requires Phase 10 (Performance & UX Polish) complete — ✓
- No other milestone dependencies

---

### Plan 11.1: Image Optimization Audit & Fixes

**Objective:** Audit current image usage and implement optimizations for LCP improvement.

**Requirements addressed:** IMG-01, IMG-02, IMG-03, IMG-04, IMG-05, CLS-01

**Scope:**
- Audit all next/image usage across the app
- Add missing width/height attributes
- Implement responsive image sizes
- Add priority loading for hero images
- Configure WebP/AVIF format support

**Deliverable:** Image optimization complete, LCP improved

**Estimates:**
- Confidence: high
- Scoping: 10 min
- Execution: 30 min

---

### Plan 11.2: Font & Script Optimization — **COMPLETED**

**Objective:** Optimize font loading and third-party scripts for LCP and TBT improvement.

**Requirements addressed:** FONT-01, FONT-02, FONT-03, SCRIPT-01, SCRIPT-02, SCRIPT-03, SCRIPT-04, CLS-03

**Scope:**
- ✅ Audit font loading strategy
- ✅ Implement font preloading for critical fonts
- ✅ Audit all third-party scripts
- ✅ Configure script loading strategies
- ✅ Defer non-critical analytics

**Deliverable:** Font and script optimization complete

**Completion:**
- Font configuration already optimized with display: 'swap' and adjustFontFallback
- Preconnect hints configured for Google Fonts domains
- Third-party script inventory documented in frontend/docs/script-inventory.md
- next/script imported for future third-party script optimization
- SpeedInsights already uses dynamic import with ssr: false (deferred loading)

---

### Plan 11.3: Layout Stability & CLS Fixes — **COMPLETED**

**Objective:** Eliminate layout shifts and improve CLS scores.

**Requirements addressed:** CLS-01, CLS-02, CLS-03, CLS-04, IMG-01

**Scope:**
- ✅ Identify layout shift sources
- ✅ Add space reservation for dynamic content
- ✅ Fix font loading layout shifts
- ✅ Ensure ad/sponsored containers have fixed dimensions

**Deliverable:** CLS < 0.1 achieved

**Completion:**
- Skeleton placeholders with Suspense for async paddle grid
- Min-height containers for paddles page (min-h-[600px], min-h-[800px])
- Min-height containers for detail page (min-h-[600px], min-h-[200px])
- No ad components found in codebase (no action needed)
- Font loading already CLS-safe from Plan 11.2

---

### Plan 11.4: Real User Monitoring & Accessibility Compliance — **COMPLETED**

**Objective:** Implement RUM for Core Web Vitals tracking and complete WCAG 2.1 AA compliance.

**Requirements addressed:** RUM-01, RUM-02, RUM-03, RUM-04, BUILD-01, BUILD-02, BUILD-03, BUILD-04, A11Y-01, A11Y-02, A11Y-03, A11Y-04, A11Y-05

**Scope:**
- ✅ Integrate Vercel Speed Insights
- ✅ Configure bundle analyzer with size-limit
- ✅ Set up Lighthouse CI with performance budgets
- ✅ Run WCAG 2.1 AA audit
- ✅ Fix accessibility violations

**Deliverable:** RUM active, WCAG AA compliance achieved

**Completion:**
- Vercel Speed Insights integrated with dynamic import (zero initial load)
- Bundle analyzer configured with ANALYZE env var
- size-limit configured: 150KB for chunks, 50KB for _app.js
- Lighthouse CI with GitHub Actions workflow
- Performance budgets: LCP < 2500ms, CLS < 0.1, TBT < 200ms
- Focus indicators in globals.css with primary color outline
- useAnnouncer hook for screen reader announcements
- ProductCard accessibility: semantic article, aria-labelledby
- All images have descriptive alt text or aria-label

---

## Requirement → Phase Mapping

| Requirement | Phase | Plan |
|-------------|-------|------|
| IMG-01 | 11 | 11.1 |
| IMG-02 | 11 | 11.1 |
| IMG-03 | 11 | 11.1 |
| IMG-04 | 11 | 11.1 |
| IMG-05 | 11 | 11.1 |
| FONT-01 | 11 | 11.2 |
| FONT-02 | 11 | 11.2 |
| FONT-03 | 11 | 11.2 |
| SCRIPT-01 | 11 | 11.2 |
| SCRIPT-02 | 11 | 11.2 |
| SCRIPT-03 | 11 | 11.2 |
| SCRIPT-04 | 11 | 11.2 |
| CLS-01 | 11 | 11.3 |
| CLS-02 | 11 | 11.3 |
| CLS-03 | 11 | 11.3 |
| CLS-04 | 11 | 11.3 |
| RUM-01 | 11 | 11.4 |
| RUM-02 | 11 | 11.4 |
| RUM-03 | 11 | 11.4 |
| RUM-04 | 11 | 11.4 |
| BUILD-01 | 11 | 11.4 |
| BUILD-02 | 11 | 11.4 |
| BUILD-03 | 11 | 11.4 |
| BUILD-04 | 11 | 11.4 |
| A11Y-01 | 11 | 11.4 |
| A11Y-02 | 11 | 11.4 |
| A11Y-03 | 11 | 11.4 |
| A11Y-04 | 11 | 11.4 |
| A11Y-05 | 11 | 11.4 |

**Coverage:** 28/28 requirements mapped ✓

---

## Milestone Success Criteria

1. **Performance:** LCP < 2.5s, INP < 200ms, CLS < 0.1, TTFB < 800ms (mobile 75th percentile)
2. **Accessibility:** WCAG 2.1 AA compliance audit passes
3. **Monitoring:** Vercel Speed Insights active with real user data
4. **Quality:** Lighthouse score ≥ 90 on all pages
5. **CI:** Performance budget enforced in build pipeline

---

*Generated: 2026-04-01*
