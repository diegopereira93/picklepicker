# Phase 13: NVIDIA UI Redesign — Context

**Source:** `frontend/nvidia/UI-SPEC.md` (approved design contract, 2026-04-02)
**Goal:** Restyle the PickleIQ Next.js frontend to match the NVIDIA-inspired design system. Custom CSS only — no new component libraries. All styling decisions are locked in UI-SPEC.md; executor must not deviate.

---

## PRD Requirements (from UI-SPEC.md)

### NV-01 — Design System Setup
- Remove all Tailwind utility classes that conflict with the NVIDIA palette
- Load NVIDIA-EMEA font with fallback: `font-family: 'NVIDIA-EMEA', Arial, Helvetica, sans-serif`
- Load Font Awesome 6 Pro + FA 6 Sharp via CDN in `layout.tsx` (icon glyphs only)
- Establish CSS custom properties for all palette colors in `globals.css`

### NV-02 — Color Palette
Apply the full palette as CSS variables:
- `--color-green: #76b900` — borders, underlines, CTA outlines, active indicators (NOT fills)
- `--color-black: #000000` — primary background, dominant bg tone
- `--color-white: #ffffff` — text on dark, light section bg, card surfaces
- `--color-green-light: #bff230` — hover highlights
- `--color-near-black: #1a1a1a` — dark card bg
- `--color-gray-border: #5e5e5e` — subtle borders, dividers
- `--color-gray-300: #a7a7a7`, `--color-gray-400: #898989`, `--color-gray-500: #757575`
- Status: error `#e52020`, success `#3f8500`, info `#0046a4`
- Decorative: purple `#4d1368`, fuchsia `#8c1c55`
- Interactive: link-hover `#3860be`, button-hover `#1eaedb`, button-active `#007fff`

### NV-03 — Typography
Apply 4 canonical sizes with 2 weights only:
- 24px / weight 700 / line-height 1.25 → Display Hero, Section Heading, Card Title, Button Large
- 24px / weight 400 / line-height 1.75 → Sub-heading
- 16px / weight 400 / line-height 1.50 → Body, Body Small
- 16px / weight 700 / line-height 1.25–1.50 → Body Bold, Button, Button Compact
- 14px / weight 700 / line-height 1.43 → Link, Link Uppercase, Caption
- 12px / weight 400–700 → Caption Small, Micro Label, Micro
- Navigation: 14px weight 700 `text-transform: uppercase`
- Letter-spacing: normal everywhere except Button Compact (0.144px)

### NV-04 — Spacing & Border Radius
- Base unit: 8px. Key tokens: xs=4px, sm=8px, md=16px, lg=24px, xl=32px, 2xl=48px, 3xl=64px, 4xl=80px
- Button padding: exactly `11px 13px` (do not normalize)
- Border radius: `2px` universal default; `50%` for avatars only; `1px` for inline spans
- Card grid gap: 20px

### NV-05 — Button Components
Replace all shadcn button variants with:
- **Primary:** `background: transparent; border: 2px solid #76b900; border-radius: 2px; padding: 11px 13px; font: 16px weight 700`
  - `:hover` → `background: #1eaedb; color: #fff`
  - `:active` → `background: #007fff; border: 1px solid #003eff`
  - `:focus` → `background: #1eaedb; outline: 2px solid #000`
- **Secondary:** same but `border: 1px solid #76b900`
- **Compact:** 16px weight 700, `letter-spacing: 0.144px`, `line-height: 1.00`

### NV-06 — Cards & Containers
- Light section: `background: #ffffff; border-radius: 2px; box-shadow: rgba(0,0,0,0.3) 0px 0px 5px 0px`
- Dark section: `background: #1a1a1a` (same shadow)
- Card title: green underline `border-bottom: 2px solid #76b900`
- Product grid: 3-col desktop / 2-col tablet / 1-col mobile; gap: 20px

### NV-07 — Navigation Bar
Restyle `header.tsx`:
- `background: #000000` sticky full-width
- Logo: left-aligned NVIDIA wordmark (use PickleIQ logo, left-aligned)
- Links: 14px weight 700 uppercase white, `:hover` → `#3860be`
- CTA: Primary green-border button, right-aligned
- Collapse to hamburger overlay at `≤1024px`

