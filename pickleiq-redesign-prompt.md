# PickleIQ — Complete UI/UX Redesign

## Project Overview

PickleIQ is a data intelligence and AI platform for the pickleball equipment niche,
monetized via affiliate marketing. It serves players of ALL skill levels — from
first-time buyers to competitive athletes — helping them find the ideal paddle
through a personalized AI recommendation engine powered by a player profile quiz.

## Tech Stack

- Frontend: Next.js 14 (App Router), Tailwind CSS, shadcn/ui, Radix UI, Vercel
- Backend: FastAPI, PostgreSQL, Railway
- AI: Claude 3.5 Sonnet + Pinecone (RAG) + Langfuse
- Data: Firecrawl API (real-time price and inventory monitoring)
- Auth: Optional — required only for Price Alerts and history (magic link or OAuth)
- Affiliate: Generic `affiliateUrl` prop for now; multi-store ready via `/lib/affiliate.ts`

## Core User Journey

```
Landing Page → Quiz (player profile) → AI Chat (recommendations) 
     ↓
Catalog (browse) → Product Detail → Compare (2 paddles side-by-side)
     ↓
Price Alert (register email, light login gate)
```

---

## Design System — Generate MASTER.md First

Before writing any code, create `design-system/MASTER.md` with the full token set below.

### Aesthetic Direction

- **Mode:** Dark mode as absolute default (no toggle required in v1)
- **Tone:** Premium sports analytics — think ESPN Stats meets Vercel Dashboard meets Linear
- **Feel:** Data-dense, intelligent, performance-oriented, trustworthy
- **Memorable element:** Every number on screen (price, attribute score, match %) must feel
  alive — animated on load, mono-spaced, color-coded by context
- **Avoid:** Generic SaaS blues, purple gradients, stock-photo heroes, system fonts,
  cluttered layouts, Inter/Roboto/Space Grotesk

### Color System (design with justification)

Provide:
- Background hierarchy: `base` / `surface` / `elevated` / `overlay`
- Brand primary: one energetic sport accent (neon green OR electric orange — choose and justify)
- Semantic: `success` / `warning` / `danger` / `info`
- Text hierarchy: `primary` / `secondary` / `muted` / `disabled`
- Price delta: `price-up` (red) / `price-down` (green) / `price-neutral`
- All pairs must pass WCAG AA contrast

### Typography (pick distinctive, non-generic fonts)

- **Display:** Bold, impactful — for hero, section titles, paddle names
- **Body:** Highly legible — for descriptions, chat messages, specs
- **Mono:** Mandatory for all prices, attribute scores, numeric data
- Scale: `xs` → `sm` → `base` → `lg` → `xl` → `2xl` → `3xl` → `4xl` → `5xl`

### Spacing, Radius & Shadow

- Spacing scale: multiples of 4px (4, 8, 12, 16, 24, 32, 48, 64, 96)
- Radius: `sharp` (0–2px) for data tables and prices; `rounded` (8–16px) for cards/chat
- Shadows: `sm` for inputs; `md` for cards; `lg` for elevated panels; `glow` for CTAs

### Motion Principles

- Page transitions: fade + subtle slide (150ms ease-out)
- Card hover: lift (translateY -2px) + accent color glow
- Chat messages: slide-in from bottom (200ms)
- Price drop badge: pulse animation (looping)
- Match score counter: count-up animation on enter
- Skeleton: shimmer sweep on all data-loading components
- Quiz steps: horizontal slide between steps (300ms ease-in-out)

---

## Pages — Generate design-system/pages/[page].md for each

---

### A. Landing Page (`/`) — `design-system/pages/landing.md`

**Goal:** Convert visitor → quiz start → AI chat

Sections (in order):

1. **Hero**
   - Headline: punchy, sport-forward (e.g. "Find Your Perfect Paddle. Powered by AI.")
   - Sub: 1 line explaining the quiz + AI flow
   - Primary CTA: "Find My Paddle" → starts quiz
   - Background: animated chat preview OR abstract paddle graphic in dark atmosphere
   - No stock photography

2. **How It Works** — 3 steps with icons
   - Step 1: Take the 2-min quiz (understand your game)
   - Step 2: AI recommends the best paddles for your profile
   - Step 3: Compare prices, track deals, buy with confidence

3. **Social Proof Strip**
   - Animated number counters: paddles monitored / avg price savings found / players helped
   - Display numbers in mono font with accent color

4. **Feature Highlights** — 4 cards
   - Smart Quiz / AI Chat Recommendations / Paddle Comparison / Price Alerts

5. **Final CTA** — full-width dark section, repeat primary CTA

---

### B. Player Profile Quiz (`/quiz`) — `design-system/pages/quiz.md`

**Goal:** Capture player profile to enrich RAG context for AI chat

UX Requirements:
- Full-screen wizard, ONE question per screen
- Progress bar at top (step X of 7)
- Each option rendered as a visual card with icon/illustration, not plain radio buttons
- Smooth horizontal slide transition between steps
- Back button on all steps except first
- Final screen: "Analyzing your profile..." with animated loader (2s) then redirect to `/chat`
- Profile stored in `localStorage` as `pickleiq_player_profile`
- If user is logged in, sync profile to database on completion

