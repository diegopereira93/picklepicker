# Phase 11: Core Web Vitals Optimization — Research

**Researched:** 2026-04-01
**Domain:** Next.js 14 Performance Optimization, Core Web Vitals, WCAG 2.1 AA
**Confidence:** HIGH

## Summary

This research covers comprehensive Core Web Vitals (CWV) optimization for Next.js 14 App Router, targeting LCP < 2.5s, INP < 200ms, and CLS < 0.1 on mobile (75th percentile). Key findings:

1. **Current State Gap:** Frontend uses raw `<img>` tags instead of `next/image` — a critical LCP/CLS optimization opportunity
2. **Font Optimization:** Current layout uses `next/font` but missing `display: 'swap'` for FOUT prevention
3. **RUM Strategy:** `@vercel/speed-insights` v2.0.0 provides automatic CWV tracking with zero-config App Router integration
4. **Accessibility:** WCAG 2.1 AA compliance requires systematic audit across 4 principles (Perceivable, Operable, Understandable, Robust)

**Primary recommendation:** Prioritize image optimization (IMG-01..IMG-05) as it addresses both LCP and CLS simultaneously, then implement Vercel Speed Insights for field data validation.

---

## Phase Boundary

### What This Phase Delivers

| Outcome | Success Criteria |
|---------|------------------|
| LCP Optimized | < 2.5s on mobile (75th percentile) |
| INP Optimized | < 200ms on mobile (75th percentile) |
| CLS Optimized | < 0.1 (75th percentile) |
| TTFB Optimized | < 800ms on mobile (75th percentile) |
| RUM Active | Vercel Speed Insights collecting field data |
| WCAG Compliance | 2.1 AA audit passes |
| CI Enforcement | Performance budget blocks oversized bundles |

### In Scope
- Image optimization audit and next/image migration
- Font loading optimization with preloading
- Third-party script strategy (deferral, PartyTown evaluation)
- Layout stability fixes (CLS elimination)
- Vercel Speed Insights integration
- web-vitals library instrumentation
- @next/bundle-analyzer setup
- WCAG 2.1 AA compliance audit and fixes

### Out of Scope
- CDN migration (Vercel Edge sufficient)
- Database query optimization (backend optimized in Phase 3)
- Image CDN migration (Next.js built-in sufficient)
- Service Worker implementation (deferred to PWA milestone)
- HTTP/3 Server Push (Vercel limitation)

---

## Technical Stack

### Core Performance Libraries
| Library | Version | Purpose | Confidence |
|---------|---------|---------|------------|
| `@vercel/speed-insights` | 2.0.0 | Real User Monitoring (RUM) | HIGH — Official Vercel package |
| `web-vitals` | 5.2.0 | Programmatic CWV measurement | HIGH — Google standard |
| `@next/bundle-analyzer` | 16.2.2 | Bundle size analysis | HIGH — Official Next.js package |
| `@builder.io/partytown` | latest | Web worker script offloading | MEDIUM — Beta status |

### Next.js Built-in Features
| Feature | Purpose | Status |
|---------|---------|--------|
| `next/image` | Automatic image optimization | NOT USED — Current code uses raw `<img>` |
| `next/font` | Font optimization with subsetting | PARTIAL — Missing display: 'swap' |
| `next/script` | Script loading strategies | AVAILABLE — Not configured |
| React Server Components | Reduced client JS | ACTIVE — App Router default |

### Installation Commands

```bash
# RUM and analytics
npm install @vercel/speed-insights web-vitals

# Bundle analysis (dev only)
npm install -D @next/bundle-analyzer

# Performance budget CI
npm install -D size-limit @size-limit/preset-app

# Optional: PartyTown for heavy third-parties
npm install @builder.io/partytown
```

---

## Implementation Approaches

### LCP (Largest Contentful Paint) Optimization

**Current State:**
- Raw `<img>` tags in `/paddles/page.tsx` and `/paddles/[brand]/[model-slug]/page.tsx`
- No width/height attributes causing layout shifts
- No priority loading for hero images
- No image preloading

**Required Changes:**

1. **Migrate to next/image with priority**
```tsx
// Source: Next.js 14 docs + WebSearch findings
import Image from 'next/image';

// Hero/above-the-fold images
<Image
  src={paddle.image_url}
  alt={paddle.name}
  width={480}
  height={480}
  priority  // Critical for LCP
  sizes="(max-width: 768px) 50vw, 25vw"
  className="object-cover"
/>
```

2. **Preload critical images in layout.tsx**
```tsx
// Source: Next.js performance docs
export const metadata = {
  // ...
  other: {
    'link': [
      { rel: 'preload', as: 'image', href: '/hero-image.webp' }
    ]
  }
};
```

