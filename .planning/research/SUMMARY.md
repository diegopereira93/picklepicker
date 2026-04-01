# Core Web Vitals Optimization — Research Summary

## Stack Additions

### Performance Tools
- **@vercel/speed-insights** — Real User Monitoring (RUM) for Core Web Vitals
- **@next/bundle-analyzer** — Bundle size analysis
- **web-vitals** library — Programmatic CWV measurement
- **Lighthouse CI** — Automated performance testing in CI/CD

### No New Runtime Dependencies
Core Web Vitals optimization primarily uses Next.js built-in features:
- `next/image` for automatic image optimization
- `next/font` for font optimization
- `next/script` for script loading strategies
- React Server Components for reduced bundle size

## Feature Categories

### Table Stakes (Must-have)
1. **Image Optimization** — WebP/AVIF conversion, responsive sizes, lazy loading
2. **Font Optimization** — Subsetting, display: swap, preloading
3. **Code Splitting** — Route-based splitting, dynamic imports
4. **CSS Optimization** — Purge unused CSS, critical CSS extraction

### Differentiators (Competitive)
1. **Real User Monitoring** — Actual CWV metrics from production users
2. **Performance Budgets** — Automated bundle size enforcement
3. **Streaming SSR** — Progressive rendering with Suspense

### Anti-Features (Avoid)
1. Heavy analytics scripts in `<head>`
2. Synchronous third-party scripts
3. Unoptimized video backgrounds
4. Excessive animation libraries

## Architecture Considerations

### Integration Points
- **Next.js App Router** — Server Components reduce client JS
- **Edge Runtime** — Middleware for caching, reduced latency
- **ISR** — Static generation with incremental updates

### Build Optimizations
- Tree shaking enabled by default in Next.js
- Module concatenation for production builds
- Minification with SWC (Rust-based, fast)

### Data Flow
- Prefer Server Components for data fetching
- Use `loading.js` for instant loading states
- Implement proper error boundaries

## Watch Out For

### Common Pitfalls
1. **Lighthouse Lab ≠ Field Data** — Lab scores can differ from real user experiences
2. **Over-optimization** — Don't sacrifice UX for marginal gains
3. **Third-party scripts** — These are often the biggest performance killers
4. **Layout shifts** — Images without dimensions cause CLS

### Prevention Strategies
1. Measure before optimizing — establish baselines
2. Use `next/image` with explicit width/height
3. Defer non-critical scripts with `strategy="lazyOnload"`
4. Monitor Core Web Vitals in production

## Recommended Phase Structure

1. **Phase 11: Core Web Vitals Optimization**
   - Image optimization audit and fixes
   - Font loading optimization
   - Third-party script optimization
   - Real User Monitoring setup

## Key Decisions

- Use `@vercel/speed-insights` for RUM (Vercel native integration)
- Leverage existing `next/image` usage, audit for improvements
- No new heavy libraries — optimization should reduce, not add