Questions:
1. What is your playing level? → Beginner / Intermediate / Advanced / Competitive
2. How would you describe your style? → Baseline Grinder / Dink & Control / Power Hitter / All-Round
3. What is your top priority? → Control / Power / Spin / Speed
4. What is your budget? → Under $80 / $80–150 / $150–250 / $250+
5. Weight preference? → Light (<7.5oz) / Medium (7.5–8.2oz) / Heavy (>8.2oz) / No preference
6. Where do you mostly play? → Indoor / Outdoor / Both
7. Any paddle in mind? → Free text, optional ("Skip" available)

---

### C. AI Recommendation Chat (`/chat`) — `design-system/pages/chat.md`

**Goal:** Recommend paddles via conversation enriched with quiz profile context

Layout:
- Left sidebar (280px, collapsible): Player profile panel
- Main area: chat interface

Sidebar content:
- Player profile as readable chips/tags (level, style, budget, priority)
- "Edit Profile" button → back to quiz
- "Start Over" to clear and restart

Chat area:
- AI messages can contain **embedded Product Cards** inline (not just text)
- User input at bottom with quick-prompt suggestion chips above it:
  - "Show options under $100"
  - "Best for beginners"
  - "Compare top 2 picks"
- Streaming response with typewriter effect
- Animated typing indicator (3 pulsing dots)
- Each session prefixed with system context from quiz profile (hidden from UI)

Embedded Product Card (inside AI message):
- Paddle image (small, 80px)
- Name + Brand
- Current price (mono font)
- Match score badge: "94% match" with color ring
- Two action buttons: `[Buy →]` (affiliate CTA) and `[Compare]`

---

### D. Full Catalog (`/catalog`) — `design-system/pages/catalog.md`

**Goal:** Browse and filter the complete paddle catalog with real price data

Layout: Sticky filter sidebar (left 260px) + product grid (right, 3-col desktop / 2-col tablet / 1-col mobile)

Filter panel:
- Recommended level (checkboxes)
- Price range (dual-handle range slider)
- Brand (checkboxes, search within)
- Weight class (chips)
- Core material: Polypropylene / Carbon Fiber / Nomex / Graphite
- On sale / Price dropped this week (toggle)

Product Card in catalog:
- Paddle image (aspect-ratio fixed)
- Brand (small, muted) + Name (bold display font)
- Current price in mono font
- Price delta badge: "↓ 12% this week" (pulsing if dropped today)
- Attribute mini-badges: Power / Control / Spin (colored dots with score)
- Match score with quiz profile (if quiz completed): "89% match"
- Actions: `[Details]` / `[+ Compare]` / `[🔔 Alert]`

---

### E. Paddle Comparison (`/compare?a=[slug]&b=[slug]`) — `design-system/pages/compare.md`

**Goal:** Side-by-side comparison of exactly 2 paddles

UX Requirements:
- Paddle selection via search/autocomplete at top (pre-filled from query params)
- Two fixed columns with sticky header showing paddle image + name + price
- Comparison rows (each attribute on its own row):
  - Current Price / Weight / Core Material / Length / Width / Core Thickness
  - Power Rating / Control Rating / Spin Rating / Sweet Spot Size
  - Recommended Level / Affiliate Price Sources
- Winning value per row highlighted in accent color (subtle green glow)
- Radar chart overlay: two semi-transparent polygons (Power / Control / Spin / Speed / Sweet Spot)
- **AI Verdict section** (below the table):
  - If quiz profile exists: "Based on your profile as a [level] [style] player with a [budget] budget, [Paddle A] is the better choice because..."
  - If no profile: generic AI comparison paragraph
  - Generate on page load via streaming API call
- Two CTA columns: one affiliate button per paddle

Deep link format: `/compare?a=selkirk-vanguard-power-air&b=joola-hyperion-cgx`

---

### F. Product Detail (`/catalog/[slug]`) — `design-system/pages/product-detail.md`

**Goal:** Full paddle info, price history, and high-conversion affiliate CTA

Layout (top to bottom):
1. **Header block** (above the fold, 2-col)
   - Left: large paddle image with zoom-on-hover
   - Right: Name, Brand, Current price (large mono), stock status,
     `[Buy Now →]` affiliate CTA (prominent, accent-colored),
     `[+ Compare]` secondary button,
     `[🔔 Alert me if price drops]` tertiary link
2. **Technical Specs table** — all attributes in clean mono-font table
3. **Price History chart** (Recharts, last 90 days) — line chart with:
   - Hover tooltip showing exact date + price
   - Horizontal reference line at current price
   - Highlighted regions for price drop events
4. **AI Summary** — "Strengths & Weaknesses" generated by AI (2 short paragraphs)
5. **Ideal for...** — profile chips: "Best for Intermediate / Control players / Outdoor"
6. **Similar Paddles** — horizontal scroll carousel of 4–6 related paddles