### NV-08 — Links
- On dark bg: `color: #ffffff; text-decoration: none` → hover `#3860be`
- On light bg: `color: #000000; text-decoration: underline 2px solid #76b900` → hover `#3860be; text-decoration: none`
- Universal hover: always `#3860be`

### NV-09 — Layout & Section Alternation
- Max content width: 1200px centered
- Dark sections (`background: #000000`, white text) alternate with light sections (`background: #ffffff`, black text)
- Section labels on dark bg: uppercase 14px `#76b900`
- Section vertical padding: 64–80px desktop, 48–64px tablet, 32–48px mobile

### NV-10 — Responsive Breakpoints
Implement via CSS media queries (not Tailwind breakpoints):
- `< 375px` — compact single column
- `375–600px` — standard mobile
- `600–768px` — 2-col grids begin
- `768–1024px` — full card grids
- `1024–1350px` — standard desktop
- `> 1350px` — max width with margins

### NV-11 — Depth & Elevation
- Standard shadow: `rgba(0,0,0,0.3) 0px 0px 5px 0px`
- Green accent border: `2px solid #76b900` (active/selected)
- Focus ring: `2px solid #000000 outline` — all interactive elements
- No glassmorphism, no blur effects

### NV-12 — Image Treatment
- Product images: full-width hero, maintain aspect ratio
- Screenshots: apply standard shadow
- Avatars: `border-radius: 50%`
- All images scale to container width

---

## Scope — Files to Restyle

**High priority:**
- `frontend/src/app/globals.css` — CSS custom properties, base resets, typography scale
- `frontend/src/components/layout/header.tsx` — Nav bar redesign
- `frontend/src/components/layout/footer.tsx` — Footer multi-column → stacked mobile
- `frontend/src/app/page.tsx` — Home page section alternation, hero, CTAs
- `frontend/src/app/paddles/page.tsx` — Product catalog grid
- `frontend/src/app/paddles/[brand]/[model-slug]/page.tsx` — Product detail page
- `frontend/src/components/ui/button.tsx` — Replace with NVIDIA button contracts
- `frontend/src/components/ui/card.tsx` — NVIDIA card contract

**Medium priority:**
- `frontend/src/components/chat/chat-widget.tsx` — Dark surface styling
- `frontend/src/components/quiz/quiz-flow.tsx` — Green accent interactive elements
- `frontend/src/app/chat/page.tsx` — Page layout
- `frontend/src/components/paddle-card-skeleton.tsx` — Match card styling

**Out of scope (do not touch):**
- API routes (`src/app/api/`)
- Business logic (`src/lib/`)
- Admin pages (separate concern)
- Tests

---

## Constraints

1. **Custom CSS only** — no new npm packages, no Tailwind utility overrides beyond globals
2. **Preserve existing functionality** — all existing interactions, forms, navigation links must still work
3. **No breaking changes to component props** — only restyle, do not refactor APIs
4. **Font Awesome via CDN only** — add `<link>` tag in `layout.tsx`, do not `npm install` it
5. **NVIDIA-EMEA font** — load via `@font-face` if available locally, fallback to Arial if not found
6. **Accessibility** — maintain WCAG AA compliance; focus rings required on all interactive elements

---

## Acceptance Criteria

- [ ] All pages use #000000 / #ffffff as dominant bg/text with #76b900 accents only on borders/underlines
- [ ] Buttons match green-border contract exactly (2px solid #76b900, 11px 13px padding)
- [ ] Navigation is sticky black, uppercase links, collapses at ≤1024px
- [ ] Product grid is 3-col/2-col/1-col at respective breakpoints
- [ ] Dark/light section alternation visible on home and catalog pages
- [ ] Card titles have green underline (2px solid #76b900)
- [ ] All links hover to #3860be universally
- [ ] Focus rings present on all interactive elements
- [ ] Typography uses only 24px/16px/14px/12px at weights 400/700
