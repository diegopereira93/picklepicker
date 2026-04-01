# Third-Party Script Inventory

**Generated:** 2026-04-01
**Phase:** 11.2 — Font & Script Optimization

## Script Inventory

| Script | Purpose | Current Loading | Classification | Recommended Strategy |
|--------|---------|-----------------|----------------|----------------------|
| @clerk/nextjs | Authentication | npm import + ClerkProvider | Critical | Keep as-is (required for auth) |
| @vercel/speed-insights | RUM / Performance monitoring | npm import + component | Non-critical | afterInteractive |

## Analysis

### Critical Scripts (Required for core functionality)

#### @clerk/nextjs
- **Purpose:** User authentication, session management, protected routes
- **Current loading:** NPM package imported and used via ClerkProvider
- **Impact:** Required for auth state; blocks protected routes
- **Strategy:** Keep eager loading — auth is critical to app functionality
- **Location:** `frontend/src/app/layout.tsx` (root layout)

### Non-Critical Scripts (Can be deferred)

#### @vercel/speed-insights
- **Purpose:** Real user monitoring (RUM) for Core Web Vitals tracking
- **Current loading:** Component imported and rendered in layout
- **Impact:** Nice-to-have analytics, not blocking user experience
- **Strategy:** Load with `afterInteractive` strategy
- **Location:** `frontend/src/app/layout.tsx` (body end)

## Script Loading Strategy Reference

| Strategy | When it loads | Use for |
|----------|---------------|---------|
| `beforeInteractive` | Before page becomes interactive | Critical analytics, A/B testing |
| `afterInteractive` | After page becomes interactive | Widgets, non-critical UI enhancements |
| `lazyOnload` | When browser becomes idle | Analytics, tracking, non-essential scripts |

## Recommendations

1. **Clerk**: Keep current eager loading — auth is critical
2. **Speed Insights**: Already loaded at end of body, consider wrapping in Suspense or using dynamic import

## Notes

- No external `<script>` tags found in codebase — all third-party scripts use npm packages
- SpeedInsights is already positioned at end of body (line 62), minimizing render-blocking impact
- No Google Analytics, Facebook Pixel, or other marketing scripts detected
