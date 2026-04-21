# PickleIQ — Design System

**Version:** 5.0 (Dark Premium Sports Analytics, 2026-04-20)
**Type:** APP UI — dark-only, data-driven, quiz-centric, premium sports tech

**Changelog v5.0:**
- Complete rewrite to match actual dark-theme implementation
- Dark-only design (bg-base #0a0a0a) — no light mode
- Fonts: Bebas Neue (display), Source Sans 3 (body), JetBrains Mono (data)
- Brand primary: lime #84CC16 (CTAs, highlights), secondary: orange #F97316
- All color values verified against tailwind.config.ts
- Font loading via next/font/google with CSS variables
- Removed all light-first, warm-white, warm-cream, Inter references

---

## Design Philosophy

**Product:** PickleIQ — Brazilian pickleball paddle recommendation platform
**Positioning:** Premium sports analytics — intelligent, data-driven, trustworthy
**Voice:** Brazilian Portuguese, knowledgeable and encouraging

**Core insight:** PickleIQ serves players seeking the perfect paddle through data and AI guidance. Design must feel premium and credible without being intimidating.

**Design pillars:**
- **Dark premium** — Sports analytics aesthetic, high contrast, immersive
- **Quiz-centric** — 7-step emotional journey as core experience
- **Data credibility** — Clean spec tables, price tracking, comparison tools
- **Trust through clarity** — Explain "why", show freshness, social proof

---

## Aesthetic Direction

**Direction:** Dark Premium Sports Analytics
**Mood:** Premium, data-driven, trustworthy, Brazilian
**Reference sites:** Strava (sports analytics), Wirecutter (research-backed recommendations), ESPN (data presentation)

**Decoration:** Minimal — dark surfaces, lime accents, sharp data presentation
**Imagery:** Real paddle photography on dark backgrounds, spec-first presentation

---

## Color System

### Background Hierarchy

| Token | Tailwind Class | Value | Usage |
|-------|---------------|-------|-------|
| base | `bg-base` | #0a0a0a | Page background, default |
| surface | `bg-surface` | #141414 | Cards, panels, elevated sections |
| elevated | `bg-elevated` | #1f1f1f | Hover states, nested surfaces |

### Brand Colors

| Token | Tailwind Class | Value | Usage |
|-------|---------------|-------|-------|
| brand-primary | `bg-brand-primary` | #84CC16 | Primary CTAs, links, highlights, success |
| brand-secondary | `bg-brand-secondary` | #F97316 | Secondary accent, warnings, emphasis |

### Text Hierarchy

| Token | Tailwind Class | Value | Usage |
|-------|---------------|-------|-------|
| text-primary | `text-text-primary` | #FAFAFA | Headlines, body text |
| text-secondary | `text-text-secondary` | #A3A3A3 | Descriptions, secondary info |
| text-muted | `text-text-muted` | #737373 | Captions, disabled text |
| text-disabled | `text-text-disabled` | #525252 | Inactive elements |

### Semantic Colors

| Token | Tailwind Class | Value | Usage |
|-------|---------------|-------|-------|
| success | `text-success` | #84CC16 | Success states, beginner level |
| warning | `text-warning` | #FBBF24 | Warnings, intermediate level |
| danger | `text-danger` | #EF4444 | Errors, destructive actions, advanced level |
| info | `text-info` | #60A5FA | Information, links |

### Price Delta Colors

| Token | Tailwind Class | Value | Usage |
|-------|---------------|-------|-------|
| price-up | `text-price-up` | #EF4444 | Price increased |
| price-down | `text-price-down` | #84CC16 | Price decreased |
| price-neutral | `text-price-neutral` | #737373 | No change |

### Skill Level Colors

| Level | Color | Tailwind | Usage |
|-------|-------|----------|-------|
| Iniciante | #22C55E | green-500 | Beginner paddles, badges |
| Intermediário | #FBBF24 | amber-400 | Intermediate paddles |
| Avançado | #EF4444 | red-500 | Advanced paddles |

**Usage:** Skill level badges on product cards, filter chips, quiz profile display. Background with white text.

---

## Typography

### Font Stack

| Role | Font | CSS Variable | Weights | Usage |
|------|------|-------------|---------|-------|
| Display | Bebas Neue | `--font-display` | 400 | Hero text, section headlines |
| Body | Source Sans 3 | `--font-body` | 400, 500, 600, 700 | Paragraphs, buttons, UI text |
| Mono | JetBrains Mono | `--font-mono` | 400, 500, 600, 700 | Prices, specs, data, code |

### Font Loading

Loaded via `next/font/google` in `layout.tsx` with CSS variables:

```typescript
// frontend/src/app/layout.tsx
const bebasNeue = Bebas_Neue({ subsets: ["latin"], weight: "400", variable: "--font-display", display: "swap" })
const sourceSans3 = Source_Sans_3({ subsets: ["latin"], variable: "--font-body", display: "swap", weight: ["400", "500", "600", "700"] })
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap", weight: ["400", "500", "600", "700"] })
```

Applied to `<html>` element: `className="${bebasNeue.variable} ${sourceSans3.variable} ${jetbrainsMono.variable}"`

Tailwind mapping:
```typescript
fontFamily: {
  display: ["var(--font-display)"],  // Bebas Neue
  sans: ["var(--font-body)"],        // Source Sans 3
  mono: ["var(--font-mono)"],        // JetBrains Mono
}
```

### Scale

| Element | Class | Desktop | Mobile | Weight | Line Height |
|---------|-------|---------|--------|--------|-------------|
| H1 (Hero) | `text-5xl font-display` | 48px | 48px | 400 (Bebas) | 1 |
| H2 (Section) | `text-3xl font-display` | 30px | 30px | 400 (Bebas) | 2.25rem |
| H3 (Card) | `text-xl font-sans` | 20px | 20px | 600 | 1.75rem |
| Body | `text-base font-sans` | 16px | 16px | 400 | 1.5rem |
| Data/Price | `text-sm font-mono` | 14px | 14px | 500-700 | 1.25rem |
| Caption | `text-xs font-sans` | 12px | 12px | 400-500 | 1rem |

### Content Tone

- Sentence case for labels (warmer than uppercase, except Bebas Neue headlines which are naturally uppercase)
- Conversational PT-BR: "Como voce se descreve?" not "Selecione seu nivel"
- Plain language: "Facil de controlar" not "Alta controlabilidade"

---

## Spacing System

**Base unit:** 4px (fine-grained control)

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 4px | Micro gaps, icon spacing |
| space-2 | 8px | Tight padding, element gaps |
| space-3 | 12px | Card internal padding |
| space-4 | 16px | Default element gap |
| space-6 | 24px | Card padding, section internal |
| space-8 | 32px | Section gaps |
| space-10 | 40px | Major section breaks |
| space-12 | 48px | Page-level padding |
| space-16 | 64px | Hero section padding |

**Pattern:** Use `gap: 20px` for product grids, `padding: 64px 0` for section vertical spacing, `padding: 24px` for card internal padding.

---

## Border Radius

| Token | Tailwind Class | Value | Usage |
|-------|---------------|-------|-------|
| sharp | `rounded-sharp` | 2px | Data tables, technical elements |
| rounded | `rounded-rounded` | 8px | Buttons, inputs |
| lg | `rounded-lg` | 12px | Cards, panels |
| xl | `rounded-xl` | 16px | Chat bubbles, containers |
| full | `rounded-full` | 9999px | Pills, badges, toggles |

---

## Layout

### Max Content Width

```css
/* Default: content pages, quiz, marketing */
max-width: 1280px;
margin: 0 auto;
padding: 0 2rem;

/* Data-dense: comparison tables */
max-width: 88rem;
margin: 0 auto;
padding: 0 2rem;
```

### Section Backgrounds

Dark-only hierarchy:
- **Default:** `bg-base` (#0a0a0a) — page background
- **Alternating sections:** `bg-surface` (#141414) — cards, panels
- **Emphasis:** `bg-elevated` (#1f1f1f) — hover states, nested cards

No light mode. All pages use dark theme exclusively.

### Responsive Breakpoints

| Viewport | Layout |
|----------|--------|
| < 768px (mobile) | Single column, full-width quiz cards, 48px touch targets |
| 768-1024px (tablet) | 2-column grids, side-by-side quiz options |
| > 1024px (desktop) | 3-column grids, centered quiz container (max-width 480px) |

### Grid System

- **Product grid:** 3-col desktop / 2-col tablet / 1-col mobile, `gap: 20px`
- **Quiz grid:** 2-col tablet+ / 1-col mobile, `gap: 16px`
- **Comparison table:** Full width, sticky header

---

## Components

### Buttons

#### Primary CTA (Lime)

```css
.btn-primary {
  background: #84CC16;           /* brand-primary */
  color: #0a0a0a;                /* dark text on lime */
  font-weight: 600;
  font-family: Source Sans 3;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 150ms ease;
}

.btn-primary:hover {
  background: #9ad619;
  box-shadow: 0 0 20px rgba(132, 204, 22, 0.3);  /* glow-green */
}

.btn-primary:active {
  transform: scale(0.98);
}
```

#### Secondary (Outline Lime)

```css
.btn-secondary {
  background: transparent;
  border: 2px solid #84CC16;     /* brand-primary */
  color: #84CC16;
  font-weight: 600;
  font-family: Source Sans 3;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 150ms ease;
}

.btn-secondary:hover {
  background: rgba(132, 204, 22, 0.1);
}
```

#### Tertiary (Ghost)

```css
.btn-tertiary {
  background: transparent;
  color: #A3A3A3;                /* text-secondary */
  font-weight: 500;
  font-family: Source Sans 3;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: color 150ms ease;
}

.btn-tertiary:hover {
  color: #84CC16;                /* brand-primary */
}
```

### Product Cards (Catalog)

```css
.product-card {
  background: #141414;           /* bg-surface */
  border: 1px solid hsl(var(--border));
  border-radius: 12px;
  overflow: hidden;
  transition: transform 150ms ease, box-shadow 150ms ease;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.8);  /* shadow-lg */
}
```

**Structure:**
- Image container (dark bg, aspect ratio 3:4)
- Brand (uppercase, 12px, text-secondary)
- Product name (600, 16px, text-primary, Source Sans 3)
- Price (bold, brand-primary #84CC16, JetBrains Mono)
- Level badge (pill, skill level colors)
- "Para voce" badge (when profile matches, brand-primary glow)
- [+ Comparar] button (tertiary)

### Quiz Cards

**Default state:**
```css
.quiz-card {
  background: #141414;           /* bg-surface */
  border: 2px solid hsl(var(--border));
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 200ms ease;
}

.quiz-card:hover {
  border-color: #84CC16;         /* brand-primary */
  background: #1f1f1f;           /* bg-elevated */
}
```

**Selected state:**
```css
.quiz-card.selected {
  border-color: #84CC16;         /* brand-primary */
  background: rgba(132, 204, 22, 0.1);
  box-shadow: 0 0 20px rgba(132, 204, 22, 0.3);  /* glow-green */
}
```

**Structure:**
- Icon/image on left (48x48px)
- Label (bold, text-primary) + description (regular, text-secondary) in center
- Checkmark icon on right (visible when selected)

### Recommendation Cards

```css
.recommendation-card {
  background: #141414;           /* bg-surface */
  border: 1px solid hsl(var(--border));
  border-radius: 12px;
  padding: 24px;
  transition: box-shadow 200ms ease;
}

.recommendation-card:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.8);  /* shadow-lg */
}
```

**Structure:**
1. Badge (e.g., "MELHOR COMBINACAO GERAL" with brand-primary accent)
2. Product image (140x200px, rounded-xl)
3. Brand (uppercase, text-secondary, 12px, Source Sans 3)
4. Product name (bold, 20px, text-primary)
5. Price (brand-primary, 24px, bold, JetBrains Mono)
6. Stock status (text-muted, 14px)
7. "Por que pra voce" section (bg-elevated bg, brand-primary border)
8. CTA button (full-width, brand-primary with glow-green)

### Chat Components

#### Message Bubbles

**User message:**
```css
.chat-bubble-user {
  background: #84CC16;           /* brand-primary */
  color: #0a0a0a;                /* dark text on lime */
  border-radius: 16px;
  padding: 12px 16px;
  max-width: 80%;
  align-self: flex-end;
}
```

**AI message:**
```css
.chat-bubble-ai {
  background: #1f1f1f;           /* bg-elevated */
  color: #FAFAFA;                /* text-primary */
  border-radius: 16px;
  padding: 12px 16px;
  max-width: 80%;
  align-self: flex-start;
  animation: slide-in 250ms ease forwards;
}
```

#### Typing Indicator

```css
.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #737373;           /* text-muted */
  animation: typing-dot 1.4s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 200ms; }
.typing-dot:nth-child(3) { animation-delay: 400ms; }
```

### Interactive Widgets

#### Quiz Pills

```css
.quiz-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  border: 2px solid hsl(var(--border));
  border-radius: 9999px;
  background: transparent;
  color: #A3A3A3;                /* text-secondary */
  font-weight: 500;
  font-family: Source Sans 3;
  cursor: pointer;
  transition: all 150ms ease;
}

.quiz-pill:hover {
  border-color: #84CC16;         /* brand-primary */
}

.quiz-pill.selected {
  border-color: #84CC16;
  background: #84CC16;
  color: #0a0a0a;                /* dark text on lime */
}
```

#### Toggle Switch

```css
.toggle-track {
  width: 40px;
  height: 22px;
  border-radius: 9999px;
  background: #1f1f1f;           /* bg-elevated */
  position: relative;
  cursor: pointer;
  transition: background 150ms ease;
}

.toggle-track.active {
  background: #84CC16;           /* brand-primary */
}

.toggle-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #FAFAFA;           /* text-primary */
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 150ms ease;
}

.toggle-track.active .toggle-thumb {
  transform: translateX(18px);
}
```

#### Progress Dots

```css
.progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #525252;           /* text-disabled */
  transition: background 150ms ease;
}

.progress-dot.active {
  background: #84CC16;           /* brand-primary */
}
```

---

## Motion System

### Duration Scale

| Token | Value | Usage |
|-------|-------|-------|
| instant | 50ms | Hover states, micro-feedback |
| fast | 150ms | Button presses, toggles, pill selection |
| normal | 250ms | Card transitions, message enter |
| slow | 400ms | Profile reveal, page transitions |

### Easing

```css
:root {
  --ease-enter: cubic-bezier(0, 0, 0.2, 1);
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);
  --ease-move: cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Animation Patterns

**Quiz card selection:**
```css
.quiz-card {
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

.quiz-card.selected {
  transform: scale(0.98);
  border-color: #84CC16;
  box-shadow: 0 0 20px rgba(132, 204, 22, 0.3);
}
```

**Results card entrance (staggered):**
```css
@keyframes results-enter {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.recommendation-card {
  animation: results-enter 300ms cubic-bezier(0, 0, 0.2, 1) forwards;
}

.recommendation-card:nth-child(1) { animation-delay: 0ms; }
.recommendation-card:nth-child(2) { animation-delay: 150ms; }
.recommendation-card:nth-child(3) { animation-delay: 300ms; }
```

**Profile summary reveal:**
```css
@keyframes profile-enter {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.profile-summary {
  animation: profile-enter 400ms cubic-bezier(0, 0, 0.2, 1) forwards;
}
```

### Tailwind Animations (from config)

| Class | Duration | Usage |
|-------|----------|-------|
| `animate-slide-in` | 200ms | Elements entering view |
| `animate-slide-out` | 200ms | Elements leaving view |
| `animate-pulse-glow` | 2s infinite | Loading states |
| `animate-shimmer` | 2s infinite | Skeleton loading |
| `animate-count-up` | 400ms | Number counters |
| `animate-typing-dot` | 1.4s infinite | Chat typing indicator |

---

## Box Shadows

| Token | Tailwind Class | Value | Usage |
|-------|---------------|-------|-------|
| sm | `shadow-sm` | 0 1px 2px rgba(0,0,0,0.5) | Subtle elevation |
| md | `shadow-md` | 0 4px 6px -1px rgba(0,0,0,0.7) | Cards |
| lg | `shadow-lg` | 0 10px 15px -3px rgba(0,0,0,0.8) | Hover elevation |
| glow-green | `shadow-glow-green` | 0 0 20px rgba(132,204,22,0.3) | Brand primary glow |
| glow-orange | `shadow-glow-orange` | 0 0 20px rgba(249,115,22,0.3) | Brand secondary glow |

---

## Quiz Specification

### 7-Step Emotional Progression

| Step | Question | Type | Purpose | Micro-copy |
|------|----------|------|---------|------------|
| 1 | Welcome splash | CTA | Set expectations | "Vamos encontrar sua raquete perfeita" |
| 2 | "Como voce se descreve?" | Image cards (3) | Identity framing | "Vamos la!" |
| 3 | "O que voce mais valoriza?" | Visual cards (3) | Play style | "Ja sei quem voce e..." |
| 4 | "O que te frustra?" | Multi-select checkboxes | Pain points | "Quase la!" |
| 5 | "Com que frequencia joga?" | Single select (3) | Context | "So mais uma..." |
| 6 | "Qual seu orcamento?" | Slider (R$200-2000) | Budget | "Ultima pergunta!" |
| 7 | Analyzing... | Loading animation | Personalization theater | "Analisando seu perfil..." |

### Interaction Patterns

- **Auto-advance:** Steps 2, 3, 5, 6 advance on selection (no "Next" button)
- **Explicit advance:** Step 4 (multi-select) requires "Proximo →" button
- **Progress indicator:** Animated dots with encouraging copy at each step
- **Budget slider:** Continuous range with "smart zone" hint (R$400-800 for beginners)
- **Loading state:** Checklist animation ("Nivel identificado", "Buscando raquetes...")

### Results Page Structure

1. **Profile summary card** (brand-primary gradient background, 4 attributes)
2. **3 recommendation cards** with badges:
   - Melhor combinacao geral
   - Melhor custo-beneficio
   - Melhor para evoluir
3. **"Por que pra voce" section** on each card (2-3 bullet points)
4. **Secondary CTAs:** "Falar com IA", "Ver catalogo", "Refazer quiz"

---

## Accessibility

### WCAG 2.2 Compliance

| Check | Requirement | Implementation |
|-------|-------------|----------------|
| Color contrast | AA for text | Lime #84CC16 on dark #0a0a0a = 8.2:1 (AAA). Text-primary #FAFAFA on #0a0a0a = 18:1 (AAA) |
| Focus indicators | Visible outline | 2px ring on all interactive elements |
| Touch targets | 48px minimum | All buttons, cards, pills ≥ 48px height |
| Screen reader | ARIA labels | `aria-label` on image buttons, `role="radio"` on quiz cards |
| Keyboard nav | Tab order | Visual order matches DOM order, Escape closes modals |
| Error states | Clear messaging | Red border + error icon + descriptive text |

### ARIA Implementation

```html
<!-- Quiz cards as radio group -->
<div role="radiogroup" aria-label="Como voce se descreve como jogador?">
  <div role="radio" aria-checked="true" aria-label="Iniciante - Jogo por diversao e saude" class="quiz-card selected">
    ...
  </div>
</div>

<!-- Chat message list -->
<div role="log" aria-live="polite" aria-label="Mensagens do chat">
  ...
</div>

<!-- Affiliate CTAs -->
<a href="..." aria-label="Ver Selkirk Gamma no site Brazil Store, R$ 689">
  Ver no site →
</a>
```

### PT-BR Accessibility

- Plain language throughout (no jargon without explanation)
- Descriptive button labels ("Ver minhas recomendacoes" not "Ver")
- Alt text for all images in Portuguese
- Sentence case for readability

---

## AI Slop Avoidance Checklist

Before shipping any UI, verify:

- [ ] No generic "Welcome to..." / "Your all-in-one solution" copy
- [ ] No centered-everything layout (left-align body copy)
- [ ] No decorative blobs or wavy SVG dividers
- [ ] No purple/violet gradient backgrounds
- [ ] No icons in colored circles as decoration
- [ ] No 3-column feature grid with icons
- [ ] Cards exist for function, not decoration
- [ ] Section labels are sentence case, not uppercase
- [ ] Brand-primary (#84CC16) used for CTAs and highlights, not overused
- [ ] Quiz feels like guidance, not interrogation
- [ ] Recommendations explain "why", not just "what"
- [ ] Brazilian Portuguese feels natural, not translated

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-20 | Dark-only design | Premium sports analytics aesthetic. Dark provides better contrast for data presentation and matches sports tech conventions. |
| 2026-04-20 | Bebas Neue for display | Bold, athletic, high-impact for headlines. Uppercase-only naturally. Loaded via next/font/google for zero layout shift. |
| 2026-04-20 | Source Sans 3 for body | Clean, readable, slightly warmer than Inter for Portuguese text. Multiple weights for hierarchy. |
| 2026-04-20 | JetBrains Mono for data | Credible spec tables, clear price display. Retained from v3.0 for data credibility. |
| 2026-04-20 | Lime #84CC16 primary CTA | High contrast on dark backgrounds (8.2:1). Distinctive brand color. Better accessibility than orange on dark. |
| 2026-04-20 | Orange #F97316 secondary | Warm accent for emphasis, warnings, secondary highlights. Complements lime without competing. |
| 2026-04-05 | 7-step quiz | Emotional investment increases conversion. Noom has 40+ questions with 80% completion. |
| 2026-04-05 | Soft corners (8-12px) for cards | Approachable feel while maintaining premium look. Sharp corners (2px) reserved for data tables. |
| 2026-04-05 | "Por que pra voce" section | Wirecutter pattern: explain recommendations, don't just list products. |
| 2026-04-05 | Skill level colors retained | Intuitive visual taxonomy (green/amber/red) works across cultures. |
