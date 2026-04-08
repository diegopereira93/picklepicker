# Compare Page Specification

## 1. ROUTE & GOAL

- **Route path:** `/compare?a=[slug]&b=[slug]`
- **Primary conversion goal:** Side-by-side comparison of 2 paddles → affiliate click on winner
- **Entry points:**
  - Catalog page "Compare" button (adds to compare, redirects when 2+ items)
  - Chat page product card "Compare" button
  - Direct deep link (shared comparison URL)
  - Product detail page "Compare" button
- **Exit points:**
  - Affiliate links (primary desired exit - monetization)
  - `/catalog/[slug]` (from paddle name links)
  - `/catalog` (browse more options)
  - `/chat` (ask AI about comparison)

---

## 2. LAYOUT STRUCTURE

### Desktop (1280px+)
- **Container max-width:** 1280px, centered with `mx-auto`
- **Layout:** Single column, vertical scroll
- **Horizontal padding:** `px-16`
- **Two-column comparison:** Grid with 2 equal columns (50% each), `gap-8`
- **Sticky headers:** Paddle image + name + price stick to top during scroll

### Tablet (768px-1279px)
- **Container max-width:** 100% (fluid)
- **Layout:** Same single column
- **Two-column comparison:** Same 50/50 grid, `gap-6`
- **Horizontal padding:** `px-8`
- **Sticky headers:** Same behavior

### Mobile (375px-767px)
- **Container max-width:** 100% (fluid)
- **Layout:** Single column, **stacked comparison** (NOT side-by-side)
- **Comparison rows:** Each row shows both values stacked vertically
- **Horizontal padding:** `px-4`
- **Sticky headers:** Only paddle A header sticks, paddle B header scrolls away
- **Radar chart:** Full width, smaller (height 250px vs 350px)

---

## 3. SECTIONS (top to bottom)

### Section 1: Search/Selection Bar

**Component(s):** `CompareSearchBar`, `PaddleAutocomplete` (×2)

**Content requirements:**
- Label: "Compare Paddles"
  - Font: Source Sans 3 `font-semibold`, `text-sm`, `text-foreground`
- Two autocomplete inputs (side by side):
  - Placeholder: "Search paddle A..." / "Search paddle B..."
  - Pre-filled from query params `?a=[slug]&b=[slug]`
  - Dropdown: List of paddles with thumbnail, brand, name, price
  - Keyboard nav: Arrow keys to navigate, Enter to select
- Swap button: `Lucide.ArrowLeftRight` (20px), centered between inputs
  - Action: Swap A and B values, update URL

**Padding:**
- Section vertical: `py-6`
- Input gap: `gap-4`

**Background:**
- `bg-surface`
- Border bottom: `border-b border-border`

---

### Section 2: Comparison Table

**Component(s):** `ComparisonTable`, `ComparisonRow` (×11), `StickyHeader` (×2)

**Content requirements:**
- **Sticky headers (2 columns):**
  - Image: Aspect ratio 4/3, object-cover, rounded-lg
  - Brand: Muted caption, `text-xs`, `text-muted-foreground`
  - Name: Bebas Neue, `text-2xl`, `text-foreground`
  - Price: JetBrains Mono, `text-3xl`, `text-lime-400`
  - Stock status: "Em estoque" / "Fora de estoque" (dot indicator)
  - Affiliate CTA: "Comprar Agora" (primary button, neon green, glow on hover)

- **Comparison rows (11 rows, alternating bg):**

| Row | Data Source | Winner Logic |
|-----|-------------|--------------|
| Price | `paddle.price` | Lower price wins (green highlight) |
| Weight | `paddle.weight` | Depends on user preference (show both values) |
| Core Material | `paddle.coreMaterial` | No winner (info only) |
| Length | `paddle.length` | Longer wins for power, shorter for control |
| Width | `paddle.width` | Wider = larger sweet spot |
| Core Thickness | `paddle.coreThickness` | Thicker = more power |
| Power Rating | `paddle.powerRating` | Higher wins (green highlight) |
| Control Rating | `paddle.controlRating` | Higher wins (green highlight) |
| Spin Rating | `paddle.spinRating` | Higher wins (green highlight) |
| Sweet Spot Size | `paddle.sweetSpotSize` | Larger wins (green highlight) |
| Recommended Level | `paddle.level` | Match to quiz profile (green if match) |

**Row specs:**
- Label column: 150px fixed width (left)
- Value columns: Equal width, centered
- Winner highlight: Subtle neon green background glow (`bg-lime-500/5`)
- Value text: Source Sans 3 `text-base`, `text-foreground`
- Winner indicator: Checkmark icon (neon green) next to winning value

