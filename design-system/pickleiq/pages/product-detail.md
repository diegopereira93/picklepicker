# Product Detail Page Specification

## 1. ROUTE & GOAL

- **Route path:** `/catalog/[slug]`
- **Primary conversion goal:** Full paddle info + high-conversion affiliate CTA
- **Entry points:**
  - Catalog page product card "Details" button
  - Chat page embedded ProductCard "Details" button
  - Compare page paddle name links
  - Search engine results (SEO-optimized product pages)
  - Social media shares (deep links)
- **Exit points:**
  - Affiliate link (primary desired exit - monetization)
  - `/compare` (from "Compare" button)
  - `/catalog` (browse more options)
  - `/chat` (ask AI about this paddle)

---

## 2. LAYOUT STRUCTURE

### Desktop (1280px+)
- **Container max-width:** 1280px, centered with `mx-auto`
- **Layout:** Single column, vertical scroll
- **Horizontal padding:** `px-16`
- **Section 1 (Header block):** Two-column grid (50/50), `gap-12`
- **Subsequent sections:** Full width, max-width `prose` for text content

### Tablet (768px-1279px)
- **Container max-width:** 100% (fluid)
- **Layout:** Same single column
- **Header block:** Same two-column grid, `gap-8`
- **Horizontal padding:** `px-8`

### Mobile (375px-767px)
- **Container max-width:** 100% (fluid)
- **Layout:** Single column, **stacked** (image on top, details below)
- **Header block:** Single column, `gap-6`
- **Horizontal padding:** `px-4`
- **Image:** Full width, aspect ratio 4/3

---

## 3. SECTIONS (top to bottom)

### Section 1: Header Block

**Component(s):** `ProductHeader`, `ProductImage`, `ProductInfo`, `AffiliateCta`

**Content requirements:**
- **Left column (Image):**
  - Image: Aspect ratio 4/3, object-cover, rounded-2xl
  - Zoom on hover: Scale 1 → 1.05, cursor-zoom-in
  - Lightbox on click: Full-screen overlay with zoomed image
  - Alt text: "[Brand] [Name] paddle"
  - Stock badge (top-right corner): "Em estoque" (green) / "Fora de estoque" (red)
    - Font: JetBrains Mono, `text-xs`, rounded-full, `px-2 py-1`

- **Right column (Info):**
  - Brand: Muted caption, `text-xs`, `text-muted-foreground`, uppercase `tracking-wide`
  - Name: Bebas Neue, `text-5xl` (desktop), `text-4xl` (tablet), `text-3xl` (mobile), `text-foreground`
  - Price row:
    - Price: JetBrains Mono, `text-4xl`, `text-lime-400`
    - Price history link: "Ver histórico" (text button, `text-xs`, `text-muted-foreground`)
  - Stock status (if not shown on image): Same as above
  - Affiliate CTA:
    - Text: "Comprar Agora em [Retailer]"
    - Style: Primary button, full width, neon green background, glow on hover
    - Icon: `Lucide.ExternalLink` (20px)
    - Link: Affiliate URL (tracked, opens in new tab)
  - Secondary actions (horizontal row below CTA):
    - Compare button: `Lucide.GitCompare` (16px), "Comparar", ghost button
    - Alert link: `Lucide.Bell` (16px), "Alerta de Preço", text button
    - Share button: `Lucide.Share` (16px), "Compartilhar", text button

**Padding:**
- Section vertical: `py-12`
- Column gap: `gap-12` (desktop), `gap-8` (tablet), `gap-6` (mobile)
- Internal gaps: `gap-4` (info items)

**Background:**
- `bg-background` (transparent)

---

### Section 2: Technical Specs Table

**Component(s):** `SpecsTable`, `SpecsRow` (×N)

**Content requirements:**
- Title: "Especificações Técnicas"
  - Font: Source Sans 3 `font-semibold`, `text-lg`, `text-foreground`
- Table (2 columns, alternating row colors):

| Spec | Value | Format |
|------|-------|--------|
| Peso | "250g" | JetBrains Mono |
| Material do Core | "Polímero" | Source Sans 3 |
| Comprimento | "410mm" | JetBrains Mono |
| Largura | "200mm" | JetBrains Mono |
| Espessura do Core | "16mm" | JetBrains Mono |
| Nível Recomendado | "Intermediário" | Source Sans 3 |
| Formato | "Padrão" | Source Sans 3 |
| Garantia | "1 ano" | Source Sans 3 |

