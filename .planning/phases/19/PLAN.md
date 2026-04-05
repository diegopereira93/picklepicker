# Phase 19: Catalog-A Comparison Table + Polish

**Status:** Ready for execution
**Milestone:** v1.6.0 — UI Redesign
**Dependencies:** Phase 16 (DESIGN.md v3.0) — COMPLETE, Phase 17 (Home-C) — COMPLETE, Phase 18 (Chat-B) — COMPLETE
**Created:** 2026-04-05

## Goal

Redesign the catalog with a sortable data table and visual grid toggle, then polish cross-screen coherence.

## Context

**Design Review Source:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/`
**Approved Variant:** Catalog-A (Comparison Table) + product images from Catalog-B + grid toggle — score 8/10

**Current State (v1.4.0):**
- Catalog page (`frontend/src/app/paddles/page.tsx`) is a server component that fetches paddles via `fetchPaddlesList` from `@/lib/seo.ts`
- Renders a grid of product cards using `hy-product-card` and `hy-catalog-grid` classes
- No sorting, no filtering, no table view, no comparison feature
- No client-side interactivity (server-rendered)

**Root Causes:**
1. Current catalog uses basic product cards — no comparison capability
2. Analytical persona needs sortable, scannable data
3. No way to compare paddles side-by-side on mobile

## Requirements Coverage

| Requirement | Tasks | Notes |
|-------------|-------|-------|
| CAT-01 | 19.1, 19.2 | Filter bar + comparison table with sortable columns |
| CAT-02 | 19.3 | Product grid view with hover-reveal specs |
| CAT-03 | 19.1 | Table/card toggle |
| CAT-04 | 19.4 | Score badges (color-coded) |
| COH-01 | 19.5 | Cross-screen navigation consistency |
| COH-02 | 19.5 | CTA style consistency |
| COH-03 | 19.5 | Funnel paths (Home→Chat→Catalog) |
| COH-04 | 19.5 | Responsive at 375px, 768px, 1440px |
| QA-01 | 19.6 | New component tests |
| QA-02 | 19.7 | Full test suite + AI slop audit |
| QA-03 | 19.7 | Responsive smoke test |

## Execution Waves

```
Wave 1 (parallel — new components):
├── 19.2a: FilterBar component
├── 19.2b: ComparisonTable component
├── 19.3a: ProductGrid component (polished card view)
└── 19.3b: SelectionBar component

Wave 2 (after Wave 1 — assemble page):
└── 19.1: Redesign paddles/page.tsx as client component with filter + table + grid toggle

Wave 3 (after Wave 2 — polish):
└── 19.5: Cross-screen coherence verification

Wave 4 (after all — verification):
└── 19.7: Build + tests + AI slop audit
```

---

## Task Details

### Task 19.1 — Redesign Catalog Page

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/app/paddles/page.tsx`
**Dependencies:** Wave 1 components (FilterBar, ComparisonTable, ProductGrid, SelectionBar)
**Requirements:** CAT-01, CAT-03, COH-01–04

**Changes:**

1. Convert from server component to client component with `'use client'` directive
2. Fetch paddles on mount via `useEffect` + `fetchPaddles` from `@/lib/api` (NOT `fetchPaddlesList` from seo.ts)
3. Add state: `viewMode: 'table' | 'grid'`, `sortBy: string`, `sortDir: 'asc' | 'desc'`, `selectedIds: Set<number>`, `filterBrand: string | null`, `filterLevel: string | null`
4. Page structure:
   ```
   <section className="hy-dark-section">
     <div className="hy-container" style={{ maxWidth: 'var(--max-width-data)' }}>
       <Breadcrumb />
       <SectionLabel>CATÁLOGO</SectionLabel>
       <H1>Catálogo de Raquetes</H1>
       <FilterBar filters={...} onFilterChange={...} />
       <ResultsCount />
       <ViewToggle />
       {viewMode === 'table' ? <ComparisonTable paddles={sorted} selected={selectedIds} onSelect={...} /> : <ProductGrid paddles={sorted} selected={selectedIds} onSelect={...} />}
       {selectedIds.size > 0 && <SelectionBar count={selectedIds.size} onCompare={...} />}
     </div>
   </section>
   ```
