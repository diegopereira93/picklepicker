# Phase 18: Chat-B Sidebar Companion

**Status:** Ready for execution
**Milestone:** v1.6.0 — UI Redesign
**Dependencies:** Phase 16 (DESIGN.md v3.0 + globals.css tokens) — COMPLETE
**Created:** 2026-04-05
**Updated:** 2026-04-05

## Goal

Redesign the chat screen with a split-panel layout that keeps product details visible during conversation. The left panel displays the recommended paddle (image, specs, price, CTA) while the right panel hosts the conversational AI chat. AI responses include structured card components (product cards, comparison tables, tip cards) instead of plain text.

## Context

**Design Review Source:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/`
**Approved Variant:** Chat-B (Sidebar Companion) + card responses from Chat-C — score 8/10
**HTML Mockup:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/variant-chat-B.html`
**Screenshot:** `~/.gstack/projects/diegopereira93-picklepicker/designs/all-screens-20260405/screenshot-chat-B.png`

**Hybrid Enhancement:** Chat-B base (split-panel layout) + card responses from Chat-C (ProductCard, ComparisonCard, TipCard).

```
[Navbar: Black, sticky]
[Split Panel: 55%/45%]
  [Left Panel (55%): Light #ffffff]
    SidebarProductCard
      Image container (180px height)
      Paddle name (Instrument Sans 600, 20px)
      Brand (Inter 12px, uppercase)
      Price (JetBrains Mono 20px, data-green)
      Specs grid (weight, face material, core thickness)
      Score badge (color-coded)
      "Comprar na loja" CTA button
    RelatedPaddles
      Horizontal row of 3+ smaller cards
  [Right Panel (45%): Dark #1a1a1a — continuous dark per DESIGN.md]
    Chat header ("PickleIQ" + "Editar perfil")
    Messages area (scrollable)
      Empty state: PI avatar + greeting + suggested questions
      User messages: right-aligned, dark bg, lime border
      AI messages: left-aligned, transparent bg
      Card responses: ProductCard / ComparisonCard / TipCard
      Typing indicator (3 dots)
    Input area (bottom-pinned)
      Suggested question pills (above input)
      Text input + send button
```

**Current State (v1.4.0):**
- Chat page (`frontend/src/app/chat/page.tsx`) is full-width: quiz gate → full-height `ChatWidget`
- `ChatWidget` (`frontend/src/components/chat/chat-widget.tsx`) uses `@ai-sdk/react`'s `useChat` with `DefaultChatTransport` to `/api/chat`
- `MessageBubble` (`frontend/src/components/chat/message-bubble.tsx`) renders text + `ProductCard` grid from `data-*` annotations
- `ProductCard` (`frontend/src/components/chat/product-card.tsx`) shows paddle name, brand, price, reason, stock, affiliate CTA
- Backend SSE events: `recommendations` (paddle array), `reasoning` (streamed text), `done`, `error`
- Chat proxy (`frontend/src/app/api/chat/route.ts`) transforms Vercel AI SDK format → FastAPI SSE
- DESIGN.md v3.0 already documents Chat Components section (message bubbles, card responses, typing indicator, input area, streaming animation)
- `globals.css` has `.hy-chat-bubble`, `.hy-chat-message-user`, `.hy-chat-input-container`, `.hy-chat-input`, `.hy-chat-send`, `.hy-chat-card-product`, `.hy-chat-card-tip`, `.hy-chat-card-comparison` classes ready (Phase 16)
- `globals.css` has `.hy-animate-chat-enter`, `.hy-animate-card-enter`, `.hy-streaming-cursor` animation classes ready (Phase 16)
- Full-dark exception in DESIGN.md: "Chat interfaces may use continuous dark backgrounds" — applies to right panel
- `--radius-conversational: 8px` token available for chat elements
- `--max-width-data: 1440px` token available for data-dense layouts

**Root Causes (from ROADMAP.md):**

1. **Current chat is full-width** — Product information is not visible while chatting. Users must scroll through conversation history to see the buy button, losing conversion opportunities.
2. **Buy button is only accessible by scrolling** — The affiliate CTA is buried inside message cards deep in the chat. "Comprar na loja" should always be visible.
3. **AI responses are plain text** — No structured product cards, comparison tables, or tip cards. The AI's recommendations are rendered as simple text with inline product cards below, but there's no visual hierarchy or rich formatting.

### Split-Panel Architecture

The split-panel is implemented as a **CSS flex container** (NOT a Sheet/Drawer — those are overlay-based and designed for mobile navigation). The chat page becomes a two-column layout at desktop widths.

```
chat/page.tsx
├── Quiz Gate (no profile → show QuizFlow)
└── Split Panel (profile exists)
    ├── Left Panel (55%) — Light #ffffff
    │   ├── SidebarProductCard (selectedPaddle: Paddle, score: number, affiliateUrl: string)
    │   │   ├── Image (SafeImage, paddle.image_url, 180px height)
    │   │   ├── Name (Instrument Sans 600)
    │   │   ├── Brand (Inter 12px, uppercase)
    │   │   ├── Price (JetBrains Mono 20px, data-green)
    │   │   ├── Specs Grid (weight, face material, core thickness)
    │   │   ├── Score Badge (color-coded)
    │   │   └── "Comprar na loja" CTA button
    │   └── RelatedPaddles (fetchPaddles, 3+ Paddle cards)
    └── Right Panel (45%) — Dark #1a1a1a
        ├── Chat Header
        ├── ChatWidget (messages + input)
        │   ├── MessageBubble (updated styling)
        │   │   ├── Text content
        │   │   └── Card response (ProductCard / ComparisonCard / TipCard)
        ├── Typing Indicator
        └── Input Area
            ├── Suggested Questions
            ├── Text Input
            └── Send Button
```

### State Flow