**Padding:**
- Row vertical: `py-4`
- Row horizontal: `px-6`
- Label padding: `pr-8`

**Background:**
- Alternating: `bg-background` / `bg-surface` (row striping)
- Winner row: `bg-lime-500/5` overlay

---

### Section 3: Radar Chart

**Component(s):** `RadarChartContainer`, `RechartsRadarChart`

**Content requirements:**
- Title: "Performance Comparison"
  - Font: Source Sans 3 `font-semibold`, `text-lg`, `text-foreground`
- Radar chart:
  - Axes: Power, Control, Spin, Speed, Sweet Spot (5 axes)
  - Polygon A: Semi-transparent neon green (`rgba(132, 204, 22, 0.3)`)
  - Polygon B: Semi-transparent orange (`rgba(255, 165, 0, 0.3)`)
  - Stroke A: Neon green (`#84CC16`), 2px
  - Stroke B: Orange (`#FFA500`), 2px
  - Grid lines: `stroke-border`, 1px
  - Axis labels: Source Sans 3 `text-xs`, `text-muted-foreground`
  - Tooltip: On hover, shows values for both paddles
- Legend: 2 items below chart (A: neon green dot + name, B: orange dot + name)

**Padding:**
- Section vertical: `py-8`
- Chart internal: `p-4`

**Background:**
- `bg-elevated`
- Rounded: `rounded-2xl`
- Border: `border border-border`

---

### Section 4: AI Verdict

**Component(s):** `AiVerdict`, `StreamingText`

**Content requirements:**
- Header: "AI Verdict"
  - Font: Bebas Neue, `text-xl`, `text-foreground`
  - Icon: `Lucide.Bot` (24px, neon green)
- Streaming paragraph:
  - Font: Source Sans 3 `text-base`, `text-muted-foreground`
  - Content: Personalized recommendation based on quiz profile (if exists)
  - Example without profile: "Paddle A excels in power and spin, making it ideal for aggressive players. Paddle B offers superior control and a larger sweet spot, better suited for beginners or defensive players."
  - Example with profile: "Based on your intermediate level and power-focused style, **Paddle A** is the better fit. Its higher power rating (9/10 vs 7/10) aligns with your aggressive play, though you'll sacrifice some control."
- Typewriter effect: 20ms per character
- Key terms: Bold (`font-semibold`) for emphasis

**Padding:**
- Section vertical: `py-8`
- Internal gap: `gap-4`

**Background:**
- `bg-surface`
- Rounded: `rounded-2xl`
- Border: `border border-border`
- Left accent: 4px neon green border-left

---

### Section 5: Final CTAs

**Component(s):** `CtaGrid` (2 columns)

**Content requirements:**
- Two affiliate buttons (one per paddle):
  - Text: "Buy [Paddle Name] on [Retailer]"
  - Style: Primary button, full width, neon green background
  - Icon: `Lucide.ExternalLink` (16px)
  - Link: Affiliate URL (tracked)
- Price note below each: "Price as of [date]" (JetBrains Mono, `text-xs`, `text-muted-foreground`)

**Padding:**
- Section vertical: `py-8`
- Button gap: `gap-8`

**Background:**
- `bg-background` (transparent)

---

## 4. COMPONENT TREE

