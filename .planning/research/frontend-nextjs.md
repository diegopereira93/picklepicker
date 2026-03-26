# Frontend Research: Next.js 14 App Router for PickleIQ

**Domain:** Next.js 14 (App Router) — AI chat + product comparison + SEO
**Researched:** 2026-03-26
**Overall confidence:** HIGH (Next.js 14, Vercel AI SDK, Clerk, Recharts are all stable and well-documented as of Aug 2025 training cutoff)

---

## 1. Streaming AI Chat Responses

### Verdict: Route Handler + Vercel AI SDK `streamText` (NOT Server Actions)

**Why not Server Actions for streaming:**
Server Actions return a single resolved value. While Next.js 15 adds experimental streaming support for Server Actions, in Next.js 14 they do not natively support token-by-token streaming. Using them for AI chat requires workarounds that break the UX.

**Why not WebSocket:**
Vercel's serverless/Edge runtime does not support persistent WebSocket connections. Overkill for a chat widget; adds infrastructure complexity (need a separate WebSocket server or Pusher/Ably).

**Recommended pattern: Route Handler + Vercel AI SDK**

```typescript
// app/api/chat/route.ts
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

export const runtime = 'edge'; // critical for low latency

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4o-mini'),
    system: 'You are a pickleball paddle expert...',
    messages,
  });

  return result.toDataStreamResponse();
}
```

```typescript
// components/ChatWidget.tsx (Client Component)
'use client';
import { useChat } from 'ai/react';

export function ChatWidget() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
  });
  // render messages with streaming tokens
}
```

**Key decisions:**
- `useChat` hook handles SSE parsing, message state, and error handling automatically
- `toDataStreamResponse()` uses Vercel's AI data stream protocol (more robust than raw SSE)
- Edge runtime reduces cold starts from ~300ms to ~50ms — critical for chat feel
- `gpt-4o-mini` recommended for recommendations (fast + cheap); fall back to `gpt-4o` for complex queries
- Confidence: HIGH (Vercel AI SDK v3+ is the de facto standard for this pattern)

### Streaming gotchas
- Set `export const maxDuration = 30;` in the route file for Vercel Pro (default is 10s, too short for long responses)
- Do NOT use `export const dynamic = 'force-static'` on chat routes
- CORS: if frontend and API are same Next.js app, no CORS config needed

---

## 2. Product Comparison with Radar Charts

### Verdict: Recharts for radar charts, not Chart.js or D3

**Comparison:**

| Criterion | Recharts | Chart.js | D3 |
|-----------|----------|----------|----|
| React integration | Native (JSX components) | Wrapper libs (react-chartjs-2) | Manual DOM manipulation |
| Bundle size | ~90KB | ~60KB (core) | ~80KB |
| Radar chart support | Yes (`RadarChart`) | Yes | Yes (most flexible) |
| TypeScript | Excellent | Good | Adequate |
| SSR compatibility | Client-only (use dynamic import) | Client-only | Client-only |
| Learning curve | Low | Low-Med | High |
| Customization | Medium | Medium | Unlimited |

**Why Recharts:**
- First-class React/JSX API — no imperative `canvas` refs or `useEffect` wiring
- `RadarChart` + `PolarGrid` + `PolarAngleAxis` + `Radar` components compose naturally
- Responsive via `ResponsiveContainer` wrapper
- Sufficient customization for a paddle comparison (power, control, spin, speed, forgiveness axes)

**Why not D3:** Massive overkill. D3 is for custom visualizations; a radar chart with 5 axes doesn't need it.

**Why not Chart.js:** `react-chartjs-2` wrapper adds an extra abstraction layer; ref-based API fights React's model.