```
Page Load
  └── useEffect → getProfile()
      ├── null (new visitor) → show QuizFlow gate
      └── UserProfile (existing) → show Split Panel
          ├── selectedPaddle = null (sidebar shows empty state)
          ├── selectedScore = undefined
          ├── selectedAffiliateUrl = undefined
          └── ChatWidget renders in right panel

ChatWidget receives recommendations from stream
  └── onRecommendations(recs: ChatRecommendation[]) callback → page.tsx
      ├── const rec = recs[0]
      ├── setSelectedScore(rec.similarity_score)
      ├── setSelectedAffiliateUrl(rec.affiliate_url)
      └── fetchPaddle(rec.paddle_id) → setSelectedPaddle(fullPaddle)
          └── SidebarProductCard renders with Paddle data + score + affiliateUrl
          └── fetchRelatedPaddles(fullPaddle) → RelatedPaddles renders

User clicks paddle in RelatedPaddles
  └── setSelectedPaddle(related) → SidebarProductCard updates
      └── selectedScore/affiliateUrl cleared (no score for manually selected)

User clicks "Comprar na loja" in sidebar
  └── window.open(affiliateUrl, '_blank')
```

### SSE Event → Card Response Mapping

The backend sends events that map to card types:

| Backend Event | Data | Card Type | Render Location |
|---------------|------|-----------|-----------------|
| `recommendations` | `{ paddles: ChatRecommendation[] }` | **ProductCard** (1 paddle) or **ComparisonCard** (2+ paddles) | Inside MessageBubble (right panel) |
| `recommendations` | `{ paddles: ChatRecommendation[] }` | → triggers `fetchPaddle(rec.paddle_id)` | SidebarProductCard (left panel, full Paddle data) |
| `reasoning` | `{ text: string }` | Text message (or **TipCard** if no recommendations follow) | Inside MessageBubble (right panel) |
| `degraded` | `{ paddles: ChatRecommendation[] }` | **ProductCard** (with degraded prefix text) | Inside MessageBubble (right panel) |

**Card selection logic in MessageBubble:**
- `recommendations.length === 1` → render single `ProductCard`
- `recommendations.length >= 2` → render `ComparisonCard` (mini-table)
- No recommendations + text content → check for tip keywords → render `TipCard` or plain text
- Max 1 card type per AI response (per DESIGN.md)

### Prerequisite Files (verified to exist)

| File | Purpose | Status |
|------|---------|--------|
| `frontend/src/lib/profile.ts` | `getProfile()`, `saveProfile()` for localStorage | ✅ Exists |
| `frontend/src/types/paddle.ts` | `Paddle`, `ChatRecommendation`, `UserProfile` interfaces | ✅ Exists |
| `frontend/src/lib/api.ts` | `fetchPaddles()`, `fetchPaddle()` API client | ✅ Exists |
| `frontend/src/components/ui/safe-image.tsx` | `SafeImage` for retailer CDN images | ✅ Exists |
| `frontend/src/components/chat/chat-widget.tsx` | `ChatWidget` with `useChat` + `DefaultChatTransport` | ✅ Exists |
| `frontend/src/components/chat/message-bubble.tsx` | `MessageBubble` with recommendation rendering | ✅ Exists |
| `frontend/src/components/chat/product-card.tsx` | `ProductCard` with affiliate CTA | ✅ Exists |
| `frontend/src/app/globals.css` | `.hy-chat-*`, `.hy-animate-*` classes (Phase 16) | ✅ Exists |
| `DESIGN.md` | v3.0 Chat Components section | ✅ Exists |
| `frontend/src/components/quiz/quiz-flow.tsx` | `QuizFlow` gate component | ✅ Exists |
| `frontend/package.json` | `@ai-sdk/react` dependency | ✅ Exists |

## Requirements Coverage

| Requirement | Tasks | Notes |
|-------------|-------|-------|
| CHAT-01 | 18.1, 18.2 | Split-panel layout with product sidebar |
| CHAT-02 | 18.2 | SidebarProductCard + RelatedPaddles components |
| CHAT-03 | 18.3 | Card-structured AI responses (ProductCard, ComparisonCard, TipCard) |
| CHAT-04 | 18.4 | Updated message styling (per DESIGN.md v3.0) |
| CHAT-05 | 18.5 | Suggested questions component |
| CHAT-06 | 18.6 | Responsive stacking below 1024px |

## Execution Waves

```
Wave 0 (pre-check — verify dependencies):
└── Verify all prerequisite files exist (see Context: Prerequisite Files table)
└── Verify globals.css has .hy-chat-card-product, .hy-chat-card-tip, .hy-chat-card-comparison classes

Wave 1 (parallel — no dependencies):
├── 18.2: SidebarProductCard + RelatedPaddles components (new files in components/chat/)
├── 18.4: Update message styling in message-bubble.tsx (per DESIGN.md v3.0)
└── 18.5: SuggestedQuestions component (new file in components/chat/)

Wave 2 (after Wave 1 — depends on SidebarProductCard + RelatedPaddles):
└── 18.1: Redesign chat/page.tsx with split-panel layout (assembles Wave 1 components)

Wave 3 (after Wave 2 — depends on page layout + updated message styling):
└── 18.3: Card-structured AI responses in chat-widget.tsx + message-bubble.tsx

Wave 4 (after all — verification):
└── 18.6: Responsive behavior + visual QA
```

---

## Task Details

### Task 18.1 — Redesign Chat Page with Split-Panel Layout

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/app/chat/page.tsx`
**Dependencies:** Wave 1 complete (18.2 SidebarProductCard + RelatedPaddles must exist)
**Requirements:** CHAT-01

**Changes:**

1. **Replace the full-width layout** with a split-panel. The page structure becomes:

```typescript
'use client'

import { useState, useEffect, useCallback } from 'react'
import type { UserProfile, ChatRecommendation, Paddle } from '@/types/paddle'
import { getProfile, saveProfile } from '@/lib/profile'
import { fetchPaddles } from '@/lib/api'
import dynamic from 'next/dynamic'

const QuizFlow = dynamic(
  () => import('@/components/quiz/quiz-flow').then((mod) => mod.QuizFlow),
  { loading: () => <div className="animate-pulse"><div className="h-96 bg-muted" /></div> }
)

const ChatWidget = dynamic(
  () => import('@/components/chat/chat-widget').then((mod) => mod.ChatWidget),
  { loading: () => <div className="animate-pulse"><div className="h-96 bg-muted" /></div> }
)

const SidebarProductCard = dynamic(
  () => import('@/components/chat/sidebar-product-card').then((mod) => mod.SidebarProductCard),
  { loading: () => <div className="animate-pulse"><div className="h-[400px] bg-muted" /></div> }
)