**Row specs:**
- Label: Source Sans 3 `text-sm`, `text-muted-foreground`
- Value: JetBrains Mono `text-base`, `text-foreground`
- Alternating background: `bg-surface` / `bg-elevated`

**Padding:**
- Section vertical: `py-8`
- Row vertical: `py-3`
- Row horizontal: `px-4`

**Background:**
- `bg-surface`
- Rounded: `rounded-2xl`
- Border: `border border-border`

---

### Section 3: Price History Chart

**Component(s):** `PriceHistoryChart`, `RechartsLineChart`

**Content requirements:**
- Title: "Histórico de Preço (90 dias)"
  - Font: Source Sans 3 `font-semibold`, `text-lg`, `text-foreground`
- Line chart:
  - X-axis: Date (last 90 days, formatted as "DD/MM")
  - Y-axis: Price (BRL, formatted as "R$ XXX")
  - Line: Neon green (`#84CC16`), 2px stroke
  - Current price reference line: Dashed, orange (`#FFA500`), 1px
  - Drop regions: Highlighted in red background (`bg-red-500/10`)
  - Tooltip: On hover, shows date + price
  - Zoom: Brush at bottom for zooming (optional, MVP can skip)
- Stats below chart:
  - Lowest: "Menor: R$ XXX" (JetBrains Mono, `text-sm`)
  - Highest: "Maior: R$ XXX" (JetBrains Mono, `text-sm`)
  - Average: "Média: R$ XXX" (JetBrains Mono, `text-sm`)
  - Current vs Average: "Atual: X% abaixo da média" (green/red text)

**Padding:**
- Section vertical: `py-8`
- Chart internal: `p-4`

**Background:**
- `bg-elevated`
- Rounded: `rounded-2xl`
- Border: `border border-border`

---

### Section 4: AI Summary

**Component(s):** `AiSummary`, `StreamingText`

**Content requirements:**
- Header: "Análise IA"
  - Font: Bebas Neue, `text-xl`, `text-foreground`
  - Icon: `Lucide.Bot` (24px, neon green)
- Streaming paragraphs (2):
  - **Paragraph 1 (Strengths):**
    - Font: Source Sans 3 `text-base`, `text-muted-foreground`
    - Content: "Este paddle se destaca em [power/control/spin] devido ao [core material/design]. Ideal para jogadores que [playstyle]."
  - **Paragraph 2 (Weaknesses):**
    - Font: Source Sans 3 `text-base`, `text-muted-foreground`
    - Content: "Pontos de atenção: [weakness]. Jogadores [type] podem preferir alternativas com mais [attribute]."
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

### Section 5: Ideal For

**Component(s):** `IdealFor`, `ProfileChips`

**Content requirements:**
- Title: "Ideal Para"
  - Font: Source Sans 3 `font-semibold`, `text-lg`, `text-foreground`
- Profile chips (horizontal wrap):
  - Level: e.g., "Intermediário"
  - Style: e.g., "Power"
  - Location: e.g., "Sudeste" (based on availability/pricing)
  - Each chip: `bg-lime-500/10`, `text-lime-400`, `text-xs`, `px-3 py-1.5`, rounded-full
  - Icon: `Lucide.Check` (12px) before each label

**Padding:**
- Section vertical: `py-6`
- Chip gap: `gap-2`

**Background:**
- `bg-background` (transparent)

---

### Section 6: Similar Paddles

**Component(s):** `SimilarPaddles`, `ProductCarousel`, `ProductCard` (compact)

**Content requirements:**
- Title: "Paddles Similares"
  - Font: Source Sans 3 `font-semibold`, `text-lg`, `text-foreground`
- Horizontal scroll carousel:
  - 4-6 product cards (compact mode)
  - Card width: 200px (fixed)
  - Gap: `gap-4`
  - Scroll: Horizontal, snap-to-center
  - Navigation: Left/Right arrows (appear on hover, desktop only)
