---
phase: 04-frontend-chat-product-ui
plan: all
type: execute
wave: 1-5
depends_on: [03]
files_modified:
  - frontend/package.json
  - frontend/tsconfig.json
  - frontend/next.config.js
  - frontend/tailwind.config.ts
  - frontend/app/layout.tsx
  - frontend/app/page.tsx
  - frontend/app/quiz/page.tsx
  - frontend/app/quiz/layout.tsx
  - frontend/app/api/chat/route.ts
  - frontend/app/compare/page.tsx
  - frontend/app/compare/layout.tsx
  - frontend/app/admin/queue/page.tsx
  - frontend/app/admin/catalog/page.tsx
  - frontend/app/admin/layout.tsx
  - frontend/components/QuizStep.tsx
  - frontend/components/ChatWidget.tsx
  - frontend/components/ProductCard.tsx
  - frontend/components/ComparisonTable.tsx
  - frontend/components/RadarChartComponent.tsx
  - frontend/components/AdminReviewQueue.tsx
  - frontend/components/AdminCatalog.tsx
  - frontend/hooks/useChat.ts
  - frontend/hooks/useQuiz.ts
  - frontend/lib/api.ts
  - frontend/lib/affiliate.ts
  - frontend/lib/auth.ts
  - frontend/styles/globals.css
  - frontend/tests/quiz.test.ts
  - frontend/tests/chat-widget.test.ts
  - frontend/tests/comparison.test.ts
  - frontend/tests/affiliate.test.ts
  - frontend/tests/admin.test.ts
autonomous: true
requirements: [R4.1, R4.2, R4.3, R4.4, R4.5]
user_setup:
  - service: vercel
    why: "Next.js 14 deployment target for preview + production"
    env_vars:
      - name: VERCEL_PROJECT_ID
        source: "Vercel Dashboard → Project settings"
      - name: VERCEL_ORG_ID
        source: "Vercel Dashboard → Team settings"
  - service: backend_api
    why: "FastAPI /chat endpoint proxy from Phase 3"
    env_vars:
      - name: NEXT_PUBLIC_API_URL
        source: "Railway staging API URL (e.g., https://pickleiq-api-staging.up.railway.app)"
  - service: admin_secret
    why: "ADMIN_SECRET for /admin panel protection"
    env_vars:
      - name: ADMIN_SECRET
        source: "Generate random string (e.g., openssl rand -hex 32)"

must_haves:
  truths:
    - "Next.js 14 scaffolding runs on Vercel with Tailwind + shadcn/ui components"
    - "Quiz onboarding completes 3-step flow (skill level → play style → budget) and launches chat"
    - "Chat widget streams responses from /api/chat proxy (Phase 3 /chat endpoint) with SSE"
    - "Product cards render inline in chat with clickable affiliate links"
    - "Comparison page searches/autocompletes paddle catalog, displays side-by-side table"
    - "RadarChart renders without hydration errors (ssr: false) on mobile viewports"
    - "Affiliate clicks log to Edge Route Handler with keepalive fetch and UTM preservation"
    - "Admin panel /admin/queue shows review queue, /admin/catalog shows CRUD paddles"
    - "Admin panel requires ADMIN_SECRET header or query param (no UI login yet)"
    - "No user authentication (Phase 5 adds Clerk) — quiz state in URL params or sessionStorage"

  artifacts:
    - path: "frontend/app/layout.tsx"
      provides: "Root layout with Tailwind + provider setup"
      exports: ["RootLayout"]
    - path: "frontend/app/page.tsx"
      provides: "Landing page with quiz entry point"
      exports: ["HomePage"]
    - path: "frontend/app/quiz/page.tsx"
      provides: "3-step quiz onboarding flow (skill → style → budget)"
      exports: ["QuizPage"]
    - path: "frontend/app/api/chat/route.ts"
      provides: "POST /api/chat proxy to Phase 3 backend /chat endpoint with SSE streaming"
      exports: ["POST"]
    - path: "frontend/components/ChatWidget.tsx"
      provides: "Chat UI using useChat hook from ai/react, SSE transform, message list"
      exports: ["ChatWidget"]
    - path: "frontend/components/ProductCard.tsx"
      provides: "Inline product card rendered in chat with affiliate link"
      exports: ["ProductCard"]
    - path: "frontend/app/compare/page.tsx"
      provides: "Comparison page with search/autocomplete, table, RadarChart"
      exports: ["ComparePage"]
    - path: "frontend/components/ComparisonTable.tsx"
      provides: "Side-by-side table for paddle specs comparison"
      exports: ["ComparisonTable"]
    - path: "frontend/components/RadarChartComponent.tsx"
      provides: "Recharts RadarChart with ssr: false for hydration safety"
      exports: ["RadarChart"]
    - path: "frontend/app/admin/queue/page.tsx"
      provides: "Review queue UI showing manual review items (ADMIN_SECRET protected)"
      exports: ["AdminQueuePage"]
    - path: "frontend/app/admin/catalog/page.tsx"
      provides: "CRUD interface for paddle catalog management (ADMIN_SECRET protected)"
      exports: ["AdminCatalogPage"]
    - path: "frontend/hooks/useChat.ts"
      provides: "Custom hook adapting ai/react useChat to SSE from /api/chat"
      exports: ["useChat"]
    - path: "frontend/hooks/useQuiz.ts"
      provides: "Quiz state management (skill, style, budget → URL params)"
      exports: ["useQuiz"]
    - path: "frontend/lib/api.ts"
      provides: "Fetch utilities for /paddles, /compare, /admin endpoints"
      exports: ["fetchPaddles()", "fetchCompare()"]
    - path: "frontend/lib/affiliate.ts"
      provides: "Affiliate tracking (keepalive fetch, UTM preservation)"
      exports: ["trackAffiliateClick()"]
    - path: "frontend/lib/auth.ts"
      provides: "Admin secret validation (header or query param check)"
      exports: ["validateAdminSecret()"]
    - path: "frontend/tests/quiz.test.ts"
      provides: "Unit tests for quiz flow (state transitions, param encoding)"
      min_tests: 4
    - path: "frontend/tests/chat-widget.test.ts"
      provides: "Tests for chat widget SSE streaming, message rendering"
      min_tests: 5
    - path: "frontend/tests/comparison.test.ts"
      provides: "Tests for search, autocomplete, table rendering, RadarChart"
      min_tests: 6
    - path: "frontend/tests/affiliate.test.ts"
      provides: "Tests for affiliate tracking (keepalive, UTM params)"
      min_tests: 3
    - path: "frontend/tests/admin.test.ts"
      provides: "Tests for admin panel secret validation, CRUD operations"
      min_tests: 4

  key_links:
    - from: "frontend/app/page.tsx"
      to: "frontend/app/quiz/page.tsx"
      via: "user clicks 'Start Quiz' button"
      pattern: "router.push.*quiz"
    - from: "frontend/app/quiz/page.tsx"
      to: "frontend/components/ChatWidget.tsx"
      via: "quiz completion redirects to chat with URL params"
      pattern: "router.push.*chat\\?.*params"
    - from: "frontend/components/ChatWidget.tsx"
      to: "frontend/app/api/chat/route.ts"
      via: "useChat hook sends user message to /api/chat"
      pattern: "fetch.*api/chat.*POST"
    - from: "frontend/app/api/chat/route.ts"
      to: "Phase 3 backend /chat endpoint"
      via: "proxy request to FastAPI with SSE streaming"
      pattern: "fetch.*NEXT_PUBLIC_API_URL.*chat"
    - from: "frontend/components/ChatWidget.tsx"
      to: "frontend/components/ProductCard.tsx"
      via: "render product cards from SSE response metadata"
      pattern: "response.metadata.*products"
    - from: "frontend/components/ProductCard.tsx"
      to: "frontend/lib/affiliate.ts"
      via: "trackAffiliateClick on product link click"
      pattern: "onClick.*trackAffiliateClick"
    - from: "frontend/app/compare/page.tsx"
      to: "frontend/lib/api.ts"
      via: "fetchPaddles for search/autocomplete"
      pattern: "fetchPaddles.*search"
    - from: "frontend/components/ComparisonTable.tsx"
      to: "frontend/components/RadarChartComponent.tsx"
      via: "render RadarChart for selected paddles"
      pattern: "RadarChart.*selectedPaddles"
    - from: "frontend/app/admin/queue/page.tsx"
      to: "frontend/lib/auth.ts"
      via: "validateAdminSecret middleware before rendering"
      pattern: "validateAdminSecret.*ADMIN_SECRET"
    - from: "frontend/app/admin/catalog/page.tsx"
      to: "frontend/lib/api.ts"
      via: "CRUD operations on paddle catalog"
      pattern: "fetch.*api/admin/catalog"

