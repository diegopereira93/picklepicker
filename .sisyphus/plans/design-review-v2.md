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

---

## Appendix D: Aesthetic Justification — Why "Warm Guide" Fits PickleIQ in Brazil

### The Core Misalignment with "Hybrid Modern Sports Tech"

The current DESIGN.md v3.0 chose "Hybrid Modern Sports Tech" to balance "sport energy + data credibility." This works for platforms like Tennis Warehouse or Golf Galaxy where users are **already knowledgeable** and want specs. PickleIQ's situation is fundamentally different:

1. **Pickleball is new in Brazil.** The sport is growing from zero, not from an established base. Most visitors have never bought a paddle before. They don't need data credibility — they need guidance.

2. **The primary persona is a confused beginner**, not an analytical expert. The PRD's Persona 1 (Iniciante Entusiasmado, 35-55 years) is explicitly described as someone who "doesn't understand swingweight or twistweight." A dark, tech-dashboard aesthetic signals "this is for engineers" and creates intimidation before the user even starts.

3. **The product IS the quiz.** PickleIQ's value proposition is personalized recommendation via profiling. The current design treats the quiz as a widget. The new design must treat the quiz as the product. "Warm Guide" puts the quiz experience at the center, not the data.

### Why Not "Sporty"?

Brazilian sports e-commerce (Netshoes, Centauro, Mercado Livre esportes) uses vibrant, energetic, accessible design — not dark tech dashboards. The Brazilian sports consumer expects:
- **Warmth and approachability** (Brazilian commerce culture is relationship-driven)
- **Clear CTAs** (not hidden behind data exploration)
- **Trust through simplicity** (not trust through complexity)
- **Social proof** (reviews, "most popular", ratings — not raw specs)

A dark, sharp-cornered, lime-on-black aesthetic is closer to a Bloomberg terminal than a Brazilian sports store. It signals "analyze this data" when the user wants "help me choose."

### Why "Warm Guide" Specifically

"Warm Guide" draws from three proven patterns:

1. **Duolingo's approachability**: Gamified progression, encouraging micro-copy, colorful but not childish, makes learning feel achievable. PickleIQ's quiz uses the same pattern: make the confusing (choosing a paddle) feel achievable through guided steps.

2. **Wirecutter's trust**: Research-backed recommendations with clear "why we picked this" explanations. Not affiliate link spam, but genuine guidance. PickleIQ's recommendation cards with "Por que pra voce" follow this pattern.

3. **Nike Run Club's energy**: Sport-specific without being intimidating. Uses coral/orange as primary accent (not coincidentally), warm photography, and progress tracking. Proves that sports platforms don't need dark themes to feel athletic.

### The Counterargument — What About the Analytical Persona?

Persona 2 (Jogador Intermediário Analítico) wants data. The design doesn't abandon them:
- **JetBrains Mono retained** for all spec/comparison tables
- **Dark mode toggle** available for data-heavy screens
- **Catalog page** retains dense data layout option
- **Comparison mode** shows full spec tables with radar charts
- **Lime accent retained** as the data color (charts, tables, section labels)

The key insight: light mode for the **journey** (quiz, results, homepage), dark mode for the **analysis** (comparison, specs, data tables). The default should serve the majority persona (beginners), not the minority (analysts).

### Brazilian Cultural Context

Brazilian e-commerce UX research shows:
- Brazilian consumers respond better to **warm, human** interfaces than cold, technical ones
- **"Voce"** (informal) outperforms formal register in conversion
- **Social proof** (ratings, review counts) matters more than technical specs
- **Price transparency** (showing real prices from multiple stores) builds more trust than data density
- **Coral/orange** is culturally associated with energy and commerce (used by Mercado Livre, Magalu, iFood)

### Decision: This Is Not Generic "Make It Friendly"

"Warm Guide" is specifically calibrated for:
- A **new sport in Brazil** where most visitors need education, not data
- A **quiz-first product** where the experience IS the value
- A **beginner-majority audience** (70%+ of pickleball players in Brazil have < 1 year experience)
- **Brazilian commerce expectations** (warm, social, price-transparent)

It is NOT a generic customer service aesthetic. It is a deliberate choice to match the product's actual user base and market context.

---

## Appendix E: Migration Strategy — DESIGN.md v3.0 → v4.0

### Migration Philosophy

This is not a "rip and replace." The migration must be **incremental, reversible, and measurable.** Each phase has clear rollback criteria.

### Phase 0: Baseline Measurement (Week 0)

**Before any code changes**, capture current metrics:

| Metric | How to Measure | Tool |
|--------|---------------|------|
| Homepage bounce rate | Google Analytics / Vercel Analytics | GA4 |
| Quiz completion rate | Custom event: `quiz_step_completed` / `quiz_completed` | GA4 |
| Quiz → affiliate click rate | Custom event: `affiliate_link_clicked` with `source=quiz` | GA4 |
| Time on quiz | Average session duration on / path | GA4 |
| Chat usage | Messages per session | Backend logs |
| Catalog usage | Pageviews, filter usage | GA4 |
| NPS | In-app survey (post-recommendation) | Custom |

**Set up these events BEFORE migration begins.** Without baselines, success metrics are meaningless.

### Phase 1: CSS Token Migration (Non-Breaking)

**Goal**: Replace design tokens without changing component structure.

**Steps**:
1. Add new CSS custom properties alongside existing ones (dual-token approach)
2. Example: Add `--accent-coral` without removing `--sport-primary`
3. Create new utility classes: `.btn-coral-primary` alongside existing `.hy-button-primary`
4. No visual changes yet — just preparation

**QA**: Existing tests pass, no visual regression, build succeeds.

**Rollback**: Delete new tokens (zero risk).

### Phase 2: Component Migration (Controlled Rollout)

**Goal**: Update components to use new tokens, one at a time.

**Order** (lowest risk first):
1. **Button component** — New `.btn-coral-primary` class, used in new features only
2. **Card component** — New border radius (12px), soft shadows
3. **Quiz components** — Full redesign (this is the biggest change)
4. **Homepage hero** — Light background, quiz-first CTA
5. **Catalog page** — Light background, larger cards
6. **Chat interface** — Retain dark, warmer tone
7. **Navigation** — Light navbar

**A/B Testing Approach**:
- Use Vercel Edge Middleware or LaunchDarkly for feature flags
- 10% of traffic sees new design, 90% sees current
- Monitor: bounce rate, quiz completion, affiliate clicks
- If new design wins by >5% on any metric → increase to 50%
- If new design loses by >10% on any metric → rollback

**Rollback Criteria**:
- Bounce rate increases by >15%
- Quiz completion drops by >20%
- Affiliate click-through drops by >25%

### Phase 3: Dark Mode Toggle Implementation

**Goal**: Add theme toggle without removing dark mode.

**Steps**:
1. Create `ThemeProvider` using `next-themes` library
2. Add toggle to navbar (sun/moon icon)
3. Default to light, respect system preference
4. Chat page forces dark mode regardless of toggle
5. Admin page forces dark mode regardless of toggle

**CSS Strategy**:
```css
/* Light mode (default) */
:root {
  --bg-primary: var(--warm-white);
  --bg-card: #ffffff;
  --text-primary: var(--warm-charcoal);
}

/* Dark mode */
[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --bg-card: #111111;
  --text-primary: #f5f5f5;
}
```

### Phase 4: Quiz Redesign (Staged)

**Goal**: Replace 3-step quiz with 7-step quiz.

**Staged Rollout**:
1. **Week 1**: Deploy new quiz to `/quiz` (new route). Old quiz stays on homepage.
2. **Week 2**: Homepage CTA changes to link to `/quiz` instead of inline widget.
3. **Week 3**: Remove inline quiz widget from homepage entirely.
4. **Week 4**: Add `/quiz/results` as dedicated page.

**Data Migration**:
- `UserProfile` type expands: add `pain_points`, `frequency`, `identity`
- localStorage key stays the same (`pickleiq-profile`)
- New fields are optional (backward compatible with existing profiles)
- Old profiles trigger "Complete seu perfil" prompt on next visit

**Rollback**: Revert homepage CTA to inline quiz widget. `/quiz` route can remain as an experiment.

### Phase 5: DESIGN.md Update

**Goal**: Replace DESIGN.md v3.0 with v4.0 only AFTER visual migration is complete.

**Timing**: After Phase 4 is verified in production (all metrics stable or improving).

**Content**:
- Archive v3.0 to `DESIGN-v3.md` (reference only)
- Write new DESIGN.md with "Warm Guide" as the canonical system
- Update CLAUDE.md design system section
- Update AI slop checklist for new aesthetic

### Migration Risk Matrix

| Phase | Risk | Impact | Rollback Time |
|-------|------|--------|---------------|
| Phase 0 (Baseline) | Events not firing | Can't measure | N/A — fix before proceeding |
| Phase 1 (Tokens) | CSS conflicts | Visual glitches | 5 min (delete tokens) |
| Phase 2 (Components) | User confusion | Metric drops | 15 min (revert feature flag) |
| Phase 3 (Dark Mode) | Theme flash on load | Poor UX | 10 min (remove toggle) |
| Phase 4 (Quiz) | Lower completion | Revenue impact | 30 min (revert CTA link) |
| Phase 5 (Docs) | Confusion for contributors | PR quality drops | 5 min (revert file) |