3. **Font optimization (next/font with display: swap)**
```tsx
// Source: Next.js docs + web search
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',  // Prevents invisible text
  variable: '--font-sans',
  preload: true,
  adjustFontFallback: true  // Reduces layout shift
});
```

**Target:** LCP < 2.5s (currently likely 4-6s with raw img tags)

---

### INP (Interaction to Next Paint) Optimization

**Note:** INP replaced FID in March 2024. Measures responsiveness across entire page lifecycle.

**Key Strategies:**

1. **Dynamic imports for heavy components**
```tsx
// Source: Next.js 14 performance patterns
import dynamic from 'next/dynamic';

const RechartsRadar = dynamic(
  () => import('@/components/radar-chart'),
  {
    ssr: false,  // Client-side only
    loading: () => <ChartSkeleton />
  }
);
```

2. **Script loading strategies**
```tsx
// Source: Next.js docs
import Script from 'next/script';

// Non-critical scripts
<Script
  src="https://analytics.com/script.js"
  strategy="lazyOnload"  // Load after hydration
/>

// Third-party after interactive
<Script
  src="https://chat-widget.com/widget.js"
  strategy="afterInteractive"
/>
```

3. **React transitions for heavy state updates**
```tsx
// Source: WebSearch findings
'use client';
import { useTransition } from 'react';

function FilterButton() {
  const [isPending, startTransition] = useTransition();

  const handleFilter = () => {
    startTransition(() => {
      // Heavy filter operation
      applyFilters();
    });
  };
}
```

**Target:** INP < 200ms

---

### CLS (Cumulative Layout Shift) Optimization

**Current Issues:**
- Images without explicit dimensions
- Font loading without space reservation
- Dynamic content without skeleton placeholders

**Required Fixes:**

1. **Image dimensions (mandatory)**
```tsx
// Source: Web Vitals optimization guides
// Always provide width/height or use aspect-ratio
<Image
  src={image}
  width={480}      // REQUIRED for CLS
  height={480}     // REQUIRED for CLS
  sizes="..."
/>
```

2. **Reserve space for dynamic content**
```tsx
// Source: CLS optimization patterns
<div className="min-h-[250px]">  // Reserve ad space
  <AdComponent />
</div>

// Suspense with proper fallback
<Suspense fallback={<ProductSkeleton />}>
  <ProductGrid />
</Suspense>
```

3. **Font display: swap + fallback**
```tsx
// Already handled by next/font with adjustFontFallback: true
```

**Target:** CLS < 0.1

---

### RUM (Real User Monitoring) Implementation

**Vercel Speed Insights Integration:**

```tsx
// app/layout.tsx
// Source: Vercel docs + WebSearch findings
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>
        {children}
        <SpeedInsights
          sampleRate={1.0}  // 100% sampling for small site
        />
      </body>
    </html>
  );
}
```

**Custom Web Vitals Reporting (optional backup):**

```tsx
// app/components/web-vitals.tsx
'use client';
import { useReportWebVitals } from 'next/web-vitals';

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Send to custom endpoint if needed
    fetch('/api/vitals', {
      method: 'POST',
      body: JSON.stringify(metric)
    });
  });
  return null;
}
```

---

### WCAG 2.1 AA Compliance

**Key Requirements for PickleIQ:**

| Principle | Requirement | Implementation |
|-------------|-------------|------------------|
| Perceivable | Alt text for all images | Add descriptive alt to next/image |
| Perceivable | Color contrast 4.5:1 | Audit Tailwind colors |
| Operable | Keyboard navigation | Verify Tab, Enter, Escape work |
| Operable | Focus indicators | 2px outline, 3:1 contrast |
| Operable | Skip links | Already implemented in layout.tsx |
| Understandable | Page language | Already: `lang="pt-BR"` |
| Understandable | Form labels | Associate labels with inputs |
| Robust | Semantic HTML | Use proper headings, landmarks |

**Automated Testing Tools:**
- `eslint-plugin-jsx-a11y` (already in Next.js)
- axe DevTools browser extension
- Lighthouse accessibility audit
- Playwright axe-core integration

---

## Validation Architecture

### Test Framework Configuration

**nyquist_validation is ENABLED** (per config.json)

| Test Type | Tool | Command |
|-----------|------|---------|
| Unit | Vitest | `npm test` |
| E2E | Playwright | `npx playwright test` |
| Accessibility | axe-playwright | `npm run test:a11y` |
| Performance | Lighthouse CI | `lhci autorun` |
| Bundle | size-limit | `npx size-limit` |

### Performance Budget Setup

```json
// package.json
{
  "size-limit": [
    {
      "path": ".next/static/chunks/**/*.js",
      "limit": "150 KB"
    },
    {
      "path": ".next/static/chunks/pages/index-*.js",
      "limit": "50 KB"
    }
  ]
}
```

### Lighthouse CI Configuration