---

<objective>
Build a complete Next.js 14 web interface for PickleIQ with quiz onboarding, real-time chat widget streaming AI recommendations, side-by-side paddle comparison, affiliate tracking, and admin tooling.

**Purpose:**
Phase 4 transforms Phase 3's RAG agent into a user-facing web application. The frontend:
1. Guides users through a 3-step quiz (skill level, play style, budget) to establish their profile
2. Streams AI-powered paddle recommendations via a chat widget (SSE from /api/chat proxy)
3. Renders product cards inline with clickable affiliate links
4. Provides a comparison page for searching/filtering paddles with visual RadarChart analytics
5. Logs affiliate clicks with keepalive fetch and UTM parameter preservation for revenue tracking
6. Offers an admin panel for review queue management and paddle catalog CRUD (ADMIN_SECRET protected)
7. Deploys on Vercel with preview environments for each PR

**Output:**
- Fully functional Next.js 14 app on Vercel (preview + staging)
- Quiz → Chat → Comparison user journey tested E2E
- 22+ passing tests (4 quiz + 5 chat + 6 comparison + 3 affiliate + 4 admin)
- Affiliate tracking validated (keepalive fetch, UTM preservation)
- Admin panel secured with ADMIN_SECRET
- Lighthouse score ≥ 90 (performance + accessibility)
- Zero console errors on mobile (iOS/Android tested via /browse skill)
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/03-rag-agent-ai-core/PHASE-3-COMPLETE.md
@.planning/phases/03-rag-agent-ai-core/03-05-SUMMARY.md

## Phase 3 Handoff

Phase 3 provides (verified ✅):
- **POST /chat endpoint** on Railway staging API (NEXT_PUBLIC_API_URL env var)
- **SSE streaming response** format: `data: {type, content, metadata}`
  - `type: "recommendation"` → paddle object
  - `type: "degraded"` → fallback top-3 by price
  - `metadata: {top_paddles: [...], latency_ms: N}`
- **Latency budget**: P95 < 3s (acceptable range for Phase 4 UI)
- **Degraded mode**: LLM timeout (>8s) → returns top-3 by price
- **Langfuse tracing**: All /chat queries logged with latency, tokens, cost

## Phase 3 API Contract (used in Phase 4)

```python
# POST /chat (FastAPI endpoint)
# Request body:
{
  "query": "quiero una raqueta para principiantes con presupuesto bajo",
  "skill_level": "principiante",  # from quiz
  "play_style": "defensivo",      # from quiz
  "budget": "bajo"                # from quiz
}

# Response (SSE stream):
data: {"type": "recommendation", "content": {...paddle object...}, "metadata": {...}}
data: {"type": "recommendation", "content": {...}, "metadata": {...}}
data: {"type": "recommendation", "content": {...}, "metadata": {...}}
data: [DONE]
```

## Phase 2 Paddle API (used for comparison page)

```python
# GET /paddles (with search params)
{
  "items": [
    {
      "id": "uuid",
      "brand": "Selkirk",
      "model": "Prime Infinite",
      "specs": {
        "swingweight": 85,
        "twistweight": 45,
        "core": "polymer",
        "face": "carbon fiber"
      },
      "latest_prices": [...]
    }
  ]
}
```