- Compact product card:
  - Image: Aspect ratio 4/3, rounded-lg
  - Brand: `text-xs`, muted
  - Name: Bebas Neue, `text-base`, line-clamp-2
  - Price: JetBrains Mono, `text-lg`, lime-400
  - Action: Click → navigate to `/catalog/[slug]`

**Padding:**
- Section vertical: `py-8`
- Carousel internal: `px-4` (for overflow)

**Background:**
- `bg-background` (transparent)

---

## 4. COMPONENT TREE

```
ProductDetailPage
├── PageContainer (max-w-1280, mx-auto, px-16/8/4)
│   ├── ProductHeader (grid, 2 cols desktop, 1 col mobile, gap-12/8/6, py-12)
│   │   ├── LeftColumn (Image)
│   │   │   ├── ImageContainer (relative, aspect-4/3, rounded-2xl, overflow-hidden)
│   │   │   │   ├── Image (object-cover, zoom on hover, lightbox on click)
│   │   │   │   └── StockBadge (absolute, top-2 right-2, JetBrains Mono, xs, rounded-full)
│   │   └── RightColumn (Info)
│   │       ├── Brand (text-xs, muted, uppercase, tracking-wide)
│   │       ├── Name (Bebas Neue, 5xl/4xl/3xl)
│   │       ├── PriceRow (flex, items-center, gap-4)
│   │       │   ├── Price (JetBrains Mono, 4xl, lime-400)
│   │       │   └── HistoryLink (text button, xs, muted)
│   │       ├── StockStatus (conditional, if not on image)
│   │       ├── AffiliateCta (primary, full-width, neon green, glow on hover)
│   │       │   ├── Text "Comprar Agora em [Retailer]"
│   │       │   └── Icon (Lucide.ExternalLink, 20px)
│   │       └── SecondaryActions (flex, gap-4, mt-4)
│   │           ├── CompareButton (ghost, flex, items-center, gap-2)
│   │           ├── AlertLink (text button, flex, items-center, gap-2)
│   │           └── ShareButton (text button, flex, items-center, gap-2)
│   ├── SpecsSection (bg-surface, rounded-2xl, border, py-8)
│   │   ├── Title (Source Sans 3, lg, semibold)
│   │   └── SpecsTable
│   │       └── SpecsRow[] (×8, alternating bg)
│   │           ├── Label (Source Sans 3, sm, muted)
│   │           └── Value (JetBrains Mono, base)
│   ├── PriceHistorySection (bg-elevated, rounded-2xl, border, py-8)
│   │   ├── Title (Source Sans 3, lg, semibold)
│   │   ├── RechartsLineChart (90 days, lime line, orange reference, red drop regions)
│   │   │   ├── XAxis (date, DD/MM format)
│   │   │   ├── YAxis (price, BRL format)
│   │   │   ├── Line (stroke=lime, 2px)
│   │   │   ├── ReferenceLine (stroke=orange, dashed)
│   │   │   ├── Brush (optional, zoom)
│   │   │   └── Tooltip (hover, date + price)
│   │   └── StatsRow (flex, gap-8, mt-4)
│   │       ├── Lowest (JetBrains Mono, sm)
│   │       ├── Highest (JetBrains Mono, sm)
│   │       ├── Average (JetBrains Mono, sm)
│   │       └── CurrentVsAverage (green/red text)
│   ├── AiSummarySection (bg-surface, rounded-2xl, border, border-l-lime-500, py-8)
│   │   ├── Header (flex, items-center, gap-3)
│   │   │   ├── Icon (Lucide.Bot, 24px, lime-400)
│   │   │   └── Title (Bebas Neue, xl)
│   │   └── StreamingText (2 paragraphs, Source Sans 3, base, muted, typewriter 20ms/char)
│   ├── IdealForSection (py-6)
│   │   ├── Title (Source Sans 3, lg, semibold)
│   │   └── ProfileChips (flex-wrap, gap-2)
│   │       └── ProfileChip[] (×3)
│   │           ├── Icon (Lucide.Check, 12px, lime-400)
│   │           └── Label (bg-lime-500/10, text-lime-400, xs, px-3 py-1.5, rounded-full)
│   └── SimilarPaddlesSection (py-8)
│       ├── Title (Source Sans 3, lg, semibold)
│       └── ProductCarousel (horizontal-scroll, snap-center, px-4)
│           ├── NavButton (left, conditional, desktop only)
│           ├── ProductCard[] (×4-6, compact, 200px width)
│           │   ├── Image (aspect-4/3, rounded-lg)
│           │   ├── Brand (text-xs, muted)
│           │   ├── Name (Bebas Neue, base, line-clamp-2)
│           │   └── Price (JetBrains Mono, lg, lime-400)
│           └── NavButton (right, conditional, desktop only)
```