const RelatedPaddles = dynamic(
  () => import('@/components/chat/related-paddles').then((mod) => mod.RelatedPaddles),
  { loading: () => <div className="animate-pulse flex gap-3"><div className="h-24 w-32 bg-muted" /></div> }
)
```

2. **State management:**

```typescript
const [profile, setProfile] = useState<UserProfile | null>(null)
const [editingProfile, setEditingProfile] = useState(false)
const [hydrated, setHydrated] = useState(false)
const [selectedPaddle, setSelectedPaddle] = useState<Paddle | null>(null)
const [selectedScore, setSelectedScore] = useState<number | undefined>(undefined)
const [selectedAffiliateUrl, setSelectedAffiliateUrl] = useState<string | undefined>(undefined)
const [relatedPaddles, setRelatedPaddles] = useState<Paddle[]>([])
```

3. **Split-panel layout** (replaces the single `<main>` with two-column flex):

```typescript
// After profile check + quiz gate (same as current)...

return (
  <main className="h-screen flex flex-col chat-full-dark">
    {/* Header */}
    <header className="border-b border-[var(--color-gray-border)] px-4 py-3 flex items-center justify-between"
            style={{ backgroundColor: 'var(--color-near-black)' }}>
      <h1 className="font-bold text-lg text-white">PickleIQ</h1>
      <button
        type="button"
        onClick={() => setEditingProfile(true)}
        className="text-sm text-[var(--color-gray-300)] hover:text-white underline transition-colors"
      >
        Editar perfil
      </button>
    </header>

    {/* Split Panel */}
    <div className="flex-1 flex overflow-hidden">
      {/* Left Panel — Product Sidebar (55%) */}
      <aside className="w-[55%] overflow-y-auto p-6 border-r border-[var(--color-gray-border)]"
             style={{ backgroundColor: 'var(--color-white)' }}>
        {selectedPaddle ? (
          <SidebarProductCard
            paddle={selectedPaddle}
            score={selectedScore}
            affiliateUrl={selectedAffiliateUrl}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                 style={{ backgroundColor: 'var(--color-near-black)' }}>
              <span className="text-2xl font-bold" style={{ color: 'var(--sport-primary)' }}>PI</span>
            </div>
            <p style={{ color: 'var(--color-gray-500)', fontSize: 'var(--font-size-body)' }}>
              Envie uma mensagem para ver recomendacoes aqui.
            </p>
          </div>
        )}

        {relatedPaddles.length > 0 && (
          <div className="mt-8">
            <h3 className="text-sm font-bold uppercase tracking-wider mb-4"
                style={{ color: 'var(--color-gray-500)' }}>
              Raquetes relacionadas
            </h3>
            <RelatedPaddles
              paddles={relatedPaddles}
              onSelect={(p) => {
                setSelectedPaddle(p)
                setSelectedScore(undefined)  // no score for manually selected
                setSelectedAffiliateUrl(undefined)
              }}
            />
          </div>
        )}
      </aside>

      {/* Right Panel — Chat (45%) */}
      <div className="w-[45%] flex flex-col" style={{ backgroundColor: 'var(--color-near-black)' }}>
        <ChatWidget
          profile={profile!}
          onRecommendations={handleRecommendations}
        />
      </div>
    </div>
  </main>
)
```

4. **handleRecommendations callback** — called by ChatWidget when recommendations arrive from SSE stream:

```typescript
import { fetchPaddle } from '@/lib/api'

const handleRecommendations = useCallback(async (recs: ChatRecommendation[]) => {
  if (recs.length === 0) return
  const rec = recs[0]
  setSelectedScore(rec.similarity_score)
  setSelectedAffiliateUrl(rec.affiliate_url)

  // Fetch full Paddle data (has image_url, specs that ChatRecommendation lacks)
  try {
    const fullPaddle = await fetchPaddle(rec.paddle_id)
    if (fullPaddle) {
      setSelectedPaddle(fullPaddle)
    }
  } catch (err) {
    console.error('[fetchPaddle] failed:', err)
    // Fallback: create minimal Paddle object from ChatRecommendation
    setSelectedPaddle({
      id: rec.paddle_id,
      name: rec.name,
      brand: rec.brand,
      price_min_brl: rec.price_min_brl,
    })
  }
}, [])
```

5. **Fetch related paddles** when selectedPaddle changes:

```typescript
useEffect(() => {
  if (!selectedPaddle) return
  async function fetchRelated() {
    try {
      const result = await fetchPaddles({ limit: 10 })
      // Filter out the selected paddle and take up to 4
      const related = result.items
        .filter(p => p.id !== selectedPaddle.id)
        .slice(0, 4)
      setRelatedPaddles(related)
    } catch (err) {
      console.error('[fetchRelated] failed:', err)
    }
  }
  fetchRelated()
}, [selectedPaddle])
```

5. **Responsive wrapper** — wraps the split-panel in a responsive container. Desktop (≥1024px): side-by-side flex. Below 1024px: stacked vertically (50% height each). This is handled by Tailwind classes + a wrapper div:

```typescript
{/* Responsive wrapper */}
<div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
  {/* Left Panel */}
  <aside className="lg:w-[55%] h-[50vh] lg:h-full overflow-y-auto p-6 border-b lg:border-b-0 lg:border-r border-[var(--color-gray-border)]"
         style={{ backgroundColor: 'var(--color-white)' }}>
    {/* ... sidebar content ... */}
  </aside>

  {/* Right Panel */}
  <div className="lg:w-[45%] h-[50vh] lg:h-full flex flex-col" style={{ backgroundColor: 'var(--color-near-black)' }}>
    {/* ... chat content ... */}
  </div>
