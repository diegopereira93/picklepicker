# PickleIQ — Design System

**Version:** 4.0 (Warm Guide — UI Redesign, 2026-04-05)
**Type:** APP UI — light-first, approachable, quiz-centric, Brazilian warmth

**Changelog v4.0:**
- Complete redesign from "Hybrid Modern Sports Tech" to "Warm Guide"
- Light-first aesthetic with warm-white backgrounds (#FAFAF8)
- Coral (#F97316) as primary CTA accent, lime retained for data
- Soft corners (8-12px) replacing sharp 2px tech edges
- 7-step quiz with emotional progression as core experience
- Recommendation cards with "Por que pra voce" explanations
- Dark mode optional (next-themes toggle), chat forces dark
- WCAG 2.2 compliance with coral focus indicators

**Changelog v3.0:** (superseded — see v4.0)

---

## Design Philosophy

**Product:** PickleIQ — Brazilian pickleball paddle recommendation platform
**Positioning:** "The warm guide to your perfect paddle" — approachable, conversational, trustworthy
**Voice:** Brazilian warmth, conversational, encouraging — like a knowledgeable friend

**Core insight:** PickleIQ serves confused beginners, not data analysts. The quiz IS the product. Design must guide, not intimidate.

**Design pillars:**
- **Light-first** — Warm, approachable, not a tech dashboard
- **Quiz-centric** — 7-step emotional journey, not a 3-step widget
- **Brazilian warmth** — Conversational PT-BR, coral accent, generous whitespace
- **Trust through clarity** — Explain "why", show freshness, social proof

**What this is NOT:**
- NOT a data dashboard (too cold for beginners)
- NOT a pure sports app (too one-dimensional)
- NOT dark-first (intimidating for new players)

---

## Aesthetic Direction

**Direction:** Warm Guide
**Mood:** Approachable, conversational, Brazilian, trustworthy
**Reference sites:** Duolingo (gamified guidance), Wirecutter (research-backed recommendations), Nike Run Club (sporty warmth)

**Decoration:** Intentional — warm textures, lifestyle photography, clean surfaces
**Imagery:** Real paddle photography, diverse Brazilian players, white/cream product backgrounds

---

## Color System

### Base Palette

```css
:root {
  --warm-white: #FAFAF8;      /* Primary background */
  --warm-cream: #F5F2EB;      /* Secondary background, cards */
  --warm-charcoal: #2A2A2A;   /* Primary text */
}
```

### Accent Colors

```css
:root {
  --accent-coral: #F97316;        /* Primary CTA, buttons, links */
  --accent-coral-hover: #EA580C;  /* Hover state */
  --accent-lime: #84CC16;         /* Secondary accent, data highlights */
  --accent-amber: #F59E0B;        /* Warnings, tips, intermediate level */
}
```

**Contrast rule:** Coral (#F97316) has 3.5:1 on white — AA for large text only.
- ✅ Use coral for buttons, headlines, CTAs
- ❌ Never use coral for small body text on light backgrounds

### Trust & Semantic Colors

```css
:root {
  --trust-blue: #0EA5E9;      /* Links, trust signals */
  --success-green: #22C55E;   /* Success states, beginner level */
  --error-red: #EF4444;       /* Errors, advanced level */
}
```

### Neutral Scale

```css
:root {
  --gray-100: #F3F4F6;
  --gray-200: #E5E7EB;
  --gray-300: #D1D5DB;
  --gray-400: #9CA3AF;
  --gray-500: #6B7280;        /* Secondary text */
  --gray-600: #4B5563;
  --gray-700: #374151;
  --gray-800: #1F2937;
}
```

### Skill Level Colors (Retained from v3.0)

```css
:root {
  --level-beginner: #22C55E;      /* Green — Iniciante */
  --level-intermediate: #F59E0B;  /* Amber — Intermediário */
  --level-advanced: #EF4444;      /* Red — Avançado */
}
```

**Usage:** Skill level badges on product cards, filter chips, quiz profile display. Background color with white text (beginner/advanced) or dark text (intermediate).

### Data Credibility (Retained from v3.0)

```css
:root {
  --data-green: #76b900;        /* Charts, specs, comparison highlights */
}
```

**Usage:** Green accent for data elements: charts, table highlights, spec badges. NOT for CTAs.

---

## Typography

### Font Stack

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Display/Hero | Inter | 700 | Headlines, H1, H2 |
| Body | Inter | 400 | Paragraphs, descriptions, chat |
| Body Bold | Inter | 600-700 | Button labels, emphasis |
| Data/Specs | JetBrains Mono | 400 | Comparison tables, spec values, prices |
| Caption | Inter | 400-500 | Metadata, timestamps, tooltips |

**Retained from v3.0:** Inter for display/body, JetBrains Mono for data.

### Font Loading

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

### Scale

| Element | Desktop | Mobile | Weight | Line Height |
|---------|---------|--------|--------|-------------|
| H1 (Hero) | 64px | 48px | 700 | 1.1 |
| H2 (Section) | 32px | 28px | 700 | 1.25 |
| H3 (Card) | 20px | 18px | 600 | 1.3 |
| Body | 16px | 16px | 400 | 1.6 |
| Body Bold | 16px | 16px | 600-700 | 1.6 |
| Data | 14px | 14px | 400 | 1.5 |
| Caption | 12px | 12px | 400-500 | 1.43 |

**Changes from v3.0:** Larger mobile headlines (48px vs 40px), increased body line-height (1.6 vs 1.5) for readability.

### Content Tone

- Sentence case for labels (warmer than uppercase)
- Conversational: "Como voce se descreve?" not "Selecione seu nivel"
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

```css
:root {
  --radius-sm: 8px;     /* Buttons, small elements */
  --radius-md: 12px;    /* Cards, quiz options */
  --radius-lg: 16px;    /* Chat bubbles, containers */
  --radius-xl: 24px;    /* Large containers, profile cards */
  --radius-full: 9999px; /* Pills, toggle switches */
}
```

**Why soft corners?** Warm, approachable, conversational. Sharp corners signal "tech dashboard" — wrong for a guidance platform.

**Usage:**
- Buttons: 8px
- Product cards: 12px
- Quiz cards: 12px
- Chat bubbles: 16px
- Profile summary: 24px
- Pills/toggles: full (9999px)

---

## Layout

### Max Content Width

```css
/* Default: content pages, quiz, marketing */
max-width: 1200px;
margin: 0 auto;
padding: 0 24px;

/* Data-dense: comparison tables, dashboards */
max-width: 1440px;
margin: 0 auto;
padding: 0 24px;
```

**When to use which:** Default `1200px` for homepage, quiz, catalog cards, chat. Use `1440px` for 9+ column comparison tables and data-dense layouts.

### Section Backgrounds

**Default:** Light-first aesthetic
```css
/* Light section (default) */
background: var(--warm-white);
color: var(--warm-charcoal);

/* Warm cream (secondary sections) */
background: var(--warm-cream);
color: var(--warm-charcoal);
```

**Exception — Dark Sections:**
- Chat interface: forces dark mode (immersive conversation)
- Admin dashboard: dark mode (data-heavy)
- Comparison tables: optional dark mode (user toggle)

```css
/* Dark section (chat, dashboards) */
.chat-dark {
  background: #1a1a1a;
  color: #ffffff;
}
```

### Responsive Breakpoints

| Viewport | Layout |
|----------|--------|
| < 768px (mobile) | Single column, full-width quiz cards, 48px touch targets |
| 768-1024px (tablet) | 2-column grids, side-by-side quiz options |
| > 1024px (desktop) | 3-column grids, centered quiz container (max-width 480px) |

### Grid System

**Product grid:** 3-col desktop / 2-col tablet / 1-col mobile, `gap: 20px`
**Quiz grid:** 2-col tablet+ / 1-col mobile, `gap: 16px`
**Comparison table:** Full width, sticky header

---

## Components

### Buttons

#### Primary CTA (Coral)

```css
.btn-primary {
  background: var(--accent-coral);
  color: #ffffff;
  font-weight: 600;
  padding: 12px 24px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  transition: all 150ms ease;
}

.btn-primary:hover {
  background: var(--accent-coral-hover);
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.24);
}

.btn-primary:active {
  transform: scale(0.98);
}
```

#### Secondary (Outline Coral)

```css
.btn-secondary {
  background: transparent;
  border: 2px solid var(--accent-coral);
  color: var(--accent-coral);
  font-weight: 600;
  padding: 12px 24px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 150ms ease;
}

.btn-secondary:hover {
  background: rgba(249, 115, 22, 0.04);
}
```

#### Tertiary (Ghost)

```css
.btn-tertiary {
  background: transparent;
  color: var(--gray-500);
  font-weight: 500;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: color 150ms ease;
}

.btn-tertiary:hover {
  color: var(--accent-coral);
}
```

### Quiz Cards

**Default state:**
```css
.quiz-card {
  background: #ffffff;
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: 20px;
  cursor: pointer;
  transition: all 200ms ease;
}

.quiz-card:hover {
  border-color: var(--accent-coral);
  background: var(--gray-100);
}
```

**Selected state:**
```css
.quiz-card.selected {
  border-color: var(--accent-coral);
  background: rgba(249, 115, 22, 0.04);
  box-shadow: 0 0 0 2px var(--accent-coral);
}

.quiz-card.selected .checkmark {
  display: flex;
  /* Shows checkmark icon */
}
```

**Structure:**
- Icon/image on left (48x48px)
- Label (bold) + description (regular) in center
- Checkmark icon on right (visible when selected)

### Recommendation Cards

```css
.recommendation-card {
  background: #ffffff;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: box-shadow 200ms ease;
}

.recommendation-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
```

**Structure:**
1. Badge (e.g., "⭐ MELHOR COMBINACAO GERAL")
2. Product image (140x200px, rounded-lg)
3. Brand (uppercase, lime-600, 12px)
4. Product name (bold, 20px)
5. Price (coral-500, 24px, bold)
6. Stock status (gray-500, 14px)
7. "Por que pra voce" section (lime-50 bg, lime-200 border)
8. CTA button (full-width, coral primary)

### Product Cards (Catalog)

```css
.product-card {
  background: #ffffff;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 150ms ease, box-shadow 150ms ease;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}
```

**Structure:**
- Image container (white bg, aspect ratio 3:4)
- Brand (uppercase, 12px, gray-500)
- Product name (600, 16px)
- Price (bold, coral-600, JetBrains Mono)
- Level badge (pill, skill level colors)
- "Para voce" badge (when profile matches)
- [+ Comparar] button (tertiary)

### Chat Components

#### Message Bubbles

**User message:**
```css
.chat-bubble-user {
  background: var(--accent-coral);
  color: #ffffff;
  border-radius: var(--radius-lg);
  padding: 12px 16px;
  max-width: 80%;
  align-self: flex-end;
}
```

**AI message:**
```css
.chat-bubble-ai {
  background: var(--warm-cream);
  color: var(--warm-charcoal);
  border-radius: var(--radius-lg);
  padding: 12px 16px;
  max-width: 80%;
  align-self: flex-start;
  animation: message-enter 250ms ease forwards;
}
```

#### Typing Indicator

```css
.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gray-400);
  animation: typing-bounce 600ms ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 150ms; }
.typing-dot:nth-child(3) { animation-delay: 300ms; }

@keyframes typing-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
```

### Interactive Widgets

#### Quiz Pills (Inline Selection)

```css
.quiz-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  border: 2px solid var(--gray-300);
  border-radius: var(--radius-full);
  background: #ffffff;
  color: var(--gray-600);
  font-weight: 500;
  cursor: pointer;
  transition: all 150ms ease;
}

.quiz-pill:hover {
  border-color: var(--accent-coral);
}

.quiz-pill.selected {
  border-color: var(--accent-coral);
  background: var(--accent-coral);
  color: #ffffff;
}
```

#### Toggle Switch

```css
.toggle-track {
  width: 40px;
  height: 22px;
  border-radius: var(--radius-full);
  background: var(--gray-300);
  position: relative;
  cursor: pointer;
  transition: background 150ms ease;
}

.toggle-track.active {
  background: var(--accent-coral);
}

.toggle-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ffffff;
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
  background: var(--gray-300);
  transition: background 150ms ease;
}

.progress-dot.active {
  background: var(--accent-coral);
}

.progress-line {
  width: 24px;
  height: 2px;
  background: var(--gray-300);
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
  --ease-enter: cubic-bezier(0, 0, 0.2, 1);   /* Elements entering */
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);    /* Elements leaving */
  --ease-move: cubic-bezier(0.4, 0, 0.2, 1);  /* Position changes */
}
```

### Animation Patterns

**Quiz card selection:**
```css
.quiz-card {
  transition: all 200ms var(--ease-move);
}

.quiz-card.selected {
  transform: scale(0.98);
  border-color: var(--accent-coral);
  box-shadow: 0 0 0 2px var(--accent-coral);
}
```

**Results card entrance (staggered):**
```css
@keyframes results-enter {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.recommendation-card {
  animation: results-enter 300ms var(--ease-enter) forwards;
}

.recommendation-card:nth-child(1) { animation-delay: 0ms; }
.recommendation-card:nth-child(2) { animation-delay: 150ms; }
.recommendation-card:nth-child(3) { animation-delay: 300ms; }
```

**Profile summary reveal:**
```css
.profile-summary {
  animation: profile-enter 400ms var(--ease-enter) forwards;
}

@keyframes profile-enter {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

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
- **Loading state:** Checklist animation ("✓ Nivel identificado", "◐ Buscando raquetes...")

### Results Page Structure

1. **Profile summary card** (gradient coral background, 4 attributes)
2. **3 recommendation cards** with badges:
   - ⭐ Melhor combinacao geral
   - 💰 Melhor custo-beneficio
   - 🎯 Melhor para evoluir
3. **"Por que pra voce" section** on each card (2-3 bullet points)
4. **Secondary CTAs:** "Falar com IA", "Ver catalogo", "Refazer quiz"

---

## Dark Mode

### Implementation

- Toggle via `next-themes` (user preference)
- **Default:** Light mode (warm, approachable)
- **Forced dark:** `/chat` interface (immersive conversation)
- **Optional dark:** `/paddles` comparison view, admin dashboard

### Dark Mode Tokens

```css
[data-theme="dark"] {
  --warm-white: #1a1a1a;
  --warm-cream: #111111;
  --warm-charcoal: #f5f5f5;
  --gray-100: #1f2937;
  --gray-200: #374151;
  --gray-300: #4b5563;
  --gray-400: #6b7280;
  --gray-500: #9ca3af;
  --gray-600: #d1d5db;
  --gray-700: #e5e7eb;
  --gray-800: #f3f4f6;
}
```

### When to Use Dark Mode

| Screen | Mode | Rationale |
|--------|------|-----------|
| Homepage | Light | First impression, warmth |
| Quiz | Light | Approachable, encouraging |
| Results | Light | Celebration, clarity |
| Chat | Dark (forced) | Immersive conversation |
| Catalog | Light (default) / Dark (toggle) | User preference |
| Comparison | Light (default) / Dark (toggle) | Data density |
| Admin | Dark | Dashboard aesthetic |

---

## Accessibility

### WCAG 2.2 Compliance

| Check | Requirement | Implementation |
|-------|-------------|----------------|
| Color contrast | AA for text | Coral for large text only (3.5:1), charcoal for body (12.6:1) |
| Focus indicators | Visible 2px outline | 2px coral outline on all interactive elements |
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
- [ ] Coral used for CTAs only, not body text
- [ ] Quiz feels like guidance, not interrogation
- [ ] Recommendations explain "why", not just "what"
- [ ] Brazilian Portuguese feels natural, not translated

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | "Warm Guide" aesthetic | Beginners need guidance, not data dashboard. Light-first reduces intimidation. |
| 2026-04-05 | Coral primary accent | Warm, energetic, Brazilian sports commerce standard. Outperforms lime for CTAs. |
| 2026-04-05 | 7-step quiz | Emotional investment increases conversion. Noom has 40+ questions with 80% completion. |
| 2026-04-05 | Soft corners (8-12px) | Sharp corners signal "tech" — wrong for conversational guidance. |
| 2026-04-05 | "Por que pra voce" section | Wirecutter pattern: explain recommendations, don't just list products. |
| 2026-04-05 | Dark mode optional | Chat needs immersion; data screens benefit from dark. Light remains default for warmth. |
| 2026-04-05 | JetBrains Mono retained | Analytical users still need credible spec tables. Keep data credibility layer. |
| 2026-04-05 | Skill level colors retained | Intuitive visual taxonomy (green/amber/red) works across cultures. |

(End of DESIGN.md v4.0 — 776 lines)