```typescript
// components/PaddleRadarChart.tsx
'use client';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend, ResponsiveContainer } from 'recharts';

const AXES = ['Power', 'Control', 'Spin', 'Speed', 'Forgiveness'];

export function PaddleRadarChart({ paddles }: { paddles: Paddle[] }) {
  const data = AXES.map(axis => ({
    axis,
    ...Object.fromEntries(paddles.map(p => [p.name, p.stats[axis.toLowerCase()]]))
  }));

  const COLORS = ['#3b82f6', '#f59e0b', '#10b981'];

  return (
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="axis" />
        <PolarRadiusAxis domain={[0, 10]} tick={false} />
        {paddles.map((p, i) => (
          <Radar key={p.id} name={p.name} dataKey={p.name} stroke={COLORS[i]} fill={COLORS[i]} fillOpacity={0.2} />
        ))}
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  );
}
```

**Import pattern (critical for SSR):**
```typescript
// In the parent page/layout:
import dynamic from 'next/dynamic';
const PaddleRadarChart = dynamic(() => import('@/components/PaddleRadarChart'), { ssr: false });
```
Recharts uses browser APIs (`ResizeObserver`, `canvas`). Always `dynamic` import with `ssr: false`.

---

## 3. SSR Strategy for SEO Product Pages

### Verdict: Server Components + `generateMetadata` + JSON-LD script tag

**Page rendering model:**
- Product detail pages: **SSR (dynamic)** via Server Components — fresh price/stock data matters for SEO
- Product listing pages: **ISR** with `revalidate: 3600` — content changes infrequently, cache for performance

```typescript
// app/paddles/[slug]/page.tsx
import { Metadata } from 'next';

// Dynamic metadata per product
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const paddle = await getPaddle(params.slug);
  return {
    title: `${paddle.name} Review — PickleIQ`,
    description: paddle.shortDescription,
    openGraph: {
      title: paddle.name,
      images: [{ url: paddle.imageUrl, width: 800, height: 600 }],
    },
  };
}

export default async function PaddlePage({ params }: { params: { slug: string } }) {
  const paddle = await getPaddle(params.slug);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: paddle.name,
    image: paddle.imageUrl,
    description: paddle.description,
    brand: { '@type': 'Brand', name: paddle.brand },
    offers: {
      '@type': 'Offer',
      priceCurrency: 'USD',
      price: paddle.price,
      availability: 'https://schema.org/InStock',
      url: paddle.affiliateUrl,
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: paddle.rating,
      reviewCount: paddle.reviewCount,
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      {/* page content */}
    </>
  );
}
```

**ISR for listing pages:**
```typescript
// app/paddles/page.tsx
export const revalidate = 3600; // revalidate every hour

export async function generateStaticParams() {
  const slugs = await getAllPaddleSlugs();
  return slugs.map(slug => ({ slug }));
}
```

**Key SEO rules:**
- JSON-LD in `<script>` tag (not `next/head`) — App Router renders it server-side correctly
- `generateMetadata` runs on the server, so you can fetch from DB directly
- Use `alternates.canonical` in metadata to prevent duplicate URL penalties (e.g., `?utm_source=` variants)
- Image alt text must be descriptive: `"Selkirk Vanguard Power Air pickleball paddle"` not `"paddle"`
- Confidence: HIGH — Schema.org/Product + Next.js generateMetadata is the standard pattern

---

## 4. Affiliate Link Click Tracking

### Verdict: Client-side event + server-side log via Route Handler (not third-party only)

**Pattern:**

```typescript
// lib/tracking.ts (client utility)
export async function trackAffiliateClick(paddleId: string, source: string) {
  // 1. Fire-and-forget to own server (for data ownership)
  fetch('/api/track/click', {
    method: 'POST',
    body: JSON.stringify({ paddleId, source, timestamp: Date.now() }),
    headers: { 'Content-Type': 'application/json' },
    keepalive: true, // survives page navigation
  });

  // 2. Optional: also fire GA4 event
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'affiliate_click', {
      paddle_id: paddleId,
      source,
    });
  }
}
```

