# PickleIQ Design Review v2.0

**Branch:** `feat/design-review-v2`
**Date:** 2026-04-05
**Status:** Review Complete
**Verdict:** Major redesign recommended

---

## Executive Summary

PickleIQ's current "Hybrid Modern Sports Tech" design (dark, tech dashboard, lime accent, sharp corners) fundamentally misaligns with its product nature. This is a **recommendation platform for beginners**, not a data dashboard. The quiz is an afterthought buried in a hero section. The new direction must make the quiz the hero, feel warm and Brazilian, and build trust through clarity.

**Proposed New Direction: "Warm Guide" Aesthetic**
- Light-first (approachable) with dark mode for data-heavy screens
- Coral (#F97316) primary accent for CTAs, Lime (#84CC16) secondary for data
- Soft corners (8-12px), generous whitespace
- Quiz as the hero of the entire experience (7 steps, emotional progression)
- Conversational tone, Brazilian warmth in micro-copy

---

## Step 0: Design Scope Assessment

### 0A. Design Completeness Rating: 3/10

The current plan (existing codebase) rates 3/10 on design completeness because:
- Quiz is 3 generic steps with emoji buttons and zero emotional arc
- Recommendation result is a single card with no explanation
- Homepage hero embeds the quiz as a widget, not as the primary experience
- No gift buyer flow exists despite being a named persona in the PRD
- No profile summary or personalization theater after quiz completion
- Chat interface uses generic dark theme with no warm elements
- No loading/analyzing state between quiz completion and results

**What a 10 looks like**: Every screen has clear hierarchy, every state (empty, loading, error, success) is designed, the quiz builds emotional investment, recommendations explain *why*, and the entire flow feels like a trusted friend guiding you.

### 0B. DESIGN.md Status

DESIGN.md v3.0 exists with "Hybrid Modern Sports Tech" direction. **User explicitly instructed to IGNORE it** and find a direction that fits the project's nature. Proceeding with universal design principles + research-backed recommendations.

### 0C. Existing Design Leverage

- **JetBrains Mono** for data/specs tables - keep, signals credibility
- **shadcn/ui component library** - keep base components (Button, Card, Dialog, etc.)
- **Inter font** - keep, works well for PT-BR
- **Skill level color system** (green/amber/red) - keep, intuitive
- **Profile localStorage persistence** - keep, good UX for returning users
- **SafeImage component** - keep, handles broken images gracefully
- **Tailwind CSS + CSS variables** - keep, solid foundation

### 0D. Focus Areas

Biggest gaps identified:
1. **Quiz experience** - the core differentiator, currently an afterthought
2. **Recommendation results** - single card, no explanation, no emotional payoff
3. **Gift buyer flow** - named persona, zero implementation
4. **Trust signals** - no social proof, no retailer logos, no freshness indicators
5. **Information architecture** - quiz buried in homepage, no dedicated /quiz route
6. **Content strategy** - cold technical tone, not warm Brazilian guide

---

## Step 1: Information Architecture

### Current Structure (Problems)

```
/ (Landing) → quiz widget embedded in hero
/paddles (Catalog)
/chat (AI chat)
/admin (Dashboard)
/blog (Placeholder)
```

**Problems:**
- No dedicated quiz page - quiz is a widget inside the homepage
- No quiz results page - results appear inline after quiz
- No gift buyer entry point
- No way to edit profile after completion
- Chat and catalog feel disconnected from quiz

### Proposed Structure

```
/ (Landing)
  Primary CTA: "Comecar Quiz" → /quiz
  Secondary: "Ver Catalogo" → /paddles
  Trust signals, featured paddles, how it works

/quiz (Dedicated Quiz Page - NEW)
  7-step emotional progression
  Full viewport, no distractions
  Progress indicator + encouraging copy

/quiz/results (Recommendation Results - NEW)
  Profile summary card
  3 recommended paddles with "Why this matches you"
  CTAs: Chat, Catalog, Redo Quiz

/paddles (Catalog - Enhanced)
  Light background, larger cards
  Filters: level, brand, price, style
  Comparison mode (select 2-3)
  "Recommended for you" badge when profile exists

/chat (AI Chat - Enhanced)
  Dark mode retained (works for chat)
  Warmer AI tone
  Product cards with match explanations
  Context-aware: knows user profile

/gift (Gift Buyer Flow - NEW)
  Simplified 3-question quiz
  "Quem vai receber?" framing
  Gift-specific results page
```

### IA Rating: 4/10 → 9/10

Key improvements: dedicated quiz page, quiz results page, gift buyer flow, profile-aware catalog.

---

## Step 2: Interaction Design

### Quiz Flow Redesign

**Current**: 3 steps (level, style, budget), ~30 seconds, text buttons, single result
**Proposed**: 7 steps, 2-3 minutes, image cards + slider, 3 results + profile

| Step | Question | Type | Purpose |
|------|----------|------|---------|
| 1 | Welcome + CTA | Splash | Set expectations |
| 2 | "Como voce se descreve como jogador?" | Image cards | Identity framing |
| 3 | "O que voce mais valoriza no jogo?" | Visual selection | Play style |
| 4 | "O que te frustra na sua raquete atual?" | Multi-select checkboxes | Pain points |
| 5 | "Com que frequencia voce joga?" | Single select | Context |
| 6 | "Qual seu orcamento?" | Slider R$200-2000 | Budget |
| 7 | Analyzing... | Animated loading | Personalization theater |

### Interaction Patterns

**Auto-advance**: Most steps advance automatically on selection (no "Next" button needed). Exception: multi-select (step 4) requires explicit "Proximo".

**Progress indicator**: Animated dots with encouraging micro-copy at each step:
- Step 1: "" (splash)
- Step 2: "Vamos la!"
- Step 3: "Ja sei quem voce e..."
- Step 4: "Quase la!"
- Step 5: "So mais uma..."
- Step 6: "Ultima pergunta!"
- Step 7: "Analisando..."

**Selection feedback**: Scale down (0.98) + coral border + checkmark icon on selected cards. Smooth 200ms transition.

**Budget slider**: Continuous range R$200-2000 with "smart zones" highlighted (R$400-800 for beginners).

**Results reveal**: Staggered card entrance (0ms, 150ms, 300ms delays). Profile summary appears first with fade-in.

### ID Rating: 3/10 → 8/10

---

## Step 3: Visual Design

### Color Palette Shift

| Role | Current (v3.0) | Proposed (v4.0) |
|------|---------------|-----------------|
| Background | #000000 (black) | #FAFAF8 (warm white) |
| Card BG | #1a1a1a (near-black) | #FFFFFF (white) |
| Primary CTA | #84CC16 (lime) | #F97316 (coral) |
| Secondary accent | #FCD34D (amber) | #84CC16 (lime, for data) |
| Data accent | #76b900 (green) | #76b900 (retained) |
| Text primary | #FFFFFF | #2A2A2A (charcoal) |
| Text secondary | #a7a7a7 | #6B7280 (gray-500) |
| Trust/links | #3860be | #0EA5E9 (sky blue) |

### Typography

Retain Inter for display/body, JetBrains Mono for data. Key changes:
- Larger headlines on mobile (48px vs 40px)
- More generous line-height for body (1.6 vs 1.5)
- Section labels: sentence case, not uppercase (warmer feel)

### Border Radius

| Element | Current | Proposed |
|---------|---------|----------|
| Buttons | 2px | 8px |
| Cards | 4px | 12px |
| Quiz options | rounded-xl (12px) | 12px (retained) |
| Chat bubbles | 8px | 16px |
| Large containers | 2px | 16-24px |

### Imagery Direction

- Real paddle photography (not illustrations)
- Lifestyle shots of diverse Brazilians playing
- Avoid generic stock photos
- Product images on white/cream backgrounds
- Hero could feature a lifestyle shot with overlay

### VD Rating: 5/10 → 8/10

---

## Step 4: Responsive Design

### Breakpoints (Retain)

| Viewport | Layout |
|----------|--------|
| < 768px (mobile) | Single column, full-width quiz cards |
| 768-1024px (tablet) | 2-column grids, side-by-side quiz options |
| > 1024px (desktop) | 3-column grids, centered quiz container |

### Quiz Responsiveness

- Mobile: Full-width cards, stacked vertically, larger touch targets (48px min)
- Desktop: Quiz container max-width 480px, centered, option cards in row for 3-option steps
- Budget slider: Full-width on all sizes

### RD Rating: 6/10 → 8/10

---

## Step 5: Accessibility

### WCAG 2.2 Compliance

| Check | Status | Fix |
|-------|--------|-----|
| Coral (#F97316) on white contrast | 3.5:1 (AA large text) | Use for buttons/headlines only, not body text |
| Coral on warm-white (#FAFAF8) | 3.4:1 | Same as above |
| Charcoal (#2A2A2A) on white | 12.6:1 (AAA) | Pass |
| Gray-500 (#6B7280) on white | 4.6:1 (AA) | Pass |
| Focus indicators | Missing | Add 2px coral outline on all interactive elements |
| Tap targets | 44px min | Increase to 48px minimum |
| Screen reader support | Partial | Add aria-labels to image-based quiz options |
| Keyboard navigation | Partial | Ensure all quiz steps are keyboard-navigable |

### PT-BR Accessibility

- Plain language throughout (no jargon without explanation)
- Descriptive button labels ("Ver minha recomendacao" not "Ver")
- Alt text for all images in Portuguese

### A11y Rating: 4/10 → 8/10

---

## Step 6: Motion & Animation

### Principles

1. Purposeful: Every animation aids comprehension
2. Fast: 150-300ms (nobody waits for decoration)
3. Smooth: ease-out for entrances, ease-in for exits

### Animation Inventory

| Element | Animation | Duration | Trigger |
|---------|-----------|----------|---------|
| Quiz card select | Scale 0.98 + border pulse | 200ms | Click |
| Quiz step transition | Fade out + slide left, fade in + slide right | 300ms | Step change |
| Progress dot | Subtle pulse | 600ms | Active step |
| Results card entrance | Fade up + stagger | 300ms + 150ms delay | Page load |
| Profile summary | Fade in + scale | 400ms | Results page |
| CTA hover | Scale 1.02 + shadow | 150ms | Hover |
| Analyzing state | Typing dots + progress bar fill | Continuous | Step 7 |

### MA Rating: 5/10 → 8/10

---

## Step 7: Content Strategy

### Tone Shift

**From**: Technical, professional, cold ("Selecione seu nivel de habilidade")
**To**: Warm, conversational, Brazilian ("Como voce se descreve como jogador?")

### Voice Guidelines

- Use "voce" (informal, not "senhor/senhora")
- First-person plural: "Vamos encontrar sua raquete..."
- Conversational: "Quase la!" "Boa escolha!"
- Plain language: "Facil de controlar" not "Alta controlabilidade"
- Aspirational framing: "Como voce quer jogar?" not "Qual seu nivel?"

### Microcopy Examples

| Element | Current | Proposed |
|---------|---------|----------|
| Quiz CTA | "Comecar" | "Vamos la!" or "Comecar →" |
| Budget label | "Orcamento maximo" | "Quanto voce quer investir?" |
| Results CTA | "Ver recomendacoes" | "Ver minhas recomendacoes →" |
| Back button | "Voltar" | "← Voltar" |
| Empty state | (none) | "Nenhuma raquete encontrada. Tente ampliar seu orcamento." |
| Loading | (spinner) | "Buscando as melhores opcoes para voce..." |
| Error | (none) | "Ops! Algo deu errado. Tente novamente." |

### CS Rating: 3/10 → 8/10

---

## Current vs Proposed: Summary

| Dimension | Current | Proposed | Gap |
|-----------|---------|----------|-----|
| Information Architecture | 4/10 | 9/10 | Dedicated quiz page, results page, gift flow |
| Interaction Design | 3/10 | 8/10 | 7-step quiz, auto-advance, emotional progression |
| Visual Design | 5/10 | 8/10 | Light-first, coral accent, soft corners |
| Responsive Design | 6/10 | 8/10 | Larger touch targets, quiz-responsive |
| Accessibility | 4/10 | 8/10 | WCAG 2.2, focus indicators, ARIA labels |
| Motion & Animation | 5/10 | 8/10 | Purposeful animations, staggered reveals |
| Content Strategy | 3/10 | 8/10 | Warm Brazilian tone, plain language |
| **OVERALL** | **3.6/10** | **8.1/10** | **+4.5 points** |

---

## Design System: "Warm Guide" v4.0

### Color Tokens

```css
:root {
  /* Base */
  --warm-white: #FAFAF8;
  --warm-cream: #F5F2EB;
  --warm-charcoal: #2A2A2A;

  /* Accent */
  --accent-coral: #F97316;
  --accent-coral-hover: #EA580C;
  --accent-lime: #84CC16;
  --accent-amber: #F59E0B;

  /* Trust */
  --trust-blue: #0EA5E9;
  --success-green: #22C55E;
  --error-red: #EF4444;

  /* Neutral */
  --gray-100: #F3F4F6;
  --gray-200: #E5E7EB;
  --gray-300: #D1D5DB;
  --gray-400: #9CA3AF;
  --gray-500: #6B7280;
  --gray-600: #4B5563;
  --gray-700: #374151;
  --gray-800: #1F2937;

  /* Skill Levels (retained) */
  --level-beginner: #22C55E;
  --level-intermediate: #F59E0B;
  --level-advanced: #EF4444;
}
```

### Typography Tokens

```css
:root {
  --font-display: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-data: 'JetBrains Mono', monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;

  --leading-tight: 1.25;
  --leading-normal: 1.6;
  --leading-relaxed: 1.75;
}
```

### Spacing Tokens

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
}
```

### Border Radius Tokens

```css
:root {
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;
}
```

### Motion Tokens

```css
:root {
  --duration-instant: 50ms;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  --ease-enter: cubic-bezier(0, 0, 0.2, 1);
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);
  --ease-move: cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Implementation Roadmap

### Phase 1: Design System Foundation
- Update DESIGN.md to v4.0 "Warm Guide"
- Update CSS variables in globals.css
- Update button components (coral CTA)
- Update card components (soft radius, warm shadows)

### Phase 2: Quiz Redesign
- Create 7-step quiz flow component
- Implement image-based selection cards
- Add budget slider
- Create animated progress indicator
- Create analyzing/loading state
- Create profile summary reveal
- Create /quiz/results page with 3 recommendations

### Phase 3: Homepage Redesign
- Quiz-first hero (light background)
- Trust signals section (retailer logos, stats)
- Featured paddles section
- "How it works" section
- Coral CTAs throughout

### Phase 4: Chat & Catalog
- Warmer chat tone
- "Why this matches you" in chat product cards
- Light catalog background
- Dark mode toggle
- Profile-aware recommendations in catalog

### Phase 5: Gift Buyer Flow
- Simplified 3-question gift quiz
- Gift-specific results page
- Gift section on homepage

### Phase 6: Accessibility & Polish
- WCAG 2.2 compliance audit
- ARIA labels for all quiz components
- Keyboard navigation
- Screen reader testing
- Focus indicators

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| 7-step quiz feels too long | Drop-off | Auto-advance removes friction; Noom has 40+ questions |
| Coral CTA underperforms lime | Lower conversions | A/B test; keep lime as data accent |
| Light mode feels less credible | Analytical users leave | Dark mode toggle for data screens; JetBrains Mono retained |
| Gift flow cannibalizes main quiz | Confusion | Clear entry points, separate tracking |

---

## Success Metrics

| Metric | Current | 30-day Target | 90-day Target |
|--------|---------|---------------|---------------|
| Quiz completion rate | ~60% | 75% | 85% |
| Results page -> affiliate click | ~3% | 5% | 7% |
| Time on quiz | ~30s | 2-3min | 2-3min |
| NPS | Unknown | 40 | 60 |

---

## Appendix A: Detailed Wireframes

### A1. Homepage (/) - Quiz-First Approach

```
┌─────────────────────────────────────────────────────────────┐
│  [PickleIQ Logo]              [Chat]  [Catalogo]    [Tema] │  ← Navbar (light, warm-white bg)
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                                                             │
│                      🎾                                     │
│                                                             │
│          Encontre a raquete perfeita                        │
│                para o SEU jogo                              │
│                                                             │
│     Responda 7 perguntas rapidas e receba                  │
│     recomendacoes personalizadas com os                    │
│     melhores precos do Brasil.                              │
│                                                             │
│            [ VAMOS LA → ]         ← Coral CTA, 8px radius  │
│                                                             │
│       ⭐ 4.9/5 · 500+ raquetes · 3 lojas                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  PRECOS MONITORADOS EM TEMPO REAL                          │
│                                                             │
│   [Brazil Store]  [Drop Shot]  [Mercado Livre]             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  RAQUETES EM DESTAQUE                                      │
│  [Ver todas →]                                             │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  [IMG]   │  │  [IMG]   │  │  [IMG]   │                 │
│  │          │  │          │  │          │                 │
│  │ Selkirk  │  │  Joola   │  │  Head    │                 │
│  │ Gamma    │  │ Ben Johns│  │ Extreme  │                 │
│  │          │  │          │  │          │                 │
│  │ R$ 689   │  │ R$ 549   │  │ R$ 899   │                 │
│  │ Iniciante│  │ Intermed.│  │ Avancado │                 │
│  │ [Ver →]  │  │ [Ver →]  │  │ [Ver →]  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  COMO FUNCIONA                                             │
│                                                             │
│  ① Responda o quiz      ② Receba recomendacoes            │
│     7 perguntas            personalizadas                  │
│                                                             │
│  ③ Compare precos        ④ Compre com confianca            │
│     em tempo real           nos melhores precos             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [PickleIQ] · Sobre · Blog · Contato                       │
│  Feito com 🎾 para jogadores brasileiros                   │
└─────────────────────────────────────────────────────────────┘
```

### A2. Quiz Flow (/quiz) - 7 Steps

**Step 1: Welcome Splash**
```
┌─────────────────────────────────────────────┐
│                                             │
│                                             │
│              🎾                              │
│                                             │
│     Vamos encontrar sua raquete             │
│          perfeita em 2 minutos              │
│                                             │
│  Responda algumas perguntas rapidas e      │
│  receba recomendacoes personalizadas       │
│  com os melhores precos do Brasil.         │
│                                             │
│         [ COMECAR → ]                       │
│                                             │
│  ~2 minutos · Sem cadastro necessario      │
│                                             │
└─────────────────────────────────────────────┘
```

**Step 2: Identity**
```
┌─────────────────────────────────────────────┐
│  ← Voltar                                   │
│                                             │
│  Vamos la!                     1 de 7       │
│  ──────────────────────────                │
│  Como voce se descreve como jogador?       │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  🎯  Estou comecando                 │   │  ← selected state:
│  │      Jogo por diversao e saude       │   │     coral border,
│  └─────────────────────────────────────┘   │     coral bg tint
│  ┌─────────────────────────────────────┐   │
│  │  ⚡  Jogo regularmente               │   │
│  │      Participo de jogos competitivos │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  🏆  Levo o jogo a serio             │   │
│  │      Treino e participo de torneios  │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ● ○ ○ ○ ○ ○ ○                             │
└─────────────────────────────────────────────┘
```

**Step 3: Play Style (Visual Cards)**
```
┌─────────────────────────────────────────────┐
│  ← Voltar                                   │
│                                             │
│  Ja sei quem voce e...         2 de 7       │
│  ──────────────────────────                │
│  O que voce mais valoriza no jogo?         │
│                                             │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐│
│  │  [PHOTO]  │ │  [PHOTO]  │ │  [PHOTO]  ││
│  │           │ │           │ │           ││
│  │ CONTROLE  │ │ POTENCIA  │ │EQUILIBRIO ││
│  │           │ │           │ │           ││
│  │ Precisao  │ │ Smashes   │ │ Melhor    ││
│  │ e toque   │ │ fortes    │ │ dos dois  ││
│  └───────────┘ └───────────┘ └───────────┘│
│                                             │
│  ○ ● ○ ○ ○ ○ ○                             │
└─────────────────────────────────────────────┘
```

**Step 4: Pain Points (Multi-select)**
```
┌─────────────────────────────────────────────┐
│  ← Voltar                                   │
│                                             │
│  Quase la!                      3 de 7      │
│  ──────────────────────────                │
│  O que te frustra na sua raquete atual?    │
│  (selecione todos que se aplicam)          │
│                                             │
│  ☑ Nao tem potencia suficiente             │
│  ☐ Erro muitos tiros na rede               │
│  ☑ Braço cansa depois de jogar             │
│  ☐ Nao consigo gerar spin                  │
│  ☐ E muito pesada                          │
│  ☐ Nao sei, nunca prestei atencao         │
│                                             │
│              [ PROXIMO → ]                  │
│                                             │
│  ○ ○ ○ ● ○ ○ ○                             │
└─────────────────────────────────────────────┘
```

**Step 5: Frequency**
```
┌─────────────────────────────────────────────┐
│  ← Voltar                                   │
│                                             │
│  Quase la!                      4 de 7      │
│  ──────────────────────────                │
│  Com que frequencia voce joga?             │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Uma vez por semana ou menos         │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  2-3 vezes por semana               │   │  ← selected
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  4+ vezes por semana                │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ○ ○ ○ ○ ● ○ ○                             │
└─────────────────────────────────────────────┘
```

**Step 6: Budget (Slider)**
```
┌─────────────────────────────────────────────┐
│  ← Voltar                                   │
│                                             │
│  So mais uma...                 5 de 7      │
│  ──────────────────────────                │
│  Quanto voce quer investir?                │
│                                             │
│  R$ 200 ━━━━━━━━━━━●━━━━━━ R$ 2.000       │
│                                             │
│           R$ 750                             │
│                                             │
│  💡 A maioria dos iniciantes encontra      │
│     otimas opcoes entre R$ 400-800         │
│                                             │
│  ○ ○ ○ ○ ○ ● ○                             │
└─────────────────────────────────────────────┘
```

**Step 7: Analyzing (Loading)**
```
┌─────────────────────────────────────────────┐
│                                             │
│                                             │
│           🎯 Analisando seu perfil...       │
│                                             │
│  ✓ Nivel de jogo identificado              │
│  ✓ Estilo de jogo mapeado                  │
│  ◐ Buscando raquetes compativeis...        │
│                                             │
│  ████████████████░░░░░░ 72%                │
│                                             │
│                                             │
│                                             │
└─────────────────────────────────────────────┘
```

### A3. Quiz Results (/quiz/results)

```
┌─────────────────────────────────────────────────────────────┐
│  ← Voltar ao quiz                    [REFAZER QUIZ]         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎉 SUAS RECOMENDACOES                                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SEU PERFIL                                          │   │
│  │                                                      │   │
│  │  Tipo: Intermediario Casual                          │   │
│  │  Estilo: Equilibrado                                 │   │
│  │  Prioridade: Precisao + conforto                     │   │
│  │  Orcamento: Ate R$ 750                               │   │
│  │                                                      │   │
│  │  Encontramos 3 raquetes perfeitas para voce.        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ⭐ MELHOR COMBINACAO GERAL                          │   │
│  │                                                      │   │
│  │  [IMG]   Selkirk Gamma 1.0                          │   │
│  │          R$ 689 · Brazil Store                      │   │
│  │          ✓ Em estoque · Atualizado hoje             │   │
│  │                                                      │   │
│  │  POR QUE PRA VOCE:                                   │   │
│  │  ✓ Equilibrado para seu estilo de jogo              │   │
│  │  ✓ Preco dentro do seu orcamento                    │   │
│  │  ✓ Ideal para quem joga 2-3x/semana                 │   │
│  │                                                      │   │
│  │  [VER NO SITE →]                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  💰 MELHOR CUSTO-BENEFICIO                           │   │
│  │                                                      │   │
│  │  [IMG]   Joola Ben Johns                             │   │
│  │          R$ 549 · Drop Shot                          │   │
│  │          ✓ Em estoque                                │   │
│  │                                                      │   │
│  │  POR QUE PRA VOCE:                                   │   │
│  │  ✓ Melhor preco para specs similares                │   │
│  │  ✓ Confiavel para intermediarios                    │   │
│  │                                                      │   │
│  │  [VER NO SITE →]                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🎯 MELHOR PARA EVOLUIR                              │   │
│  │                                                      │   │
│  │  [IMG]   Selkirk INVICTUS                            │   │
│  │          R$ 749 · Brazil Store                      │   │
│  │          ⚠ Ultimas unidades                          │   │
│  │                                                      │   │
│  │  POR QUE PRA VOCE:                                   │   │
│  │  ✓ Evolui com voce (bom para subir de nivel)       │   │
│  │  ✓ T700 carbon face                                 │   │
│  │                                                      │   │
│  │  [VER NO SITE →]                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Quer mais opcoes?                                  │   │
│  │  [FALAR COM NOSSA IA →]    [VER CATALOGO →]         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### A4. Chat Interface (/chat) - Enhanced

```
┌─────────────────────────────────────────────────────────────┐
│  [PickleIQ]     Chat com a IA    [Perfil: Intermediário]   │  ← Dark navbar
├──────────────────────────────┬──────────────────────────────┤
│                              │                              │
│  🤖 PickleIQ                 │  SEU PERFIL                 │
│                              │                              │
│  Ola! Vejo que voce e um     │  Nivel: Intermediario       │
│  jogador intermediario que   │  Estilo: Equilibrado        │
│  valoriza equilibrio. Posso  │  Orcamento: Ate R$750       │
│  te ajudar! O que procura?   │                              │
│                              │  Suas recomendacoes:         │
│                              │  1. Selkirk Gamma R$689     │
│  ─────────────────────       │  2. Joola Ben Johns R$549   │
│                              │  3. Selkirk INVICTUS R$749  │
│  👤 Voce                    │                              │
│                              │  [VER DETALHES →]           │
│  Quero uma raquete com bom   │                              │
│  spin, ate R$800             │                              │
│                              │                              │
│  ─────────────────────       │                              │
│                              │                              │
│  🤖 PickleIQ                 │                              │
│                              │                              │
│  Para spin com ate R$800,    │                              │
│  recomendo estas opcoes:     │                              │
│                              │                              │
│  ┌─────────────────────────┐ │                              │
│  │ [IMG] Selkirk Vanguard   │ │                              │
│  │ R$ 749 · Brazil Store    │ │                              │
│  │ Spin: ★★★★☆             │ │                              │
│  │ Por que: Face texturizada│ │                              │
│  │ gera mais spin, ideal    │ │                              │
│  │ para seu estilo equil.   │ │                              │
│  │ [VER NO SITE →]          │ │                              │
│  └─────────────────────────┘ │                              │
│                              │                              │
├──────────────────────────────┴──────────────────────────────┤
│  [Digite sua pergunta...                        ] [Enviar] │
└─────────────────────────────────────────────────────────────┘
```

### A5. Product Catalog (/paddles) - Enhanced

```
┌─────────────────────────────────────────────────────────────┐
│  [PickleIQ]              [Chat]  [Catalogo]    [Tema]      │
├─────────────────────────────────────────────────────────────┤
│  CATALOGO DE RAQUETES                                       │
│  Encontre a raquete ideal entre 500+ opcoes                │
│                                                             │
│  [Todos] [Iniciante] [Intermediario] [Avancado]  ← Pills   │
│                                                             │
│  Ordenar: [Relevancia ▼]    Preco: [R$0 - R$2000]          │
│                                                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐             │
│  │   [IMG]    │ │   [IMG]    │ │   [IMG]    │             │
│  │            │ │            │ │            │             │
│  │ Selkirk    │ │ Joola      │ │ Head       │             │
│  │ Gamma 1.0  │ │ Ben Johns  │ │ Extreme    │             │
│  │            │ │            │ │            │             │
│  │ R$ 689     │ │ R$ 549     │ │ R$ 899     │             │
│  │            │ │            │ │            │             │
│  │ [Inic.]    │ │ [Interm.]  │ │ [Avanc.]   │             │
│  │            │ │ ⭐ Para vc │ │            │             │
│  │ [+Comparar]│ │ [+Comparar]│ │ [+Comparar]│             │
│  └────────────┘ └────────────┘ └────────────┘             │
│                                                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐             │
│  │   [IMG]    │ │   [IMG]    │ │   [IMG]    │             │
│  │  ...       │ │  ...       │ │  ...       │             │
│  └────────────┘ └────────────┘ └────────────┘             │
│                                                             │
│  [Carregar mais...]                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix B: Component Specification

### B1. Button Component

```tsx
// Primary CTA - Coral
<button className="
  bg-coral-500 hover:bg-coral-600
  text-white font-semibold
  px-6 py-3 rounded-lg
  transition-all duration-150
  hover:scale-[1.02]
  hover:shadow-lg hover:shadow-coral-500/24
  active:scale-[0.98]
  focus:outline-none focus:ring-2 focus:ring-coral-500 focus:ring-offset-2
">
  Vamos la →
</button>

// Secondary - Outline Coral
<button className="
  border-2 border-coral-500 text-coral-500
  font-semibold px-6 py-3 rounded-lg
  hover:bg-coral-50
  transition-all duration-150
">
  Ver catalogo
</button>

// Tertiary - Ghost
<button className="
  text-gray-500 hover:text-coral-500
  font-medium px-4 py-2
  transition-colors duration-150
">
  ← Voltar
</button>
```

### B2. Quiz Card Component

```tsx
<div className={`
  w-full p-5 rounded-xl border-2 cursor-pointer
  transition-all duration-200
  ${selected
    ? 'border-coral-500 bg-coral-50 shadow-md'
    : 'border-gray-200 hover:border-coral-300 hover:bg-gray-50'
  }
`}>
  <div className="flex items-center gap-4">
    <div className="w-12 h-12 rounded-lg bg-coral-100 flex items-center justify-center text-xl">
      {icon}
    </div>
    <div className="flex-1">
      <div className="font-semibold text-warm-charcoal">{label}</div>
      <div className="text-sm text-gray-500">{description}</div>
    </div>
    {selected && (
      <div className="w-6 h-6 rounded-full bg-coral-500 flex items-center justify-center">
        <CheckIcon className="w-4 h-4 text-white" />
      </div>
    )}
  </div>
</div>
```

### B3. Recommendation Card Component

```tsx
<div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm
            hover:shadow-md transition-shadow duration-200">
  {/* Badge */}
  <div className="flex items-center gap-2 mb-4">
    <span className="text-sm font-bold">{badgeIcon} {badgeLabel}</span>
  </div>

  {/* Product */}
  <div className="flex gap-5">
    <div className="w-[140px] h-[200px] rounded-lg overflow-hidden bg-gray-100">
      <SafeImage src={paddle.image_url} alt={paddle.name} />
    </div>
    <div className="flex-1">
      <p className="text-xs font-bold uppercase tracking-wider text-lime-600 mb-1">
        {paddle.brand}
      </p>
      <h3 className="text-xl font-bold text-warm-charcoal">{paddle.name}</h3>
      <p className="text-2xl font-bold text-coral-500 mt-1">
        R$ {paddle.price_min_brl}
      </p>
      <div className="flex items-center gap-2 mt-2 text-sm text-gray-500">
        <span>✓ Em estoque</span>
        <span>·</span>
        <span>Atualizado hoje</span>
      </div>
    </div>
  </div>

  {/* Why This Matches You */}
  <div className="mt-4 p-3 bg-lime-50 rounded-lg border border-lime-200">
    <p className="text-xs font-bold uppercase tracking-wider text-lime-700 mb-2">
      Por que pra voce:
    </p>
    <ul className="space-y-1">
      {reasons.map(r => (
        <li className="text-sm text-gray-700 flex items-start gap-2">
          <span className="text-lime-500 mt-0.5">✓</span> {r}
        </li>
      ))}
    </ul>
  </div>

  {/* CTA */}
  <button className="w-full mt-4 bg-coral-500 hover:bg-coral-600
                     text-white font-semibold py-3 rounded-lg
                     transition-all duration-150 hover:scale-[1.02]">
    Ver no site →
  </button>
</div>
```

### B4. Profile Summary Component

```tsx
<div className="bg-gradient-to-br from-coral-500 to-coral-600
            rounded-2xl p-6 text-white">
  <h2 className="text-2xl font-bold mb-4">🎉 Seu Perfil de Jogador</h2>
  <div className="grid grid-cols-2 gap-4">
    <div>
      <p className="text-coral-100 text-sm">Tipo</p>
      <p className="font-semibold">{profile.typeLabel}</p>
    </div>
    <div>
      <p className="text-coral-100 text-sm">Estilo</p>
      <p className="font-semibold">{profile.styleLabel}</p>
    </div>
    <div>
      <p className="text-coral-100 text-sm">Prioridade</p>
      <p className="font-semibold">{profile.priorityLabel}</p>
    </div>
    <div>
      <p className="text-coral-100 text-sm">Orcamento</p>
      <p className="font-semibold">Ate R$ {profile.budget_max}</p>
    </div>
  </div>
  <p className="mt-4 text-coral-100 text-sm">
    Encontramos 3 raquetes perfeitas para voce.
  </p>
</div>
```

---

## Appendix C: Dark Mode Tokens

```css
@media (prefers-color-scheme: dark) {
  :root {
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
}
```

Dark mode is available via toggle but NOT the default. Light mode is the primary experience for the warm, approachable feel. Dark mode is recommended for:
- Chat interface (retains current dark aesthetic)
- Data-heavy comparison tables
- Admin dashboard