```
ComparePage
├── PageContainer (max-w-1280, mx-auto, px-16/8/4)
│   ├── CompareSearchBar (bg-surface, border-b, py-6)
│   │   ├── Label (Source Sans 3, sm, semibold)
│   │   ├── InputContainer (flex, gap-4, items-center)
│   │   │   ├── PaddleAutocomplete (flex-1)
│   │   │   │   ├── Input (placeholder, pre-filled from query params)
│   │   │   │   └── Dropdown (thumbnail, brand, name, price)
│   │   │   ├── SwapButton (Lucide.ArrowLeftRight, 20px)
│   │   │   └── PaddleAutocomplete (flex-1)
│   ├── ComparisonTable (grid, 2 cols, gap-8)
│   │   ├── StickyHeader[] (×2, sticky, top-0, bg-elevated, z-10)
│   │   │   ├── Image (aspect-4/3, rounded-lg, object-cover)
│   │   │   ├── Brand (text-xs, muted)
│   │   │   ├── Name (Bebas Neue, 2xl)
│   │   │   ├── Price (JetBrains Mono, 3xl, lime-400)
│   │   │   ├── StockStatus (dot indicator, text-xs)
│   │   │   └── AffiliateCta (primary, full-width, neon green)
│   │   ├── ComparisonRow[] (×11, alternating bg)
│   │   │   ├── Label (150px, Source Sans 3, base, medium)
│   │   │   ├── ValueA (centered, with winner indicator)
│   │   │   └── ValueB (centered, with winner indicator)
│   ├── RadarChartContainer (bg-elevated, rounded-2xl, border, py-8)
│   │   ├── Title (Source Sans 3, lg, semibold)
│   │   ├── RechartsRadarChart (5 axes, 2 polygons, semi-transparent)
│   │   │   ├── PolarGrid (border color)
│   │   │   ├── PolarAngleAxis (5 labels)
│   │   │   ├── PolarRadiusAxis (hidden)
│   │   │   ├── Radar (name="A", stroke=lime, fill=lime/30)
│   │   │   ├── Radar (name="B", stroke=orange, fill=orange/30)
│   │   │   └── Tooltip (hover, shows both values)
│   │   └── Legend (2 items, dots + names)
│   ├── AiVerdict (bg-surface, rounded-2xl, border, border-l-lime-500, py-8)
│   │   ├── Header (flex, items-center, gap-3)
│   │   │   ├── Icon (Lucide.Bot, 24px, lime-400)
│   │   │   └── Title (Bebas Neue, xl)
│   │   └── StreamingText (Source Sans 3, base, muted, typewriter 20ms/char)
│   └── CtaGrid (grid, 2 cols, gap-8, py-8)
│       ├── AffiliateButton[] (×2, primary, full-width, neon green)
│       │   ├── Text "Buy [Name] on [Retailer]"
│       │   └── Icon (Lucide.ExternalLink, 16px)
│       └── PriceNote (JetBrains Mono, xs, muted)
```

**Props:**
- `CompareSearchBar`: `paddleA`, `paddleB`, `onSwap`, `onChange`
- `PaddleAutocomplete`: `value`, `onChange`, `placeholder`
- `StickyHeader`: `paddle`, `onAffiliateClick`
- `ComparisonRow`: `label`, `valueA`, `valueB`, `winner` ('a' | 'b' | 'none')
- `RadarChartContainer`: `paddleA`, `paddleB`
- `AiVerdict`: `paddleA`, `paddleB`, `profile` (optional)

**State management:**
- **Local state (ComparePage component):**
  - `paddleA`: Paddle | null
  - `paddleB`: Paddle | null
  - `isLoading`: boolean
  - `verdict`: string (streaming)
- **URL state:**
  - Query params: `?a=[slug]&b=[slug]`
  - Sync on swap or autocomplete change
- **Global state:** None required

---

## 5. INTERACTIONS

### User actions available
| Element | Action | Result |
|---------|--------|--------|
| Autocomplete input | Type | Filter paddle list, show dropdown |
| Autocomplete dropdown | Click/Enter | Select paddle, update URL, refetch comparison |
| Swap button | Click | Swap A and B, update URL (no refetch) |
| Affiliate CTA (header) | Click | Open affiliate link in new tab, track click |
| Paddle name link | Click | Navigate to `/catalog/[slug]` |
| Radar chart | Hover | Show tooltip with values for both paddles |
| AI Verdict | Select text | Highlight for copying (no special behavior) |
| Affiliate CTA (bottom) | Click | Same as header CTA |

### Animation/transition specs
- **Page load:** Fade in 300ms ease-out
- **Sticky header stick:** Instant (CSS `position: sticky`)
- **Winner highlight:** Background fade-in 200ms ease-out
- **Radar chart appear:** Scale 0.9 → 1, opacity 0 → 1, 400ms ease-out
- **AI verdict streaming:** Typewriter effect, 20ms per character
- **Swap button hover:** Rotate 180deg, 200ms ease-out

### Loading state behavior
- **Initial page load (no query params):**
  - Show search bar only
  - Prompt: "Select two paddles to compare"
- **Initial page load (with query params):**
  - Skeleton for headers (image + text lines)
  - Skeleton for comparison rows (8 rows)
  - Skeleton for radar chart
  - AI verdict: "Analyzing..." placeholder
- **Autocomplete change:**
  - Keep current comparison visible
  - Show subtle spinner on search bar
  - Replace content on complete

### Error state behavior
- **Invalid slug (404):**
  - Show error state: "Paddle not found"
  - Suggest: "Try searching for a different paddle"
  - CTA: "Browse Catalog" → `/catalog`