```typescript
// app/api/track/click/route.ts
export const runtime = 'edge';

export async function POST(req: Request) {
  const { paddleId, source } = await req.json();
  // Log to DB (Supabase/PlanetScale) or queue (Upstash)
  await logClick({ paddleId, source, ip: req.headers.get('x-forwarded-for') });
  return new Response(null, { status: 204 });
}
```

**Critical: use `keepalive: true`** — without it, `fetch` is cancelled when user navigates to affiliate URL. This is the most common bug in affiliate tracking implementations.

**Affiliate link pattern (avoid plain `<a>` tags):**
```typescript
// components/AffiliateButton.tsx
'use client';
export function AffiliateButton({ paddle }: { paddle: Paddle }) {
  const handleClick = () => {
    trackAffiliateClick(paddle.id, 'product-detail');
    window.open(paddle.affiliateUrl, '_blank', 'noopener');
  };
  return <button onClick={handleClick}>Buy on Amazon</button>;
}
```

**Do NOT use `<a href>` with `onClick`** — browser may navigate before async tracking fires, even with `keepalive`.

---

## 5. Clerk Authentication — App Router Patterns and Gotchas

### Verdict: Clerk is the right choice; middleware setup is the critical step

**Installation:**
```bash
npm install @clerk/nextjs
```

**Middleware (required — the most common gotcha):**
```typescript
// middleware.ts (root level, NOT inside app/)
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/alerts(.*)',
]);

export default clerkMiddleware((auth, req) => {
  if (isProtectedRoute(req)) auth().protect();
});

export const config = {
  matcher: ['/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jinja2|ico|webp|avif|jpg|jpeg|png|gif|svg|ttf|woff2?|eot|otf|map)).*)'],
};
```

**Server Component auth (reading user without redirect):**
```typescript
import { auth, currentUser } from '@clerk/nextjs/server';

export default async function DashboardPage() {
  const { userId } = await auth(); // just the ID, fast
  const user = await currentUser(); // full user object, slower
  // ...
}
```

**Key gotchas:**

| Gotcha | Detail |
|--------|--------|
| Middleware location | Must be `/middleware.ts` at project root, NOT inside `/app/` |
| `auth()` is async in v5+ | Use `await auth()` — older tutorials show non-async version |
| `clerkMiddleware` vs `authMiddleware` | `authMiddleware` is deprecated in Clerk v5; use `clerkMiddleware` |
| Public routes default | In v5, ALL routes are public by default unless you call `auth().protect()` |
| Environment variables | `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` + `CLERK_SECRET_KEY` both required |
| Clerk + Edge runtime | Clerk middleware runs on Edge by default — compatible, but don't use Node-only APIs in middleware |
| `<ClerkProvider>` placement | Must wrap root layout, not individual pages |

