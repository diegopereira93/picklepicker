---
phase: nvidia
slug: nvidia-design-system
status: approved
reviewed_at: 2026-04-02
shadcn_initialized: false
preset: none
created: 2026-04-02
---

# NVIDIA Design System — UI Design Contract

> Complete visual and interaction contract derived from DESIGN.md.
> All decisions are sourced from that document. No user questions required.
> Executor must implement from this contract without consulting DESIGN.md.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — custom CSS only |
| Preset | not applicable |
| Component library | PrimeReact + Fluent UI + Element Plus (multi-framework) |
| Icon library | Font Awesome 6 Pro (weight 900 solid, 700 regular) + Font Awesome 6 Sharp (weight 300 light, 400 regular) |
| Font | NVIDIA-EMEA, Arial, Helvetica, sans-serif |

---

## Color Palette

### Primary Brand

| Role | Hex | Usage |
|------|-----|-------|
| NVIDIA Green | `#76b900` | Borders, link underlines, CTA outlines, active indicators — NEVER as large surface fills |
| True Black | `#000000` | Primary page background, text on light surfaces, dominant background tone |
| Pure White | `#ffffff` | Text on dark backgrounds, light section backgrounds, card surfaces |

### Extended Brand

| Role | Hex | Usage |
|------|-----|-------|
| NVIDIA Green Light | `#bff230` | Hover highlights, bright lime accent |
| Orange 400 | `#df6500` | Alerts, featured badges, energy-related contexts |
| Yellow 300 | `#ef9100` | Secondary warm accent, product category highlights |
| Yellow 050 | `#feeeb2` | Light warm surface for callout backgrounds |

### Status / Semantic

| Role | Hex | Usage |
|------|-----|-------|
| Red 500 | `#e52020` | Error states, destructive actions, critical alerts |
| Red 800 | `#650b0b` | Severe warning backgrounds |
| Green 500 | `#3f8500` | Success states, positive indicators (darker than brand green) |
| Blue 700 | `#0046a4` | Informational accents, link hover alternative |

### Decorative

| Role | Hex | Usage |
|------|-----|-------|
| Purple 800 | `#4d1368` | Gradient ends, premium / AI contexts |
| Purple 100 | `#f9d4ff` | Light purple surface tint |
| Fuchsia 700 | `#8c1c55` | Special promotions, featured content |

### Neutral Scale

| Role | Hex | Usage |
|------|-----|-------|
| Gray 300 | `#a7a7a7` | Muted text, disabled labels, body text on dark bg |
| Gray 400 | `#898989` | Secondary text, metadata |
| Gray 500 | `#757575` | Tertiary text, placeholders, footers |
| Gray Border | `#5e5e5e` | Subtle borders, divider lines |
| Near Black | `#1a1a1a` | Dark card backgrounds, dark surface variant |

### Interactive States

| State | Value | Applies To |
|-------|-------|------------|
| Link default (dark bg) | `#ffffff` | All links on black/dark sections |
| Link default (light bg) | `#000000` | All links on white/light sections |
| Link hover (universal) | `#3860be` | All link variants on hover, regardless of default color |
| Button hover | `#1eaedb` | All button variants on hover, text becomes `#ffffff` |
| Button active / pressed | `#007fff` | All button variants on active, border becomes `1px solid #003eff` |
| Focus ring | `2px solid #000000` outline | Keyboard focus — all interactive elements |

### 60 / 30 / 10 Split

| Band | Color | Role |
|------|-------|------|
| 60% dominant | `#000000` | Page backgrounds, dark sections |
| 30% secondary | `#ffffff` / `#1a1a1a` | Cards, light sections, nav surfaces |
| 10% accent | `#76b900` | Borders on CTAs, link underlines on light bg, active indicators, section label text |

**Accent reserved for:** button borders, link underlines (light bg), active state indicators, section label text in dark sections, card title underline accents. Not used as surface fill.

**Destructive color:** `#e52020` — destructive actions only.

---

## Typography

### Font Stack

```
font-family: 'NVIDIA-EMEA', Arial, Helvetica, sans-serif;
```

Icons: Font Awesome 6 Pro / Sharp loaded via CDN. No shadcn registry involved.

### Canonical Size Scale

The scale uses exactly 4 canonical sizes and exactly 2 weights. All roles map to the nearest canonical size. Original source sizes are noted inline for fidelity reference only — do not introduce intermediate sizes in implementation.