**Props:**
- `ProductHeader`: `paddle`, `onCompare`, `onAlert`, `onShare`
- `ImageContainer`: `src`, `alt`, `onLightboxOpen`
- `AffiliateCta`: `url`, `retailer`, `paddleName`
- `SpecsTable`: `specs` (array of { label, value })
- `PriceHistoryChart`: `history` (array of { date, price }), `currentPrice`
- `AiSummary`: `paddle`, `profile` (optional, for personalization)
- `IdealFor`: `level`, `style`, `location`
- `ProductCarousel`: `products[]`, `onProductClick`

**State management:**
- **Local state (ProductDetailPage component):**
  - `paddle`: Paddle | null
  - `isLoading`: boolean
  - `aiSummary`: string (streaming)
  - `lightboxOpen`: boolean
  - `isAlertSet`: boolean
- **URL state:**
  - Slug from route: `/catalog/[slug]`
- **Global state:** None required

---

## 5. INTERACTIONS

### User actions available
| Element | Action | Result |
|---------|--------|--------|
| Product image | Hover | Zoom in (scale 1.05) |
| Product image | Click | Open lightbox (full-screen zoom) |
| Lightbox | Click/Escape | Close lightbox |
| Affiliate CTA | Click | Open affiliate link in new tab, track click |
| Compare button | Click | Add to compare, navigate to `/compare` if 2+ items |
| Alert link | Click | Toggle price alert, show confirmation toast |
| Share button | Click | Open share dialog (native Web Share API or fallback) |
| Price history link | Click | Scroll to price history section (smooth scroll) |
| Similar paddle card | Click | Navigate to `/catalog/[slug]` |
| Carousel arrows | Click | Scroll carousel left/right |

### Animation/transition specs
- **Page load:** Fade in 300ms ease-out
- **Image zoom:** Scale 1 → 1.05, 200ms ease-out
- **Lightbox appear:** Fade in + scale 0.95 → 1, 300ms ease-out
- **Affiliate CTA hover:** Glow effect (shadow-lime-500/25), 150ms ease-out
- **AI summary streaming:** Typewriter effect, 20ms per character
- **Carousel scroll:** Smooth scroll, 300ms ease-out
- **Carousel arrows appear:** Fade in on hover, 150ms ease-out

### Loading state behavior
- **Initial page load:**
  - Skeleton for header (image placeholder, text lines)
  - Skeleton for specs table (8 rows)
  - Skeleton for price chart
  - AI summary: "Analisando..." placeholder
- **Image loading:** Low-quality placeholder (blurhash) → full resolution
- **AI summary:** Streaming SSE, first chunk ~500ms

### Error state behavior
- **404 (invalid slug):**
  - Show error state: "Paddle não encontrado"
  - Suggest: "Busque por outro modelo ou volte ao catálogo"
  - CTA: "Ver Catálogo" → `/catalog`
- **API error:**
  - Show error banner: "Erro ao carregar paddle. Tentar novamente?"
  - Retry button inline
- **AI summary error:**
  - Fallback to static summary (pre-generated or generic)
  - Show note: "Análise indisponível no momento"

