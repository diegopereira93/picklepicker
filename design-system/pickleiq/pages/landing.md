# Landing Page Specification

## 1. ROUTE & GOAL

- **Route path:** `/`
- **Primary conversion goal:** Convert visitor → quiz start → AI chat
- **Entry points:**
  - Direct traffic (bookmarks, typed URL)
  - Organic search (Google, Bing)
  - Social media links (Instagram, TikTok, Facebook groups)
  - Affiliate partner referrals
  - Email campaign links
- **Exit points:**
  - `/quiz` (primary desired exit)
  - `/catalog` (secondary - browse without quiz)
  - `/chat` (if returning user with existing profile)

---

## 2. LAYOUT STRUCTURE

### Desktop (1280px+)
- **Container max-width:** 1280px, centered with `mx-auto`
- **Grid:** Single column flow, sections stack vertically
- **Horizontal padding:** 64px left/right (`px-16`)
- **Section spacing:** 80px vertical gap between major sections

### Tablet (768px-1279px)
- **Container max-width:** 100% (fluid)
- **Horizontal padding:** 32px left/right (`px-8`)
- **Section spacing:** 64px vertical gap
- **How It Works:** 3 steps wrap to 2 rows (2 on top, 1 centered below)
- **Feature Highlights:** 2x2 grid maintained

### Mobile (375px-767px)
- **Container max-width:** 100% (fluid)
- **Horizontal padding:** 16px left/right (`px-4`)
- **Section spacing:** 48px vertical gap
- **How It Works:** 3 steps stack vertically
- **Feature Highlights:** 1 column stack
- **Social Proof Strip:** 3 cards stack vertically

---

## 3. SECTIONS (top to bottom)

### Section 1: Hero

**Component(s):** `HeroSection`, `GradientBackground`, `AbstractPaddleGraphic`

**Content requirements:**
- Headline: "Find Your Perfect Paddle. Powered by AI."
  - Font: Bebas Neue
  - Size: `text-5xl` (desktop), `text-4xl` (tablet), `text-3xl` (mobile)
  - Weight: `font-normal` (Bebas Neue is inherently bold)
  - Line height: `leading-tight`
  - Color: `text-white`
- Subtitle: "Answer 7 quick questions. Get personalized recommendations from our AI. No spam, no BS."
  - Font: Source Sans 3
  - Size: `text-base` (desktop), `text-sm` (mobile)
  - Weight: `font-normal`
  - Line height: `leading-relaxed`
  - Color: `text-muted-foreground`
- CTA Button: "Find My Paddle"
  - Link: `/quiz`
  - Style: Primary button (neon green background)
  - Size: `h-12 px-8`
  - Font: Source Sans 3 `font-semibold`

**Padding:**
- Vertical: `py-24` (desktop), `py-16` (tablet), `py-12` (mobile)
- Horizontal: Inherited from container

**Background:**
- Base color: `bg-background` (dark)
- Overlay: Abstract paddle graphic (SVG, low opacity ~10%)
- Graphic specs: Geometric paddle silhouette, neon green stroke, positioned bottom-right

---

### Section 2: How It Works

**Component(s):** `HowItWorksSection`, `StepCard` (×3), `LucideIcon`

**Content requirements:**
- Section title: "How It Works" (hidden on mobile, visible sr-only)
- 3 steps in horizontal layout:

| Step | Icon | Title | Description |
|------|------|-------|-------------|
| 1 | `Lucide.ListChecks` | "Take the Quiz" | "7 questions about your game, style, and budget" |
| 2 | `Lucide.Bot` | "AI Analyzes" | "Our AI matches you with perfect paddles from 500+ options" |
| 3 | `Lucide.Trophy` | "Play Better" | "Get your personalized recommendations instantly" |

**Step card specs:**
- Number badge: JetBrains Mono, `text-2xl`, neon green background circle (48px diameter)
- Icon: Lucide, 32px, `text-muted-foreground`
- Title: Source Sans 3 `font-semibold`, `text-lg`, `text-foreground`
- Description: Source Sans 3 `text-sm`, `text-muted-foreground`, max-width 200px

**Padding:**
- Section vertical: `py-20`
- Card internal: `p-6`

**Background:**
- `bg-surface` (slightly lighter than base)

---