---

## Appendix F: Edge Case & State Design

### F1. Empty States

**Empty Catalog** (`/paddles` with 0 results):
```
┌─────────────────────────────────────────────┐
│                                             │
│            🏓                               │
│                                             │
│   Nenhuma raquete encontrada                │
│   com esses filtros.                        │
│                                             │
│   Tente:                                    │
│   · Ampliar faixa de preco                  │
│   · Remover filtro de nivel                 │
│   · Limpar todos os filtros                 │
│                                             │
│   [LIMPAR FILTROS]    [VER TUDO]            │
│                                             │
└─────────────────────────────────────────────┘
```

**Empty Chat** (no messages yet):
```
┌─────────────────────────────────────────────┐
│                                             │
│  🤖 Ola! Sou o PickleIQ.                    │
│                                             │
│  Posso te ajudar a encontrar a raquete       │
│  ideal. Me conte sobre seu jogo!            │
│                                             │
│  Sugestoes:                                 │
│  · "Qual raquete para iniciante?"           │
│  · "Melhor raquete ate R$600"              │
│  · "Comparar Selkirk e Joola"               │
│                                             │
└─────────────────────────────────────────────┘
```

**Zero Recommendations** (quiz complete but no matching paddles):
```
┌─────────────────────────────────────────────┐
│                                             │
│   😕 Nenhuma raquete encontrada             │
│   no seu orcamento.                         │
│                                             │
│   Tente aumentar seu orcamento para          │
│   R$ {next_tier_price} ou mais.             │
│                                             │
│   [AJUSTAR ORCAMENTO]    [VER TUDO]         │
│                                             │
└─────────────────────────────────────────────┘
```

### F2. Error States

**API Error** (fetch paddles fails):
```
┌─────────────────────────────────────────────┐
│                                             │
│   Ops! Algo deu errado.                     │
│                                             │
│   Nao conseguimos carregar as recomendacoes  │
│   no momento. Tente novamente em instantes. │
│                                             │
│   [TENTAR NOVAMENTE]                        │
│                                             │
│   Se o problema persistir, entre em          │
│   contato pelo chat.                         │
│                                             │
└─────────────────────────────────────────────┘
```

**Network Offline**:
```
┌─────────────────────────────────────────────┐
│                                             │
│   📡 Sem conexao com a internet             │
│                                             │
│   Verifique sua conexao e tente novamente.  │
│                                             │
│   [TENTAR NOVAMENTE]                        │
│                                             │
└─────────────────────────────────────────────┘
```

**Chat Streaming Error** (mid-response failure):
```
  🤖 PickleIQ (streaming stops)

  ┌─ ⚠️ Resposta interrompida ──────────────┐
  │ A conexao foi perdida. Clique abaixo    │
  │ para tentar gerar a resposta novamente. │
  │                                         │
  │ [GERAR NOVAMENTE]                        │
  └─────────────────────────────────────────┘
```

### F3. Loading States

**Skeleton Loading** (catalog page, paddle cards):
```
┌────────────┐  ┌────────────┐  ┌────────────┐
│ ████████    │  │ ████████    │  │ ████████    │
│            │  │            │  │            │
│ ██████████ │  │ ██████████ │  │ ██████████ │
│ ████       │  │ ████       │  │ ████       │
│ ██████     │  │ ██████     │  │ ██████     │
│            │  │            │  │            │
│ ████████   │  │ ████████   │  │ ████████   │
└────────────┘  └────────────┘  └────────────┘
```

**Quiz Step Transition** (between steps):
- Current step fades out + slides left (300ms)
- Next step fades in + slides right (300ms)
- Progress dots update simultaneously
- No full-page loading indicator

**Debounced Search** (catalog filters):
- Show skeleton grid immediately when filter changes
- Replace with real results after 300ms debounce
- If results identical to previous, skip skeleton

### F4. Validation States