### Empty state behavior
- **No similar paddles:**
  - Hide section entirely (don't show empty carousel)
- **No price history (< 7 days):**
  - Show note: "Histórico disponível após 7 dias de monitoramento"
  - Hide chart, show only current price

---

## 6. DATA REQUIREMENTS

### API endpoints called
| Endpoint | Method | Purpose | Caching |
|----------|--------|---------|---------|
| `GET /api/paddles/[slug]` | GET | Fetch paddle details | ISR (revalidate: 3600) |
| `GET /api/paddles/[slug]/history` | GET | Fetch 90-day price history | ISR (revalidate: 3600) |
| `GET /api/paddles/[slug]/similar` | GET | Fetch 4-6 similar paddles | ISR (revalidate: 3600) |
| `POST /api/paddles/[slug]/ai-summary` | POST | Generate AI summary (streaming) | No caching (real-time) |
| `POST /api/alerts` | POST | Toggle price alert | No caching |
| `POST /api/compare` | POST | Add to compare list | No caching |

### Data shape expected
```typescript
// URL route param
interface ProductDetailRoute {
  slug: string;
}

// Paddle detail response
interface Paddle {
  slug: string;
  brand: string;
  name: string;
  price: number;
  previousPrice?: number;
  image: string;
  images: string[]; // Multiple angles
  weight: number;
  coreMaterial: 'polymer' | 'nomex' | 'aluminum' | 'hybrid';
  length: number;
  width: number;
  coreThickness: number;
  powerRating: number;
  controlRating: number;
  spinRating: number;
  sweetSpotSize: 'small' | 'medium' | 'large';
  level: 'beginner' | 'intermediate' | 'advanced' | 'pro';
  shape: 'standard' | 'wide' | 'elongated';
  warranty: string;
  stockStatus: 'in_stock' | 'out_of_stock';
  retailer: string;
  affiliateUrl: string;
}

// Price history response
interface PriceHistory {
  history: { date: string; price: number }[]; // Last 90 days
  lowest: number;
  highest: number;
  average: number;
}

// AI summary request
interface AiSummaryRequest {
  paddle: Paddle;
  profile?: PlayerProfile; // Optional, for personalization
}

// AI summary response (streaming SSE)
interface AiSummaryResponse {
  strengths: string;
  weaknesses: string;
}
```

### Loading strategy
- **Initial page load:** SSR (fetch paddle, history, similar server-side)
- **AI summary:** Streaming SSE (client-side)
- **Images:** Lazy loading for secondary images, eager for primary
- **Similar paddles:** ISR (cached, no loading state needed)

---

## 7. ACCESSIBILITY

### ARIA labels needed
- Product image: `aria-label="[Brand] [Name] paddle image"`, `role="img"`
- Stock badge: `aria-label="In stock"` or `aria-label="Out of stock"`
- Affiliate CTA: `aria-label="Buy [Paddle Name] on [Retailer] (opens in new tab)"`
- Compare button: `aria-label="Compare [Paddle Name] with other paddles"`
- Alert link: `aria-label="Set price alert for [Paddle Name]"`, `aria-pressed={isAlertSet}`
- Share button: `aria-label="Share [Paddle Name]"`
- Price history chart: `aria-label="Price history over 90 days"`, `role="img"`, `aria-describedby="chart-description"`
- AI summary: `aria-label="AI analysis of [Paddle Name]"`, `aria-live="polite"` (for streaming)
- Similar paddles carousel: `aria-label="Similar paddles"`, `role="list"`
- Carousel arrows: `aria-label="Scroll left"`, `aria-label="Scroll right"`
- Lightbox: `aria-label="Zoomed image of [Paddle Name]"`, `role="dialog"`, `aria-modal="true"`

### Keyboard navigation flow
1. Tab order: Product image → Affiliate CTA → Compare button → Alert link → Share button → Specs table (not focusable, skip) → Price history chart (not focusable, skip) → AI summary (not focusable, skip) → Similar paddles carousel (cards focusable) → Carousel arrows
2. Arrow keys in carousel: Navigate between product cards (Left/Right)
3. Enter on product card: Navigate to product detail
4. Escape in lightbox: Close lightbox
5. Tab in lightbox: Trap focus within lightbox (close button only)

### Screen reader announcements
- **On page load:** "[Brand] [Name], [Price], [Stock status]"
- **On AI summary streaming:** "AI analysis: [Full text]" (announced once complete, aria-live polite)
- **On alert toggle:** "Price alert set for [Paddle Name]" or "Price alert removed"
- **On lightbox open:** "Zoomed image of [Paddle Name]. Press Escape to close."
- **Headings hierarchy:**
  - H1: Paddle name (Bebas Neue, 5xl)
  - H2: "Especificações Técnicas"
  - H2: "Histórico de Preço (90 dias)"
  - H2: "Análise IA"
  - H2: "Ideal Para"
  - H2: "Paddles Similares"
