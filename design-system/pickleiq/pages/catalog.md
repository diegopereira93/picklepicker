# Catalog Page Specification

## 1. ROUTE & GOAL

- **Route path:** `/catalog`
- **Primary conversion goal:** Browse and filter complete paddle catalog → product detail or compare
- **Entry points:**
  - Landing page "Browse Catalog" link (secondary CTA)
  - Chat page product card "View All" link
  - Direct navigation (users who know what they want)
  - Search engine results (SEO-optimized category pages)
- **Exit points:**
  - `/catalog/[slug]` (primary desired exit - product detail)
  - `/compare` (from compare button on product cards)
  - `/chat` (from "Ask AI" floating button)

---

## 2. LAYOUT STRUCTURE

### Desktop (1280px+)
- **Container max-width:** 1280px, centered with `mx-auto`
- **Layout:** Two-column grid
  - Left sidebar (filters): 260px fixed width, `flex-shrink-0`, sticky `top-0`
  - Main content (product grid): `flex-1`, remaining width
- **Horizontal padding:** Container `px-16`, sidebar `px-4`, grid `px-8`
- **Sidebar:** Sticky, `position: sticky`, `top-0`, `h-screen`, `overflow-y-auto`

### Tablet (768px-1279px)
- **Container max-width:** 100% (fluid)
- **Layout:** Same two-column structure
- **Sidebar:** 240px width, sticky
- **Horizontal padding:** Container `px-8`, sidebar `px-4`, grid `px-6`
- **Grid:** 2 columns (see below)

### Mobile (375px-767px)
- **Container max-width:** 100% (fluid)
- **Layout:** Single column (sidebar hidden by default)
- **Sidebar:** Filter sheet/drawer, slides up from bottom or in from right
- **Toggle:** "Filters" button (sticky top bar) opens filter sheet
- **Horizontal padding:** Container `px-4`
- **Grid:** 1 column

---

## 3. SECTIONS (top to bottom)

### Sticky Filter Sidebar

**Component(s):** `FilterSidebar`, `FilterSection`, `CheckboxGroup`, `PriceRangeSlider`, `ChipGroup`, `ToggleFilter`

**Content requirements:**
- Header: "Filters"
  - Font: Source Sans 3 `font-semibold`, `text-sm`, `text-foreground`
  - Clear all button: "Clear All" (text button, appears when filters active)
- Filter sections (collapsible, all expanded by default):

| Filter | Type | Options |
|--------|------|---------|
| Recommended Level | Checkboxes | Iniciante, Intermediário, Avançado, Profissional |
| Price Range | Dual-handle slider | R$ 0 - R$ 1000+ (step R$ 50) |
| Brand | Checkboxes + Search | Selkirk, JOOLA, Paddletek, Head, Wilson, etc. (10+ brands) |
| Weight Class | Chips | Leve (≤240g), Médio (240-260g), Pesado (≥260g) |
| Core Material | Chips | Polímero, Nomex, Alumínio, Híbrido |
| On Sale | Toggle | Single checkbox |
| Price Dropped | Toggle | Single checkbox (last 7 days) |

**Filter section specs:**
- Section title: Source Sans 3 `font-medium`, `text-sm`, `text-foreground`
- Checkboxes: Radix Checkbox, 18px, neon green when checked
- Slider: Dual-handle, neon green track, JetBrains Mono labels
- Chips: `bg-surface`, `text-xs`, `px-3 py-1.5`, rounded-full, selected `bg-lime-500`, `text-lime-950`
- Toggles: Radix Switch, 20px, neon green when on

**Padding:**
- Section vertical gap: `gap-6`
- Internal section gap: `gap-3`
- Chip gap: `gap-2`

**Background:**
- `bg-surface`
- Border right: `border-r border-border`

---

### Product Grid Header

**Component(s):** `CatalogHeader`, `SortDropdown`, `ResultCount`

**Content requirements:**
- Result count: "Showing X paddles"
  - Font: Source Sans 3 `text-sm`, `text-muted-foreground`
- Sort dropdown:
  - Options: "Relevância", "Preço: Menor → Maior", "Preço: Maior → Menor", "Nome: A-Z", "Mais Recentes"
  - Default: "Relevância" (quiz-matched first if profile exists)
  - Style: Select button, `bg-surface`, `text-sm`, `px-3 py-1.5`, rounded-md