- **Only one slug provided:**
  - Show paddle A header
  - Prompt: "Select a second paddle to compare"
  - Highlight paddle B autocomplete
- **API error:**
  - Show error banner: "Failed to load comparison. Try again?"
  - Retry button inline

### Empty state behavior
- **No paddles selected:**
  - Show search bar only
  - Illustration: `Lucide.GitCompare` (64px, muted)
  - Title: "Compare Paddles"
  - Description: "Select two paddles to see detailed comparison"

---

## 6. DATA REQUIREMENTS

### API endpoints called
| Endpoint | Method | Purpose | Caching |
|----------|--------|---------|---------|
| `GET /api/paddles/[slug]` | GET | Fetch paddle A details | ISR (revalidate: 3600) |
| `GET /api/paddles/[slug]` | GET | Fetch paddle B details | ISR (revalidate: 3600) |
| `POST /api/compare/verdict` | POST | Generate AI verdict (streaming) | No caching (real-time) |

### Data shape expected
```typescript
// URL query params
interface CompareQueryParams {
  a: string; // paddle slug
  b: string; // paddle slug
}

// Paddle detail response (same as product detail page)
interface Paddle {
  slug: string;
  brand: string;
  name: string;
  price: number;
  image: string;
  weight: number;
  coreMaterial: 'polymer' | 'nomex' | 'aluminum' | 'hybrid';
  length: number; // mm
  width: number; // mm
  coreThickness: number; // mm
  powerRating: number; // 1-10
  controlRating: number; // 1-10
  spinRating: number; // 1-10
  sweetSpotSize: 'small' | 'medium' | 'large';
  level: 'beginner' | 'intermediate' | 'advanced' | 'pro';
  stockStatus: 'in_stock' | 'out_of_stock';
  affiliateUrl: string;
  retailer: string;
}

// AI verdict request
interface VerdictRequest {
  paddleA: Paddle;
  paddleB: Paddle;
  profile?: PlayerProfile; // Optional, from localStorage
}

// AI verdict response (streaming SSE)
interface VerdictResponse {
  content: string; // Streaming text
  recommendedPaddle: 'a' | 'b' | 'tie';
}
```

### Loading strategy
- **Initial page load (with query params):** SSR (fetch both paddles server-side)
- **AI verdict:** Streaming SSE (client-side)
  - First chunk: ~500ms
  - Full verdict: 2-4s
- **Autocomplete suggestions:** CSR (debounced fetch, 300ms)
- **Images:** Eager loading (above the fold)

---

## 7. ACCESSIBILITY

### ARIA labels needed
- Search bar: `aria-label="Select paddles to compare"`, `aria-labelledby="compare-label"`
- Autocomplete inputs: `aria-label="Search paddle A"`, `aria-label="Search paddle B"`, `aria-autocomplete="list"`, `aria-expanded`, `aria-controls`
- Swap button: `aria-label="Swap paddle A and B"`
- Comparison table: `role="table"`, `aria-label="Paddle comparison"`
- Comparison rows: `role="row"`, `aria-rowindex`
- Cell labels: `role="rowheader"`, `aria-label="Price"`
- Cell values: `role="cell"`, `aria-label="Paddle A: R$ 350"`
- Winner indicator: `aria-label="Paddle A wins in this category"`
- Radar chart: `aria-label="Performance comparison radar chart"`, `role="img"`, `aria-describedby="radar-description"`
- AI verdict: `aria-label="AI recommendation"`, `aria-live="polite"` (for streaming)
- Affiliate buttons: `aria-label="Buy [Paddle Name] on [Retailer] (opens in new tab)"`

### Keyboard navigation flow
1. Tab order: Paddle A input → Paddle B input → Swap button → Comparison table (row by row) → Radar chart (not focusable) → AI verdict (not focusable) → Affiliate button A → Affiliate button B
2. Arrow keys in autocomplete: Navigate dropdown options
3. Enter in autocomplete: Select focused option
4. Escape in autocomplete: Close dropdown
5. Tab in comparison table: Skip to next row (cells not individually focusable)

### Screen reader announcements
- **On page load:** "Comparing [Paddle A name] vs [Paddle B name]"
- **On swap:** "Paddles swapped"
- **On AI verdict streaming:** "AI verdict: [Full text]" (announced once complete, aria-live polite)
- **On winner highlight:** No announcement (visual only)
- **Headings hierarchy:**
  - H1: "Compare Paddles"
  - H2: "Performance Comparison"
  - H2: "AI Verdict"
  - Paddle names in headers: Not headings (use `aria-labelledby` instead)