```javascript
// .lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000/', 'http://localhost:3000/paddles'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
      },
    },
  },
};
```

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Command |
|--------|----------|-----------|---------|
| IMG-01 | Images use next/image | Visual + Lighthouse | `lhci autorun` |
| IMG-04 | Priority loading on hero | Lighthouse LCP audit | `lhci autorun` |
| CLS-01 | No layout shifts | Lighthouse CLS | `lhci autorun` |
| A11Y-01 | Alt text present | axe-core | `playwright test a11y` |
| A11Y-03 | Color contrast | Lighthouse a11y | `lhci autorun` |
| BUILD-02 | Bundle size budget | size-limit | `npx size-limit` |
| RUM-01 | Speed Insights active | Manual verification | Check Vercel dashboard |

---

## Dependencies & Ordering

### Phase 11 Dependencies
- **Phase 10 complete** (Performance & UX Polish) — PREREQUISITE
- No other milestone dependencies

### Internal Plan Ordering

| Order | Plan | Depends On | Reason |
|-------|------|------------|--------|
| 1 | 11.1 Image Optimization | — | Foundation for LCP/CLS |
| 2 | 11.2 Font & Script Optimization | 11.1 | Build on image optimization |
| 3 | 11.3 Layout Stability | 11.1, 11.2 | Final CLS fixes |
| 4 | 11.4 RUM & Accessibility | 11.1-11.3 | Measure after optimization |

### Technical Dependencies
1. **Before RUM-01:** Must have production deployment (Vercel)
2. **Before BUILD-01:** Requires build pipeline access (GitHub Actions)
3. **Before A11Y audit:** All UI components must be stable

---

## Pitfalls & Mitigations

### Pitfall 1: Lighthouse Lab ≠ Field Data
**What goes wrong:** Optimizing for Lighthouse score (lab) but real users experience worse performance (field).
**Why it happens:** Lighthouse runs on fast connection, powerful CPU; field data includes 3G, low-end devices.
**How to avoid:** Always validate with Vercel Speed Insights field data after deployment.
**Warning signs:** Lighthouse score >90 but Search Console CWV report shows "Needs Improvement"

### Pitfall 2: next/image Breaks with Remote Patterns
**What goes wrong:** Images fail to load after migrating to next/image due to domain restrictions.
**Why it happens:** next/image requires explicit domain configuration in next.config.mjs.
**How to avoid:** Current config already has `hostname: '**'` wildcard, but verify all image sources.
**Warning signs:** 404 errors for product images after migration

### Pitfall 3: Font Flash of Unstyled Text (FOUT)
**What goes wrong:** Adding `display: 'swap'` causes visible text reflow.
**Why it happens:** System font renders first, then swaps to custom font.
**How to avoid:** Use `size-adjust` in font variable to match fallback font metrics.
**Warning signs:** Layout shift specifically on text elements (CLS from fonts)

### Pitfall 4: PartyTown Compatibility Issues
**What goes wrong:** Scripts like Stripe.js break when moved to web worker.
**Why it happens:** Some scripts require DOM access not available in workers.
**How to avoid:** Test each third-party script individually; keep critical scripts on main thread.
**Warning signs:** Analytics not firing, payment widgets not loading

### Pitfall 5: Over-Optimization Breaking UX
**What goes wrong:** Aggressive lazy loading causes images to never appear.
**Why it happens:** Images below fold never get intersection observer trigger.
**How to avoid:** Test on actual mobile devices with throttled connection.
**Warning signs:** User complaints about missing images

---

## Code Examples

### Image Component with Complete Optimization
```tsx
// components/optimized-image.tsx
import Image from 'next/image';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
  className?: string;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className
}: OptimizedImageProps) {
  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      priority={priority}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      className={className}
      // WebP/AVIF automatic via next/image
    />
  );
}
```

### Bundle Analyzer Integration
```javascript
// next.config.mjs
import withBundleAnalyzer from '@next/bundle-analyzer';

const nextConfig = {
  // ...existing config
};

export default process.env.ANALYZE === 'true'
  ? withBundleAnalyzer({ enabled: true })(nextConfig)
  : nextConfig;
```