**Padding:**
- Vertical: `py-4`
- Horizontal: `px-8` (desktop), `px-4` (mobile)

**Background:**
- `bg-background` (transparent)

---

### Product Grid

**Component(s):** `ProductGrid`, `ProductCard` (×N), `SkeletonCard` (×6 for loading)

**Content requirements:**
- Grid layout:
  - Desktop: 3 columns, `gap-5`
  - Tablet: 2 columns, `gap-4`
  - Mobile: 1 column, `gap-4`
- Product card (see ProductCard spec below):
  - Image: Aspect ratio 4/3, object-cover
  - Brand: Muted caption, `text-xs`, `text-muted-foreground`
  - Name: Display font (Bebas Neue), `text-lg`, `font-normal`
  - Price: JetBrains Mono, `text-xl`, `text-foreground`
  - Price delta badge: "↓ R$ 50" (red) or "↑ R$ 30" (green), `text-xs`
  - Attribute badges: Power/Control/Spin as dots (neon green / orange / blue)
  - Match score (if quiz done): Circular badge, percentage, neon green border
  - Action buttons: Details (primary), Compare (ghost), Alert (icon)

**Padding:**
- Grid gap: `gap-5` (desktop), `gap-4` (tablet/mobile)
- Card internal: See ProductCard spec

**Background:**
- `bg-background` (transparent)

---

### Pagination / Load More

**Component(s):** `LoadMoreButton` or `Pagination`

**Content requirements:**
- Option A (infinite scroll): "Load More" button at bottom
  - Style: Ghost button, full width
  - Appears when scroll nears bottom
- Option B (pagination): Page numbers + Next/Prev
  - Style: Button group, current page highlighted

**Padding:**
- Vertical: `py-8`
- Horizontal: Centered

**Background:**
- `bg-background` (transparent)

---

### Empty State

**Component(s):** `EmptyState`, `LucideIcon`

**Content requirements:**
- Icon: `Lucide.SearchX` (64px, `text-muted-foreground`)
- Title: "No paddles match your filters"
  - Font: Source Sans 3 `font-semibold`, `text-xl`
- Description: "Try adjusting your filters or ask the AI chat for recommendations"
  - Font: Source Sans 3 `text-sm`, `text-muted-foreground`
- CTA: "Ask AI Chat" → `/chat`
  - Style: Primary button, neon green

**Padding:**
- Section vertical: `py-20`
- Internal gap: `gap-4`

**Background:**
- `bg-surface`
- Rounded: `rounded-2xl`
- Border: `border border-border`

---

## 4. COMPONENT TREE

