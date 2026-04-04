# PickleIQ — Design System

**Version:** 2.0 (Hybrid Modern Sports Tech, 2026-04-02)
**Type:** APP UI — task-focused, data-dense, sporty + tech-credible

**Changelog v2.0:**
- Replaced sport-only aesthetic with Hybrid Modern Sports Tech
- Added data credibility layer (green accent for charts/specs)
- Introduced JetBrains Mono for data tables
- Alternating dark/light sections instead of all-light
- Sharp 2px border radius (tech edge, not rounded)
- Section labels in uppercase with accent color

---

## Design Philosophy

**Product:** PickleIQ — Brazilian pickleball paddle recommendation platform
**Positioning:** "The smart way to buy a paddle" — sporty energy + data credibility
**Voice:** Smart, friendly, Brazilian — not corporate, not generic

**Core tension:** PickleIQ sits at the intersection of sports (energy, accessibility) and AI/data (trust, precision). The Hybrid design system balances both:
- Sport energy through lime accent and bold typography
- Data credibility through green accent, monospace specs, and sharp corners
- Brazilian warmth through conversational copy and approachable cards

---

## Aesthetic Direction

**Direction:** Modern Sports Tech (Hybrid)
**Mood:** Smart, friendly, Brazilian — sporty enough for players, techy enough for data-conscious buyers
**Decoration:** Intentional — subtle textures on dark surfaces, clean light surfaces
**Reference sites:** Pickleball Effect (editorial), Apple specs pages (data presentation), Duolingo (playful + educational)

**What this is NOT:**
- NOT a pure sports app (like Nike Training) — too one-dimensional
- NOT a corporate tech dashboard — too cold for pickleball
- NOT NVIDIA-inspired black/white — too detached from the sport

---

## Color System

### Sport Energy (on dark backgrounds only)

```css
--sport-primary: #84CC16;     /* lime-500: primary actions, accent elements */
--sport-secondary: #FCD34D;   /* amber-300: secondary highlights, CTAs */
```