| Canonical Size | Roles That Map to It |
|---------------|----------------------|
| `24px` | Display Hero (source: 36px — scales to 24px on mobile; 24px is the canonical implementation size), Section Heading (source: 24px), Sub-heading (source: 22px → nearest canonical), Card Title (source: 20px → nearest canonical), Body Large (source: 18px → nearest canonical), Button Large (source: 18px → nearest canonical) |
| `16px` | Body, Body Bold, Button, Button Compact (source: 14.4px → nearest canonical) |
| `14px` | Link, Link Uppercase, Caption (source: 14px) |
| `12px` | Caption Small (source: 12px), Micro Label (source: 10px → nearest canonical), Micro (source: 11px → nearest canonical) |

**Mapping note:** DESIGN.md specifies 12 distinct sizes (36, 24, 22, 20, 18, 16, 15, 14.4, 14, 12, 11, 10px). These are collapsed to 4 canonical sizes per the design contract maximum. Display Hero at 36px is a source-document size; the canonical implementation uses 24px (which also matches the mobile-scaled value from the responsive table). Roles retain their semantic names and line-height values; only the pixel size is normalized to the nearest canonical step.

### Type Scale (All Roles)

| Role | Canonical Size | Weight | Line Height | Letter Spacing | Notes |
|------|---------------|--------|-------------|----------------|-------|
| Display Hero | 24px (1.50rem) | 700 | 1.25 | normal | Max-impact headlines. Source size 36px; canonical 24px matches mobile-scaled value |
| Section Heading | 24px (1.50rem) | 700 | 1.25 | normal | Section titles |
| Sub-heading | 24px (1.50rem) | 400 | 1.75 | normal | Feature descriptions, subtitles. Source: 22px |
| Card Title | 24px (1.50rem) | 700 | 1.25 | normal | Card and module headings. Source: 20px |
| Body Large | 24px (1.50rem) | 700 | 1.67 | normal | Emphasized body, lead paragraphs. Source: 18px |
| Body | 16px (1.00rem) | 400 | 1.50 | normal | Standard reading text |
| Body Bold | 16px (1.00rem) | 700 | 1.50 | normal | Strong labels, nav items |
| Body Small | 16px (1.00rem) | 400 | 1.67 | normal | Secondary content, descriptions. Source: 15px |
| Body Small Bold | 16px (1.00rem) | 700 | 1.50 | normal | Emphasized secondary content. Source: 15px |
| Button Large | 24px (1.50rem) | 700 | 1.25 | normal | Primary CTA buttons. Source: 18px |
| Button | 16px (1.00rem) | 700 | 1.25 | normal | Standard buttons |
| Button Compact | 16px (1.00rem) | 700 | 1.00 | 0.144px | Small / inline CTAs. Source: 14.4px |
| Link | 14px (0.88rem) | 700 | 1.43 | normal | Standard links |
| Link Uppercase | 14px (0.88rem) | 700 | 1.43 | normal | `text-transform: uppercase` — nav labels |
| Caption | 14px (0.88rem) | 700 | 1.50 | normal | Metadata, timestamps. Source weight: 600 → normalized to 700 |
| Caption Small | 12px (0.75rem) | 400 | 1.25 | normal | Fine print, legal |
| Micro Label | 12px (0.75rem) | 700 | 1.50 | normal | `text-transform: uppercase` — tiny badges. Source: 10px |
| Micro | 12px (0.75rem) | 700 | 1.00 | normal | Smallest UI text. Source: 11px |

### Typography Principles

- Exactly 2 weights in use: **400** (body, descriptions) and **700** (all headings, buttons, links, labels).
- Weight 600 is not used. Caption was source-specified at 600; it is normalized to 700 for consistency with NVIDIA's bold-dominant voice.
- Heading line-height: 1.25 (tight). Body line-height: 1.50–1.67 (relaxed).
- Navigation uses `text-transform: uppercase` at 14px weight 700.
- Letter-spacing is normal throughout except Button Compact (0.144px).
- No decorative tracking. The font carries industrial character without manipulation.

---

## Spacing Scale

Base unit: 8px.