```
CatalogPage
├── PageContainer (flex, max-w-1280, mx-auto)
│   ├── FilterSidebar (260px, flex-shrink-0, sticky, top-0, h-screen, overflow-y-auto, bg-surface, border-r)
│   │   ├── FilterHeader
│   │   │   ├── Title (Source Sans 3, sm, semibold)
│   │   │   └── ClearAllButton (text button, conditional)
│   │   ├── FilterSection[] (×7, collapsible)
│   │   │   ├── SectionTitle (Source Sans 3, sm, medium)
│   │   │   ├── CheckboxGroup (for Level, Brand)
│   │   │   │   ├── SearchInput (for Brand)
│   │   │   │   └── Checkbox[] (Radix, 18px, lime when checked)
│   │   │   ├── PriceRangeSlider (dual-handle, lime track, mono labels)
│   │   │   ├── ChipGroup (for Weight, Core Material)
│   │   │   │   └── Chip[] (bg-surface, selected: bg-lime-500, text-lime-950)
│   │   │   └── ToggleFilter (for On Sale, Price Dropped)
│   │   │       └── Switch (Radix, 20px, lime when on)
│   └── MainContent (flex-1)
│       ├── CatalogHeader (flex, justify-between, items-center, py-4, px-8)
│       │   ├── ResultCount (Source Sans 3, sm, muted)
│       │   └── SortDropdown (bg-surface, text-sm, px-3 py-1.5, rounded-md)
│       ├── ProductGrid (grid, gap-5/4, px-8/4)
│       │   ├── ProductCard[] (×N, or SkeletonCard[] ×6 for loading)
│       │   │   ├── ImageContainer (aspect-4/3, object-cover, rounded-t-lg)
│       │   │   ├── Content (p-4)
│       │   │   │   ├── Brand (text-xs, muted)
│       │   │   │   ├── Name (Bebas Neue, lg, normal)
│       │   │   │   ├── PriceRow (flex, items-center, gap-2)
│       │   │   │   │   ├── Price (JetBrains Mono, xl)
│       │   │   │   │   └── PriceDeltaBadge (text-xs, red/green)
│       │   │   │   ├── AttributeBadges (flex, gap-1)
│       │   │   │   │   └── Dot[] (×3, neon/orange/blue for Power/Control/Spin)
│       │   │   │   ├── MatchScore (conditional, circular badge, percentage, lime border)
│       │   │   │   └── ActionButtons (flex, gap-2, mt-3)
│       │   │   │       ├── DetailsButton (primary, flex-1)
│       │   │   │       ├── CompareButton (ghost)
│       │   │   │       └── AlertButton (icon, ghost)
│       │   └── EmptyState (conditional, py-20, bg-surface, rounded-2xl, border)
│       │       ├── Icon (Lucide.SearchX, 64px, muted)
│       │       ├── Title (Source Sans 3, xl, semibold)
│       │       ├── Description (Source Sans 3, sm, muted)
│       │       └── CtaButton → /chat
│       └── Pagination (py-8, centered)
│           └── LoadMoreButton or PageNumbers
```

**Props:**
- `FilterSidebar`: `filters`, `onFilterChange`, `onClearAll`
- `CheckboxGroup`: `options[]`, `values[]`, `onChange`
- `PriceRangeSlider`: `min`, `max`, `value[]`, `onChange`
- `ChipGroup`: `options[]`, `selected[]`, `onChange`
- `ProductCard`: `paddle`, `matchScore` (optional), `onCompare`, `onAlert`
- `CatalogHeader`: `resultCount`, `sort`, `onSortChange`

**State management:**
- **Local state (CatalogPage component):**
  - `filters`: Object with all filter values
  - `sort`: string (current sort option)
  - `page`: number (for pagination)
  - `isLoading`: boolean
  - `products`: Paddle[]
- **URL state:**
  - Filters synced to query params: `?level=intermediate&brand=selkirk&minPrice=200&maxPrice=400`
  - Sort synced: `?sort=price_asc`
  - Page synced: `?page=2`
- **Global state:** None required

---

## 5. INTERACTIONS

### User actions available
| Element | Action | Result |
|---------|--------|--------|
| Filter checkbox | Click | Toggle filter, update URL, refetch products |
| Price slider | Drag | Update range, debounced (300ms), update URL, refetch |
| Chip | Click | Toggle filter, update URL, refetch |
| Toggle | Click | Toggle filter, update URL, refetch |
| Sort dropdown | Select | Change sort, update URL, refetch |
| Product card "Details" | Click | Navigate to `/catalog/[slug]` |
| Product card "Compare" | Click | Add to compare list, show toast, navigate if 2+ items |
| Product card "Alert" | Click | Toggle price alert, show confirmation toast |
| Clear All button | Click | Reset all filters, update URL, refetch |
| Load More button | Click | Fetch next page, append to grid |
| Filter toggle (mobile) | Click | Open filter sheet/drawer |

### Animation/transition specs
- **Filter apply:** Debounced 300ms, no animation (instant update)
- **Product card hover:** Scale 1 → 1.02, shadow increase, 200ms ease-out
- **Grid transition:** Fade out old, fade in new, 200ms (when filters change)
- **Skeleton loading:** Pulse animation, 1.5s cycle
- **Empty state appear:** Fade in + slide up 20px, 300ms ease-out

### Loading state behavior
- **Initial page load:**
  - Skeleton grid (6 cards)
  - Filters load instantly (no skeleton needed)
- **Filter change:**
  - Keep current products visible
  - Show subtle overlay spinner (top-right of grid)
  - Replace grid content on complete
- **Infinite scroll:**
  - Show skeleton cards at bottom while loading next page
  - Append on complete