</div>
```

**Key design decisions:**
- Split-panel uses CSS flex (NOT Sheet/Drawer). Sheet is overlay-based and designed for mobile nav — not suitable for persistent side-by-side layout.
- Left panel is white (#ffffff) per DESIGN.md: "Left panel (white #ffffff): product card..."
- Right panel uses continuous dark (#1a1a1a) per DESIGN.md full-dark exception for chat interfaces.
- `chat-full-dark` class from globals.css applied to `<main>`.
- Header spans full width, dark background, consistent with navbar pattern.
- Selected paddle state lifted to page.tsx so both sidebar and chat can share it.
- Dynamic imports for code-splitting (same pattern as current chat page).
- Empty state in sidebar: PI avatar + "Envie uma mensagem para ver recomendacoes aqui."

**QA:** Split-panel renders 55%/45% at 1440px. Left panel shows white background. Right panel shows dark background. Header spans full width. Quiz gate still works when no profile exists.

---

### Task 18.2 — Create SidebarProductCard + RelatedPaddles Components

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:**
- `frontend/src/components/chat/sidebar-product-card.tsx` (NEW)
- `frontend/src/components/chat/related-paddles.tsx` (NEW)
**Dependencies:** None (standalone components)
**Requirements:** CHAT-02

**Changes:**

#### 18.2a — SidebarProductCard Component

A large product display card for the left sidebar panel. Shows detailed paddle information with a persistent CTA button.

**Type design decision:** Uses `Paddle` type (from `frontend/src/types/paddle.ts`) instead of `ChatRecommendation` because `Paddle` has `image_url` and `specs` fields that `ChatRecommendation` lacks. When a recommendation arrives, the page fetches the full `Paddle` data via `fetchPaddle(id)` and passes it to this component.

```typescript
'use client'

import type { Paddle } from '@/types/paddle'
import { SafeImage } from '@/components/ui/safe-image'

interface SidebarProductCardProps {
  paddle: Paddle
  score?: number  // similarity_score from ChatRecommendation (optional)
  affiliateUrl?: string  // from ChatRecommendation (Paddle doesn't have this)
}

function formatPrice(price: number): string {
  return price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function getScoreColor(score: number): string {
  if (score >= 0.8) return 'var(--data-green)'       // High — green
  if (score >= 0.5) return '#FDE047'                    // Medium — yellow
  return '#B91C1C'                                     // Low — red
}

function getScoreLabel(score: number): string {
  if (score >= 0.8) return 'Recomendada'
  if (score >= 0.5) return 'Boa opcao'
  return 'Considere'
}

export function SidebarProductCard({ paddle, score, affiliateUrl }: SidebarProductCardProps) {
  const scoreColor = score != null ? getScoreColor(score) : null
  const scoreLabel = score != null ? getScoreLabel(score) : null

  return (
    <div className="flex flex-col gap-6">
      {/* Image — uses Paddle.image_url (ChatRecommendation doesn't have this) */}
      <div
        className="w-full overflow-hidden rounded-sm"
        style={{
          height: '180px',
          backgroundColor: 'var(--color-gray-border)',
        }}
      >
        {paddle.image_url ? (
          <SafeImage
            src={paddle.image_url}
            alt={paddle.name}
            width={400}
            height={180}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center"
               style={{ color: 'var(--color-gray-500)', fontSize: 'var(--font-size-caption)' }}>
            Foto
          </div>
        )}
      </div>

      {/* Brand */}
      <p
        className="text-xs font-bold uppercase tracking-wider"
        style={{ color: 'var(--data-green)' }}
      >
        {paddle.brand}
      </p>

      {/* Name */}
      <h2
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '20px',
          fontWeight: 600,
          lineHeight: 'var(--line-height-snug)',
          color: 'var(--color-black)',
        }}
      >
        {paddle.name}
      </h2>

      {/* Price — uses Paddle.price_min_brl */}
      <div
        style={{
          fontFamily: 'var(--font-data)',
          fontSize: '20px',
          fontWeight: 700,
          color: 'var(--data-green)',
        }}
      >
        {paddle.price_min_brl ? formatPrice(paddle.price_min_brl) : '—'}
      </div>

      {/* Specs Grid — uses Paddle.specs (ChatRecommendation doesn't have this) */}
      {paddle.specs && (
        <div className="grid grid-cols-3 gap-3">
          {paddle.specs.weight_oz != null && (
            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider mb-1"
                   style={{ color: 'var(--color-gray-500)' }}>
                Peso
              </div>
              <div style={{ fontFamily: 'var(--font-data)', fontSize: '14px', color: 'var(--color-black)' }}>
                {paddle.specs.weight_oz}oz
              </div>
            </div>
          )}
          {paddle.specs.face_material && (
            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider mb-1"
                   style={{ color: 'var(--color-gray-500)' }}>
                Face
              </div>
              <div style={{ fontSize: '14px', color: 'var(--color-black)' }}>
                {paddle.specs.face_material}
              </div>
            </div>
          )}
          {paddle.specs.core_thickness_mm != null && (
            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider mb-1"
                   style={{ color: 'var(--color-gray-500)' }}>
                Core
              </div>
              <div style={{ fontFamily: 'var(--font-data)', fontSize: '14px', color: 'var(--color-black)' }}>
                {paddle.specs.core_thickness_mm}mm
              </div>
            </div>
          )}
        </div>
      )}

      {/* Score Badge — from ChatRecommendation.similarity_score */}
      {score != null && score > 0 && (
        <div
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-sm self-start"
          style={{
            backgroundColor: scoreColor!,
            color: scoreColor === '#FDE047' ? 'var(--color-black)' : 'var(--color-white)',
            fontSize: 'var(--font-size-caption)',
            fontWeight: 700,
          }}
        >
          {scoreLabel}
          <span style={{ fontFamily: 'var(--font-data)', opacity: 0.8 }}>
            {Math.round(score * 100)}%
          </span>
        </div>
      )}

      {/* CTA Button — always visible */}
      {affiliateUrl && (
        <a
          href={affiliateUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="hy-button hy-button-cta w-full text-center py-3 text-base"
          style={{ marginTop: 'auto' }}
        >
          Comprar na loja →
        </a>
      )}
    </div>
  )
}
```

**Key design decisions:**
- Uses `Paddle` type (has `image_url`, `specs`, `price_min_brl`) instead of `ChatRecommendation` (which lacks these fields). The `score` and `affiliateUrl` props are passed separately from the recommendation data.
- Image: SafeImage with `paddle.image_url` — the `Foto` fallback renders when no image URL exists
- Paddle name: Instrument Sans 600, 20px — larger than message-bubble ProductCard
- Brand: Inter 12px, uppercase, data-green — matches DESIGN.md spec
- Price: JetBrains Mono 20px, data-green — large and prominent
- Specs grid: 3-column grid showing weight, face material, core thickness — uses `Paddle.specs` which has these fields
- Score badge: color-coded (green ≥80%, yellow ≥50%, red <50%), shows percentage match. Optional — only shown when `score` prop is provided
- CTA button: "Comprar na loja →" — always visible (no scroll needed), `hy-button-cta` class. Uses `affiliateUrl` prop from ChatRecommendation
- `marginTop: 'auto'` on CTA pushes it to bottom of sidebar when content is short
- Background is transparent (inherits white from parent `<aside>`)

#### 18.2b — RelatedPaddles Component

A horizontal row of smaller product cards shown below the SidebarProductCard.

```typescript
'use client'

