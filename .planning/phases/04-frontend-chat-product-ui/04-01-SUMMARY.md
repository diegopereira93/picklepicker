---
phase: 04-frontend-chat-product-ui
plan: 04-01
subsystem: frontend
tags: [nextjs, tailwind, shadcn-ui, typescript, vitest, layout]
dependency_graph:
  requires: []
  provides: [frontend-scaffold, shadcn-components, typescript-types, api-client, layout]
  affects: [04-02, 04-03, 04-04, 04-05]
tech_stack:
  added: [next@14.2.35, tailwindcss@3, tailwindcss-animate, shadcn-ui-radix-v3, vitest@4, @testing-library/react, lucide-react, recharts, ai, @ai-sdk/react]
  patterns: [App Router, Tailwind CSS Variables, Radix UI primitives, TDD RED-GREEN]
key_files:
  created:
    - frontend/package.json
    - frontend/tailwind.config.ts
    - frontend/vitest.config.ts
    - frontend/next.config.mjs
    - frontend/components.json
    - frontend/.env.example
    - frontend/src/app/globals.css
    - frontend/src/app/layout.tsx
    - frontend/src/app/page.tsx
    - frontend/src/lib/utils.ts
    - frontend/src/lib/api.ts
    - frontend/src/types/paddle.ts
    - frontend/src/components/layout/header.tsx
    - frontend/src/components/layout/footer.tsx
    - frontend/src/components/ui/button.tsx
    - frontend/src/components/ui/card.tsx
    - frontend/src/components/ui/input.tsx
    - frontend/src/components/ui/badge.tsx
    - frontend/src/components/ui/separator.tsx
    - frontend/src/components/ui/skeleton.tsx
    - frontend/src/components/ui/tabs.tsx
    - frontend/src/components/ui/select.tsx
    - frontend/src/components/ui/label.tsx
    - frontend/src/components/ui/dialog.tsx
    - frontend/src/components/ui/dropdown-menu.tsx
    - frontend/src/components/ui/sheet.tsx
    - frontend/src/tests/setup.ts
    - frontend/src/tests/types.test.ts
    - frontend/src/tests/api.test.ts
  modified: []
decisions:
  - shadcn init used base-nova style (Tailwind v4 + @base-ui/react) — all UI components rewritten with standard Radix UI primitives and HSL CSS variables for Tailwind v3 compatibility
  - globals.css converted from oklch/tw-animate-css imports to standard Tailwind v3 @tailwind directives with HSL variables
  - tailwindcss-animate installed separately; tailwind.config.ts extended with full shadcn color token mapping
  - Geist font replaced with Inter (Geist not available in next/font/google for Next.js 14.2)
  - .env.local gitignored; .env.example committed with NEXT_PUBLIC_FASTAPI_URL and ADMIN_SECRET
metrics:
  duration: "14 min"
  completed: "2026-03-27"
  tasks: 2
  files: 29
---

# Phase 4 Plan 1: Frontend Scaffold — Next.js 14 + Tailwind + shadcn/ui

Next.js 14 App Router project scaffolded with Tailwind v3 + Radix UI shadcn components, TypeScript types mirroring all backend Pydantic schemas, typed API client, responsive Header/Footer layout, and Vitest test runner — all Wave 2+ plans can build features without setup overhead.

## Tasks Completed

| # | Task | Commit | Status |
|---|------|--------|--------|
| 1 | Scaffold Next.js 14 + Tailwind + shadcn/ui | 2a7d976 | Done |
| 2 | TypeScript types, API client, layout (TDD) | df7a65a | Done |

## Test Results

- **8/8 tests passing**
- types.test.ts (5 tests): PaddleListResponse, ChatRequest, Paddle, PriceSnapshot, ReviewQueueItem shapes
- api.test.ts (3 tests): fetchPaddles URL params, 503 graceful fallback, NEXT_PUBLIC_FASTAPI_URL base

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] shadcn init generated Tailwind v4 / @base-ui/react components incompatible with Next.js 14**
- **Found during:** Task 1
- **Issue:** Running `npx shadcn@latest init` with the newer CLI generated components using `@base-ui/react/*` imports and `oklch()` CSS color functions (Tailwind v4 syntax), which fail to compile under Tailwind v3 + Next.js 14
- **Fix:** Rewrote all 11 UI components (button, badge, input, card, separator, label, tabs, dialog, dropdown-menu, select, sheet) using standard Radix UI primitives; rewrote globals.css with HSL CSS variables + standard `@tailwind` directives; rewrote tailwind.config.ts with full shadcn Tailwind v3 color token mapping + `tailwindcss-animate`
- **Files modified:** All `frontend/src/components/ui/*.tsx`, `frontend/src/app/globals.css`, `frontend/tailwind.config.ts`
- **Commit:** 2a7d976

**2. [Rule 1 - Bug] Geist font not available in next/font/google for Next.js 14.2**
- **Found during:** Task 1 (first build attempt)
- **Issue:** shadcn init generated layout.tsx importing `Geist` from `next/font/google` which errors on Next.js 14
- **Fix:** Replaced with `Inter` from `next/font/google`
- **Files modified:** `frontend/src/app/layout.tsx`
- **Commit:** 2a7d976

**3. [Rule 1 - Bug] ESLint `@typescript-eslint/no-empty-object-type` on InputProps interface**
- **Found during:** Task 1 build verification
- **Issue:** `export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}` fails ESLint strict rule
- **Fix:** Replaced interface with type alias: `export type InputProps = React.InputHTMLAttributes<HTMLInputElement>`
- **Files modified:** `frontend/src/components/ui/input.tsx`
- **Commit:** 2a7d976

**4. [Rule 1 - Bug] ESLint unused type imports in types.test.ts**
- **Found during:** Task 2 build verification
- **Issue:** `PaddleSpecs`, `ChatRecommendation`, `UserProfile` imported but not used in tests
- **Fix:** Removed unused type imports from test file
- **Files modified:** `frontend/src/tests/types.test.ts`
- **Commit:** df7a65a

## Known Stubs

None — all layout components render real content. API client connects to real FASTAPI_URL. No hardcoded placeholder data flows to UI.

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| frontend/src/types/paddle.ts | FOUND |
| frontend/src/lib/api.ts | FOUND |
| frontend/src/components/layout/header.tsx | FOUND |
| frontend/src/components/layout/footer.tsx | FOUND |
| frontend/src/app/layout.tsx | FOUND |
| frontend/vitest.config.ts | FOUND |
| frontend/.env.example | FOUND |
| Commit 2a7d976 (scaffold) | FOUND |
| Commit 976c96d (types+layout) | FOUND |
