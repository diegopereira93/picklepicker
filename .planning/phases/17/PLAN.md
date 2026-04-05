# Phase 17: Home-C Quiz-Forward

**Status:** Ready for execution
**Milestone:** v1.6.0 — UI Redesign
**Dependencies:** Phase 16 (DESIGN.md v3.0 + globals.css tokens) — COMPLETE
**Created:** 2026-04-05
**Updated:** 2026-04-05

## Goal

Redesign the homepage with an interactive quiz widget above-the-fold that captures user intent immediately, shows a recommendation card preview, and provides data credibility signals.

## Context

**Design Review Source:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/`
**Approved Variant:** Home-C (Quiz-Forward) — score 8/10, conversion effectiveness 9/10
**HTML Mockup:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/variant-home-C.html`
**Screenshot:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/screenshot-home-C.png`

**Hybrid Enhancement:** Home-C base + data credibility stats from Home-A below the quiz section.

```
[Navbar: Black, sticky]
[Hero Quiz Section: Dark #000]
  H1: "Encontre a raquete ideal para o seu jogo" (lime underline on "ideal")
  Subtitle: "Responda 2 perguntas e receba uma recomendacao personalizada"
  [Quiz widget with pill toggles — Nivel + Orcamento + Estilo]
  [Recommendation card preview (appears after quiz completion)]
  "Comecar Quiz →" CTA button
[Data Credibility Section: Dark #1a1a1a]
  3 stat cards: "147 raquetes analisadas" / "3 varejistas monitorados" / "Precos atualizados diariamente"
[How It Works: Light #ffffff]
  Numbered steps 1-2-3 with connecting lines
[Footer: Black]
```

**Current State (v1.4.0):**
- Homepage (`frontend/src/app/page.tsx`) is a marketing page: hero with H1 + subheading → 3-column value props (AI slop pattern) → CTA banner
- Quiz flow exists at `/chat` as a gate (`frontend/src/components/quiz/quiz-flow.tsx`) — card-based 3-step flow (level → style → budget)
- Profile stored in localStorage via `frontend/src/lib/profile.ts` (`getProfile`, `saveProfile`)
- `UserProfile` type: `{ level: string, style: string, budget_max: number }`
- DESIGN.md v3.0 already documents quiz pill toggles, progress indicators, card response patterns
- `globals.css` has `.hy-quiz-pill`, `.hy-quiz-pill.selected`, `.hy-progress-dot`, `.hy-animate-quiz-ripple` classes ready
- Backend `/api/v1/paddles` supports `price_min`, `price_max`, `limit`, `offset` filters. `Paddle` type has `skill_level` field but no backend filter for it.
- `SafeImage` component in `frontend/src/components/ui/safe-image.tsx` handles image loading (Phase 14)

**Root Causes (from ROADMAP.md):**

1. **Generic hero with 3-column feature grid** — Current homepage has an AI slop pattern (3-col value props). No interactivity above-the-fold.
2. **Quiz CTA buried below fold** — Users must scroll past hero + feature cards to see "Começar agora" button. Intent capture is delayed.
3. **No data credibility signals** — Analytical users don't see platform depth immediately. "Why should I trust your recommendations?"

### Quiz Specification (3 Selections)

The homepage quiz widget asks exactly 3 questions. Each uses pill toggle buttons (single-select within group):

| # | Label | Options (value → label) | Maps to `UserProfile` field |
|---|-------|------------------------|------------------------------|
| 1 | SEU NÍVEL | `beginner` → "Iniciante", `intermediate` → "Intermediario", `advanced` → "Avancado" | `level: string` |
| 2 | SEU ORÇAMENTO | `300` → "Ate R$300", `600` → "R$300-600", `9999` → "Acima R$600" | `budget_max: number` |
| 3 | ESTILO DE JOGO | `control` → "Controle", `power` → "Potencia", `balanced` → "Equilibrado" | `style: string` |

These match the existing quiz at `/chat` (quiz-flow.tsx) but are presented as inline pill toggles instead of card-based steps.

### Recommendation Data Source

The RecommendationCard uses **real API data** (NOT mocked). Flow:
1. User completes 3 quiz selections → `handleQuizComplete(profile)` called
2. Profile saved to localStorage via `saveProfile(profile)` from `@/lib/profile`
3. `fetchMatchingPaddle(profile)` calls `fetchPaddles({ price_max: profile.budget_max, limit: 50 })` from `@/lib/api`
4. Client-side filter: `result.items.filter(p => p.skill_level === profile.level || !p.skill_level)`
5. First matching paddle shown in RecommendationCard

**Paddle data interface** (from `frontend/src/types/paddle.ts`):
```typescript
interface Paddle {
  id: number
  name: string          // "Selkirk Vanguard Power Air"
  brand: string        // "Selkirk"
  model_slug: string   // "vanguard-power-air" (for deep link)
  image_url?: string   // retailer CDN image (rendered via SafeImage)
  price_min_brl?: number // 899 (displayed as "R$ 899")
  skill_level?: string // "intermediate" (for filtering)
  specs?: {
    weight_oz?: number     // 7.8
    face_material?: string // "Graphite"
    core_thickness_mm?: number // 16
  }
}
```

### State Flow

```
Page Load
  └── useEffect → getProfile()
      ├── null (new visitor) → show QuizWidget
      └── UserProfile (returning) → setIsReturning(true), fetchMatchingPaddle(profile)

QuizWidget.onComplete(profile)
  └── handleQuizComplete(profile)
      ├── saveProfile(profile) → localStorage
      ├── setQuizProfile(profile) → state update
      ├── setQuizComplete(true) → state update
      └── fetchMatchingPaddle(profile)
          ├── setIsLoading(true)
          ├── fetchPaddles({ price_max, limit: 50 })
          ├── filter by skill_level
          ├── setRecommendation(matching[0]) → RecommendationCard renders
          └── setIsLoading(false)

CTA Button
  ├── Before quiz: "Começar Quiz →" → scroll to quiz
  └── After quiz: "Ver recomendacoes no chat →" → Link to /chat
```

### Prerequisite Files (verified to exist)

| File | Purpose | Status |
|------|---------|--------|
| `frontend/src/lib/profile.ts` | `getProfile()`, `saveProfile()` for localStorage | ✅ Exists |
| `frontend/src/types/paddle.ts` | `UserProfile`, `Paddle` TypeScript interfaces | ✅ Exists |
| `frontend/src/lib/api.ts` | `fetchPaddles()` API client | ✅ Exists |
| `frontend/src/components/ui/safe-image.tsx` | `SafeImage` for retailer CDN images | ✅ Exists |
| `frontend/src/app/globals.css` | `.hy-quiz-pill`, `.hy-quiz-pill.selected`, `.hy-animate-quiz-ripple` | ✅ Exists (Phase 16) |
| `DESIGN.md` | v3.0 design system with Interactive Widgets section | ✅ Exists (Phase 16) |

## Requirements Coverage

| Requirement | Tasks | Notes |
|-------------|-------|-------|
| HOME-01 | 17.1, 17.2 | Quiz widget above-the-fold with pill toggles + CTA |
| HOME-02 | 17.2 | RecommendationCard component with paddle preview |
| HOME-03 | 17.3 | Data credibility stats section (JetBrains Mono, data-green) |
| HOME-04 | 17.4 | Feature steps section (numbered 1-2-3 with connecting lines) |
| HOME-05 | 17.5 | Returning visitor logic (localStorage) |

## Execution Waves

```
Wave 0 (pre-check — verify dependencies):
└── Verify all prerequisite files exist (see Context: Prerequisite Files table)

Wave 1 (parallel — no dependencies):
├── 17.2: QuizWidget + RecommendationCard components (new files in components/quiz/)
├── 17.3: DataStatsSection component (new file or inline)
└── 17.4: FeatureSteps component (new file or inline)

Wave 2 (after Wave 1 — depends on QuizWidget + RecommendationCard):
└── 17.1: Redesign page.tsx hero section (assembles all Wave 1 components)

Wave 3 (after Wave 2 — depends on full page structure):
└── 17.5: Returning visitor logic (localStorage check, alternative content)

Wave 4 (after all — verification):
└── 17.6: Visual QA + responsive verification
```

---

## Task Details

### Task 17.1 — Redesign Homepage Hero Section

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/app/page.tsx`
**Dependencies:** Wave 1 complete (17.2, 17.3, 17.4 components must exist)
**Requirements:** HOME-01

**Changes:**

1. **Replace the entire current page.tsx** with the new Home-C layout. Remove the old hero, 3-column value props, and CTA banner. New structure:

```
<section className="hy-dark-section hy-section-hero">
  <div className="hy-container">
    {/* H1 with lime underline */}
    <h1 className="hy-display">Encontre a raquete <span className="lime-underline">ideal</span> para o seu jogo</h1>
    <p className="hy-subheading">Responda 3 perguntas e receba uma recomendacao personalizada com os melhores precos do mercado brasileiro.</p>

    {/* QuizWidget (from 17.2) */}
    <QuizWidget onComplete={handleQuizComplete} />

    {/* RecommendationCard (from 17.2) — shown after quiz completion */}
    {recommendation && <RecommendationCard paddle={recommendation} />}

    {/* CTA — always visible */}
    <div className="text-center mt-8">
      <Button asChild size="lg" className="hy-button-cta">
        <Link href={quizCompleteUrl}>Comecar Quiz →</Link>
      </Button>
    </div>
  </div>
</section>

{/* DataStatsSection (from 17.3) */}
<DataStatsSection />

{/* FeatureSteps (from 17.4) */}
<FeatureSteps />
```

2. **H1 styling:** Use `hy-display` class. The word "ideal" gets a lime underline via CSS:

```css
.lime-underline {
  position: relative;
}
.lime-underline::after {
  content: '';
  position: absolute;
  bottom: 4px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: var(--sport-primary);
  border-radius: 2px;
}
```

Add this to `globals.css` as `.hy-text-underline-lime`.

3. **State management:** The page needs `'use client'` directive since it manages quiz state, recommendation state, and returning-visitor logic.

```typescript
'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { Paddle, UserProfile } from '@/types/paddle'
import { fetchPaddles } from '@/lib/api'
import { getProfile, saveProfile } from '@/lib/profile'
import { QuizWidget } from '@/components/quiz/quiz-widget'
import { RecommendationCard } from '@/components/quiz/recommendation-card'
import { DataStatsSection } from '@/components/home/data-stats-section'
import { FeatureSteps } from '@/components/home/feature-steps'
```

State variables:
```typescript
const [isReturning, setIsReturning] = useState(false)
const [quizProfile, setQuizProfile] = useState<UserProfile | null>(null)
const [recommendation, setRecommendation] = useState<Paddle | null>(null)
const [isLoading, setIsLoading] = useState(false)
const [quizComplete, setQuizComplete] = useState(false)
```

4. **handleQuizComplete logic:**
```typescript
function handleQuizComplete(profile: UserProfile) {
  saveProfile(profile)
  setQuizProfile(profile)
  setQuizComplete(true)
  // Fetch matching paddle for recommendation preview
  fetchMatchingPaddle(profile)
}
```

5. **fetchMatchingPaddle logic (with loading + error handling):**
```typescript
async function fetchMatchingPaddle(profile: UserProfile) {
  setIsLoading(true)
  try {
    const result = await fetchPaddles({
      price_max: profile.budget_max,
      limit: 50,
    })
    // Client-side filter by skill_level (backend doesn't support it yet)
    const matching = result.items.filter(p =>
      p.skill_level === profile.level || !p.skill_level
    )
    if (matching.length > 0) {
      setRecommendation(matching[0])
    }
    // If no matching paddle found, silently hide recommendation card
  } catch (err) {
    console.error('[fetchMatchingPaddle] failed:', err)
    // Don't show error to user — recommendation card simply won't appear
  } finally {
    setIsLoading(false)
  }
}
```

6. **Loading state in JSX:**
```typescript
{isLoading && (
  <div className="text-center py-8" style={{ color: 'var(--color-gray-500)' }}>
    Buscando recomendacao...
  </div>
)}
```

7. **CTA button behavior:**
- Before quiz completion: "Começar Quiz →" → scroll to quiz widget
- After quiz completion: "Ver recomendacoes no chat →" → `/chat` (profile already saved)

**QA:** Hero renders at top of page. H1 has lime underline. QuizWidget is visible above-the-fold on desktop (no scroll needed). Recommendation card appears below quiz after completion.

---

### Task 17.2 — Create QuizWidget + RecommendationCard Components

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:**
- `frontend/src/components/quiz/quiz-widget.tsx` (NEW)
- `frontend/src/components/quiz/recommendation-card.tsx` (NEW)
**Dependencies:** None (standalone components)
**Requirements:** HOME-01, HOME-02

**Changes:**

#### 17.2a — QuizWidget Component

A compact inline quiz with pill toggle buttons (NOT the card-based step flow from quiz-flow.tsx). This is a new, different interaction pattern optimized for the homepage.

```typescript
'use client'

import { useState } from 'react'
import type { UserProfile } from '@/types/paddle'

interface QuizWidgetProps {
  onComplete: (profile: UserProfile) => void
}

const LEVEL_OPTIONS = [
  { value: 'beginner', label: 'Iniciante' },
  { value: 'intermediate', label: 'Intermediario' },
  { value: 'advanced', label: 'Avancado' },
]

const BUDGET_OPTIONS = [
  { value: 300, label: 'Ate R$300' },
  { value: 600, label: 'R$300-600' },
  { value: 9999, label: 'Acima R$600' },
]

const STYLE_OPTIONS = [
  { value: 'control', label: 'Controle' },
  { value: 'power', label: 'Potencia' },
  { value: 'balanced', label: 'Equilibrado' },
]

export function QuizWidget({ onComplete }: QuizWidgetProps) {
  const [level, setLevel] = useState<string | null>(null)
  const [budget, setBudget] = useState<number | null>(null)
  const [style, setStyle] = useState<string | null>(null)

  const isComplete = level !== null && budget !== null && style !== null

  function handleComplete() {
    if (!isComplete) return
    onComplete({ level: level!, style: style!, budget_max: budget! })
  }

  return (
    <div className="quiz-widget">
      {/* Quiz container — dark card */}
      <div className="mx-auto max-w-2xl p-8 md:p-10 rounded-sm"
           style={{ backgroundColor: 'var(--color-near-black)', border: '2px solid var(--color-gray-border)' }}>

        {/* Level section */}
        <div className="mb-8">
          <span className="hy-section-label block mb-4">SEU NIVEL</span>
          <div className="flex flex-wrap justify-center gap-3">
            {LEVEL_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setLevel(opt.value)}
                className={`hy-quiz-pill ${level === opt.value ? 'selected hy-animate-quiz-ripple' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Budget section */}
        <div className="mb-8">
          <span className="hy-section-label block mb-4">SEU ORCAMENTO</span>
          <div className="flex flex-wrap justify-center gap-3">
            {BUDGET_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setBudget(opt.value)}
                className={`hy-quiz-pill ${budget === opt.value ? 'selected hy-animate-quiz-ripple' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Style section */}
        <div className="mb-0">
          <span className="hy-section-label block mb-4">ESTILO DE JOGO</span>
          <div className="flex flex-wrap justify-center gap-3">
            {STYLE_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setStyle(opt.value)}
                className={`hy-quiz-pill ${style === opt.value ? 'selected hy-animate-quiz-ripple' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* CTA button below quiz card */}
      <div className="text-center mt-6">
        <button
          type="button"
          onClick={handleComplete}
          disabled={!isComplete}
          className="hy-button hy-button-cta px-8 py-3 text-base disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Comecar Quiz →
        </button>
      </div>
    </div>
  )
}
```

**Key design decisions:**
- Uses existing `.hy-quiz-pill` and `.hy-quiz-pill.selected` classes from globals.css (Phase 16)
- Uses `.hy-animate-quiz-ripple` for selection animation (Phase 16)
- Uses `.hy-section-label` for quiz section labels (lime, uppercase)
- All 3 questions visible simultaneously (not step-based) — compact and scannable
- `max-w-2xl` (672px) to match the mockup's centered layout
- No `level` color coding on pills (keep them neutral — colors reserved for catalog badges)
- On mobile: pills wrap naturally via `flex-wrap`

#### 17.2b — RecommendationCard Component

Shows a paddle recommendation preview after quiz completion. Uses real data from the API.

```typescript
'use client'

import Link from 'next/link'
import type { Paddle } from '@/types/paddle'
import { SafeImage } from '@/components/ui/safe-image'

interface RecommendationCardProps {
  paddle: Paddle
}

export function RecommendationCard({ paddle }: RecommendationCardProps) {
  const detailUrl = paddle.model_slug && paddle.brand
    ? `/paddles/${encodeURIComponent(paddle.brand.toLowerCase())}/${encodeURIComponent(paddle.model_slug)}`
    : `/paddles`

  return (
    <div className="mx-auto max-w-2xl mt-8 hy-animate-card-enter"
         style={{
           backgroundColor: 'var(--color-near-black)',
           border: '2px solid var(--sport-primary)',
           borderRadius: 'var(--radius-sharp)',
           padding: 'var(--space-md)',
         }}>
      <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-6 items-center">
        {/* Paddle image */}
        <div className="w-[120px] h-[180px] rounded-sm overflow-hidden mx-auto md:mx-0"
             style={{ backgroundColor: 'var(--color-gray-border)' }}>
          {paddle.image_url ? (
            <SafeImage
              src={paddle.image_url}
              alt={paddle.name}
              width={120}
              height={180}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-xs"
                 style={{ color: 'var(--color-gray-500)' }}>
              Foto
            </div>
          )}
        </div>

        {/* Paddle info */}
        <div>
          <h3 className="hy-card-title-text" style={{ fontSize: '1.5rem', border: 'none' }}>
            {paddle.name}
          </h3>
          {paddle.brand && (
            <p className="text-xs font-bold uppercase tracking-wider mb-2"
               style={{ color: 'var(--data-green)' }}>
              {paddle.brand}
            </p>
          )}
          <div className="hy-product-card-price" style={{ fontSize: '1.5rem', marginBottom: '12px' }}>
            R$ {paddle.price_min_brl?.toLocaleString('pt-BR') ?? '—'}
          </div>

          {/* Key specs */}
          {paddle.specs && (
            <div className="flex flex-wrap gap-4 mb-3" style={{ fontSize: 'var(--font-size-caption)', color: 'var(--color-gray-300)' }}>
              {paddle.specs.weight_oz && <span>• {paddle.specs.weight_oz}oz</span>}
              {paddle.specs.face_material && <span>• {paddle.specs.face_material}</span>}
              {paddle.specs.core_thickness_mm && <span>• {paddle.specs.core_thickness_mm}mm core</span>}
            </div>
          )}

          <p className="mb-4" style={{ fontSize: '14px', color: 'var(--color-gray-300)' }}>
            Recomendado baseado no seu perfil e orcamento.
          </p>

          <Link
            href={detailUrl}
            className="hy-button hy-button-primary inline-block"
          >
            Ver detalhes
          </Link>
        </div>
      </div>
    </div>
  )
}
```

**Key design decisions:**
- Lime border (2px solid `--sport-primary`) signals this is a recommendation — matches mockup
- Uses `SafeImage` (Phase 14) for image loading with fallback
- Uses `hy-animate-card-enter` for entrance animation (Phase 16)
- Grid layout: image left, info right on desktop. Stacked on mobile.
- Paddle name uses `hy-card-title-text` but larger (1.5rem) and without bottom border (the lime card border replaces it)
- Price in JetBrains Mono via `hy-product-card-price` (existing class)
- Specs shown as bullet points with lime dots
- "Ver detalhes" links to paddle detail page (SEO-friendly deep link)

**QA:** QuizWidget renders 3 question groups with pill toggles. Selected pills show lime border + glow. All 3 selected → "Começar Quiz →" enabled. RecommendationCard renders paddle data from API. "Ver detalhes" link navigates correctly.

---

### Task 17.3 — Data Credibility Stats Section

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:**
- `frontend/src/components/home/data-stats-section.tsx` (NEW)
**Dependencies:** None
**Requirements:** HOME-03

**Changes:**

Create a dark section with 3 stat cards showing platform depth. This builds trust with analytical users.

```typescript
export function DataStatsSection() {
  const stats = [
    { value: '147', label: 'raquetes analisadas' },
    { value: '3', label: 'varejistas monitorados' },
    { value: 'Diaria', label: 'atualizacao de precos' },
  ]

  return (
    <section className="hy-near-black-section hy-section">
      <div className="hy-container">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          {stats.map((stat) => (
            <div key={stat.label} className="p-6">
              <div className="hy-data" style={{
                fontSize: '2.5rem',
                fontWeight: 700,
                color: 'var(--data-green)',
                lineHeight: 1.1,
                marginBottom: '8px',
              }}>
                {stat.value}
              </div>
              <div style={{
                fontSize: 'var(--font-size-body)',
                color: 'var(--color-gray-300)',
                fontWeight: 500,
              }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

**Key design decisions:**
- Dark `#1a1a1a` background via `hy-near-black-section`
- 3-column grid on desktop, stacked on mobile
- Values in JetBrains Mono (`hy-data` class), large (2.5rem), bold, `--data-green` color
- Labels in Inter, regular weight, gray-muted color
- No cards/borders around stats — clean, minimal, data-forward
- Stats are hardcoded for now (no API call needed — these change rarely)
- `hy-near-black-section` + `hy-section` gives the alternating dark pattern

**Design system compliance:**
- JetBrains Mono for data values (DESIGN.md: "JetBrains Mono for specs/tables — signals 'we take data seriously'")
- Green (#76b900) for data elements (DESIGN.md: "Green accent for data elements: charts, table highlights, spec badges, section labels")
- Dark section alternation (DESIGN.md: "Pages alternate between dark and light sections")

**QA:** 3 stat cards render in a row on desktop. Values in JetBrains Mono, data-green color. Labels in Inter, gray-muted. Section alternates correctly (dark after hero dark — note: hero is `#000`, this is `#1a1a1a`, creating subtle depth difference). Mobile stacks vertically.

---

### Task 17.4 — Feature Steps Section

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:**
- `frontend/src/components/home/feature-steps.tsx` (NEW)
**Dependencies:** None
**Requirements:** HOME-04

**Changes:**

Create a light section with 3 numbered steps and connecting lines explaining how the platform works.

```typescript
export function FeatureSteps() {
  const steps = [
    {
      number: 1,
      title: 'Responda o quiz',
      description: 'Responda 3 perguntas sobre seu nivel, orcamento e estilo de jogo',
    },
    {
      number: 2,
      title: 'Analise com IA',
      description: 'Nosso sistema processa suas respostas e gera recomendacoes personalizadas',
    },
    {
      number: 3,
      title: 'Compare precos',
      description: 'Acesse ofertas reais das lojas brasileiras e faca sua escolha',
    },
  ]

  return (
    <section className="hy-light-section hy-section">
      <div className="hy-container">
        <span className="hy-section-label text-center block mb-10">COMO FUNCIONA</span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-6 relative">
          {steps.map((step, index) => (
            <div key={step.number} className="text-center relative">
              {/* Connecting line (desktop only) */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-8 left-1/2 w-full h-[2px]"
                     style={{
                       backgroundColor: 'var(--sport-primary)',
                       opacity: 0.5,
                     }} />
              )}

              {/* Numbered circle */}
              <div className="relative z-10 mx-auto mb-6 w-16 h-16 rounded-full flex items-center justify-center"
                   style={{
                     border: '2px solid var(--sport-primary)',
                     backgroundColor: 'var(--color-white)',
                   }}>
                <span className="hy-data" style={{
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: 'var(--data-green)',
                }}>
                  {step.number}
                </span>
              </div>

              <h3 className="hy-heading text-center mb-3" style={{ color: '#000000' }}>
                {step.title}
              </h3>
              <p style={{
                fontSize: 'var(--font-size-link)',
                color: 'var(--color-gray-500)',
                lineHeight: 'var(--line-height-normal)',
              }}>
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

**Key design decisions:**
- Light `#ffffff` background via `hy-light-section`
- 3-column grid on desktop, stacked on mobile
- Numbered circles: 64px diameter, white fill, lime border (2px), number in JetBrains Mono data-green
- Connecting lines between circles on desktop (lime, 2px, 50% opacity) — hidden on mobile
- Section label "COMO FUNCIONA" in lime/green uppercase
- Step titles in `hy-heading` (black text on light bg)
- Descriptions in Inter 14px, gray-500
- No icons — numbers are sufficient and avoid AI slop icon-in-circle pattern
- Circles have `relative z-10` to sit above connecting lines

**Design system compliance:**
- Light section alternation (DESIGN.md: alternating dark/light)
- Section label pattern (DESIGN.md: "14px, weight 700, uppercase, green accent")
- JetBrains Mono for numbers (DESIGN.md: data font for numeric values)
- Lime for decorative elements only (DESIGN.md: "Lime on dark backgrounds only" — connecting lines are on white, which is technically a light bg. However, the mockup uses lime for connecting lines on white. This is a deliberate design choice from the approved variant. The lime here is decorative/structural, not a text color on white, so contrast rules don't apply.)

**Mobile considerations:**
- Steps stack vertically on mobile
- Connecting lines hidden (they don't work vertically)
- Circle size remains 64px (good touch target)

**QA:** 3 steps render in a row on desktop with connecting lines. Numbers in circles with lime border. Titles in black, descriptions in gray. Mobile stacks without connecting lines.

---

### Task 17.5 — Returning Visitor Logic

**Category:** `quick`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/app/page.tsx`
**Dependencies:** Task 17.1 complete (full page structure must exist)
**Requirements:** HOME-05

**Changes:**

Add returning visitor detection that shows alternative content for users who already completed the quiz.

1. **Check for existing profile** using `getProfile()` from `@/lib/profile`:

```typescript
useEffect(() => {
  const existing = getProfile()
  if (existing) {
    setIsReturning(true)
    setQuizProfile(existing)
    fetchMatchingPaddle(existing)
  }
}, [])
```

2. **Conditional rendering** in the hero section:

```typescript
{isReturning ? (
  // Returning visitor — show recommendation + CTA to chat
  <div className="text-center">
    <p className="hy-subheading mb-4">
      Bem-vindo de volta! Seu perfil esta salvo.
    </p>
    {recommendation && <RecommendationCard paddle={recommendation} />}
    <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-center">
      <Button asChild size="lg" className="hy-button-cta">
        <Link href="/chat">Falar com o PickleIQ</Link>
      </Button>
      <Button asChild variant="outline" size="lg" className="hy-button-primary">
        <Link href="/paddles">Ver catalogo</Link>
      </Button>
    </div>
  </div>
) : (
  // New visitor — show quiz widget
  <>
    <QuizWidget onComplete={handleQuizComplete} />
    {recommendation && <RecommendationCard paddle={recommendation} />}
  </>
)}
```

3. **Behavior rules:**
- `getProfile()` returns `null` for new visitors → show quiz widget
- `getProfile()` returns a profile → show "Bem-vindo de volta" + recommendation card + CTA to chat/catalog
- After quiz completion (handleQuizComplete): profile is saved, state updates to show recommendation card inline
- User can still see the quiz widget below if they scroll (it's replaced by the returning state)

4. **localStorage key:** Uses existing `pickleiq:profile:{uid}` from `profile.ts`. No new keys needed.

5. **Edge case:** If `fetchMatchingPaddle` returns no results for returning visitor, hide the RecommendationCard and show only the CTAs.

**QA:** First visit (no localStorage) → quiz widget shown. After completing quiz → recommendation card appears. Reload page → "Bem-vindo de volta" shown with recommendation + chat/catalog CTAs. Clear localStorage → quiz widget shown again.

---

### Task 17.6 — Visual QA + Responsive Verification

**Category:** `quick`
**Skills:** `['frontend-ui-ux']`
**Files:** All Phase 17 files
**Dependencies:** Tasks 17.1–17.5 all complete
**Requirements:** All (verification)

**Checks:**

1. **Above-the-fold test:** Quiz widget visible without scrolling at 1440x900 (desktop) and 375x667 (iPhone SE)
2. **Quiz completion flow:** Select 3 pills → "Começar Quiz →" enabled → click → recommendation card appears with animation
3. **Recommendation card:** Shows real paddle data (name, brand, price, specs). "Ver detalhes" links to correct paddle page.
4. **Data stats:** 3 cards render in JetBrains Mono, data-green, on dark background
5. **Feature steps:** 3 numbered circles with connecting lines on desktop, stacked on mobile
6. **Returning visitor:** Complete quiz → reload → see "Bem-vindo de volta" + recommendation
7. **Responsive breakpoints:**
   - 375px (mobile): quiz pills wrap, recommendation card stacks, stats stack, steps stack
   - 768px (tablet): quiz pills in 2 rows, recommendation 2-col grid, stats 3-col, steps 3-col
   - 1440px (desktop): full layout as designed
8. **Design system compliance:**
   - Lime (#84CC16) only on dark backgrounds ✅
   - Green (#76b900) for data values ✅
   - JetBrains Mono for data ✅
   - No 3-column icon cards (replaced by feature steps) ✅
   - No decorative blobs or purple gradients ✅
   - Section alternation: dark → dark (near-black) → light ✅
9. **Existing tests:** Run `npm run test` in frontend/ — all 161+ tests must pass
10. **Build:** Run `npm run build` in frontend/ — no TypeScript or CSS errors
11. **No console errors:** Verify on homepage load

**AI Slop Checklist (from DESIGN.md):**
- [ ] No 3-column equal-height cards with centered icons
- [ ] No "hero + 3 features + CTA" generic layout (OLD homepage pattern — removed)
- [ ] No decorative gradient blobs
- [ ] No purple/blue color scheme
- [ ] All text is Portuguese (PT-BR)
- [ ] Every element earns its pixel (quiz is functional, stats are real data, steps explain the process)

---

## Success Criteria

1. Quiz widget renders above-the-fold on desktop and mobile
2. Quiz completes with 3 pill selections → recommendation card preview appears
3. Recommendation card shows real paddle data from API (name, price, specs)
4. "Ver detalhes" links to correct paddle detail page
5. Data stats display with JetBrains Mono values in data-green on dark background
6. Feature steps show numbered progression with connecting lines on desktop
7. Returning users see "Bem-vindo de volta" with recommendation + CTAs (not quiz again)
8. All existing frontend tests pass (161+)
9. Frontend builds without errors
10. AI slop checklist passes

## Commit Strategy

5 atomic commits:

1. `feat(home): add QuizWidget component with pill toggle buttons`
2. `feat(home): add RecommendationCard component with real paddle data`
3. `feat(home): add DataStatsSection and FeatureSteps components`
4. `feat(home): redesign homepage hero with quiz-forward layout + returning visitor logic`
5. `test(home): verify responsive layout and design system compliance`