5. Sort logic: client-side sorting by name, brand, price, score. Default: name asc.
6. Filter logic: client-side filter by brand (unique brands from data), skill_level
7. Keep existing SEO metadata via `generateMetadata` in a separate layout or keep server component wrapper

**QA:** Table sorts by clicking column headers. Grid/table toggle switches views. Filters narrow results. Selection bar appears when items selected.

---

### Task 19.2 — FilterBar + ComparisonTable Components

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:**
- `frontend/src/components/catalog/filter-bar.tsx` (NEW)
- `frontend/src/components/catalog/comparison-table.tsx` (NEW)

**FilterBar:**
- Props: `{ brands: string[], levels: string[], activeBrand: string | null, activeLevel: string | null, onBrandChange, onLevelChange, resultCount: number, viewMode, onViewModeChange }`
- Brand filter: row of filter chips using `.hy-filter-chip` / `.hy-filter-chip.active` classes
- Level filter: row of filter chips for beginner/intermediate/advanced
- Sort dropdown: `<select>` styled with dark bg, white text, 2px border
- View toggle: two buttons "Tabela" / "Cards" using `.hy-toggle-track` pattern
- Results count: "X raquetes encontradas" in gray text

**ComparisonTable:**
- Props: `{ paddles: Paddle[], selected: Set<number>, onSelect: (id: number) => void, sortBy: string, onSort: (col: string) => void }`
- Columns: checkbox, image thumbnail, name, brand, price, weight, face, core, score badge
- Sortable columns: click header to sort asc/desc. Sort indicator arrow.
- Alternating row colors: white / var(--color-near-black)
- Image: 40x40px, SafeImage, fallback "Foto"
- Price: JetBrains Mono, data-green
- Score badge: color-coded (high green, medium yellow, low red) per DESIGN.md
- Checkbox: toggle selection. Use `<input type="checkbox">`
- Responsive: horizontal scroll on mobile

---

### Task 19.3 — ProductGrid + SelectionBar Components

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:**
- `frontend/src/components/catalog/product-grid.tsx` (NEW)
- `frontend/src/components/catalog/selection-bar.tsx` (NEW)

**ProductGrid:**
- Props: `{ paddles: Paddle[], selected: Set<number>, onSelect: (id: number) => void }`
- 3-column grid (1 col mobile, 2 col tablet, 3 col desktop)
- Cards: image container, hover-reveal specs overlay, compare checkbox
- Uses existing `hy-product-card` classes as base
- Link to paddle detail page
- Checkbox in top-right corner for comparison selection

**SelectionBar:**
- Props: `{ count: number, onCompare: () => void, onClear: () => void }`
- Sticky bottom bar, dark background, lime border-top
- Shows: "X raquetes selecionadas" + "Comparar" CTA button + "Limpar" text button
- Only renders when count > 0

---

### Task 19.5 — Cross-Screen Coherence Verification

**Category:** `quick`
**Skills:** `['frontend-ui-ux']`
**Files:** All Phase 17, 18, 19 files
**Dependencies:** All implementation complete

**Checks:**
1. Navigation consistent across Home/Chat/Catalog (same nav bar, same links)
2. CTA styles match (hy-button-cta used everywhere)
3. Funnel paths: Home→Quiz→Chat, Home→Catalog, Home→Chat→Catalog
4. Responsive at 375px, 768px, 1440px

---

### Task 19.7 — Build + Tests + AI Slop Audit

**Category:** `quick`
**Skills:** `['frontend-ui-ux']`
**Files:** All frontend files

**Checks:**
1. `npm run build` — no TypeScript or CSS errors
2. `npm run test` — all 161+ tests pass
3. AI slop checklist on all 3 screens

---

## Success Criteria

1. Comparison table sorts by any column (price, score, name)
2. Table/card toggle switches views without page reload
3. Score badges color-coded correctly
4. Bottom selection bar appears on selection with correct count
5. All 3 funnel paths work end-to-end
6. All existing tests pass + no new test failures
7. AI slop checklist passes on all screens

## Commit Strategy

4 atomic commits:
1. `feat(catalog): add FilterBar and ComparisonTable components`
2. `feat(catalog): add ProductGrid and SelectionBar components`
3. `feat(catalog): redesign catalog page with table/grid toggle + filters`
4. `test(catalog): verify cross-screen coherence and responsive layout`
