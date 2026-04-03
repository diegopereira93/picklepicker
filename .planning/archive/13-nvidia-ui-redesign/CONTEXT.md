# Phase 13: Hybrid UI Redesign — Context

**Source:** `DESIGN.md` v2.0 (Hybrid Modern Sports Tech, 2026-04-02)
**Goal:** Restyle the PickleIQ Next.js frontend with the Hybrid Modern Sports Tech design system. Custom CSS only — no new component libraries. All styling decisions are locked in DESIGN.md; executor must not deviate.

---

## Design Philosophy

**Aesthetic:** Modern Sports Tech (Hybrid) — sport energy + data credibility
**Mood:** Smart, friendly, Brazilian — sporty enough for players, techy enough for data-conscious buyers
**Positioning:** "The smart way to buy a paddle"

**Key differentiation from NVIDIA:**
- Lime (#84CC16) is now the primary sport accent (on dark backgrounds)
- Green (#76b900) is for data elements only (charts, tables, section labels)
- JetBrains Mono for data/specs (signals "we take data seriously")
- 2px border radius throughout (sharp corners = precision, not "fun and bouncy")
- Section labels in uppercase with green accent (category/taxonomy visual language)

---

## Implementation Requirements

### HY-01 — Typography System
Load fonts via Google Fonts CDN in `layout.tsx`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

Apply font families:
- Display/Hero: `Instrument Sans` weight 700
- Body: `Inter` weight 400/700
- Data/Specs: `JetBrains Mono` weight 400
- Navigation: `Inter` weight 700, uppercase, letter-spacing 0.05em

### HY-02 — Color System
Update CSS custom properties in `globals.css`:

**Sport Energy (on dark backgrounds only):**
- `--sport-primary: #84CC16` (lime-500) — primary actions, accent elements
- `--sport-secondary: #FCD34D` (amber-300) — secondary highlights, CTAs

**Data Credibility (charts, specs, comparison):**
- `--data-green: #76b900` — chart accent, comparison highlights
- `--data-green-light: #bff230` — hover state

**Base Palette:**
- `--color-white: #ffffff` — text on dark, light section backgrounds
- `--color-near-black: #1a1a1a` — dark section backgrounds, cards
- `--color-black: #000000` — navigation, hero sections
- `--color-gray-border: #5e5e5e` — subtle dividers
- `--color-gray-muted: #a7a7a7` — secondary text

**Interactive:**
- `--color-link-hover: #3860be` — universal link hover
- `--color-button-hover: #1eaedb` — button hover state
- `--color-button-active: #007fff` — button active state

**Contrast rule:** Lime (#84CC16) has 2.7:1 contrast on white — fails WCAG AA. Use on dark backgrounds ONLY.

### HY-03 — Spacing & Border Radius
Base unit: 8px (not 4px)

Key tokens:
- `--space-2xs: 4px` — micro gaps, icon spacing
- `--space-xs: 8px` — tight padding
- `--space-sm: 16px` — default element gap
- `--space-md: 24px` — card padding, section internal
- `--space-lg: 32px` — section gaps
- `--space-xl: 48px` — major section breaks
- `--space-2xl: 64px` — page-level padding
- `--space-3xl: 80px` — hero section padding

**Border radius:**
- `--radius-sharp: 2px` — default (sharp, tech edge)
- `--radius-card: 4px` — subtle rounding for cards
- `--radius-circle: 50%` — avatars only

### HY-04 — Button Components
Replace shadcn button variants with Hybrid styles:

**Primary (green-border on transparent):**
```css
background: transparent;
border: 2px solid #84CC16;
color: #ffffff;
padding: 11px 13px;
font-size: 14px;
font-weight: 700;
border-radius: 2px;
```
- `:hover` → `background: #1eaedb; border-color: #1eaedb; color: #ffffff;`
- `:focus` → `outline: 2px solid #000000; outline-offset: 2px;`

**CTA (solid lime fill):**
```css
background: #84CC16;
border: none;
color: #1a1a1a;
padding: 11px 13px;
font-weight: 700;
border-radius: 2px;
```
- `:hover` → `background: #FCD34D;`

### HY-05 — Cards & Containers
**Product card:**
```css
background: #1a1a1a;
border-radius: 4px;
box-shadow: rgba(0, 0, 0, 0.3) 0px 0px 5px 0px;
overflow: hidden;
transition: transform 150ms ease, box-shadow 150ms ease;
```
- `:hover` → `transform: translateY(-2px); box-shadow: rgba(0, 0, 0, 0.5) 0px 4px 12px 0px;`

**Card title:** `border-bottom: 2px solid #76b900;` (green underline for data accent)

**Product grid:** 3-col desktop / 2-col tablet / 1-col mobile, `gap: 20px;`

### HY-06 — Navigation Bar
Restyle `header.tsx`:
- `background: #000000` sticky full-width
- Logo: left-aligned, "PickleIQ" with `<span>` in lime
- Links: 14px weight 700 uppercase white, `:hover` → `#3860be`
- CTA: Primary lime-border button, right-aligned
- Collapse to hamburger overlay at `≤1024px`

### HY-07 — Links
```css
/* On dark bg */
a { color: #ffffff; text-decoration: none; }
a:hover { color: #3860be; }

/* On light bg */
a { color: #1a1a1a; text-decoration: underline 2px solid #76b900; }
a:hover { color: #3860be; text-decoration: none; }

/* Universal */
a:hover { color: #3860be; }
```

### HY-08 — Layout & Section Alternation
Max content width: 1200px centered

Alternation pattern:
```
[Hero: Dark #000000] →
[Products: Light #ffffff] →
[Quiz: Dark #1a1a1a] →
[Comparison: Light #ffffff] →
[Chat: Dark #1a1a1a]
```

Section labels:
- On dark: 14px weight 700 uppercase, `color: #76b900`
- On light: 14px weight 700 uppercase, `color: #84CC16`

### HY-09 — Responsive Breakpoints
CSS media queries (not Tailwind):
- `< 375px` — compact single column
- `375–600px` — standard mobile
- `600–768px` — 2-col grids begin
- `768–1024px` — full card grids
- `1024–1350px` — standard desktop
- `> 1350px` — max width with margins

### HY-10 — Motion System
Duration scale:
- `instant: 50ms` — hover states, micro-feedback
- `fast: 150ms` — button presses, toggles
- `normal: 250ms` — card transitions, modals
- `slow: 400ms` — page transitions, reveals

Easing:
- `ease-enter: cubic-bezier(0, 0, 0.2, 1)` — elements entering
- `ease-exit: cubic-bezier(0.4, 0, 1, 1)` — elements leaving
- `ease-move: cubic-bezier(0.4, 0, 0.2, 1)` — position/size changes

### HY-11 — Class Prefix Migration
Replace `nv-*` prefixes with `hy-*` prefixes:
- `nv-dark-section` → `hy-dark-section`
- `nv-light-section` → `hy-light-section`
- `nv-product-card` → `hy-product-card`
- `nv-catalog-grid` → `hy-catalog-grid`
- `nv-nav` → `hy-nav`
- `nv-section-label` → `hy-section-label`
- `nv-card` → `hy-card`
- etc.

**Compatibility aliases:** Keep `nv-*` classes as aliases for gradual migration.

### HY-12 — AI Slop Avoidance
Verify before shipping:
- [ ] No 3-column feature grid with icons in colored circles
- [ ] No icons in colored circles as decoration
- [ ] No centered-everything layout (left-align body copy)
- [ ] No "Welcome to..." / "Your all-in-one solution" copy
- [ ] No decorative blobs or wavy SVG dividers
- [ ] No purple/violet gradient backgrounds
- [ ] No rounded corners on buttons (use 2px, not 8px+)
- [ ] Cards exist because they're functional, not decorative

---

## Scope — Files to Update

**CSS (already updated):**
- `frontend/src/app/globals.css` — Hybrid CSS system with `.hy-*` classes

**Components to restyle:**
- `frontend/src/components/layout/header.tsx` — Nav with lime accent on logo
- `frontend/src/components/layout/footer.tsx` — Footer with green section labels
- `frontend/src/app/page.tsx` — Home page with dark/light alternation
- `frontend/src/app/paddles/page.tsx` — Catalog grid with updated classes
- `frontend/src/app/paddles/[brand]/[model-slug]/page.tsx` — Detail page
- `frontend/src/components/ui/card.tsx` — Card with green underline
- `frontend/src/components/paddle-card-skeleton.tsx` — Skeleton with shimmer

**Font loading:**
- `frontend/src/app/layout.tsx` — Add Google Fonts CDN link

---

## Constraints

1. **Custom CSS only** — no new npm packages
2. **Preserve existing functionality** — all interactions must still work
3. **No breaking changes to component props** — only restyle, do not refactor APIs
4. **Google Fonts** — Instrument Sans, Inter, JetBrains Mono via CDN
5. **Accessibility** — maintain WCAG AA compliance; focus rings required

---

## Acceptance Criteria

- [ ] Google Fonts loaded: Instrument Sans, Inter, JetBrains Mono
- [ ] Lime (#84CC16) used on dark backgrounds only
- [ ] Green (#76b900) used for data elements (tables, charts, section labels)
- [ ] All `nv-*` classes migrated to `hy-*` (with aliases)
- [ ] Navigation has lime accent on "IQ" in logo
- [ ] Product grid is 3-col/2-col/1-col at breakpoints
- [ ] Dark/light section alternation visible on home page
- [ ] Card titles have green underline
- [ ] Links hover to #3860be universally
- [ ] Focus rings present on all interactive elements
- [ ] Typography uses correct fonts per role (display/body/data)
- [ ] No AI slop patterns (verify checklist)