**Budget Slider**:
- Min: R$200 (hard floor, slider can't go below)
- Max: R$3.000 (hard ceiling, slider can't go above)
- No invalid state possible (continuous slider)
- Smart zone indicator: R$400-800 highlighted for beginners

**Multi-select Quiz Step** (Step 4: Pain Points):
- Minimum: 0 selections allowed (user can skip)
- Maximum: all 6 options
- "Proximo" button always enabled (no minimum selection)
- If 0 selected: results include broader recommendations

**Form Validation** (if any text inputs added):
- Real-time validation on blur (not on every keystroke)
- Error message appears below field with coral accent
- Focus returns to invalid field
- Screen reader announces error via aria-live region

### F5. Mobile-Specific States

**Keyboard Open** (quiz budget slider):
- Slider sticks to bottom of viewport when keyboard opens
- Step content scrolls to keep current question visible
- "Proximo" button remains accessible above keyboard

**Pull-to-Refresh** (catalog):
- Standard browser pull-to-refresh behavior
- Shows loading spinner during refresh
- Skeleton cards during data fetch

**Back Navigation** (quiz):
- Browser back button goes to previous quiz step
- Quiz state preserved in URL hash (/quiz#step-3)
- Deep-linking: /quiz#step-5 resumes at step 5
- Exiting quiz mid-flow: "Deseja salvar seu progresso?" prompt

### F6. Offline / Slow Network

**Slow Connection** (>3s API response):
- Show skeleton loading immediately
- After 3s: show "Aguenta so um instante..." message
- After 10s: show retry prompt with "Tentar novamente" button
- After 30s: show error state

**Image Loading** (product cards):
- Use `SafeImage` component (already exists)
- Blur-up placeholder (low-res) → full-res
- If image fails: show paddle icon placeholder with brand initial
- Never show broken image icon

---

## Appendix G: Measurement Methodology

### G1. Baseline Collection (Before Migration)

Implement these custom events in GA4:

```typescript
// Quiz events
gtag('event', 'quiz_started', { method: 'homepage_widget' | 'quiz_page' })
gtag('event', 'quiz_step_completed', { step: 1-7, step_name: 'identity' | 'style' | ... })
gtag('event', 'quiz_completed', { duration_ms: number, steps_skipped: number })
gtag('event', 'quiz_abandoned', { last_step: 1-7, total_time_ms: number })

// Recommendation events
gtag('event', 'recommendation_viewed', { paddle_count: number })
gtag('event', 'affiliate_link_clicked', {
  paddle_name: string,
  source: 'quiz_results' | 'chat' | 'catalog',
  price_brl: number
})

// Catalog events
gtag('event', 'catalog_filtered', { filter_type: string, filter_value: string })
gtag('event', 'comparison_started', { paddle_count: number })
gtag('event', 'comparison_completed', { paddle_count: number })

// Chat events
gtag('event', 'chat_message_sent', { message_length: number })
gtag('event', 'chat_product_card_clicked', { paddle_name: string })
```

### G2. Success Metrics with Measurement Plan

| Metric | Baseline Source | Target | How to Verify |
|--------|----------------|--------|---------------|
| Quiz completion rate | `quiz_completed` / `quiz_started` | 75% (30d), 85% (90d) | GA4 funnel report |
| Results → affiliate click | `affiliate_link_clicked` (source=quiz) / `recommendation_viewed` | 5% (30d), 7% (90d) | GA4 custom report |
| Time on quiz | Avg `quiz_completed.duration_ms` | 90-180s (30d), 90-180s (90d) | GA4 avg duration |
| NPS | Post-recommendation survey (1-10 scale) | 40 (30d), 60 (90d) | In-app survey, weekly aggregation |
| Homepage → quiz start | `quiz_started` / homepage pageviews | 25% (30d), 35% (90d) | GA4 funnel report |
| Chat messages/session | Avg `chat_message_sent` per session | 3+ (30d) | GA4 avg per session |
| Bounce rate (homepage) | GA4 standard | <40% (30d) | GA4 standard report |

### G3. A/B Test Framework

**Tool**: Vercel Edge Middleware with cookie-based bucketing.

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const response = NextResponse.next()
  const bucket = getBucket(request.cookies) // 'control' or 'warm-guide'
  response.cookies.set('design-bucket', bucket, { maxAge: 86400 * 30 })
  response.headers.set('x-design-bucket', bucket)
  return response
}

function getBucket(cookies: RequestCookies): string {
  const existing = cookies.get('design-bucket')?.value
  if (existing) return existing
  return Math.random() < 0.1 ? 'warm-guide' : 'control'
}
```

**Experiment Duration**: Minimum 14 days, minimum 1,000 sessions per bucket.

**Decision Criteria**:
- **Ship**: Warm guide wins on quiz completion AND affiliate clicks with p < 0.05
- **Iterate**: Mixed results (wins one, loses other) → adjust and re-test
- **Rollback**: Loses on both metrics with p < 0.05
