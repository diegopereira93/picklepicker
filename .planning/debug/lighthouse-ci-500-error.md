---
status: investigating
trigger: "Lighthouse CI fails in GitHub Actions with HTTP 500 errors when trying to access http://localhost:3000/"
created: 2026-04-01T00:00:00Z
updated: 2026-04-01T00:00:00Z
---

## Current Focus

hypothesis: CONFIRMED - GitHub Actions workflow has typo in Clerk env var (NEXT_PUBLIC_CLERK_PUBLISH_KEY vs NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY)
test: Verify Clerk SDK documentation and fix the typo
expecting: Lighthouse CI should pass after fixing the environment variable name
next_action: Fix the typo in .github/workflows/lighthouse.yml

## Symptoms

expected: Lighthouse CI should successfully audit the Next.js app running on localhost:3000
actual: Lighthouse fails with "ERRORED_DOCUMENT_REQUEST" and "Status code: 500" for all page requests
errors: |
  Runtime error encountered: Lighthouse was unable to reliably load the page you requested.
  Make sure you are testing the correct URL and that the server is properly responding to all requests.
  (Status code: 500)
reproduction: Run `npm run lighthouse:ci` in GitHub Actions or locally without backend running
timeline: Recent commits show attempts to fix: "force dynamic rendering for paddles page", "configure Lighthouse CI to start Next.js server", "add error handling for backend unavailability during SSG"
started: Recent (commits from phase-12-data-pipeline-quality branch)

## Eliminated

## Evidence

- timestamp: 2026-04-01T00:00:00Z
  checked: .github/workflows/lighthouse.yml
  found: Environment variable NEXT_PUBLIC_CLERK_PUBLISH_KEY is set but Clerk expects NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY (missing "ABLE")
  implication: ClerkProvider fails to initialize without the correct publishable key, causing runtime 500 errors

## Resolution

root_cause: |
  Múltiplos problemas causando HTTP 500 no CI:
  1. Página `/paddles/[brand]/[model-slug]/page.tsx` fazia fetch durante SSG
  2. Workflow não tinha CLERK_SECRET_KEY (só tinha NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY)
  3. Conflito de nome entre import `dynamic` e export `const dynamic`

fix: |
  1. Renomeado import `dynamic` → `nextDynamic` para evitar conflito
  2. Adicionado `export const dynamic = 'force-dynamic'` às páginas dinâmicas
  3. Adicionado `CLERK_SECRET_KEY` ao workflow do GitHub Actions
  4. Página `/paddles` já tinha sido corrigida em commit anterior

verification: |
  - TypeScript compila sem erros
  - Build local passa
  - Aguardando CI para validação final após adicionar CLERK_SECRET_KEY

files_changed:
  - frontend/src/app/paddles/[brand]/[model-slug]/page.tsx
  - .github/workflows/lighthouse.yml