## Frontend Directory Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout (Tailwind, providers)
│   ├── page.tsx                # Landing page + quiz entry
│   ├── quiz/
│   │   ├── page.tsx            # 3-step quiz flow
│   │   └── layout.tsx          # Quiz layout
│   ├── chat/                   # (Optional: dedicated chat page, or modal in /page.tsx)
│   ├── compare/
│   │   ├── page.tsx            # Comparison page
│   │   └── layout.tsx
│   ├── admin/
│   │   ├── queue/
│   │   │   └── page.tsx        # Review queue
│   │   ├── catalog/
│   │   │   └── page.tsx        # CRUD paddles
│   │   └── layout.tsx          # Admin auth middleware
│   └── api/
│       ├── chat/
│       │   └── route.ts        # POST /api/chat (proxy + SSE)
│       └── admin/
│           └── catalog/
│               └── route.ts    # Admin CRUD endpoint (optional)
├── components/
│   ├── QuizStep.tsx            # Individual quiz step UI
│   ├── ChatWidget.tsx          # Chat message list + input
│   ├── ProductCard.tsx         # Inline product card
│   ├── ComparisonTable.tsx     # Side-by-side table
│   ├── RadarChartComponent.tsx # Recharts radar (ssr: false)
│   ├── AdminReviewQueue.tsx    # Review queue table
│   └── AdminCatalog.tsx        # CRUD interface
├── hooks/
│   ├── useChat.ts              # Chat state + SSE logic
│   ├── useQuiz.ts              # Quiz state (URL params)
│   └── ...
├── lib/
│   ├── api.ts                  # Fetch utilities
│   ├── affiliate.ts            # Tracking logic
│   ├── auth.ts                 # ADMIN_SECRET validation
│   └── ...
├── tests/
│   ├── quiz.test.ts
│   ├── chat-widget.test.ts
│   ├── comparison.test.ts
│   ├── affiliate.test.ts
│   └── admin.test.ts
├── package.json                # next, tailwind, shadcn/ui, recharts, ai
├── tsconfig.json
├── next.config.js
└── tailwind.config.ts
```

---

</context>

<design>

## Screen Hierarchy — Information Architecture

### Landing Page
**Goal:** Sport-first. Get users to start the quiz.
```
H1 (72px bold): "Encontre a raquete ideal para o seu jogo"
H2 (20px regular): "IA que analisa specs, preços e avaliações para recomendar a raquete certa para você."
Primary CTA: [ COMEÇAR QUIZ → ] (full-width on mobile, centered on desktop)
Secondary: Link to /compare (below the fold)
```
Single column layout. No hero image required — headline IS the hero.
Background: white or very light neutral gray.

### Quiz Steps (pattern applies to all 3 steps)
**Pattern:** Large selection cards — full-width on mobile, 2-col on tablet+
```
Step indicator: "1 de 3" (top, small, secondary text color)
H2 (28px bold): Question (e.g., "Qual é seu nível de jogo?")
Cards: [emoji icon + label + 1-line description] — 3-4 options max
Progress: Dot indicator below cards
Back link: text link (not a button), secondary placement
```
**Card selection auto-advances** to next step — no explicit "Próximo" button.
PT-BR truncation: card labels max 24 chars, descriptions max 48 chars.

### Quiz → Chat Bridge (quiz completion)
Before launching chat, show a 1-second summary screen:
```
"Seu perfil: [Nível] · [Estilo] · [Orçamento]"
Subtext: "Encontrando as melhores raquetes para você..."
Animated: spinner or subtle progress bar
```
This bridge confirms the user's input mattered before entering the AI experience.

### Chat Widget
**Message alignment:** AI responses left (PickleIQ avatar icon), user messages right.
```
Empty state: centered + "Analisando seu perfil..." spinner (before first AI message)
Streaming: tokens render inline as they arrive (no flash/flicker)
Product cards: appear BELOW the AI text block (never inline mid-sentence)
Product card limit: 3 cards per response maximum
Input: bottom-pinned, full-width
Placeholder: "Faça uma pergunta sobre raquetes..."
```

### Comparison Page
**Priority order:**
1. Search/autocomplete input (top, full-width)
2. Selected paddle chips/tags (below input — max 3 paddles, disabled state at 3)
3. Side-by-side spec table (primary content)
4. RadarChart (below table, collapsible on mobile)

**RadarChart axes** (6 attributes, hardcoded): Potência, Controle, Toque, Swing Weight, Peso, Equilíbrio

### Product Detail Page
**Priority order:**
```
H1: "[Marca] [Modelo]" (large, 40px+)
Price block: R$ price (large, accent color) + retailer name
Primary CTA: [ VER NO SITE → ] (affiliate link, opens new tab)
Secondary CTA: [ + COMPARAR ]
Specs: accordion/tabs below the fold
Price history chart: last section, 90-day default
```

## Responsive & Accessibility

### Breakpoints
| Viewport | Class | Key Layout Changes |
|----------|-------|-------------------|
| Mobile | < 640px (sm) | Single column, full-width cards, bottom-pinned chat input, stacked product cards |
| Tablet | 640–1024px (md) | Quiz cards 2-col grid, comparison table scrollable horizontally |
| Desktop | > 1024px (lg) | Landing: max-w-2xl centered, quiz: 2-col cards, chat: max-w-2xl centered |

### Mobile-Critical Specs
**Quiz (mobile):**
- Cards: full-width, min-height 72px, tap target ≥ 44px
- Step indicator + question + cards + back link all visible without scroll on iPhone SE (375px)
- Budget step (step 3): large tappable cards — NOT a slider (sliders are hard to control on mobile)

**Chat widget (mobile):**
- Input pinned to bottom with `position: fixed` or `sticky`
- Message list: `overflow-y: auto` with padding-bottom = input height + 16px
- Product cards: full-width, stacked vertically (no horizontal scroll)

**Comparison page (mobile):**
- RadarChart: hidden by default behind "Ver gráfico radar ▼" accordion toggle
- Table: horizontal scroll with sticky first column (paddle name)

### Accessibility Minimums
- All interactive elements: keyboard navigable (tab order follows visual order)
- Quiz cards: `role="radio"` with `aria-checked`, `aria-label` includes full option text
- Chat messages: `role="log"` on message list, `aria-live="polite"` for streaming
- Buttons: contrast ratio ≥ 4.5:1 (lime-500 on white = 2.7 — use text-primary-foreground on dark bg instead)
- Product card CTA: `aria-label="Ver Selkirk Luxx Control no site Brazil Store"` (not just "VER NO SITE →")
- Touch targets: minimum 44×44px for all tappable elements

**Contrast fix:** `--primary: #84CC16` (lime-500) on white fails 4.5:1 contrast. Apply lime-500 only to large text (H1, H2) or on dark backgrounds. Use `--primary-foreground: #0F172A` (near-black) for button text on lime background.

## Resolved Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Quiz persistence | URL params (`?skill=&style=&budget=`) | Shareable, survives refresh, no storage API needed |
| Comparison max paddles | 3 | RadarChart readable; 4th add button disabled with "Máximo 3 raquetes" tooltip |
| Affiliate link behavior | `target="_blank" rel="noopener"` | User keeps chat open; standard for comparison/recommendation tools |
| Quiz UI pattern | Large selection cards, auto-advance | Mobile-friendly, 44px+ tap targets, no explicit "Próximo" button |
| Landing page H1 direction | Sport-first: "Encontre a raquete ideal para o seu jogo" | Benefits-forward, works for all skill levels |
| Product card trust element | "Por que essa raquete?" + 1-line AI reason | Makes recommendations feel earned, not ad-like |
| Chat streaming error | Inline retry below partial response | User keeps context, retry is actionable |
| RadarChart axes | Potência, Controle, Toque, Swing Weight, Peso, Equilíbrio (6, hardcoded) | Avoids open-ended product decision at component level |

## Design System & Brand Tokens

**Type:** APP UI (task-focused, data-dense, utility language — not marketing)

