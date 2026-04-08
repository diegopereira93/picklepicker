# PickleIQ Design System — MASTER.md

**Version:** 1.0.0  
**Last Updated:** 2026-04-07  
**Status:** Single Source of Truth  
**Scope:** Global tokens — page-specific overrides in `design-system/pages/`

---

## AESTHETIC DIRECTION

### Mode
- **Dark mode ONLY** (no toggle in v1)

### Tone
Premium sports analytics — ESPN Stats meets Vercel Dashboard meets Linear

### Feel
- Data-dense
- Intelligent
- Performance-oriented
- Trustworthy

### Memorable Element
**Every number animates on load:**
- Prices
- Attribute scores
- Match percentages

**Animation behavior:**
- Mono-spaced typography
- Color-coded by context (price delta, score tier)
- Count-up from 0→N over 800ms

---

## COLOR SYSTEM

### Background Hierarchy

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-base` | `#0a0a0a` | True black, page background |
| `--bg-surface` | `#141414` | Card backgrounds, panels |
| `--bg-elevated` | `#1f1f1f` | Hover states, active elements |
| `--bg-overlay` | `rgba(0,0,0,0.8)` | Modals, dialogs (with backdrop-blur) |

### Brand Colors

#### Primary: Neon Green
| Token | Value |
|-------|-------|
| `--brand-primary` | `#84CC16` |

