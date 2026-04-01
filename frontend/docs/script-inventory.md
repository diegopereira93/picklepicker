# Third-Party Script Inventory

Generated: 2026-04-01

## Script Inventory

| Script | Purpose | Current Loading | Classification | Recommended Strategy |
|--------|---------|-----------------|----------------|---------------------|
| @clerk/nextjs | Authentication | npm import (ClerkProvider) | Critical | Keep as-is (required for auth) |
| @vercel/speed-insights | Performance monitoring | dynamic import with ssr: false | Non-critical | Already optimized - consider next/script wrapper |

## Analysis

### Current State
- Clerk: Loaded via npm package in layout.tsx, wrapped in ClerkProvider - this is the recommended approach
- SpeedInsights: Loaded via dynamic import with ssr: false - good for deferring load

### Recommendations Applied
1. **SpeedInsights**: Already using dynamic import which defers loading until after hydration
2. **Clerk**: Critical for auth, should remain eager loaded via ClerkProvider

### Next/Script Migration
For additional third-party scripts that may be added in the future:
- Use `next/script` with `strategy="lazyOnload"` for analytics/tracking
- Use `strategy="afterInteractive"` for non-critical widgets
- Use `strategy="beforeInteractive"` only for truly critical scripts

## Font Loading Strategy Documentation

### Primary Font (Inter)
- **Display**: swap (immediate text visibility)
- **Fallback**: system-ui, sans-serif (minimizes FOUT)
- **Subsets**: Latin only
- **Preload**: true (critical font preloaded)
- **adjustFontFallback**: true (reduces layout shift)

### Loading Order
1. System font fallback displays immediately
2. Google Font loads in background
3. Font swap happens when loaded (no invisible text)