**Color system** — override shadcn defaults in `globals.css`:
```css
/* Sport-appropriate palette for Brazilian pickleball */
--primary: #84CC16;           /* lime-500: pickleball yellow-green */
--primary-foreground: #0F172A;
--accent: #FCD34D;            /* amber-300: paddle face/ball color */
--accent-foreground: #0F172A;
/* Background, foreground, border, card: keep shadcn neutral defaults */
```

**Typography:**
- Font: Inter (already installed — Geist unavailable in Next.js 14.2)
- H1: 64px (desktop) / 40px (mobile), font-bold
- H2: 28px, font-semibold
- Body: 16px, font-normal
- Small/label: 14px, font-medium

**AI Slop avoidance checklist** (verify before ship):
- [ ] No 3-column feature grid on landing page
- [ ] No icons in colored circles as decoration
- [ ] No centered-everything layout (left-align body copy)
- [ ] No generic hero copy ("Welcome to...", "Your all-in-one solution for...")
- [ ] No decorative blobs or wavy SVG dividers
- [ ] Cards in comparison table earn existence (they ARE the interaction)

## User Journey & Emotional Arc

| Step | User Does | User Feels | Design Supports It |
|------|-----------|------------|-------------------|
| 1 | Lands on homepage | Curious — "will this help me?" | Sport-first H1 names their goal directly |
| 2 | Reads H1 + H2 | Oriented — understands what the product does | Clear value prop, single CTA |
| 3 | Clicks "COMEÇAR QUIZ →" | Committed | Button is prominent, no friction |
| 4 | Answers 3 quiz steps | Engaged — "this is getting to know me" | Large cards with descriptions feel personalized |
| 5 | Completes step 3 | Anticipatory | Bridge screen: shows their profile summary + loading spinner |
| 6 | Chat loads | Curious — "what will it recommend?" | "Analisando seu perfil..." spinner maintains anticipation |
| 7 | AI response streams | Excited — watching live AI reasoning | Streaming text renders as tokens arrive |
| 8 | Product cards appear | Trust: "this feels like a real recommendation" | "Por que essa raquete?" 1-line explanation per card |
| 9 | Clicks "VER NO SITE →" | Decisive | Button is clear, opens new tab (doesn't abandon chat) |
| 10 | Returns to chat | Satisfied or wanting more | Chat input remains active for follow-up questions |

**Product Card Anatomy** (trust-first design):
```
+-------------------------------+
| [paddle image]  Brand + Model |
|                 R$ price · store |
|                               |
| Por que essa raquete?         |
| [1-line AI reason from SSE    |
|  metadata field]              |
|                               |
| [     VER NO SITE →     ]    |
+-------------------------------+
```
The `reason` field must be included in the SSE metadata response from Phase 3 backend.
If absent: fall back to "Recomendada para o seu perfil de jogo."

## Interaction States

| Feature | LOADING | EMPTY | ERROR | SUCCESS | PARTIAL |
|---------|---------|-------|-------|---------|---------|
| Landing page | — | — | — | Static render | — |
| Quiz step | Skeleton cards (rare — static) | — | "Erro ao carregar. Recarregue a página." | Auto-advance to next step | — |
| Quiz→Chat bridge | Spinner + "Encontrando as melhores raquetes..." | — | — | Auto-redirect to chat | — |
| Chat (initial) | "Analisando seu perfil..." centered spinner | — | — | First AI token renders | — |
| Chat (streaming) | Typing indicator (3 dots) | — | Inline: "⚠️ Erro ao carregar resposta. [Tentar novamente]" — keeps partial text | All tokens received + product cards render below | Product cards not yet rendered — show skeleton below text |
| Product cards | Skeleton card (image + 2 lines) | — | Card hidden, no broken state visible | Price + name + CTA rendered | Price shown, image failed → paddle icon placeholder |
| Comparison search | Spinner in input field | Inline: 🏓 "Nenhuma raquete encontrada para '[query]'" + search tips | Toast: "Erro ao buscar. Tente novamente." | Results dropdown appears | — |
| Comparison (3 paddles selected) | — | "Selecione raquetes para comparar" placeholder | — | Table + RadarChart render | RadarChart loading: table visible, chart skeleton |
| Comparison max (3/3) | — | — | — | — | 4th paddle search result: disabled + "Máximo 3 raquetes" tooltip |
| Admin queue | Table skeleton | "Nenhum item na fila de revisão" + 🎉 | "Erro ao carregar fila." + [Recarregar] | Table rendered | — |
| Admin catalog | Table skeleton | "Catálogo vazio. [+ Adicionar raquete]" | "Erro ao carregar catálogo." | Table rendered | — |
| Admin CRUD save | Button: spinner + disabled | — | Inline field error OR toast "Erro ao salvar" | Toast "Raquete salva ✓" (2s) | — |
| Affiliate link click | Cursor wait (brief) | — | Silent fail (log error, don't interrupt UX) | New tab opens | — |

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | — |
| Codex Review | `/codex review` | Independent 2nd opinion | 0 | — | — |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 0 | — | — |
| Design Review | `/plan-design-review` | UI/UX gaps | 1 | CLEAR | score: 2/10 → 8/10, 8 decisions made |

**UNRESOLVED:** 0
**VERDICT:** Design review CLEAR — eng review required before ship.

</design>

<tasks>

<task type="auto">
  <name>Wave 1: Next.js 14 Scaffolding + Tailwind + shadcn/ui</name>
  <files>
    frontend/package.json
    frontend/tsconfig.json
    frontend/next.config.js
    frontend/tailwind.config.ts
    frontend/app/layout.tsx
    frontend/app/page.tsx
    frontend/styles/globals.css
    frontend/components/.gitkeep
    frontend/hooks/.gitkeep
    frontend/lib/.gitkeep
    frontend/tests/.gitkeep
  </files>
  <action>
    1. **Initialize Next.js 14 App Router project** (if not already scaffolded):
       ```bash
       cd frontend
       npx create-next-app@14 --typescript --tailwind --no-eslint --app
       ```
       (Verify: `frontend/` already exists; if empty, scaffold. If populated, skip to step 2.)

    2. **Install dependencies**:
       ```bash
       npm install next@14 react@18 react-dom@18 tailwindcss@3 typescript @types/node @types/react
       npm install ai recharts shadcn-ui lucide-react clsx
       npm install -D @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom
       ```

    3. **Configure Tailwind** (frontend/tailwind.config.ts):
       - Extend colors: add pickleball theme (orange, green, neutrals)
       - Setup content paths: `["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"]`
       - Enable dark mode (optional for Phase 4, required Phase 5)

    4. **Root layout** (frontend/app/layout.tsx):
       - Import globals.css
       - Setup `<html lang="pt-BR">` (Portuguese)
       - Add metadata: `{ title: "PickleIQ", description: "AI-powered paddle recommendations" }`
       - Provider setup (if needed for chat context)
       - No auth yet (Phase 5 adds Clerk)

    5. **Landing page** (frontend/app/page.tsx):
       - Hero section with PickleIQ branding
       - "Encontre a raquete perfeita" (Find your perfect paddle) headline
       - Big button: "Começar Quiz" (Start Quiz) → navigates to /quiz
       - Optional: Show recent chat results or comparison stats

    6. **Global styles** (frontend/styles/globals.css):
       - Tailwind directives (@tailwind base, components, utilities)
       - CSS variables for pickleball colors (--orange-600, --green-600, etc.)
       - Responsive typography scales

    7. **Directory structure**:
       - Create app/quiz/, app/compare/, app/admin/ directories
       - Create components/, hooks/, lib/, tests/ directories (empty for now, populated in later waves)

    8. **Environment variables** (frontend/.env.local):
       - NEXT_PUBLIC_API_URL = "http://localhost:8000" (local) or Railway staging URL
       - ADMIN_SECRET = "placeholder" (overridden in production)

    **Dependencies created:**
    - next.config.js configured for Vercel deployment
    - tsconfig.json with path aliases (@/* for absolute imports)
    - Tailwind configured for content paths
  </action>
  <verify>
    <automated>
      npm run build 2>&1 | grep -q "Compiled successfully" && echo "PASS: Build succeeded" || echo "FAIL: Build failed"
      npm run lint 2>&1 (if linter configured)
      curl -s http://localhost:3000 | grep -q "PickleIQ" && echo "PASS: Landing page renders" || echo "FAIL: No landing page"
    </automated>
  </verify>
  <done>
    ✅ Next.js 14 scaffolding complete with App Router
    ✅ Tailwind CSS configured with content paths
    ✅ shadcn/ui installed and available
    ✅ Landing page renders with "Começar Quiz" button
    ✅ Environment variables configured (NEXT_PUBLIC_API_URL, ADMIN_SECRET)
    ✅ Build succeeds without errors
    ✅ Lighthouse baseline score captured (target ≥ 90)
  </done>
</task>

<task type="auto">
  <name>Wave 2: Quiz Onboarding (3-Step Flow)</name>
  <files>
    frontend/app/quiz/page.tsx
    frontend/app/quiz/layout.tsx
    frontend/components/QuizStep.tsx
    frontend/hooks/useQuiz.ts
    frontend/tests/quiz.test.ts
  </files>
  <action>
    1. **Quiz hook** (frontend/hooks/useQuiz.ts):
       - State: `{ step: 1-3, skillLevel, playStyle, budget }`
       - Store in URL params: `/quiz?skill=principiante&style=defensivo&budget=baixo`
       - Functions: `nextStep()`, `prevStep()`, `setAnswer()`, `getAnswers()`
       - On completion (step 4): redirect to chat page with params

    2. **Quiz layout** (frontend/app/quiz/layout.tsx):
       - Progress indicator (Step 1 of 3, Step 2 of 3, etc.)
       - Quiz container (max-width, centered)
       - No header/footer (full-screen focus)

    3. **Quiz page** (frontend/app/quiz/page.tsx):
       - Initialize useQuiz hook
       - Render current QuizStep component based on state.step
       - "Voltar" (Back) button if step > 1
       - "Próximo" (Next) button if step < 3
       - "Começar Chat" (Start Chat) button if step === 3 → redirect to / with params

    4. **QuizStep component** (frontend/components/QuizStep.tsx):
       - **Step 1: Skill Level**
         - Options: Principiante, Intermediário, Avançado
         - Radio buttons or card selection
         - Icon per level (paddle svg)

       - **Step 2: Play Style**
         - Options: Defensivo (defensive), Ofensivo (aggressive), Equilibrado (balanced)
         - Descriptions for each style

       - **Step 3: Budget**
         - Options: Baixo (<$100), Médio ($100-300), Alto (>$300)
         - Price guidance text

    5. **Test coverage** (frontend/tests/quiz.test.ts):
       - Test quiz navigation (next/prev steps)
       - Test URL param encoding/decoding
       - Test all 3 step renders
       - Test form submission (starting chat)

    **Design patterns:**
    - Use shadcn/ui RadioGroup or Card components
    - Tailwind card styling with hover states
    - Smooth transitions between steps (fade-in animation)
  </action>
  <verify>
    <automated>
      npm test -- quiz.test.ts 2>&1 | grep -q "passed" && echo "PASS: Quiz tests pass" || echo "FAIL: Quiz tests fail"
      npm run build 2>&1 | grep -q "Compiled successfully" && echo "PASS: Build includes quiz" || echo "FAIL: Build failed"
    </automated>
  </verify>
  <done>
    ✅ Quiz onboarding 3-step flow implemented
    ✅ State stored in URL params (skill, style, budget)
    ✅ All 3 steps render correctly (skill level, play style, budget)
    ✅ Navigation (back/next) works
    ✅ Quiz completion redirects to chat with params
    ✅ 4 unit tests passing (navigation, step rendering, param encoding, submission)
  </done>
</task>

<task type="auto">
  <name>Wave 3: Chat Widget + Route Handler Proxy</name>
  <files>
    frontend/app/api/chat/route.ts
    frontend/components/ChatWidget.tsx
    frontend/components/ProductCard.tsx
    frontend/hooks/useChat.ts
    frontend/lib/api.ts
    frontend/tests/chat-widget.test.ts
  </files>
  <action>
    1. **Route handler proxy** (frontend/app/api/chat/route.ts):
       - Accept POST with body: `{ query, skill_level, play_style, budget }`
       - Validate NEXT_PUBLIC_API_URL is set (error if missing)
       - Fetch Phase 3 backend `/chat` endpoint with streaming response
       - Transform SSE stream: parse `data: {...}` lines, pass through to client
       - Return 500 on backend error with fallback message
       - Handle timeout gracefully (8s limit, return error event)

    2. **useChat hook** (frontend/hooks/useChat.ts):
       - Adapt from `ai/react` useChat hook
       - State: `{ messages: [], input: "", isLoading, error }`
       - Function: `handleSubmit(e)` → POST to /api/chat with quiz params
       - SSE parsing: convert stream events to message objects
       - Product card detection: if metadata.products in response, add as special message type
       - On error: show user-friendly message (e.g., "Desculpe, não consegui gerar recomendações")

    3. **ChatWidget component** (frontend/components/ChatWidget.tsx):
       - Message list rendering (user messages on right, assistant on left)
       - Message bubbles with Tailwind styling
       - Input field at bottom with send button
       - Loading spinner during response
       - Auto-scroll to latest message
       - Product card rendering inline (via ProductCard component)

    4. **ProductCard component** (frontend/components/ProductCard.tsx):
       - Display paddle name, brand, specs (swingweight, core, face material)
       - Price if available
       - "Ver Mais" (View Details) link → /compare?compare_id={paddle_id}
       - "Comprar com Afiliado" (Buy with Affiliate Link) → trackAffiliateClick()
       - Tailwind card styling with shadow, rounded corners

    5. **API utilities** (frontend/lib/api.ts):
       - `fetchPaddles(search?: string)` → GET /paddles with optional search param
       - `fetchCompare(paddleIds: string[])` → GET /paddles?ids={...}
       - Error handling for all requests

    6. **Test coverage** (frontend/tests/chat-widget.test.ts):
       - Mock /api/chat endpoint with SSE response
       - Test message submission and rendering
       - Test product card rendering in chat
       - Test loading state
       - Test error handling
       - Test SSE stream parsing

    **SSE response format** (from Phase 3):
    ```
    data: {"type": "recommendation", "content": {paddle object}, "metadata": {...}}
    [DONE]
    ```
  </action>
  <verify>
    <automated>
      npm test -- chat-widget.test.ts 2>&1 | grep -q "passed" && echo "PASS: Chat tests pass" || echo "FAIL: Chat tests fail"
      npm run build 2>&1 | grep -q "Compiled successfully" && echo "PASS: Build includes chat" || echo "FAIL: Build failed"
    </automated>
  </verify>
  <done>
    ✅ Route handler proxy /api/chat implemented
    ✅ SSE streaming from Phase 3 backend working
    ✅ ChatWidget renders messages in real-time
    ✅ ProductCard displays paddle specs and affiliate link
    ✅ useChat hook manages state and SSE parsing
    ✅ Error handling for backend timeout/failure
    ✅ 5 chat widget tests passing (submission, rendering, product cards, loading, errors)
  </done>
</task>

<task type="auto">
  <name>Wave 4: Comparison Page + RadarChart Visualization</name>
  <files>
    frontend/app/compare/page.tsx
    frontend/app/compare/layout.tsx
    frontend/components/ComparisonTable.tsx
    frontend/components/RadarChartComponent.tsx
    frontend/tests/comparison.test.ts
  </files>
  <action>
    1. **Comparison page** (frontend/app/compare/page.tsx):
       - Read query params: `?compare_id=uuid1,uuid2,uuid3,...` (up to 5 paddles)
       - Fetch paddle details via `fetchCompare(ids)`
       - Search/autocomplete bar: real-time search for paddle name or brand
       - Add paddles to comparison (max 5)
       - Remove paddles from comparison
       - Display comparison table + radar chart

    2. **Search/autocomplete**:
       - Input field with debounce (300ms)
       - Call `fetchPaddles(searchTerm)` on change
       - Dropdown showing brand + model (e.g., "Selkirk Prime Infinite")
       - Click to add paddle to comparison (add to URL params)
       - Recently selected paddles as quick-access buttons

    3. **ComparisonTable component** (frontend/components/ComparisonTable.tsx):
       - Side-by-side columns (one per paddle)
       - Rows for spec values:
         - Brand, Model
         - Price (latest)
         - Swingweight, Twistweight
         - Core material, Face material
         - Affiliate links (one per column)
       - Color-code best values per spec (e.g., lowest price in green)
       - Responsive: collapse to vertical stack on mobile

    4. **RadarChartComponent** (frontend/components/RadarChartComponent.tsx):
       - Use Recharts `<RadarChart>` to visualize 4 specs:
         - Swingweight (0-100)
         - Twistweight (0-50)
         - Price (0-300, normalized)
         - Hardness/feel (subjective, 0-10)
       - Normalize all values to 0-100 scale
       - Color-coded series (one color per paddle, max 5)
       - Legend showing paddle names
       - **CRITICAL: Set `ssr: false` to prevent hydration mismatch** (Recharts issue)
       - Use dynamic import: `const RadarChart = dynamic(() => import(...), { ssr: false })`

    5. **Test coverage** (frontend/tests/comparison.test.ts):
       - Test search/autocomplete functionality
       - Test paddle selection (adding/removing)
       - Test comparison table rendering
       - Test RadarChart rendering (verify ssr: false)
       - Test mobile responsiveness
       - Test URL param encoding/decoding

    **Recharts RadarChart data format:**
    ```typescript
    const data = [
      { name: "Swingweight", Selkirk: 85, Prince: 78, ... },
      { name: "Twistweight", Selkirk: 45, Prince: 42, ... },
      ...
    ];
    ```
  </action>
  <verify>
    <automated>
      npm test -- comparison.test.ts 2>&1 | grep -q "passed" && echo "PASS: Comparison tests pass" || echo "FAIL: Comparison tests fail"
      npm run build 2>&1 | grep -q "Compiled successfully" && echo "PASS: Build includes comparison" || echo "FAIL: Build failed"
    </automated>
  </verify>
  <done>
    ✅ Comparison page searches/autocompletes paddle catalog
    ✅ Side-by-side table displays paddle specs (brand, model, price, swingweight, core, face)
    ✅ RadarChart renders without hydration errors (ssr: false confirmed)
    ✅ Max 5 paddles per comparison
    ✅ Mobile responsive (table stacks vertically on small screens)
    ✅ Color-coding highlights best values per spec
    ✅ 6 comparison tests passing (search, autocomplete, table, RadarChart, mobile, URL params)
  </done>
</task>

<task type="auto">
  <name>Wave 5: Affiliate Tracking + Admin Panel</name>
  <files>
    frontend/lib/affiliate.ts
    frontend/app/admin/layout.tsx
    frontend/app/admin/queue/page.tsx
    frontend/app/admin/catalog/page.tsx
    frontend/components/AdminReviewQueue.tsx
    frontend/components/AdminCatalog.tsx
    frontend/lib/auth.ts
    frontend/tests/affiliate.test.ts
    frontend/tests/admin.test.ts
  </files>
  <action>
    **Part A: Affiliate Tracking**

    1. **Affiliate tracking library** (frontend/lib/affiliate.ts):
       - Function: `trackAffiliateClick(paddleId, url, utmSource, utmMedium, utmCampaign)`
       - Append UTM params to URL: `url?utm_source=pickleiq&utm_medium=chat&utm_campaign=ai_recommendation`
       - Use fetch with `keepalive: true` to log click to Edge Route Handler (backend)
       - POST to `/api/affiliate-log` (optional, or POST directly to analytics if configured)
       - Preserve existing query params (merge, don't replace)
       - On error: still open link (don't block user)

    2. **Keepalive fetch pattern**:
       ```typescript
       fetch(`/api/affiliate-log`, {
         method: "POST",
         keepalive: true,
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ paddleId, url, utmSource, ... })
       }).catch(() => {}); // Fail silently, user already gets link
       ```

    3. **Test coverage** (frontend/tests/affiliate.test.ts):
       - Test UTM param appending (no duplicates)
       - Test keepalive fetch call
       - Test error handling (link still opens)
       - Test various affiliate link formats

    ---

    **Part B: Admin Panel**

    4. **Admin authentication** (frontend/lib/auth.ts):
       - Function: `validateAdminSecret(requestHeaders)` → boolean
       - Check header: `X-Admin-Secret: {ADMIN_SECRET}` OR query param `?admin_key={ADMIN_SECRET}`
       - Validate against `process.env.ADMIN_SECRET` (server-side)
       - Return true/false

    5. **Admin layout** (frontend/app/admin/layout.tsx):
       - Middleware-like check: if not admin, redirect to `/` with message
       - If admin: show sidebar with links to /admin/queue and /admin/catalog
       - Logout button (clear admin_key param, reload)

    6. **Review queue page** (frontend/app/admin/queue/page.tsx):
       - Fetch review queue items (backend endpoint TBD: GET /admin/queue)
       - Table showing:
         - Paddle name, brand, model
         - Submitted by (SKU dedup suggestion)
         - Status (pending, approved, rejected)
         - Action buttons: Approve, Reject, View Details
       - Filter by status
       - Pagination (20 items per page)

    7. **Admin catalog page** (frontend/app/admin/catalog/page.tsx):
       - Search paddles by name/brand
       - Table showing all paddles:
         - Brand, Model, Core, Face, Swingweight
         - Price (latest)
         - Specs version
         - Action buttons: Edit, Delete, View
       - Edit form (modal or new page):
         - Edit paddle specs (swingweight, twistweight, core, face)
         - Change category/tags
         - Manual price adjustment (temp, for testing)
       - Delete confirmation
       - Add new paddle button (basic CRUD)

    8. **Admin Review Queue component** (frontend/components/AdminReviewQueue.tsx):
       - Render queue items as table
       - Status badge styling (pending=yellow, approved=green, rejected=red)
       - Click row to expand and show full spec diff
       - Approve/Reject buttons with confirmation

    9. **Admin Catalog component** (frontend/components/AdminCatalog.tsx):
       - Render paddle list as editable table
       - Inline edit for key fields (optional)
       - Or modal/page-based edit form
       - Delete with confirmation
       - Add paddle form

    10. **Backend admin endpoints** (TBD, reference only):
        - GET /admin/queue (authenticate with ADMIN_SECRET header)
        - POST /admin/queue/{id}/approve
        - POST /admin/queue/{id}/reject
        - GET /admin/catalog (with search params)
        - PUT /admin/catalog/{id}
        - DELETE /admin/catalog/{id}
        - POST /admin/catalog

    11. **Test coverage** (frontend/tests/admin.test.ts):
        - Test admin secret validation (correct, incorrect, missing)
        - Test review queue table rendering
        - Test approve/reject flow
        - Test catalog CRUD operations
        - (Backend tests for endpoints in Phase 6)

    **Admin panel constraints:**
    - No full user authentication yet (Phase 5 adds Clerk)
    - ADMIN_SECRET only → minimal security (suitable for staging)
    - No role-based access control yet
  </action>
  <verify>
    <automated>
      npm test -- affiliate.test.ts 2>&1 | grep -q "passed" && echo "PASS: Affiliate tests pass" || echo "FAIL: Affiliate tests fail"
      npm test -- admin.test.ts 2>&1 | grep -q "passed" && echo "PASS: Admin tests pass" || echo "FAIL: Admin tests fail"
      npm run build 2>&1 | grep -q "Compiled successfully" && echo "PASS: Build includes tracking and admin" || echo "FAIL: Build failed"
    </automated>
  </verify>
  <done>
    ✅ Affiliate click tracking logs to backend with keepalive fetch
    ✅ UTM parameters preserved and appended to affiliate links
    ✅ Admin panel requires ADMIN_SECRET (header or query param)
    ✅ /admin/queue shows review queue items (status: pending/approved/rejected)
    ✅ /admin/catalog allows CRUD operations on paddle catalog
    ✅ Admin authentication validation tested
    ✅ 3 affiliate tests passing (UTM appending, keepalive, error handling)
    ✅ 4 admin tests passing (secret validation, queue rendering, CRUD operations)
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Wave 5 Checkpoint: Full Frontend E2E + Accessibility Verification</name>
  <what-built>
    All 5 waves completed:
    - Next.js 14 scaffolding with Tailwind + shadcn/ui
    - 3-step quiz onboarding (skill → style → budget)
    - Chat widget streaming from Phase 3 /chat endpoint
    - Comparison page with search and RadarChart visualization
    - Affiliate tracking with keepalive fetch
    - Admin panel (/admin/queue, /admin/catalog) protected by ADMIN_SECRET
    - 22+ tests passing (4 quiz + 5 chat + 6 comparison + 3 affiliate + 4 admin)
  </what-built>
  <how-to-verify>
    **Manual E2E Testing via /browse**:

    1. **Landing Page**
       - Visit https://pickleiq-staging.vercel.app/ (or local http://localhost:3000)
       - Verify hero section, "Começar Quiz" button visible
       - Check no console errors (DevTools → Console)

    2. **Quiz Flow**
       - Click "Começar Quiz"
       - Step 1: Select skill level (Principiante/Intermediário/Avançado)
       - Verify URL param updates: `?skill=principiante`
       - Step 2: Select play style (Defensivo/Ofensivo/Equilibrado)
       - Verify URL param: `?skill=...&style=defensivo`
       - Step 3: Select budget (Baixo/Médio/Alto)
       - Click "Começar Chat" → redirects to chat with all params

    3. **Chat Widget**
       - Enter query: "Quero uma raqueta para principiante com orçamento baixo"
       - Verify message appears on screen
       - Verify response streams in real-time (SSE)
       - Check product cards render in chat with paddle specs
       - Click "Comprar com Afiliado" on a product card
       - Verify link opens in new tab with UTM params (utm_source=pickleiq)

    4. **Comparison Page**
       - From product card, click "Ver Mais"
       - Verify comparison page loads with paddle details
       - Search for another paddle (e.g., "Selkirk")
       - Verify autocomplete suggestions appear
       - Add 2-3 paddles to comparison
       - Verify side-by-side table shows specs (brand, model, price, swingweight, core, face)
       - Verify RadarChart renders without errors (inspect DevTools for hydration warnings)
       - Test on mobile viewport (DevTools → responsive mode):
         - Table should stack vertically
         - RadarChart should be responsive
         - No layout shifts or console errors

    5. **Affiliate Tracking**
       - Open DevTools → Network tab
       - Click an affiliate link
       - Verify fetch call to `/api/affiliate-log` with keepalive (appears in Network tab)
       - Verify URL has UTM params: `utm_source=pickleiq&utm_medium=chat&utm_campaign=...`
       - On slow network (DevTools → Throttle to "Slow 3G"):
         - Click affiliate link
         - Link still opens immediately (keepalive doesn't block)

    6. **Admin Panel**
       - Visit https://pickleiq-staging.vercel.app/admin/queue?admin_key={ADMIN_SECRET}
       - Replace {ADMIN_SECRET} with actual env var
       - Verify review queue page loads (no auth error)
       - Check admin_key in query params (or X-Admin-Secret header)
       - Visit https://pickleiq-staging.vercel.app/admin/catalog
       - Verify catalog page loads with paddle list
       - (CRUD operations optional for Phase 4 verification; backend endpoints TBD)

    7. **Accessibility & Performance**
       - Run Lighthouse (DevTools → Lighthouse tab):
         - Performance ≥ 90
         - Accessibility ≥ 90
         - Best Practices ≥ 85
       - Test mobile (iOS/Android via /browse or physical device):
         - No console errors
         - All buttons/links clickable
         - Chat scrolls smoothly
         - Images load and display correctly
       - Test keyboard navigation:
         - Tab through quiz steps
         - Tab through chat input + send button
         - Tab through comparison table
       - Test dark mode (if implemented): verify colors readable

    **Automated Tests**:
    - Run `npm test` and verify all 22+ tests passing:
      ```bash
      npm test 2>&1 | tail -20
      ```
    - Build succeeds: `npm run build`
    - No warnings: `npm run lint` (if configured)

    **Vercel Deployment Check**:
    - Preview deployment URL is live
    - All env vars configured (NEXT_PUBLIC_API_URL, ADMIN_SECRET)
    - No build errors in Vercel logs
  </how-to-verify>
  <resume-signal>
    Type one of:
    - "verified" — all checks passed, ready to merge
    - "issues: [list]" — describe issues found (e.g., "console error on mobile", "RadarChart hydration warning")
    - "retry" — need to redeploy or re-run tests
  </resume-signal>
</task>

</tasks>

<verification>
**Phase 4 Completion Checklist:**

- [ ] Wave 1 (Scaffolding): Next.js 14 app builds, landing page renders, env vars configured
- [ ] Wave 2 (Quiz): 3-step quiz flow works, state in URL params, redirects to chat
- [ ] Wave 3 (Chat): Chat widget streams from /api/chat proxy, product cards render, affiliate link ready
- [ ] Wave 4 (Comparison): Search/autocomplete functional, side-by-side table displays, RadarChart renders (ssr: false)
- [ ] Wave 5 (Tracking + Admin): Affiliate keepalive logged, admin panel requires ADMIN_SECRET, /admin/queue and /admin/catalog accessible
- [ ] Testing: 22+ tests passing (quiz 4, chat 5, comparison 6, affiliate 3, admin 4)
- [ ] Vercel deployment: Preview URL live, no build errors, env vars set
- [ ] Lighthouse: Performance ≥ 90, Accessibility ≥ 90
- [ ] Mobile: No console errors (iOS/Android), responsive layout, RadarChart hydration-safe
- [ ] E2E flow: Quiz → Chat → Comparison → Affiliate click → Admin panel all work end-to-end

**Blockers to launch Phase 5:**
- Phase 3 /chat endpoint must be live (handled: verified in depends_on)
- Backend admin endpoints for /admin/queue and /admin/catalog (Phase 6 or concurrent with admin panel)
- All 22 tests passing
- Lighthouse ≥ 90 on performance/accessibility
</verification>

<success_criteria>
Phase 4 is **DONE** when:

1. **All 5 waves executed** (scaffolding, quiz, chat, comparison, tracking + admin)
2. **22+ tests passing** (≥ 4 quiz, ≥ 5 chat, ≥ 6 comparison, ≥ 3 affiliate, ≥ 4 admin)
3. **Vercel preview deployment live** with all env vars configured
4. **E2E flow verified**:
   - User completes quiz (3 steps) → chat widget launches
   - Chat streams responses from Phase 3 /chat endpoint
   - Product cards render with affiliate links
   - Comparison page searches/filters paddles, displays RadarChart
   - Affiliate clicks log with keepalive fetch + UTM params
   - Admin panel accessible with ADMIN_SECRET
5. **Lighthouse scores ≥ 90** (performance + accessibility)
6. **Mobile testing passed** (iOS/Android, no console errors, responsive layout)
7. **Zero hydration errors** (RadarChart ssr: false confirmed)
8. **Code merged to main** and committed with summary

**Measurable outcomes:**
- Quiz completion → chat launch (100% of users)
- Chat response time: average < 2s (Phase 3 P95 < 3s)
- Affiliate clicks logged: 100% with keepalive
- Admin panel: secure (ADMIN_SECRET validated)
- Test coverage: ≥ 70% for critical paths (quiz, chat, comparison, tracking)
</success_criteria>

<output>
After completion, create `.planning/phases/04-frontend-chat-product-ui/04-COMPLETE-SUMMARY.md` with:

**Phase 4 Complete: Frontend Chat & Product UI**
- **Waves**: 5 (scaffolding → quiz → chat → comparison → tracking + admin)
- **Tasks**: 6 (scaffolding, quiz, chat, comparison, affiliate + admin, verification checkpoint)
- **Tests**: 22+ passing (4 quiz, 5 chat, 6 comparison, 3 affiliate, 4 admin)
- **Deployment**: Vercel preview URL, all env vars configured
- **E2E verified**: Quiz → Chat → Comparison → Affiliate → Admin panel
- **Lighthouse**: Performance ≥ 90, Accessibility ≥ 90
- **Blockers resolved**: Phase 3 /chat endpoint verified, admin endpoints documented
- **Next phase**: Phase 5 (SEO & Growth Features) — Clerk auth, price alerts, history page

**Key decisions**:
- Quiz state in URL params (no DB needed yet, Phase 5 adds persistence with Clerk)
- Admin panel: ADMIN_SECRET only (Phase 5 upgrades to Clerk role-based access)
- RadarChart: ssr: false with dynamic import (prevents hydration mismatch)
- Affiliate tracking: keepalive fetch + UTM params (logs to backend for analytics)

**Files created/modified**: 31 files across app, components, hooks, lib, tests
**Documentation**: PLAN.md (this file) + COMPLETE-SUMMARY.md
</output>