---

### G. Price Alert Modal (global component) — `design-system/pages/price-alert-modal.md`

**Goal:** Capture email/login to register price drop notification

Trigger: clicking any "🔔 Alert me" button across the platform

Behavior:
- If user is already logged in: single-click confirm with success toast
- If not logged in: modal opens asking for email
  - "Get notified when [Paddle Name] drops in price"
  - Email input + "Notify Me" button
  - Below input: "No account needed. We'll send one email when the price drops."
  - On submit: register alert, show success state inside modal, auto-close after 2s

---

## Component Library

Implement all components in `/components/ui/`. Each must have:
- TypeScript props interface
- Loading/skeleton state
- Empty/error state where applicable
- Full dark-mode styling

```tsx
// ── Price & Data ──────────────────────────────────────────────
<PriceTag price={number} previousPrice={number} currency="USD" />
// Current price in mono font + colored delta badge

<PriceDeltaBadge delta={number} pulsing={boolean} />
// "↓ 12%" or "↑ 5%" — green/red — pulsing if drop is today

<PriceChart 
  data={PricePoint[]} 
  variant="sparkline" | "full" 
  currentPrice={number} 
/>
// Sparkline for cards; full Recharts line chart for detail page

// ── Product Cards ─────────────────────────────────────────────
<ProductCard 
  paddle={PaddleData} 
  mode="catalog" | "chat" | "compact"
  matchScore={number}           // from quiz profile, optional
  onCompare={() => void}
  onAlert={() => void}
/>

<AttributeBadge label="Control" value={9.1} variant="dot" | "pill" />
// Colored mini-badge for Power / Control / Spin ratings

<MatchScoreBadge score={number} />
// "94% match" with animated color ring (green > 80, yellow > 60, red < 60)

// ── Comparison ────────────────────────────────────────────────
<CompareRow 
  attribute={string} 
  valueA={string | number} 
  valueB={string | number}
  winner="a" | "b" | "tie"
/>

<RadarChart paddleA={AttributeSet} paddleB={AttributeSet} />
// Recharts RadarChart with two overlapping semi-transparent polygons

// ── AI & Chat ─────────────────────────────────────────────────
<AIMessage 
  content={string} 
  products={PaddleData[]}       // optional embedded product cards
  isStreaming={boolean} 
/>

<TypingIndicator />
// Three pulsing dots, accent-colored

<PlayerProfileSidebar 
  profile={QuizProfile} 
  collapsed={boolean}
  onEdit={() => void}
/>

// ── Quiz ──────────────────────────────────────────────────────
<QuizStep 
  question={string}
  options={QuizOption[]}        // { label, icon, value }
  selected={string | null}
  onSelect={(value: string) => void}
/>

<QuizProgressBar current={number} total={number} />

// ── Conversion ────────────────────────────────────────────────
<AffiliateCTA 
  affiliateUrl={string} 
  price={number}
  label={string}
  urgency?: string              // e.g. "Only 3 left in stock"
/>

<PriceAlertModal 
  paddleId={string} 
  paddleName={string}
  isOpen={boolean}
  onClose={() => void}
/>
```

---

## Global UX Patterns (non-negotiable)

- **Skeleton loading** on every component that fetches data — no layout shift
- **Optimistic UI** on Price Alert button (immediate visual feedback before API response)
- **Empty states** with AI nudge: "No results? Ask the AI chat instead →"
- **Error states** with retry on all fetches
- **Toast notifications** for: alert registered / paddle added to compare / compare full (max 2)
- **Deep links** for comparison: `/compare?a=slug1&b=slug2`
- **Quiz profile persistence**: `localStorage` → sync to DB on login
- **Affiliate service**: create `/lib/affiliate.ts` with `resolveAffiliateUrl(paddleId, store?)` 
  — returns URL with auto-generated UTM params (`utm_source=pickleiq&utm_medium=affiliate&utm_content=[page]`)

---

## Execution Order

Execute strictly in this order:

1. Generate `design-system/MASTER.md` with all tokens and reasoning
2. Generate `design-system/pages/` — one `.md` per page
3. Update `tailwind.config.ts` with all custom tokens from MASTER.md
4. Implement `/lib/affiliate.ts` (UTM-ready affiliate URL resolver)
5. Implement all components in `/components/ui/` (start with data components)
6. Implement pages in `/app/` in this order:
   - `/quiz`
   - `/chat`
   - `/catalog`
   - `/compare`
   - `/catalog/[slug]`
   - `/` (landing)

---

## Hard Constraints

- Dark mode is the absolute default — no light mode toggle in v1
- All color contrast pairs must pass WCAG AA
- Mobile-first — breakpoints: 375px / 768px / 1280px
- Mono font mandatory on all prices and numeric attribute values
- No component shipped without a loading/skeleton state
- No external CSS frameworks beyond Tailwind
- No Inter, Roboto, Arial, Space Grotesk, or system fonts
- Quiz profile must be accessible and editable from the chat sidebar
- All affiliate links must pass through `/lib/affiliate.ts`