### Section 3: Social Proof Strip

**Component(s):** `SocialProofSection`, `AnimatedCounterCard` (×3)

**Content requirements:**
- 3 animated counter cards:

| Metric | Label | Source |
|--------|-------|--------|
| 500+ | "Paddles Monitored" | Database count |
| R$ 180 | "Avg. Savings" | Historical price data |
| 2,847 | "Players Helped" | Quiz completions (cached) |

**Counter card specs:**
- Number: JetBrains Mono, `text-4xl`, `text-lime-400`, count-up animation (2s duration, ease-out)
- Label: Source Sans 3, `text-sm`, `text-muted-foreground`, uppercase `tracking-wide`
- Animation: Count from 0 to final value over 2 seconds on scroll-into-view

**Padding:**
- Section vertical: `py-16`
- Card internal: `p-8`

**Background:**
- `bg-elevated` (card-style elevation)
- Subtle border: `border border-border`

---

### Section 4: Feature Highlights

**Component(s):** `FeatureSection`, `FeatureCard` (×4), `LucideIcon`

**Content requirements:**
- 4 cards in 2×2 grid (desktop/tablet), 1 column (mobile):

| Card | Icon | Title | Description |
|------|------|-------|-------------|
| Smart Quiz | `Lucide Brain` | "Smart Quiz" | "7 questions that actually matter. No fluff, just what affects your game." |
| AI Chat | `Lucide MessageSquare` | "AI Chat" | "Ask anything. 'Best for beginners under R$300?' Get instant answers." |
| Comparison | `Lucide GitCompare` | "Paddle Comparison" | "Side-by-side specs. See exactly what's different. No guesswork." |
| Price Alerts | `Lucide Bell` | "Price Alerts" | "Track price drops. We notify you when your paddle goes on sale." |

**Feature card specs:**
- Icon container: 48px circle, neon green background (`bg-lime-500/10`), icon `text-lime-400`
- Title: Source Sans 3 `font-semibold`, `text-lg`, `text-foreground`
- Description: Source Sans 3 `text-sm`, `text-muted-foreground`, line-clamp-3

**Padding:**
- Section vertical: `py-20`
- Card internal: `p-6`

**Background:**
- `bg-background` (base dark)

---

### Section 5: Final CTA

**Component(s):** `FinalCtaSection`, `GlowButton`

**Content requirements:**
- Headline: "Ready to Find Your Perfect Paddle?"
  - Font: Bebas Neue, `text-4xl`, `text-foreground`
- Subtitle: "Join 2,847+ players who upgraded their game with AI-powered recommendations."
  - Font: Source Sans 3, `text-base`, `text-muted-foreground`
- CTA Button: "Find My Paddle" (same as hero)
  - Link: `/quiz`
  - Glow effect: Subtle neon green shadow on hover

**Padding:**
- Section vertical: `py-24`
- Horizontal: Same as container

**Background:**
- `bg-elevated`
- Border: `border border-border`
- Rounded: `rounded-2xl`

---

## 4. COMPONENT TREE

```
LandingPage
├── PageContainer (max-w-1280, mx-auto, px-16/8/4)
│   ├── HeroSection
│   │   ├── GradientBackground
│   │   ├── AbstractPaddleGraphic (SVG)
│   │   ├── Headline (Bebas Neue, 5xl)
│   │   ├── Subtitle (Source Sans 3, base)
│   │   └── CtaButton → /quiz
│   ├── HowItWorksSection
│   │   └── StepCard[] (×3)
│   │       ├── NumberBadge (JetBrains Mono, circle)
│   │       ├── LucideIcon (32px)
│   │       ├── Title (Source Sans 3, lg, semibold)
│   │       └── Description (Source Sans 3, sm, muted)
│   ├── SocialProofSection
│   │   └── AnimatedCounterCard[] (×3)
│   │       ├── Counter (JetBrains Mono, 4xl, count-up animation)
│   │       └── Label (Source Sans 3, sm, muted, uppercase)
│   ├── FeatureSection
│   │   └── FeatureCard[] (×4, 2×2 grid)
│   │       ├── IconContainer (circle, lime bg)
│   │       ├── LucideIcon (24px)
│   │       ├── Title (Source Sans 3, lg, semibold)
│   │       └── Description (Source Sans 3, sm, muted)
│   └── FinalCtaSection
│       ├── Headline (Bebas Neue, 4xl)
│       ├── Subtitle (Source Sans 3, base, muted)
│       └── CtaButton → /quiz (glow on hover)
```