import type { Paddle } from '@/types/paddle'

interface RelatedPaddlesProps {
  paddles: Paddle[]
  onSelect: (paddle: Paddle) => void
}

function formatPrice(price: number): string {
  return price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function RelatedPaddles({ paddles, onSelect }: RelatedPaddlesProps) {
  if (paddles.length === 0) return null

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-2 xl:grid-cols-4 gap-3">
      {paddles.map((paddle) => (
        <button
          key={paddle.id}
          type="button"
          onClick={() => onSelect(paddle)}
          className="text-left p-3 rounded-sm border transition-all hover:border-[var(--sport-primary)] hover:shadow-sm"
          style={{
            backgroundColor: 'var(--color-white)',
            borderColor: 'var(--color-gray-border)',
          }}
        >
          {/* Mini image placeholder */}
          <div
            className="w-full rounded-sm mb-2"
            style={{
              height: '80px',
              backgroundColor: 'var(--color-gray-border)',
            }}
          >
            {paddle.image_url ? (
              <img
                src={paddle.image_url}
                alt={paddle.name}
                className="w-full h-full object-cover rounded-sm"
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center"
                   style={{ color: 'var(--color-gray-500)', fontSize: '10px' }}>
                Foto
              </div>
            )}
          </div>

          {/* Brand */}
          <p className="text-[10px] font-bold uppercase tracking-wider"
             style={{ color: 'var(--color-gray-500)' }}>
            {paddle.brand}
          </p>

          {/* Name */}
          <p className="text-sm font-semibold truncate"
             style={{ color: 'var(--color-black)' }}>
            {paddle.name}
          </p>

          {/* Price */}
          <p className="text-sm font-bold mt-1"
             style={{ fontFamily: 'var(--font-data)', color: 'var(--data-green)' }}>
            {paddle.price_min_brl ? formatPrice(paddle.price_min_brl) : '—'}
          </p>
        </button>
      ))}
    </div>
  )
}
```

**Key design decisions:**
- Grid layout: 2-col on narrow sidebar, 4-col on wide sidebar (xl breakpoint)
- Each card is a `<button>` for accessibility — clicking selects that paddle for the sidebar
- Compact cards: 80px image, brand + name + price only
- Hover: lime border + subtle shadow
- `truncate` on paddle name to prevent overflow
- Lazy loading on images (`loading="lazy"`)
- Uses `Paddle` type (from api.ts fetchPaddles) since related paddles come from the paddle API, not the chat recommendations endpoint
- onSelect callback lifts state to page.tsx

**QA:** SidebarProductCard renders paddle name, brand (uppercase, data-green), price (JetBrains Mono, data-green), score badge (color-coded), and "Comprar na loja →" CTA. RelatedPaddles renders 3+ smaller cards in a grid. Clicking a related card triggers the onSelect callback.

---

### Task 18.3 — Card-Structured AI Responses

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:**
- `frontend/src/components/chat/chat-widget.tsx` (MODIFY)
- `frontend/src/components/chat/message-bubble.tsx` (MODIFY)
- `frontend/src/components/chat/comparison-card.tsx` (NEW)
- `frontend/src/components/chat/tip-card.tsx` (NEW)
**Dependencies:** Task 18.1 (page layout) + Task 18.4 (message styling) complete
**Requirements:** CHAT-03

**Changes:**

#### 18.3a — Add onRecommendations callback to ChatWidget

Modify `chat-widget.tsx` to accept an `onRecommendations` prop that fires when recommendations arrive from the SSE stream.

```typescript
interface ChatWidgetProps {
  profile: UserProfile
  onRecommendations?: (recommendations: ChatRecommendation[]) => void
}
```

Track recommendations at the ChatWidget level using `useRef` to avoid infinite re-render loops (the message parts array creates new references on every render, so `useEffect` with dependency on computed values would fire infinitely):

```typescript
// Inside ChatWidget component:
const prevRecCountRef = useRef(0)

// After the messages.map() rendering block, add a side effect:
useEffect(() => {
  // Extract all recommendation data parts from latest message only
  const lastMsg = messages[messages.length - 1]
  if (!lastMsg) return

  const recPart = lastMsg.parts.find((p) => p.type === 'data-recommendations')
  if (!recPart) return

  const recs = (recPart as { type: string; data: unknown }).data as ChatRecommendation[]
  if (!Array.isArray(recs) || recs.length === 0) return
  if (recs.length === prevRecCountRef.current) return  // Same count, no new recommendations

  prevRecCountRef.current = recs.length
  onRecommendations?.(recs)
}, [messages, onRecommendations])
```

**Why `useRef` instead of derived state:** The `messages` array from `useChat` creates new part references on every render. Computing `latestRecommendations` inline and using it as a `useEffect` dependency would create an infinite loop (new array ref → effect fires → state update → re-render → new array ref → ...). The `useRef` approach avoids this by only comparing the count, not the reference.

#### 18.3b — Create ComparisonCard Component

A mini-table showing 2-3 paddles side-by-side with green highlights on best values.

```typescript
'use client'

import type { ChatRecommendation } from '@/types/paddle'

interface ComparisonCardProps {
  paddles: ChatRecommendation[]
}