### Error state behavior
- **API error (products fetch):**
  - Show error banner at top: "Failed to load products. Try again?"
  - Retry button inline
  - Keep filters intact
- **No results:**
  - Show EmptyState component (see above)
  - Suggest "Ask AI Chat" as alternative

### Empty state behavior
- **Zero products:**
  - Triggered when filter combination yields no results
  - Show EmptyState component with AI chat CTA
- **No quiz profile:**
  - Match score badges hidden
  - Sort defaults to "Relevância" (not personalized)

---

## 6. DATA REQUIREMENTS

### API endpoints called
| Endpoint | Method | Purpose | Caching |
|----------|--------|---------|---------|
| `GET /api/paddles` | GET | Fetch filtered/sorted product list | No caching (dynamic filters) |
| `GET /api/paddles/[slug]` | GET | Fetch individual product (for card enrichment) | ISR (revalidate: 3600) |

### Data shape expected
```typescript
// Request query params
interface PaddleFilters {
  level?: ('beginner' | 'intermediate' | 'advanced' | 'pro')[];
  brand?: string[];
  minPrice?: number;
  maxPrice?: number;
  weight?: ('light' | 'medium' | 'heavy')[];
  coreMaterial?: ('polymer' | 'nomex' | 'aluminum' | 'hybrid')[];
  onSale?: boolean;
  priceDropped?: boolean;
  sort?: 'relevance' | 'price_asc' | 'price_desc' | 'name_asc' | 'newest';
  page?: number;
  limit?: number; // Default 24
}

// Response
interface PaddleListResponse {
  products: Paddle[];
  total: number;
  page: number;
  totalPages: number;
}

interface Paddle {
  slug: string;
  brand: string;
  name: string;
  price: number;
  previousPrice?: number; // For delta calculation
  image: string;
  level: 'beginner' | 'intermediate' | 'advanced' | 'pro';
  weight: number; // grams
  coreMaterial: 'polymer' | 'nomex' | 'aluminum' | 'hybrid';
  powerRating: number; // 1-10
  controlRating: number; // 1-10
  spinRating: number; // 1-10
  matchScore?: number; // 0-100, only if quiz profile exists
}
```

### Loading strategy
- **Initial page load:** SSR (fetch first page server-side)
- **Filter/sort change:** CSR (client-side fetch, optimistic UI)
- **Infinite scroll:** CSR (append to existing list)
- **Images:** Lazy loading (`loading="lazy"`)

---

## 7. ACCESSIBILITY

### ARIA labels needed
- Filter sidebar: `aria-label="Product filters"`, `aria-labelledby="filter-header"`
- Individual filters: `aria-labelledby="level-filter-label"`, etc.
- Checkbox group: `role="group"`, `aria-labelledby="group-label"`
- Price slider: `aria-label="Price range"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow` (for each handle)
- Product grid: `aria-label="Product catalog"`, `role="list"`
- Product card: `role="listitem"`, `aria-labelledby="product-{slug}-name"`
- Match score: `aria-label="Match score: 85%"`
- Sort dropdown: `aria-label="Sort products"`, `aria-expanded`
- Load More button: `aria-label="Load more products"`
- Empty state: `aria-label="No products found"`
- Filter toggle (mobile): `aria-label="Open filters"`, `aria-expanded={sheetOpen}`

### Keyboard navigation flow
1. Tab order (desktop): Filter sidebar (top to bottom) → Sort dropdown → Product grid (row by row, left to right) → Load More button
2. Tab order (mobile): Filter toggle → Sort dropdown → Product grid → Load More
3. Arrow keys in grid: Navigate between product cards (Up/Down/Left/Right)
4. Enter on product card: Navigate to product detail
5. Escape: Close filter sheet (mobile)

### Screen reader announcements
- **On filter change:** "X products found" (aria-live polite)
- **On sort change:** "Products sorted by [sort option]"
- **On empty state:** "No products match your filters. Try adjusting or ask AI chat."
- **On load more:** "Loading more products..." → "X more products loaded"
- **Headings hierarchy:**
  - H1: "Paddle Catalog"
  - H2: "Filters"
  - H3: Each filter section title (Level, Price, Brand, etc.)
  - Product names: Not headings (use `aria-labelledby` instead)
