# Phase 08 — Navigation UX Fixes: CONTEXT

## Phase Goal
Fix four UX issues in the frontend:
1. `/compare` route doesn't exist — home and header link to it, resulting in 404
2. "Chat IA" is exposed as a direct nav link, implying it's reachable without the quiz
3. Catalog cards are not clickable (link resolves to 404 when `model_slug` is null in DB)
4. Catalog cards show only image + name + brand + price — missing useful specs and context

---

## Prior Decisions (from earlier phases)

- **Pre-chat quiz** — 3 steps (nível → estilo → orçamento) before chat; profile stored in sessionStorage/localStorage (Phase 4.2 decision)
- **`/chat` page already gates through quiz** — `chat/page.tsx` shows `QuizFlow` if no `getProfile()` result; quiz gate is implemented, just not visible via nav UX
- **`/paddles`** — exists as the public catalog listing (ISR, grid of paddle cards)
- **Comparador with radar chart** — was planned in PROJECT.md as a future feature but **never built**; no `/compare` route exists
- **Clerk auth** — header uses `useAuth()` for sign-in/out; any nav changes must preserve this

---

## Decisions

### 1. Fix broken `/compare` links

**Decision:** Replace all `href="/compare"` references with `href="/paddles"`.

- Affected files: `frontend/src/components/layout/header.tsx`, `frontend/src/app/page.tsx`
- Label change: "Comparar" → "Catálogo" (or "Ver Raquetes") in header nav
- Label change: "Ver comparador" → "Ver catálogo" in home page hero CTA
- The full side-by-side radar chart comparador is deferred — no stub page needed

### 2. Remove "Chat IA" from header nav

**Decision:** Remove the `{ href: "/chat", label: "Chat IA" }` entry from `navLinks` in `header.tsx`.

- Rationale: The quiz → chat flow should be the only entry point to the AI. Exposing "Chat IA" in the top nav implies it's a standalone feature, not a guided wizard.
- The "Encontrar raquete" CTA button in the header stays as-is (href="/chat") — this is the correct entry point since `/chat` already shows the quiz first when no profile exists.
- Result: header nav becomes `[Home, Catálogo]` + the "Encontrar raquete" button CTA

### 3. Home page CTAs — no change needed

**Decision:** Leave home page CTAs pointing at `/chat`.

- "Comecar agora" (hero) → `/chat` ✓ correct (quiz gate is inside)
- "Falar com o PickleIQ" (CTA banner) → `/chat` ✓ correct
- Only the secondary outline button "Ver comparador" → fix to "Ver catálogo" → `/paddles`

### 4. No new routes needed

**Decision:** Do NOT create a `/quiz` standalone page or a `/compare` stub.

- The current `/chat` page already handles the quiz → chat flow correctly
- Creating a `/quiz` route would be a new capability and out of scope for this fix
- The broken `/compare` is fixed by pointing to the existing `/paddles` catalog

### 5. Fix catalog card navigation (404 on click)

**Root cause:** `paddles/page.tsx` builds the link href as:
```tsx
href={`/paddles/${paddle.brand?.toLowerCase()}/${paddle.model_slug ?? String(paddle.id)}`}
```
When `model_slug` is null in DB, it uses `String(paddle.id)` (e.g. `42`). But `fetchProductData` in `seo.ts` queries:
```
/api/v1/paddles?brand=selkirk&model_slug=42
```
The backend returns empty since no paddle has `model_slug="42"` — result: 404.

**Decision:** Update `fetchProductData` in `frontend/src/lib/seo.ts` to fall back to an ID-based lookup when `modelSlug` is a pure integer string:

```ts
// If model_slug lookup returns empty AND modelSlug is numeric, try by ID
if (!paddle && /^\d+$/.test(modelSlug)) {
  const idRes = await fetch(`${FASTAPI_URL}/api/v1/paddles/${modelSlug}`)
  if (idRes.ok) {
    const idData = await idRes.json()
    return idData.data ?? idData ?? null
  }
}
```

- The backend FastAPI already has a `/api/v1/paddles/{id}` endpoint (confirmed from route structure)
- No changes needed to URL generation in `paddles/page.tsx`
- No new routes needed

### 6. Improve catalog card information

**Decision:** Add useful fields to each paddle card in `frontend/src/app/paddles/page.tsx`. The list API already returns all fields — just render them.

Fields to add to each card (only if not null):
- `skill_level` — badge: "Iniciante" / "Intermediário" / "Avançado"
- `specs.swingweight` — shown as "SW: {value}"
- `specs.core_thickness_mm` — shown as "Core: {value}mm"
- `in_stock` — boolean badge: "Em estoque" (green) / "Fora de estoque" (gray)

**Visual placement:** Below the brand name, above the price. Use small text/badges — keep card compact.

**Do NOT** add description snippet (too long for card), rating (sparse data).

---

## Scope Boundaries

**In scope:**
- Fix `href="/compare"` → `href="/paddles"` (header + home page)
- Update label "Comparar" → "Catálogo" in header nav
- Update label "Ver comparador" → "Ver catálogo" in home page
- Remove "Chat IA" from `navLinks` array in header
- Fix `fetchProductData` fallback for numeric-slug → ID lookup
- Add skill_level, swingweight, core_thickness_mm, in_stock to catalog cards

**Out of scope (deferred):**
- Building the actual comparador with radar charts (separate future phase)
- Creating a standalone `/quiz` route
- Any changes to the quiz component or chat widget internals
- Mobile nav behavior changes beyond the navLinks array fix
- Rating/review display on cards

---

## Files to Change

| File | Change |
|------|--------|
| `frontend/src/components/layout/header.tsx` | Remove `{ href: "/chat", label: "Chat IA" }` from navLinks; change `/compare` → `/paddles` with label "Catálogo" |
| `frontend/src/app/page.tsx` | Change `<Link href="/compare">Ver comparador</Link>` → `<Link href="/paddles">Ver catálogo</Link>` |
| `frontend/src/lib/seo.ts` | Add numeric-slug ID fallback in `fetchProductData` |
| `frontend/src/app/paddles/page.tsx` | Add skill_level, swingweight, core_thickness_mm, in_stock to paddle cards |

---

## Deferred Ideas

- Full comparador with side-by-side radar chart (was in PROJECT.md "done" definition — needs its own phase)
- Standalone `/quiz` route as a dedicated onboarding page
- Rating/review count on catalog cards (data too sparse currently)