**Contrast rule:** Lime (#84CC16) has 2.7:1 contrast on white — fails WCAG AA.
- ✅ Use lime on dark backgrounds (#000000, #1a1a1a) only
- ✅ Use lime for large text (H1, H2) where 3:1 is acceptable
- ❌ Never use lime as small body text on white

### Data Credibility (charts, specs, comparison)

```css
--data-green: #76b900;        /* NVIDIA green: chart accent, comparison highlights */
--data-green-light: #bff230;  /* hover state */
```

**Usage:** Green accent for data elements: charts, table highlights, spec badges, section labels. NOT for CTAs or primary actions.

### Base Palette

```css
--white: #ffffff;             /* text on dark, light section backgrounds */
--near-black: #1a1a1a;        /* dark section backgrounds, cards */
--black: #000000;              /* navigation, hero sections */
--gray-border: #5e5e5e;       /* subtle dividers */
--gray-muted: #a7a7a7;        /* secondary text */
--gray-400: #898989;          /* tertiary text */
--gray-500: #757575;          /* placeholder text */
```

### Semantic Colors

```css
--success: #3f8500;           /* dark green */
--error: #e52020;             /* red */
--info: #0046a4;              /* blue */
```

### Interactive Colors

```css
--link-hover: #3860be;        /* universal link hover */
--button-hover: #1eaedb;      /* button hover state */
--button-active: #007fff;     /* button active state */
```

### Dark Mode Implementation

In dark mode, the system remains the same (already dark-first). Light mode is the variant:

```css
/* Light section (default on light pages) */
background: #ffffff;
color: #1a1a1a;

/* Dark section (always dark) */
background: #1a1a1a;
color: #ffffff;

/* Hero section (always black) */
background: #000000;
color: #ffffff;
```

---

## Typography

### Font Stack

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Display/Hero | Instrument Sans | 700 | Landing H1, section heroes |
| Section Heading | Instrument Sans | 600 | Quiz questions, card titles, H2s |
| Body | Inter | 400 | Paragraphs, descriptions, chat |
| Body Bold | Inter | 700 | Button labels, emphasis |
| Data/Specs | JetBrains Mono | 400 | Comparison tables, spec values, prices |
| Navigation | Inter | 700 | Nav links, step indicators |
| Caption | Inter | 400-700 | Metadata, timestamps, tooltips |

### Font Loading

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

### Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 (Hero) | 64px / 40px mobile | 700 | 1.1 |
| H2 (Section) | 28px | 600 | 1.25 |
| H3 (Card) | 20px | 600 | 1.3 |
| Body | 16px | 400 | 1.5 |
| Body Bold | 16px | 700 | 1.5 |
| Data | 14px | 400 | 1.4 |
| Navigation | 14px | 700 | — |
| Caption | 12px | 400-700 | 1.43 |

### Navigation Typography

```css
.nav-link {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

### Section Labels

```css
.section-label {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--data-green); /* on dark */
  /* or var(--sport-primary) on light */
}
```

---

## Spacing System

**Base unit:** 8px (not 4px — hybrid needs more breathing room)

| Token | Value | Usage |
|-------|-------|-------|
| 2xs | 4px | Micro gaps, icon spacing |
| xs | 8px | Tight padding |
| sm | 16px | Default element gap |
| md | 24px | Card padding, section internal |
| lg | 32px | Section gaps |
| xl | 48px | Major section breaks |
| 2xl | 64px | Page-level padding |
| 3xl | 80px | Hero section padding |

**Pattern:** Use `gap: 20px` for product grids, `padding: 64px 0` for section vertical spacing, `padding: 16px` for card internal padding.

---

## Border Radius

```css
--radius-default: 2px;   /* sharp, tech edge */
--radius-card: 4px;      /* subtle rounding for cards */
--radius-button: 2px;    /* consistent with tech aesthetic */
--radius-avatar: 50%;    /* circles only for user images */
```

**Why 2px?** Sharp corners signal precision and data. This is a deliberate choice: "we take specs seriously."

---

## Layout

### Max Content Width

```css
max-width: 1200px;
margin: 0 auto;
padding: 0 24px;
```

### Section Alternation

Pages alternate between dark and light sections:
- Dark sections: `background: #000000` or `#1a1a1a`, white text
- Light sections: `background: #ffffff`, near-black text

**Pattern:**
```
[Hero: Dark #000000]
[Products: Light #ffffff]
[Quiz: Dark #1a1a1a]
[Comparison: Light #ffffff]
[Chat: Dark #1a1a1a]
```

### Responsive Breakpoints

| Viewport | Class | Layout |
|----------|-------|--------|
| < 375px | compact | Single column, compact padding |
| 375-600px | mobile | Single column, full-width cards |
| 600-768px | tablet-sm | 2-col grids begin |
| 768-1024px | tablet | Full card grids, horizontal nav |
| 1024-1350px | desktop | Standard desktop, max-width container |
| > 1350px | wide | Max-width with margins |

### Grid System

**Product grid:** 3-col desktop / 2-col tablet / 1-col mobile, `gap: 20px`
**Quiz grid:** 2-col tablet+ / 1-col mobile, `gap: 16px`
**Comparison table:** Full width, sticky header

---

## Components

### Navigation Bar

```css
.nav {
  background: #000000;
  position: sticky;
  top: 0;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}

.nav-logo span {
  color: #84CC16; /* lime accent on "IQ" */
}

.nav-links a {
  color: #ffffff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: color 150ms ease;
}

.nav-links a:hover {
  color: #3860be;
}
```

### Button Components

```css
/* Primary: Green border on transparent */
.btn-primary {
  background: transparent;
  border: 2px solid #84CC16;
  color: #ffffff;
  padding: 11px 13px;
  font-size: 14px;
  font-weight: 700;
  border-radius: 2px;
  cursor: pointer;
  transition: background 150ms ease, color 150ms ease;
}

.btn-primary:hover {
  background: #1eaedb;
  border-color: #1eaedb;
  color: #ffffff;
}

/* Secondary: Thinner border */
.btn-secondary {
  background: transparent;
  border: 1px solid #84CC16;
  color: #ffffff;
  padding: 11px 13px;
  /* same sizing */
}

/* CTA: Solid fill */
.btn-cta {
  background: #84CC16;
  border: none;
  color: #1a1a1a;
  padding: 11px 13px;
  font-weight: 700;
  border-radius: 2px;
}

.btn-cta:hover {
  background: #FCD34D;
}
```

### Cards

```css
.product-card {
  background: #1a1a1a;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: rgba(0, 0, 0, 0.3) 0px 0px 5px 0px;
  transition: transform 150ms ease, box-shadow 150ms ease;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: rgba(0, 0, 0, 0.5) 0px 4px 12px 0px;
}

.product-card-title {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  border-bottom: 2px solid #76b900; /* green underline for data accent */
  padding-bottom: 8px;
  margin-bottom: 8px;
}
```

### Quiz Cards

```css
.quiz-card {
  background: #1a1a1a;
  border: 2px solid #5e5e5e;
  border-radius: 4px;
  padding: 24px;
  cursor: pointer;
  transition: border-color 150ms ease, background 150ms ease;
}

.quiz-card:hover {
  border-color: #84CC16;
}

.quiz-card.selected {
  border-color: #84CC16;
  background: rgba(132, 204, 22, 0.1);
  box-shadow: 0 0 0 2px #84CC16, 0 0 0 4px rgba(132, 204, 22, 0.2);
}
```

### Comparison Table

```css
.comparison-table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: rgba(0, 0, 0, 0.3) 0px 0px 5px 0px;
}

.comparison-table th {
  background: #1a1a1a;
  color: #ffffff;
  padding: 16px;
  font-family: 'Instrument Sans', sans-serif;
  font-size: 16px;
  font-weight: 600;
  text-align: left;
}

.comparison-table td {
  padding: 16px;
  border-bottom: 1px solid #5e5e5e;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
}

.comparison-table .highlight {
  background: rgba(118, 185, 0, 0.1);
}

.comparison-table .best {
  color: #76b900;
  font-weight: 700;
}
```

### Links

```css
/* On dark bg */
a {
  color: #ffffff;
  text-decoration: none;
}

a:hover {
  color: #3860be;
}

/* On light bg */
.light-section a {
  color: #1a1a1a;
  text-decoration: underline 2px solid #76b900;
}

.light-section a:hover {
  color: #3860be;
  text-decoration: none;
}
```

---

## Motion System

**Philosophy:** Intentional motion that aids comprehension, not decoration.

### Duration Scale

| Token | Value | Usage |
|-------|-------|-------|
| instant | 50ms | Hover states, micro-feedback |
| fast | 150ms | Button presses, toggles |
| normal | 250ms | Card transitions, modals |
| slow | 400ms | Page transitions, reveals |

### Easing

```css
--ease-enter: cubic-bezier(0, 0, 0.2, 1);   /* elements entering */
--ease-exit: cubic-bezier(0.4, 0, 1, 1);      /* elements leaving */
--ease-move: cubic-bezier(0.4, 0, 0.2, 1);    /* position/size changes */
```

### Component Patterns

**Chat Message Streaming:**
```css
@keyframes message-enter {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-message.ai {
  animation: message-enter 250ms var(--ease-enter) forwards;
}
```

**Quiz Card Selection:**
```css
.quiz-card {
  transition: all 150ms var(--ease-move);
}

.quiz-card.selected {
  border-color: #84CC16;
  box-shadow: 0 0 0 2px #84CC16, 0 0 0 4px rgba(132, 204, 22, 0.2);
}
```

**Product Card Hover:**
```css
.product-card {
  transition: transform 150ms var(--ease-move), box-shadow 150ms var(--ease-move);
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: rgba(0, 0, 0, 0.5) 0px 4px 12px 0px;
}
```

---

## Accessibility

- **Touch targets:** Minimum 44×44px for all interactive elements
- **Focus rings:** 2px solid #000000 outline on all focusable elements
- **Contrast:** Lime (#84CC16) on dark backgrounds only; all text meets WCAG AA
- **Quiz cards:** `role="radio"`, `aria-checked`, `aria-label` with full option text
- **Chat message list:** `role="log"`, `aria-live="polite"`
- **Affiliate CTAs:** `aria-label="Ver [Paddle Name] no site [Retailer]"`
- **Keyboard navigation:** Tab order follows visual order on all screens

---

## Screen Hierarchy

### Landing Page

```
[Hero: Dark #000000]
  H1: "Encontre a raquete ideal para o seu jogo"
  Subtitle: "IA que analisa specs, preços e avaliações..."
  CTA: [Começar Quiz →] (lime border on transparent)

[Products: Light #ffffff]
  Section Label: "RECOMENDADOS PARA VOCÊ" (lime, uppercase)
  H2: "Raquetes em destaque"
  Product Grid: 3-col → 2-col → 1-col

[Quiz Teaser: Dark #1a1a1a]
  Section Label: "QUIZ" (green, uppercase)
  H2: "Descubra sua raquete ideal em 2 minutos"
  CTA: [Começar →]

[Comparison: Light #ffffff]
  Section Label: "COMPARAÇÃO"
  H2: "Compare raquetes lado a lado"
  Table: JetBrains Mono for specs, green highlight for best values
```

### Quiz Flow

```
"1 de 3" (step indicator, uppercase, green)
H2: Question text
[Card] [Card]         ← 2-col on tablet+, full-width on mobile
[Card] [Card]
● ○ ○               ← dot progress indicator (green for current)
← Voltar            ← text link, not a button
```

**Pattern:** Large selection cards, auto-advance on selection (no "Próximo" button).

### Chat Widget

```
[PickleIQ avatar]  AI message text streaming...     (left-aligned)
                              User message          (right-aligned)
[PickleIQ avatar]  Here are my recommendations:

  +---------------------------+      +---------------------------+
  | [img] Selkirk Luxx Control|      | [img] Joola Ben Johns     |
  |       R$ 489 · Brazil Store|     |       R$ 529 · Drop Shot  |
  |                           |      |                           |
  | Por que essa raquete?     |      | Por que essa raquete?     |
  | Ideal para iniciantes...  |      | Excelente controle para.. |
  |                           |      |                           |
  | [   VER NO SITE →   ]   |      | [   VER NO SITE →   ]   |
  +---------------------------+      +---------------------------+

[_________________________________] [ Enviar ]  ← bottom-pinned input
```

### Comparison Page

```
[ Buscar raquetes...                    🔍 ]
[ Selkirk Luxx × ]  [ Joola Ben × ]  [ + Adicionar ]  ← disabled at 3

| Atributo       | Selkirk Luxx | Joola Ben |
| Preço          | R$ 489       | R$ 529    |
| Swing Weight   | 82           | 87        |
| ...            | ...          | ...       |

[ Ver gráfico radar ▼ ]  ← accordion, hidden by default on mobile
[RadarChart — Potência/Controle/Toque/Swing Weight/Peso/Equilíbrio]
```

---

## AI Slop Avoidance Checklist

Before shipping any UI, verify:
- [ ] No 3-column feature grid with icons in colored circles
- [ ] No icons in colored circles as decoration
- [ ] No centered-everything layout (left-align body copy)
- [ ] No "Welcome to..." / "Your all-in-one solution" copy
- [ ] No decorative blobs or wavy SVG dividers
- [ ] No purple/violet gradient backgrounds
- [ ] No rounded corners on buttons (use 2px, not 8px+)
- [ ] Cards exist because they're functional, not decorative
- [ ] Product grid is 3-col/2-col/1-col, not 4-col
- [ ] Section labels are uppercase, not sentence case

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-02 | Hybrid Modern Sports Tech direction | Balances sport energy with data credibility |
| 2026-04-02 | JetBrains Mono for data tables | Signals "we take specs seriously", differentiates from competitors |
| 2026-04-02 | 2px border radius everywhere | Sharp corners = precision/data, not "fun and bouncy" |
| 2026-04-02 | Lime on dark backgrounds only | Contrast constraint forces dark heroes, creates drama |
| 2026-04-02 | Green (#76b900) for section labels | Creates visual language where green = category/taxonomy |
| 2026-04-02 | Alternating dark/light sections | Industry standard for sports + tech hybrids |
| 2026-04-02 | Instrument Sans for display | Editorial meets tech, modern without being generic |
| 2026-04-02 | Section labels in uppercase | Category/taxonomy visual language |