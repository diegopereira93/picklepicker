---
phase: 04-frontend-chat-product-ui
plan: 04-02
subsystem: frontend
tags: [quiz, chat, sse, route-handler, product-card, localStorage, vercel-ai-sdk]
dependency_graph:
  requires: [04-01]
  provides: [quiz-onboarding, chat-widget, sse-proxy, product-cards, profile-management]
  affects: [chat-page, api-route]
tech_stack:
  added: [ai@6-UIMessageStream, @ai-sdk/react, DefaultChatTransport]
  patterns: [SSE-transform, edge-runtime, localStorage-UUID, TDD-red-green]
key_files:
  created:
    - frontend/src/lib/profile.ts
    - frontend/src/components/quiz/quiz-flow.tsx
    - frontend/src/components/quiz/step-level.tsx
    - frontend/src/components/quiz/step-style.tsx
    - frontend/src/components/quiz/step-budget.tsx
    - frontend/src/app/chat/page.tsx
    - frontend/src/app/api/chat/route.ts
    - frontend/src/components/chat/chat-widget.tsx
    - frontend/src/components/chat/message-bubble.tsx
    - frontend/src/components/chat/product-card.tsx
    - frontend/src/tests/unit/quiz.test.ts
    - frontend/src/tests/unit/route-handler-proxy.test.ts
    - frontend/src/tests/unit/product-card.test.ts
  modified: []
decisions:
  - "UIMessage in ai@6 has no .content property — text is extracted from msg.parts filtered by type=text"
  - "id variables in route.ts SSE parser needed explicit string type annotation due to TypeScript circular initializer inference"
  - "DefaultChatTransport used with profile in body rather than useChat body option directly"
metrics:
  duration: "5 min"
  completed_date: "2026-03-27"
  tasks_completed: 2
  files_created: 13
  tests_passing: 29
---

# Phase 04 Plan 02: Quiz Onboarding + Chat Widget + SSE Proxy Summary

**One-liner:** 3-step quiz with localStorage profile management wired to SSE-streaming chat widget via Edge Route Handler that transforms FastAPI events into Vercel AI SDK UIMessageStream format.

## What Was Built

### Task 1: Quiz Onboarding + Profile Management (13 tests pass)

- `profile.ts`: `getOrCreateUserId()` (crypto.randomUUID, persists to `pickleiq:uid`), `getProfile()`, `saveProfile()`, `clearProfile()` — all guarded for SSR (`typeof window === 'undefined'`)
- `step-level.tsx`: 3 card buttons (Iniciante/Intermediario/Avancado) with PT-BR descriptions and icons; selected state via `ring-2 ring-primary`
- `step-style.tsx`: 3 card buttons (Controle/Potencia/Equilibrado) with same selection pattern
- `step-budget.tsx`: 5 preset buttons (R$400–R$1200+) plus "Outro" custom input (R$200–R$3000)
- `quiz-flow.tsx`: State machine across 3 steps, progress dots, Voltar/Proximo navigation, Comecar on final step, editMode pre-fills from existing profile
- `chat/page.tsx`: Client component with hydration guard, shows QuizFlow full-screen if no profile, ChatWidget + "Editar perfil" button if profile exists

### Task 2: Route Handler SSE Proxy + Chat Components (16 tests pass)

- `app/api/chat/route.ts` (Edge, maxDuration=30): accepts `{ messages, profile }`, builds ChatRequest, fetches FastAPI with AbortSignal propagation, transforms SSE events:
  - `reasoning` → `text-start` + `text-delta` UIMessage parts
  - `recommendations` → `data-recommendations` data part
  - `degraded` → fallback text-delta + `data-degraded` data part
  - `done` → `finish` with finishReason=stop
  - `error` → error part
  - FastAPI unreachable or non-200 → 503
- `product-card.tsx`: renders name, brand, R$ price (pt-BR locale), stock indicator (green/yellow/red), "Comprar" affiliate link, "Recomendado" badge when similarity_score > 0.8
- `message-bubble.tsx`: user (right, primary bg) / assistant (left, muted bg) alignment; detects `ChatRecommendation[]` annotations and renders ProductCard grid
- `chat-widget.tsx`: `useChat` with `DefaultChatTransport` (profile in body), auto-scroll, typing indicator, error display, suggested questions empty state, double-submit blocked via `isLoading`

## Test Results

```
Test Files  3 passed (3)
Tests       29 passed (29)
```

- quiz.test.ts: 13/13
- route-handler-proxy.test.ts: 8/8
- product-card.test.ts: 8/8 (includes 9 scenarios)

Build: Next.js 14.2.35 compiled successfully, `/api/chat` Edge route, `/chat` static page.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] TypeScript implicit any on `id` variable in route.ts**
- **Found during:** Task 2 build
- **Issue:** `const id = textPartId ?? generateId()` — TypeScript couldn't infer the type due to circular reference with `textPartId` variable
- **Fix:** Added explicit `const id: string = textPartId ?? generateId()` in both `reasoning` and `degraded` cases
- **Files modified:** `frontend/src/app/api/chat/route.ts`
- **Commit:** cb0351b

**2. [Rule 1 - Bug] `msg.content` does not exist on UIMessage type in ai@6**
- **Found during:** Task 2 build
- **Issue:** `chat-widget.tsx` referenced `msg.content` as a fallback, but `UIMessage` in ai@6 does not expose a `.content` string — text is in `msg.parts`
- **Fix:** Removed `|| msg.content` fallback; `textContent` from parts is the authoritative source
- **Files modified:** `frontend/src/components/chat/chat-widget.tsx`
- **Commit:** cb0351b

## Known Stubs

- `ProductCard` image placeholder ("Foto em breve") — intentional; real paddle images deferred to Phase 5 SEO/media plan
- `in_stock` defaults to `available` when neither `in_stock` nor `stock_level` prop provided — stock data not yet in backend response

## Self-Check: PASSED

Files verified:
- frontend/src/lib/profile.ts — FOUND
- frontend/src/components/quiz/quiz-flow.tsx — FOUND
- frontend/src/app/api/chat/route.ts — FOUND
- frontend/src/components/chat/product-card.tsx — FOUND
- frontend/src/tests/unit/quiz.test.ts — FOUND
- frontend/src/tests/unit/route-handler-proxy.test.ts — FOUND
- frontend/src/tests/unit/product-card.test.ts — FOUND

Commits verified:
- 90ff524 (Task 1: quiz + profile) — FOUND
- cb0351b (Task 2: route handler + chat widget) — FOUND