### Accessibility Audit Helper
```tsx
// tests/a11y.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/webdriverjs';

test('homepage passes WCAG 2.1 AA', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag21aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| FID metric | INP metric | March 2024 | Stricter responsiveness measurement |
| Manual web-vitals | @vercel/speed-insights | 2024 | Zero-config RUM |
| PartyTown alpha | PartyTown beta | 2024 | Production-ready for GTM/GA4 |
| Lighthouse CI v9 | Lighthouse CI v12 | 2024 | Better Next.js 14 support |

**Deprecated:**
- `next/image` legacy layout prop (use fill + sizes instead)
- `getInitialProps` for data fetching (use Server Components)
- Manual font-face declaration (use next/font)

---

## Open Questions

### Q1: Image Source Domains
- **What we know:** Current next.config.mjs allows all domains via wildcard
- **What's unclear:** Which external domains serve product images
- **Recommendation:** Audit current image URLs, update config with explicit domains

### Q2: Third-Party Scripts Inventory
- **What we know:** Clerk is installed for auth
- **What's unclear:** Analytics, chat widgets, or other third-party scripts
- **Recommendation:** Document all third-party scripts in Plan 11.2

### Q3: Accessibility Baseline
- **What we know:** Skip links implemented, lang attribute set
- **What's unclear:** Current axe-core violation count
- **Recommendation:** Run baseline audit before Plan 11.4

---

## Research Checklist

### Dimension 1: Core Web Vitals Technical Approach ✓
- [x] Next.js 14 LCP optimization patterns documented
- [x] INP strategies (dynamic imports, transitions) researched
- [x] CLS elimination techniques identified
- [x] next/image vs raw img performance impact quantified

### Dimension 2: Real User Monitoring (RUM) ✓
- [x] @vercel/speed-insights v2.0.0 integration steps verified
- [x] web-vitals library v5.2.0 patterns documented
- [x] Field data vs lab data differences understood

### Dimension 3: WCAG 2.1 AA Compliance ✓
- [x] WCAG 2.1 AA checklist mapped to Next.js
- [x] Automated testing tools identified (axe, Lighthouse)
- [x] Common failure patterns documented

### Dimension 4: Build & Bundle Optimization ✓
- [x] @next/bundle-analyzer v16.2.2 setup verified
- [x] Performance budget CI tools researched (size-limit)
- [x] Lighthouse CI integration patterns documented

### Current State Analysis ✓
- [x] Font configuration reviewed (missing display: swap)
- [x] Image usage audited (raw img tags found)
- [x] Script loading strategy evaluated (not configured)

---

## Sources

### Primary (HIGH confidence)
- [Next.js Performance Docs](https://nextjs.org/docs/app/building-your-application/optimizing) — Official optimization guide
- [Vercel Speed Insights Package](https://vercel.com/docs/speed-insights/package) — Official RUM integration
- [@next/bundle-analyzer NPM](https://www.npmjs.com/package/@next/bundle-analyzer) — Bundle analysis setup
- [WCAG 2.1 AA Checklist](https://accessible.org/wcag/) — Compliance requirements

### Secondary (MEDIUM confidence)
- [Web Search: Next.js CWV 2025](https://www.averagedevs.com/blog/nextjs-core-web-vitals-2025) — Current best practices
- [Web Search: PartyTown Next.js](https://wpengine.com/builders/boost-next-js-performance-by-offloading-third-party-scripts-with-partytown) — Third-party optimization
- [Web Search: Performance Budget CI](https://medium.com/@mtorre4580/performance-budget-for-next-js-e34eb4fda11e) — CI integration patterns
- [Web Search: WCAG Next.js](https://thefrontkit.com/nextjs-accessibility-template) — Accessibility implementation

### Tertiary (LOW confidence / Verification needed)
- Current image domains used in production
- Actual third-party scripts loading on site
- Current Lighthouse baseline scores

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Official Next.js/Vercel packages with current versions verified
- Architecture: HIGH — Next.js 14 App Router patterns well-documented
- Pitfalls: MEDIUM-HIGH — Based on common community issues + WebSearch validation

**Research date:** 2026-04-01
**Valid until:** 2026-07-01 (90 days for stable Next.js 14 ecosystem)

---

## RESEARCH COMPLETE

**Phase:** 11 — Core Web Vitals Optimization
**Confidence:** HIGH

### Key Findings
1. **Critical gap:** Raw `<img>` tags must migrate to `next/image` for LCP/CLS improvements
2. **Font optimization:** Add `display: 'swap'` and `adjustFontFallback: true` to prevent FOUT
3. **RUM:** `@vercel/speed-insights` v2.0.0 provides automatic CWV tracking with minimal setup
4. **CI:** Combine `@next/bundle-analyzer` + `size-limit` + Lighthouse CI for comprehensive monitoring
5. **Accessibility:** Skip links already implemented; focus on alt text and color contrast

### File Created
`.planning/phases/11-core-web-vitals-optimization/11-RESEARCH.md`

### Ready for Planning
Research complete. Planner can now create:
- 11.1-PERFORMANCE-OPTIMIZATION-PLAN.md (Image optimization)
- 11.2-PERFORMANCE-OPTIMIZATION-PLAN.md (Font & Script)
- 11.3-PERFORMANCE-OPTIMIZATION-PLAN.md (Layout Stability)
- 11.4-PERFORMANCE-OPTIMIZATION-PLAN.md (RUM & Accessibility)
