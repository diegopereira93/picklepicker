---
phase: 25-fix-frontend-tests
plan: 01
status: complete
completed_at: "2026-04-12"
---

# Phase 25 — Fix Frontend Test Failures

## What was done

Fixed 3 frontend test failures caused by code drift after v2.1.0 redesign:

1. **Deleted `quiz-flow.tsx`** — Dead code importing deleted step components (`step-level`, `step-style`, `step-budget`). App uses `quiz-widget.tsx` instead.

2. **Rewrote `quiz.test.ts`** — Replaced QuizFlow tests with QuizWidget component tests. Added `await` to async `getProfile()`/`saveProfile()` calls. Tests cover: section rendering, button disabled state, selection flow, onComplete callback, localStorage persistence.

3. **Fixed `session-upgrade.test.ts`** — Added `__clerk_client_jwt` to localStorage mock so `getAuthToken()` returns truthy value, allowing `migrateProfileOnLogin` to pass auth check and reach the mocked fetch.

## Verification

- `npx vitest run` — **19/19 suites pass, 179 tests, 0 failures**
- Dead code removed: `quiz-flow.tsx` deleted
- No references to `quiz-flow` remain in test files

## Commits

- `141cf2b` — fix(25-01): rewrite quiz tests to match actual QuizWidget labels
- `ed757e0` — fix(25-01): add button count check for debugging
- `85d6943` — fix(25-01): fix button text matching to avoid encoding issues
- `b46e209` — fix(25-01): add userEvent import and fix style button selection
- `dfd23dd` — fix(25-01): fix QuizWidget tests - use exact text matching
- `96c580b` — fix(25-01): add Clerk auth token mock to session-upgrade tests
- `f0f311a` — fix(25-01): remove dead quiz-flow.tsx and rewrite quiz.test.ts
- `8afa2a8` — docs(25): create phase plan