**Root layout:**
```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

**Price alerts: store Clerk `userId` in your DB** (not email — email can change). Use `userId` as the foreign key for alert records.

---

## 6. Vercel Deployment — Edge vs Node Runtime for AI Routes

### Runtime decision matrix:

| Route | Recommended Runtime | Reason |
|-------|-------------------|--------|
| `/api/chat` (AI streaming) | `edge` | Low cold start (~50ms vs ~300ms), streaming support, global distribution |
| `/api/track/click` | `edge` | Lightweight, no Node-only deps, global |
| `/api/alerts/*` | `nodejs` (default) | May use Node crypto, complex DB queries, email sending |
| Product pages (SSR) | `nodejs` (default) | Full Next.js features, no restrictions |
| Middleware | `edge` (always) | Vercel requirement |

**Edge runtime constraints (critical to know before choosing):**
- No `fs` module
- No native Node.js crypto (use Web Crypto API instead)
- No `node:` protocol imports
- Some npm packages use Node APIs internally — will fail on Edge silently during build
- Max 1MB bundle size per Edge function (Vercel limit)
- No TCP connections (Postgres via `pg` package breaks — use HTTP-based DB like Supabase or Neon's HTTP driver)

**AI route on Edge:**
```typescript
// app/api/chat/route.ts
export const runtime = 'edge';
export const maxDuration = 30; // Vercel Pro only; Hobby = 10s max
```

**Environment variables:**
```bash
# .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Vercel Dashboard → Settings → Environment Variables
# Set each for: Production, Preview, Development
```

**Vercel-specific gotchas:**
- `NEXT_PUBLIC_*` vars are baked into client bundle at build time — changing them requires a redeploy
- Never prefix secret keys with `NEXT_PUBLIC_` (they'd be exposed in browser)
- Use Vercel's built-in integration for OpenAI (auto-manages key rotation) if available
- Set `NEXTAUTH_URL` / `NEXT_PUBLIC_APP_URL` per environment (localhost vs production domain)

---

## Architecture Recommendations for PickleIQ

### Component boundaries:

```
app/
  layout.tsx                    # ClerkProvider wraps everything
  page.tsx                      # Landing page (static)
  paddles/
    page.tsx                    # ISR listing (revalidate: 3600)
    [slug]/
      page.tsx                  # SSR detail + JSON-LD
  compare/
    page.tsx                    # Client-heavy (dynamic imports for Recharts)
  dashboard/
    page.tsx                    # Protected (Clerk auth().protect())
  api/
    chat/route.ts               # Edge runtime, Vercel AI SDK streamText
    track/click/route.ts        # Edge runtime, fire-and-forget logging
    alerts/route.ts             # Node runtime, DB + email

components/
  ChatWidget.tsx                # 'use client', useChat hook
  PaddleRadarChart.tsx          # 'use client', Recharts
  AffiliateButton.tsx           # 'use client', tracking + window.open
  PaddleCard.tsx                # Server Component (no interactivity needed)
```

### Data fetching pattern for comparison page:
The comparison page is URL-driven (`/compare?a=selkirk-vanguard&b=joola-gen3`). Fetch both paddles server-side in the page Server Component, pass static data to the Client Component for the chart. This avoids client-side waterfalls.

---

## Pitfalls Summary

| Pitfall | Impact | Prevention |
|---------|--------|------------|
| `fetch` without `keepalive` on affiliate click | Lost conversions, broken tracking | Always use `keepalive: true` |
| Recharts without `dynamic` import | SSR build failure | `dynamic(() => import(...), { ssr: false })` |
| Clerk `authMiddleware` (deprecated) | Auth bypassed silently in v5 | Use `clerkMiddleware` |
| Edge runtime + Postgres `pg` package | Runtime crash | Use Supabase/Neon HTTP drivers on Edge |
| `NEXT_PUBLIC_` on secret keys | API key exposed in browser | Never prefix secrets with `NEXT_PUBLIC_` |
| Server Actions for streaming | Token-by-token stream broken | Use Route Handler + Vercel AI SDK |
| JSON-LD in `next/head` | May not render server-side | Use `<script>` tag directly in Server Component |
| `maxDuration` not set on chat route | AI response cut off at 10s | Set `export const maxDuration = 30` (Pro plan) |

---

## Sources and Confidence

| Area | Confidence | Basis |
|------|------------|-------|
| Vercel AI SDK streaming | HIGH | Stable API as of v3, widely documented |
| Recharts radar chart | HIGH | Stable library, consistent API |
| Next.js SSR + generateMetadata | HIGH | Core Next.js 14 feature, official docs pattern |
| Schema.org/Product JSON-LD | HIGH | Schema.org spec is stable |
| Clerk v5 App Router | HIGH | Clerk v5 released mid-2024, stable |
| Vercel Edge vs Node tradeoffs | HIGH | Well-documented Vercel platform constraints |
| Affiliate tracking `keepalive` | HIGH | Web Fetch API spec, widely known pattern |

**Note on recency:** This research is based on training data through August 2025. Verify Clerk and Vercel AI SDK changelog for any breaking changes post-August 2025 before implementation. Core Next.js 14 patterns are stable.