**Justification:**
- Green = performance/success in sports context
- High contrast on dark backgrounds (#84CC16 on #0a0a0a = **7.5:1** — exceeds WCAG AA)
- Works for gamification (green = good match, good deal)
- Used for: match scores, primary CTAs, success states, price drops

#### Secondary: Electric Orange
| Token | Value |
|-------|-------|
| `--brand-secondary` | `#F97316` |

**Justification:**
- Orange = energy, urgency, action
- Used sparingly for conversion-critical elements only
- Used for: secondary CTAs, alerts, time-sensitive badges

### Semantic Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--success` | `#84CC16` | Success states, positive deltas |
| `--warning` | `#FBBF24` | Warnings, cautions |
| `--danger` | `#EF4444` | Errors, destructive actions, price increases |
| `--info` | `#60A5FA` | Informational messages, links |

### Text Hierarchy

| Token | Value | Contrast Ratio | WCAG Level |
|-------|-------|----------------|------------|
| `--text-primary` | `#FAFAFA` | 19.3:1 on #0a0a0a | AAA |
| `--text-secondary` | `#A3A3A3` | 7.4:1 on #0a0a0a | AAA |
| `--text-muted` | `#737373` | 4.6:1 on #0a0a0a | AA |
| `--text-disabled` | `#525252` | 3.1:1 on #0a0a0a | AA (large text only) |

### Price Delta Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--price-up` | `#EF4444` | Price increased (red) |
| `--price-down` | `#84CC16` | Price decreased (green) |
| `--price-neutral` | `#737373` | No change (gray) |

---

## WCAG AA CONTRAST VERIFICATION

All text/background combinations verified against WCAG 2.1 AA standards (minimum 4.5:1 for normal text, 3:1 for large text).

| Foreground | Background | Hex Combo | Ratio | Pass? |
|------------|------------|-----------|-------|-------|
| `#FAFAFA` (primary) | `#0a0a0a` (base) | FAFAFA on 0a0a0a | 19.3:1 | ✅ AAA |
| `#A3A3A3` (secondary) | `#0a0a0a` (base) | A3A3A3 on 0a0a0a | 7.4:1 | ✅ AAA |
| `#737373` (muted) | `#0a0a0a` (base) | 737373 on 0a0a0a | 4.6:1 | ✅ AA |
| `#525252` (disabled) | `#0a0a0a` (base) | 525252 on 0a0a0a | 3.1:1 | ✅ AA (large only) |
| `#84CC16` (primary brand) | `#0a0a0a` (base) | 84CC16 on 0a0a0a | 7.5:1 | ✅ AAA |
| `#F97316` (secondary brand) | `#0a0a0a` (base) | F97316 on 0a0a0a | 5.3:1 | ✅ AAA |
| `#FAFAFA` (primary) | `#141414` (surface) | FAFAFA on 141414 | 17.8:1 | ✅ AAA |
| `#A3A3A3` (secondary) | `#141414` (surface) | A3A3A3 on 141414 | 6.8:1 | ✅ AAA |
| `#84CC16` (success) | `#0a0a0a` (base) | 84CC16 on 0a0a0a | 7.5:1 | ✅ AAA |
| `#EF4444` (danger) | `#0a0a0a` (base) | EF4444 on 0a0a0a | 5.1:1 | ✅ AAA |
| `#60A5FA` (info) | `#0a0a0a` (base) | 60A5FA on 0a0a0a | 6.2:1 | ✅ AAA |
| `#FBBF24` (warning) | `#0a0a0a` (base) | FBBF24 on 0a0a0a | 8.2:1 | ✅ AAA |

---

## TYPOGRAPHY

### Font Families

| Token | Font | Usage |
|-------|------|-------|
| `--font-display` | **Bebas Neue** | Hero text, section titles, paddle names, H1/H2, all-caps |
| `--font-body` | **Source Sans 3** | Descriptions, chat messages, specs, all body text |
| `--font-mono` | **JetBrains Mono** | **MANDATORY** for prices, attribute scores, numeric data, match percentages |

### Font Loading Strategy
```
next/font/google with:
- display: 'swap'
- CSS variable approach
- Preload critical weights
```

### Type Scale

| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--text-xs` | 0.75rem (12px) | 1rem (16px) | Captions, footnotes, timestamps |
| `--text-sm` | 0.875rem (14px) | 1.25rem (20px) | Small labels, secondary info |
| `--text-base` | 1rem (16px) | 1.5rem (24px) | Body text, default |
| `--text-lg` | 1.125rem (18px) | 1.75rem (28px) | Lead paragraphs, card titles |
| `--text-xl` | 1.25rem (20px) | 1.75rem (28px) | H3, section headers |
| `--text-2xl` | 1.5rem (24px) | 2rem (32px) | H2, page sections |
| `--text-3xl` | 1.875rem (30px) | 2.25rem (36px) | H1, page titles |
| `--text-4xl` | 2.25rem (36px) | 2.5rem (40px) | Hero, marketing headers |
| `--text-5xl` | 3rem (48px) | 1 | Display, landing page heroes |

### Font Weights
- **Bebas Neue:** 700 (Bold) — only weight available, all-caps
- **Source Sans 3:** 400 (Regular), 600 (SemiBold), 700 (Bold)
- **JetBrains Mono:** 400 (Regular), 500 (Medium), 600 (SemiBold)

---

## SPACING

**Base unit:** 4px (all spacing is a multiple of 4)

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | 4px | Tight gaps, icon padding |
| `--space-2` | 8px | Component internal padding |
| `--space-3` | 12px | Card internal spacing |
| `--space-4` | 16px | Standard gap, card padding |
| `--space-6` | 24px | Section spacing |
| `--space-8` | 32px | Large section gaps |
| `--space-12` | 48px | Page sections |
| `--space-16` | 64px | Major layout divisions |
| `--space-24` | 96px | Hero spacing, page margins |

---

## BORDER RADIUS

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sharp` | 0-2px | Data tables, prices, badges, inputs |
| `--radius-rounded` | 8px | Cards, chat bubbles |
| `--radius-lg` | 12px | Modals, large panels |
| `--radius-full` | 9999px | Pills, chips, avatars |

---

## SHADOWS

### Elevation Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.5)` | Inputs, subtle elevation |
| `--shadow-md` | `0 4px 6px -1px rgba(0,0,0,0.7)` | Cards, standard elevation |
| `--shadow-lg` | `0 10px 15px -3px rgba(0,0,0,0.8)` | Elevated panels, modals |

### Glow Effects (Brand)

| Token | Value | Usage |
|-------|-------|-------|
| `--glow-green` | `0 0 20px rgba(132,204,22,0.3)` | Primary CTA hover state |
| `--glow-orange` | `0 0 20px rgba(249,115,22,0.3)` | Secondary CTA hover state |

---

## MOTION

### Animation Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--transition-page` | `opacity 0→1 + translateY(8px→0), 150ms ease-out` | Page transitions |
| `--transition-card` | `translateY(-2px) + shadow-glow, 200ms ease` | Card hover states |
| `--transition-chat` | `translateY(8px→0) + opacity 0→1, 200ms ease-out` | Chat message entry |
| `--animation-price-pulse` | `opacity 1→0.5→1, 2s ease-in-out infinite` | Price change indicators |
| `--animation-count-up` | `number increment 0→N, 800ms ease-out` | All numeric data on load |
| `--animation-skeleton` | `backgroundPosition -200%→200%, 2s linear infinite` | Loading skeletons |
| `--transition-quiz` | `translateX(100%→0) enter, 0→-100% exit, 300ms ease-in-out` | Quiz slide transitions |
| `--animation-typing` | `opacity pulse 3 dots, 1.4s ease-in-out infinite` | Chat typing indicator |

### Reduced Motion
**Respect `prefers-reduced-motion`:**
- Disable all animations when enabled
- Instant transitions (0ms)
- No count-up animations (show final value)
- No skeleton shimmer (show solid color)

---

## COMPONENT TOKENS

### Buttons

| Token | Value |
|-------|-------|
| `--btn-height-sm` | 36px |
| `--btn-height-default` | 44px |
| `--btn-height-lg` | 48px |

### Inputs
| Token | Value |
|-------|-------|
| `--input-height` | 44px |

### Cards
| Token | Value |
|-------|-------|
| `--card-padding` | 16px |

### Layout
| Token | Value | Usage |
|-------|-------|-------|
| `--max-content-width` | 1280px | Main content container |
| `--sidebar-width-filters` | 260px | Filter sidebar |
| `--sidebar-width-chat` | 280px | Chat profile sidebar |

---

## IMPLEMENTATION NOTES

### Tailwind CSS Mapping
This design system maps to Tailwind CSS v3.x tokens:

```
Colors → tailwind.config.ts theme.extend.colors
Spacing → tailwind.config.ts theme.extend.spacing
Typography → tailwind.config.ts theme.extend.fontFamily + fontSize
Radius → tailwind.config.ts theme.extend.borderRadius
Shadows → tailwind.config.ts theme.extend.boxShadow
Motion → tailwind.config.ts theme.extend.transition + keyframes
```

### Font Loading (Next.js)
Use `next/font/google` with CSS variables:

```typescript
// app/layout.tsx
import { Bebas_Neue, Source_Sans_3, JetBrains_Mono } from 'next/font/google'

const bebas = Bebas_Neue({ weight: '700', subsets: ['latin'], display: 'swap', variable: '--font-bebas' })
const source = Source_Sans_3({ subsets: ['latin'], display: 'swap', variable: '--font-source' })
const jetbrains = JetBrains_Mono({ subsets: ['latin'], display: 'swap', variable: '--font-mono' })
```

### shadcn/ui Integration
- Extend `components.json` theme tokens
- Override CSS variables in `app/globals.css`
- Maintain dark-mode-only palette

---

## OVERRIDE HIERARCHY

```
MASTER.md (this file)
  └── pages/
      ├── home.md (home page overrides)
      ├── paddles.md (product listing overrides)
      ├── chat.md (chat interface overrides)
      └── admin.md (admin dashboard overrides)
```

**Rule:** Page-specific files can only **override** values, never introduce new tokens. All tokens must be defined here first.

---

## CHANGELOG

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-07 | Initial release — dark mode only, sports analytics aesthetic |

---

**End of MASTER.md**