**Props:**
- `PageContainer`: `children`, `className`
- `HeroSection`: `headline`, `subtitle`, `ctaText`, `ctaHref`
- `StepCard`: `stepNumber`, `icon`, `title`, `description`
- `AnimatedCounterCard`: `targetValue`, `label`, `prefix` (optional)
- `FeatureCard`: `icon`, `title`, `description`
- `FinalCtaSection`: `headline`, `subtitle`, `ctaText`, `ctaHref`

**State management:**
- All state is local to components
- `AnimatedCounterCard`: `useInView` hook triggers count-up animation
- No global state required

---

## 5. INTERACTIONS

### User actions available
| Element | Action | Result |
|---------|--------|--------|
| Hero CTA button | Click | Navigate to `/quiz` |
| Feature cards | Click (optional) | Expand details inline or navigate to relevant section |
| Final CTA button | Click | Navigate to `/quiz` |
| Social proof cards | Hover | Subtle scale-up (1.02×) |

### Animation/transition specs
- **Hero fade-in:** `opacity-0` → `opacity-100` over 600ms, ease-out
- **Staggered section reveal:** Each section fades in + slides up 20px on scroll-into-view (IntersectionObserver)
- **Counter animation:** 0 → target value over 2000ms, ease-out
- **Button hover:** Background `lime-500` → `lime-400`, shadow `shadow-lg` → `shadow-lime-500/25`
- **Card hover:** `transform: scale(1.02)`, transition 200ms ease-out

### Loading state behavior
- **Initial page load:** Skeleton for Hero (headline + subtitle bars), then sections stream in
- **Image loading:** Abstract paddle graphic has low-priority loading, no skeleton needed
- **Counter data:** Fetch from API on mount, show "—" placeholder until loaded

### Error state behavior
- **Counter API failure:** Fallback to static values (500+, R$ 150, 2,000+)
- **Quiz navigation failure:** Retry once, then show inline error toast

### Empty state behavior
- Not applicable (landing page has no dynamic content that can be empty)

---

## 6. DATA REQUIREMENTS

### API endpoints called
| Endpoint | Method | Purpose | Caching |
|----------|--------|---------|---------|
| `GET /api/stats` | GET | Fetch social proof metrics (paddle count, avg savings, player count) | ISR (revalidate: 3600) |

### Data shape expected
```typescript
interface LandingStats {
  paddleCount: number;        // 523
  averageSavings: number;     // 180 (BRL)
  playersHelped: number;      // 2847
}
```

### Loading strategy
- **Hero:** SSR (static content)
- **Social proof counters:** CSR with suspense boundary, skeleton placeholder
- **Feature highlights:** SSR (static content)

---

## 7. ACCESSIBILITY

### ARIA labels needed
- Hero CTA: `aria-label="Start the quiz to find your perfect paddle"`
- Step cards: `aria-labelledby="step-1-title"`, `aria-labelledby="step-2-title"`, etc.
- Counter cards: `aria-label="500+ paddles monitored"`, `aria-label="Average savings of 180 reais"`, `aria-label="2847 players helped"`
- Feature cards: `aria-labelledby="feature-quiz-title"`, etc.
- Final CTA: `aria-label="Start the quiz to find your perfect paddle"`

### Keyboard navigation flow
1. Tab order follows visual flow: Hero CTA → Step 1 → Step 2 → Step 3 → Counter 1 → Counter 2 → Counter 3 → Feature 1 → Feature 2 → Feature 3 → Feature 4 → Final CTA
2. All interactive elements have visible `:focus-visible` ring (2px, neon green)
3. Skip link: "Skip to main content" → jumps to How It Works section

### Screen reader announcements
- **On counter animation complete:** No announcement (animation is visual only)
- **On navigation to /quiz:** Standard page load announcement
- **Headings hierarchy:**
  - H1: "Find Your Perfect Paddle. Powered by AI."
  - H2: "How It Works"
  - H2: "Feature Highlights"
  - H2: "Ready to Find Your Perfect Paddle?"