function formatPrice(price: number): string {
  return price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function ComparisonCard({ paddles }: ComparisonCardProps) {
  if (paddles.length < 2) return null

  const bestPriceIdx = paddles.reduce(
    (best, p, i) => (p.price_min_brl < paddles[best].price_min_brl ? i : best),
    0
  )
  const bestScoreIdx = paddles.reduce(
    (best, p, i) => (p.similarity_score > paddles[best].similarity_score ? i : best),
    0
  )

  return (
    <div className="hy-chat-card hy-chat-card-comparison hy-animate-card-enter mt-2">
      <table className="w-full text-sm" style={{ borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--color-gray-border)' }}>
            <th className="text-left p-3 font-bold text-xs uppercase tracking-wider"
                style={{ color: 'var(--color-gray-300)' }}>
              Raquete
            </th>
            {paddles.map((p) => (
              <th key={p.paddle_id} className="p-3 text-center">
                <span className="text-xs" style={{ color: 'var(--color-gray-300)' }}>
                  {p.brand}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {/* Name row */}
          <tr>
            <td className="p-3 text-xs font-medium" style={{ color: 'var(--color-gray-500)' }}>
              Modelo
            </td>
            {paddles.map((p) => (
              <td key={p.paddle_id} className="p-3 text-center font-semibold text-white">
                {p.name}
              </td>
            ))}
          </tr>
          {/* Price row */}
          <tr>
            <td className="p-3 text-xs font-medium" style={{ color: 'var(--color-gray-500)' }}>
              Preco
            </td>
            {paddles.map((p, i) => (
              <td
                key={p.paddle_id}
                className="p-3 text-center font-bold"
                style={{
                  fontFamily: 'var(--font-data)',
                  color: i === bestPriceIdx ? 'var(--data-green)' : 'var(--color-white)',
                }}
              >
                {formatPrice(p.price_min_brl)}
              </td>
            ))}
          </tr>
          {/* Score row */}
          <tr>
            <td className="p-3 text-xs font-medium" style={{ color: 'var(--color-gray-500)' }}>
              Match
            </td>
            {paddles.map((p, i) => (
              <td
                key={p.paddle_id}
                className="p-3 text-center font-bold"
                style={{
                  fontFamily: 'var(--font-data)',
                  color: i === bestScoreIdx ? 'var(--data-green)' : 'var(--color-white)',
                }}
              >
                {Math.round(p.similarity_score * 100)}%
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  )
}
```

**Key design decisions:**
- Uses `.hy-chat-card-comparison` class from globals.css (Phase 16) — dark bg, gray border, 8px radius
- JetBrains Mono for data cells (price, score) per DESIGN.md
- Green (#76b900) highlight on best values per DESIGN.md: "Green highlight on best values"
- No images in comparison table (keeps it compact)
- Max 3 paddles shown (backend sends max 3 recommendations)
- `hy-animate-card-enter` for entrance animation
- Only renders when 2+ paddles (single paddle uses ProductCard instead)

#### 18.3c — Create TipCard Component

Informational card with amber left border for gameplay tips and explanations.

```typescript
interface TipCardProps {
  content: string
}

export function TipCard({ content }: TipCardProps) {
  return (
    <div className="hy-chat-card hy-chat-card-tip hy-animate-card-enter mt-2">
      <p className="text-sm" style={{ color: 'var(--color-gray-300)', lineHeight: 'var(--line-height-normal)' }}>
        {content}
      </p>
    </div>
  )
}
```

**Key design decisions:**
- Uses `.hy-chat-card-tip` class from globals.css (Phase 16) — amber (#FCD34D) left border, subtle amber bg
- No CTA button per DESIGN.md: "No CTA button"
- Simple text content
- `hy-animate-card-enter` for entrance animation
- Text color: gray-300 (light gray on dark bg) for readability

#### 18.3d — Update MessageBubble to render card types

Modify `message-bubble.tsx` to choose the correct card component based on recommendation count:

```typescript
import { ProductCard } from './product-card'
import { ComparisonCard } from './comparison-card'
import { TipCard } from './tip-card'

// Inside the component, replace the current recommendations rendering:

{/* Card response — max 1 card type per AI response per DESIGN.md */}
{recommendations && recommendations.length > 0 && (
  recommendations.length >= 2 ? (
    <ComparisonCard paddles={recommendations} />
  ) : (
    <div className="grid grid-cols-1 gap-3 mt-2">
      {recommendations.map((rec) => (
        <ProductCard key={rec.paddle_id} {...rec} />
      ))}
    </div>
  )
)}

{/* TipCard — rendered when there's text but no recommendations */}
{!recommendations?.length && content && isTipContent(content) && (
  <TipCard content={content} />
)}
```

Add a simple tip detection heuristic:

```typescript
function isTipContent(text: string): boolean {
  // Heuristic: if the text contains tip-related keywords and is relatively short
  const tipKeywords = ['dica', 'importante', 'lembre-se', 'saiba que', 'recomendo', 'sugestão', 'sugestao']
  const hasKeyword = tipKeywords.some(kw => text.toLowerCase().includes(kw))
  const isShort = text.length < 300
  return hasKeyword && isShort
}
```

**Note:** The tip detection is a simple heuristic. The backend doesn't send a "tip" event type. This is a frontend-only enhancement that makes informational responses more visually distinct. If the heuristic doesn't match, the text renders as a regular AI message (transparent bg, white text) — which is still correct per DESIGN.md.

**QA:** Single recommendation renders as ProductCard. 2+ recommendations render as ComparisonCard. Best values highlighted in green. TipCard renders with amber left border for tip-like content. onRecommendations callback fires when recommendations arrive, updating the sidebar via fetchPaddle.

---

### Task 18.4 — Update Message Styling per DESIGN.md v3.0

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/components/chat/message-bubble.tsx`
**Dependencies:** None
**Requirements:** CHAT-04

**Changes:**

Replace the current shadcn-based message styling with DESIGN.md v3.0 patterns:

1. **User messages:** Right-aligned, dark (#111) background, lime (#84CC16) left border (2px), 8px border-radius, white text, max-width 80%.

```typescript
{/* User message */}
<div className="flex justify-end mb-3">
  <div
    className="chat-bubble-user"
    style={{
      backgroundColor: '#111111',
      borderLeft: '2px solid #84CC16',
      borderRadius: '8px',
      color: '#ffffff',
      maxWidth: '80%',
      padding: '12px 16px',
      alignSelf: 'flex-end',
    }}
  >
    {renderText(content)}
  </div>
</div>
```

2. **AI messages:** Left-aligned, transparent background, white text, 8px border-radius, max-width 80%. Appears with `hy-animate-chat-enter` animation.

```typescript
{/* AI message */}
<div className="flex justify-start mb-3 gap-2">
  <PickleIQAvatar />
  <div style={{ maxWidth: '80%' }}>
    <div
      className="chat-bubble-ai hy-animate-chat-enter"
      style={{
        backgroundColor: 'transparent',
        borderRadius: '8px',
        color: '#ffffff',
        padding: '12px 16px',
        alignSelf: 'flex-start',
      }}
    >
      {renderText(content)}
    </div>
    {/* Card responses rendered below the text bubble */}
    {/* ... (see Task 18.3) ... */}
  </div>
</div>
```

3. **Full updated MessageBubble component:**

Replace the entire component with:

```typescript
'use client'

import type { ChatRecommendation } from '@/types/paddle'
import { ProductCard } from './product-card'

interface MessageBubbleProps {
  role: 'user' | 'assistant'
  content: string
  annotations?: unknown[]
}

function isRecommendationArray(val: unknown): val is ChatRecommendation[] {
  return (
    Array.isArray(val) &&
    val.length > 0 &&
    typeof (val[0] as Record<string, unknown>)?.paddle_id === 'number'
  )
}

function renderText(text: string) {
  return text.split('\n').map((line, i) => (
    <span key={i}>
      {i > 0 && <br />}
      {line}
    </span>
  ))
}

function PickleIQAvatar() {
  return (
    <div
      className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
      style={{ backgroundColor: 'var(--color-near-black)' }}
      aria-hidden="true"
    >
      <span className="text-xs font-bold" style={{ color: 'var(--sport-primary)' }}>PI</span>
    </div>
  )
}

export function MessageBubble({ role, content, annotations }: MessageBubbleProps) {
  const isUser = role === 'user'

  const recommendations = annotations?.find((a) => isRecommendationArray(a)) as
    | ChatRecommendation[]
    | undefined

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 gap-2`}>
      {!isUser && <PickleIQAvatar />}

      <div style={{ maxWidth: '80%' }}>
        {content && (
          <div
            style={{
              backgroundColor: isUser ? '#111111' : 'transparent',
              borderLeft: isUser ? '2px solid #84CC16' : 'none',
              borderRadius: '8px',
              color: '#ffffff',
              padding: '12px 16px',
              fontSize: 'var(--font-size-body)',
              lineHeight: 'var(--line-height-normal)',
            }}
            className={isUser ? '' : 'hy-animate-chat-enter'}
          >
            {renderText(content)}
          </div>
        )}

        {/* ProductCard(s) or ComparisonCard — rendered inside message bubble area */}
        {recommendations && recommendations.length > 0 && (
          <div className="mt-2">
            {recommendations.length >= 2 ? (
              <ComparisonCard paddles={recommendations} />
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {recommendations.map((rec) => (
                  <ProductCard key={rec.paddle_id} {...rec} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
```

**Key design decisions:**
- User messages: dark bg (#111) + lime left border (2px) per DESIGN.md — replaces current `bg-primary text-primary-foreground` (green bg)
- AI messages: transparent bg + white text per DESIGN.md — replaces current `bg-muted text-foreground` (gray bg)
- Border radius: 8px (`--radius-conversational`) per DESIGN.md — replaces current `rounded-2xl` (16px)
- Max width: 80% per DESIGN.md — replaces current 85%
- AI avatar: dark circle with lime "PI" text — replaces current `bg-primary text-primary-foreground` (green bg)
- No `rounded-br-sm` / `rounded-bl-sm` asymmetric corners — DESIGN.md v3.0 uses uniform 8px radius
- `hy-animate-chat-enter` on AI messages for entrance animation (Phase 16)
- Card responses (ProductCard/ComparisonCard) rendered below text, inside the max-width container
- ComparisonCard import will be added in Task 18.3 (this task only handles message bubble styling)

**QA:** User messages appear right-aligned with dark background and lime left border. AI messages appear left-aligned with transparent background and white text. Both have 8px border-radius. Max width is 80% of chat container. AI messages animate in with `hy-chat-message-enter`.

---

### Task 18.5 — Suggested Questions Component

**Category:** `quick`
**Skills:** `['frontend-ui-ux']`
**Files:**
- `frontend/src/components/chat/suggested-questions.tsx` (NEW)
- `frontend/src/components/chat/chat-widget.tsx` (MODIFY — use new component)
**Dependencies:** None
**Requirements:** CHAT-05

**Changes:**

#### 18.5a — Create SuggestedQuestions Component

Extract the suggested questions from `chat-widget.tsx` into a reusable component with updated styling.

```typescript
'use client'

interface SuggestedQuestionsProps {
  questions: string[]
  onSelect: (question: string) => void
  disabled?: boolean
}

export function SuggestedQuestions({ questions, onSelect, disabled }: SuggestedQuestionsProps) {
  if (questions.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2">
      {questions.map((q) => (
        <button
          key={q}
          type="button"
          onClick={() => onSelect(q)}
          disabled={disabled}
          className="hy-quiz-pill text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:border-[var(--sport-primary)]"
        >
          {q}
        </button>
      ))}
    </div>
  )
}
```

#### 18.5b — Update ChatWidget to use SuggestedQuestions

Replace the inline suggested questions rendering in `chat-widget.tsx`:

```typescript
import { SuggestedQuestions } from './suggested-questions'

// Update SUGGESTED_QUESTIONS per ROADMAP:
const SUGGESTED_QUESTIONS = [
  'Qual a diferenca entre 13mm e 16mm?',
  'Melhor raquete para iniciante?',
  'Raquete com melhor custo-beneficio?',
]

// In the empty state, replace the inline buttons:
<SuggestedQuestions
  questions={SUGGESTED_QUESTIONS}
  onSelect={handleSuggestedQuestion}
  disabled={isLoading}
/>

// Also add suggested questions ABOVE the input area (not just in empty state):
// After the messages section, before the input:
{messages.length > 0 && (
  <div className="px-4 pt-2">
    <SuggestedQuestions
      questions={SUGGESTED_QUESTIONS}
      onSelect={handleSuggestedQuestion}
      disabled={isLoading}
    />
  </div>
)}
```

**Key design decisions:**
- Uses `.hy-quiz-pill` class from globals.css (Phase 16) — consistent with homepage quiz styling
- Hover: lime border (same as quiz pills)
- Disabled state: 40% opacity + not-allowed cursor
- Questions updated per ROADMAP: "Qual a diferenca entre 13mm e 16mm?", "Melhor raquete para iniciante?", "Raquete com melhor custo-beneficio?"
- Shown in TWO places: empty state (centered) AND above input area (after first message)
- Suggested questions persist after conversation starts (not just in empty state) — user can always click them

**QA:** Suggested questions render as pill buttons. Clicking a question sends it as a chat message. Questions are disabled during streaming. Questions appear in both empty state and above input area.

---

### Task 18.6 — Responsive Behavior + Visual QA

**Category:** `quick`
**Skills:** `['frontend-ui-ux']`
**Files:** All Phase 18 files
**Dependencies:** Tasks 18.1–18.5 all complete
**Requirements:** CHAT-06, All (verification)

**Changes:**

#### 18.6a — Responsive Layout

The responsive behavior is primarily handled in Task 18.1 via Tailwind classes on the split-panel container. This task verifies and polishes:

1. **≥1024px (desktop):** Side-by-side flex layout. Left panel 55%, right panel 45%. Both full height.
2. **768–1023px (tablet):** Stack vertically. Left panel (product) on top, 50vh height. Right panel (chat) on bottom, 50vh height. Both scrollable independently.
3. **<768px (mobile):** Same as tablet stacking but with tighter padding (p-4 instead of p-6 on sidebar).

Classes on the wrapper (from Task 18.1):
```html
<div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
  <aside className="lg:w-[55%] h-[50vh] lg:h-full overflow-y-auto p-4 lg:p-6 ...">
  <div className="lg:w-[45%] h-[50vh] lg:h-full flex flex-col ...">
</div>
```

#### 18.6b — Visual QA Checklist

**Checks:**

1. **Split-panel test:** 55%/45% split renders at 1440x900. Left panel white, right panel dark.
2. **Sidebar product card:** Shows paddle name, brand (data-green uppercase), price (JetBrains Mono), score badge (color-coded), "Comprar na loja" CTA.
3. **Related paddles:** 3+ smaller cards in a horizontal row below the product card.
4. **Chat messages:** User messages right-aligned, dark bg, lime border. AI messages left-aligned, transparent bg.
5. **Card responses:** Single recommendation → ProductCard. 2+ → ComparisonCard with green highlights.
6. **TipCard:** Renders with amber left border for tip-like content.
7. **Typing indicator:** 3 animated dots, left-aligned, gray color.
8. **Suggested questions:** Pill buttons in empty state + above input. Clicking sends message.
9. **CTA visibility:** "Comprar na loja" button always visible in sidebar (no scrolling needed).
10. **Responsive breakpoints:**
    - 375px (mobile): panels stacked, 50vh each, p-4 padding
    - 768px (tablet): panels stacked, 50vh each, p-6 padding
    - 1024px (desktop): side-by-side flex, full height
    - 1440px (wide): same as desktop, max-width-data applies
11. **Design system compliance:**
    - Lime (#84CC16) only on dark backgrounds ✅ (user message border on dark chat panel)
    - Green (#76b900) for data elements ✅ (price, score, brand)
    - JetBrains Mono for data ✅ (price in sidebar, comparison table cells)
    - 8px border-radius for chat elements ✅ (--radius-conversational)
    - Full-dark exception applied to right panel ✅
    - Section alternation NOT required (full-dark exception) ✅
12. **Existing tests:** Run `npm run test` in frontend/ — all 161+ tests must pass
13. **Build:** Run `npm run build` in frontend/ — no TypeScript or CSS errors
14. **No console errors:** Verify on chat page load

**AI Slop Checklist (from DESIGN.md):**
- [ ] No 3-column equal-height cards with centered icons
- [ ] No decorative gradient blobs
- [ ] No purple/blue color scheme
- [ ] All text is Portuguese (PT-BR)
- [ ] Every element earns its pixel (sidebar shows real data, cards are interactive, CTAs link to real retailers)
- [ ] No "hero + 3 features + CTA" generic layout
- [ ] No stock photos or placeholder illustrations

**Funnel path verification:**
- Home → Quiz complete → "Ver recomendacoes no chat →" → /chat → profile loaded → split-panel shown → send message → recommendations appear → sidebar updates → "Comprar na loja" visible

---

## Success Criteria

1. Split-panel renders at 1440px (55%/45%) and stacks vertically at 768px (50vh each)
2. Product card in sidebar shows image, name, brand, price, score badge, and "Comprar na loja" CTA
3. "Comprar na loja" button is always visible without scrolling
4. Card-structured AI responses render correctly (ProductCard for 1, ComparisonCard for 2+)
5. ComparisonCard highlights best values in green (#76b900)
6. TipCard renders with amber (#FCD34D) left border for informational content
7. Related paddles row shows 3+ smaller product cards below the main product
8. User messages: right-aligned, dark bg, lime border, 8px radius
9. AI messages: left-aligned, transparent bg, white text, 8px radius, entrance animation
10. Suggested questions appear as pill buttons in empty state and above input
11. Sidebar updates when AI sends recommendations (state sharing works)
12. All existing frontend tests pass (161+)
13. Frontend builds without errors
14. AI slop checklist passes
15. Funnel path works end-to-end: Home → Quiz → Chat → sidebar updates → affiliate click

## Commit Strategy

6 atomic commits:

1. `feat(chat): add SidebarProductCard and RelatedPaddles components`
2. `feat(chat): update message bubble styling per DESIGN.md v3.0`
3. `feat(chat): add SuggestedQuestions component with updated prompts`
4. `feat(chat): add ComparisonCard and TipCard for structured AI responses`
5. `feat(chat): redesign chat page with split-panel sidebar layout`
6. `test(chat): verify responsive layout, card responses, and design system compliance`