| Token | Value | Usage |
|-------|-------|-------|
| 1px | 1px | Micro borders, inline spans |
| 2px | 2px | Border width (accent borders) |
| xs | 4px | Tight inline gaps |
| sm | 8px | Compact element spacing, base unit |
| button-v | 11px | Button vertical padding |
| button-h | 13px | Button horizontal padding |
| md | 16px | Default element spacing, card internal padding start |
| card | 16–24px | Card internal padding range |
| lg | 24px | Section padding, card gap upper bound |
| xl | 32px | Layout gaps, mobile section spacing |
| 2xl | 48px | Major section breaks, mobile section vertical padding |
| 3xl | 64px | Desktop section vertical padding lower bound |
| 4xl | 80px | Desktop section vertical padding upper bound |

Card grid gap: 16–20px (catalog density, not gallery spacing).

Exceptions:
- Button padding is 11px 13px (non-multiple-of-4 by design — preserves NVIDIA's exact touch target spec). Do not normalize these values.
- 20px card gap preserves NVIDIA's catalog density specification. Do not normalize.
- 1px micro borders and 2px border widths are border/outline primitives, not layout spacing tokens — exempt from the 4px grid constraint by CSS border convention.

---

## Border Radius Scale

| Name | Value | Usage |
|------|-------|-------|
| Micro | 1px | Inline spans, tiny elements |
| Standard | 2px | Buttons, cards, containers, inputs — default for nearly everything |
| Circle | 50% | Avatar images, circular tab indicators |

Rule: 2px is the universal default. Do not introduce larger radii.

---

## Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat (Level 0) | No shadow | Page backgrounds, inline text |
| Subtle (Level 1) | `rgba(0,0,0,0.3) 0px 0px 5px 0px` | Standard cards, modals |
| Border (Level 1b) | `1px solid #5e5e5e` | Content dividers, section borders |
| Green Accent (Level 2) | `2px solid #76b900` | Active elements, CTAs, selected items |
| Focus (Accessibility) | `2px solid #000000` outline | Keyboard focus ring — all interactive elements |

Shadow philosophy: One shadow value used sparingly. Primary depth signal is color contrast (black next to white, green border on black), not simulated light. No glassmorphism. No blur effects.

Decorative depth:
- Green gradient washes behind hero content.
- Dark-to-darker gradients (black to near-black `#1a1a1a`) for section transitions.

---

## Component Contracts

### Button — Primary (Green Border)

```
background:    transparent
color:         #000000 (light bg) / #ffffff (dark bg)
border:        2px solid #76b900
border-radius: 2px
padding:       11px 13px
font:          16px NVIDIA-EMEA weight 700 line-height 1.25

:hover  → background #1eaedb, color #ffffff
:active → background #007fff, color #ffffff, border 1px solid #003eff
:focus  → background #1eaedb, color #ffffff, outline #000000 solid 2px, opacity 0.9
```

Use: Primary CTA actions — "Learn More", "Explore Solutions", "Shop Now".

### Button — Secondary (Green Border Thin)

```
background:    transparent
border:        1px solid #76b900
border-radius: 2px
(inherits same hover/active/focus as Primary)
```

Use: Secondary actions, alternative CTAs alongside a Primary button.

### Button — Compact / Inline

```
font:           16px NVIDIA-EMEA weight 700
letter-spacing: 0.144px
line-height:    1.00
border-radius:  2px
```

Use: Inline CTAs, compact navigation actions.

### Cards & Containers

```
background (light section): #ffffff
background (dark section):  #1a1a1a
border:        none OR 1px solid #5e5e5e
border-radius: 2px
box-shadow:    rgba(0,0,0,0.3) 0px 0px 5px 0px
padding:       16–24px internal

:hover → box-shadow intensification (increase opacity or blur)
```

### Product Cards

```
background:    #ffffff (light) or #1a1a1a (dark)
border-radius: 2px
box-shadow:    rgba(0,0,0,0.3) 0px 0px 5px

Title:         24px weight 700 line-height 1.25, color #000000 (light) / #ffffff (dark)
               border-bottom: 2px solid #76b900 (green accent underline)
Body:          16px weight 400 line-height 1.67, color #757575
CTA button:    Primary green-border button at bottom
```

Grid: 3-column on desktop, 2-column on tablet, 1-column on mobile. Gap: 20px.

### Links

| Context | Default Color | Underline | Hover Color | Underline on Hover |
|---------|--------------|-----------|-------------|-------------------|
| On dark background | `#ffffff` | none | `#3860be` | none |
| On light background | `#000000` / `#1a1a1a` | `2px solid #76b900` | `#3860be` | removed |
| Green link | `#76b900` | none | `#3860be` | none |
| Muted link | `#666666` | none | `#3860be` | none |

Rule: Link hover is always `#3860be` regardless of the link's default color.

### Navigation Bar

```
background:    #000000 (sticky, full-width)
Logo:          left-aligned, NVIDIA wordmark
Links:         14px NVIDIA-EMEA weight 700 uppercase, color #ffffff
               hover: color #3860be, no underline change
CTA button:    Primary green-border button, right-aligned
Breakpoint:    Collapses to hamburger menu at ≤1024px
               Mobile: hamburger triggers full-screen overlay menu
```

### Tech Spec Tables

```
Layout:        Industrial grid
Row alt bg:    Subtle gray shift (near-black vs. black, or white vs. off-white)
Labels:        weight 700
Values:        weight 400
Key metrics:   color #76b900 highlight
```

### Cookie / Consent Banner

```
position:      fixed bottom
buttons:       2px border-radius
borders:       gray border treatment (#5e5e5e)
```

### Image Treatment

```
Product / GPU renders:  hero images, often full-width, scale proportionally
Screenshot images:      box-shadow rgba(0,0,0,0.3) 0px 0px 5px for depth
Hero sections:          green gradient overlays on dark backgrounds
Avatars:                50% border-radius circular containers
All images:             maintain aspect ratio, scale to container width
```

---

## Layout & Grid

| Property | Value |
|----------|-------|
| Max content width | ~1200px (contained) |
| Hero sections | Full-width with contained text |
| Feature sections | 2–3 column grid (product cards) |
| Article / blog | Single column |
| Documentation | Sidebar layout |
| Section alternation | Dark (black bg, white text) alternates with light (white bg, black text) |

Dark/light alternation uses background color — not spacing alone — to separate content blocks.

---

## Responsive Breakpoints

| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile Small | < 375px | Compact single column, reduced padding |
| Mobile | 375–425px | Standard mobile layout |
| Mobile Large | 425–600px | Wider mobile, some 2-column hints |
| Tablet Small | 600–768px | 2-column grids begin |
| Tablet | 768–1024px | Full card grids, expanded nav |
| Desktop | 1024–1350px | Standard desktop layout |
| Large Desktop | > 1350px | Max content width, generous margins |

### Collapsing Strategy

| Element | Desktop | Tablet | Mobile |
|---------|---------|--------|--------|
| Display Hero | 24px | 24px | 24px |
| Section Heading | 24px | 24px | 24px |
| Body text | 16px (unchanged) | 16px | 16px |
| Button text | 16px (unchanged) | 16px | 16px |
| Navigation | Full horizontal | Full horizontal | Hamburger overlay at ≤1024px |
| Product card grid | 3-column | 2-column | 1-column stacked |
| Footer | Multi-column grid | Reduced columns | Single stacked column |
| Section vertical padding | 64–80px | 48–64px | 32–48px |

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | "Learn More" / "Explore Solutions" / "Shop Now" — specific verb + noun per context |
| Section label (dark bg) | Uppercase 14px, NVIDIA Green `#76b900` — e.g. "FEATURED PRODUCTS", "LATEST NEWS" |
| Navigation links | Uppercase 14px bold — e.g. "PRODUCTS", "SOLUTIONS", "DEVELOPERS" |
| Empty state heading | "No results found" |
| Empty state body | "Try adjusting your search or filter to find what you're looking for." |
| Error state | "Something went wrong. Refresh the page or try again later." |
| Destructive confirmation | "Remove [item]: This action cannot be undone. Confirm removal?" |
| Footer legal | 12px `#757575` — standard legal copy, copyright notice |

Tone: Engineering-direct. No casual language. No filler. Imperative verbs. Product-first.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none — not initialized | not applicable |
| Font Awesome CDN | FA 6 Pro + FA 6 Sharp icon fonts | CDN delivery only — no component code — no vetting required |
| Custom CSS | All component styles | Hand-authored — no third-party registry |

No third-party component registries. All component styling is custom CSS. Font Awesome loaded via CDN for icon glyphs only (no JS behavior, no network calls from component code).

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
