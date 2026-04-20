# Phase 28: Critical Bug Fixes & Language Fix — Research

**Researched:** 2026-04-20
**Discovery Level:** 1 — Quick Verification (codebase pattern analysis)

---

## Standard Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js 14 App Router | 14.x |
| Styling | Tailwind CSS + shadcn/ui (base-ui) | dark-only theme |
| UI Library | @base-ui/react (Button, Dialog, etc.) | via shadcn |
| Font Stack | Bebas Neue (display), Source Sans 3 (body), JetBrains Mono (mono) | Google Fonts |
| Auth | Clerk | @clerk wrapper |
| Storage | localStorage (profiles) + Supabase (backend) | |

## Design Tokens (from tailwind.config.ts)

```
Background hierarchy: base=#0a0a0a, surface=#141414, elevated=#1f1f1f
Brand: primary=#84CC16 (lime), secondary=#F97316 (orange)
Text: primary=#FAFAFA, secondary=#A3A3A3, muted=#737373, disabled=#525252
Semantic: success=#84CC16, warning=#FBBF24, danger=#EF4444, info=#60A5FA
Border radius: rounded-rounded, rounded-sharp (from design-tokens.css)
Font: font-display (Bebas Neue), font-sans (Source Sans 3), font-mono (JetBrains Mono)
```

## Architecture Patterns

### Button System
Current app uses shadcn `<Button>` component with variants:
- `default` — primary action (filled bg)
- `outline` — secondary with border
- `ghost` — minimal, hover-only
- `destructive` — danger action
- `link` — text-only with underline

Sizes: `xs`, `sm`, `default`, `lg`, `icon`

**Legacy classes to replace:**
| Legacy Class | Replacement |
|-------------|-------------|
| `wg-button-coral` | `<Button variant="default" className="bg-brand-secondary">` or `bg-brand-secondary hover:bg-brand-secondary/80 text-white rounded-lg` |
| `wg-button-ghost` | `<Button variant="ghost">` |
| `wg-button-outline` | `<Button variant="outline">` |
| `wg-container` | `container mx-auto px-4` |
| `wg-profile-summary` | `bg-surface rounded-lg p-6 border border-border` |
| `wg-recommendation-card` | `bg-surface rounded-lg p-4 shadow-md border border-border` |
| `wg-animate-fade-up` | Remove (or use `animate-in fade-in slide-in-from-bottom-4`) |
| `wg-why-matches` | `bg-elevated rounded-lg p-3 mt-2` |
| `wg-section-light` | (not in Phase 28 scope — noted for Phase 29+) |

### Layout Containers
Working catalog page pattern: `min-h-screen bg-base` → `bg-surface rounded-lg` for cards

### Color Replacements (Light → Dark)

| Light Theme (Current in broken pages) | Dark Theme Token |
|--------------------------------------|-----------------|
| `bg-[var(--warm-white)]` | `bg-base` |
| `text-[#2A2A2A]` (dark text) | `text-text-primary` |
| `text-[#757575]` (gray text) | `text-text-muted` |
| `text-[#84CC16]` | `text-brand-primary` |
| `text-[#F97316]` | `text-brand-secondary` |
| `bg-[#F5F2EB]` (light bg) | `bg-elevated` |
| `bg-yellow-50` | `bg-elevated` |
| `text-gray-600` | `text-text-secondary` |
| `text-green-700` | `text-brand-primary` |
| `text-coral` | `text-brand-secondary` |
| `hover:bg-[#EA580C]` | `hover:bg-brand-secondary/80` |
| `hover:text-[#F97316]` | `hover:text-brand-secondary` |
| `border-[#757575]` | `border-border` |
| `hover:bg-[#F97316]/5` | `hover:bg-brand-secondary/10` |

## FR-01: Broken Gift & Quiz Results Pages

### Gift Page (`frontend/src/app/gift/page.tsx`)
**Issues found (all steps: welcome, recipient, budget, analyzing, results):**
- 6 instances of `bg-[var(--warm-white)]` → `bg-base`
- 3 instances of `wg-button-coral` → use Button component or Tailwind classes
- 3 instances of `wg-button-ghost` → use Button component or Tailwind classes
- `text-coral` → `text-brand-secondary`
- `text-gray-600` → `text-text-secondary`
- `bg-yellow-50` → `bg-elevated`
- `text-green-700` → `text-brand-primary`
- Step-specific text labels already in Portuguese ✓

### Gift Results Page (`frontend/src/app/gift/results/page.tsx`)
**Issues found:**
- `wg-button-coral` (1 instance)
- `wg-button-ghost` (2 instances)
- `bg-[var(--warm-white)]` or similar light backgrounds → `bg-base`

### Quiz Results Page (`frontend/src/app/quiz/results/page.tsx`)
**Issues found (most severely broken):**
- `wg-container` (2 instances) → `container mx-auto px-4`
- `wg-profile-summary` (1 instance) → `bg-surface rounded-lg p-6`
- `wg-recommendation-card` (1 instance) → `bg-surface rounded-lg p-4 shadow-md`
- `wg-animate-fade-up` (1 instance) → remove or use animation
- `wg-why-matches` (1 instance) → `bg-elevated rounded-lg p-3`
- `wg-button-coral` (2 instances)
- `wg-button-ghost` (1 instance)
- `wg-button-outline` (1 instance)
- 12+ hardcoded hex colors → Tailwind tokens
- Light theme background colors throughout

## FR-02: HTML Language Attribute

**Root layout (`frontend/src/app/layout.tsx`):**
- Line: `<html lang="en"` → `<html lang="pt-BR"`
- Metadata title: "PickleIQ — AI Pickleball Paddle Advisor" → Portuguese
- Metadata description: English text → Portuguese
- Missing: OpenGraph locale, alternate language tags

**Proposed metadata:**
```typescript
export const metadata: Metadata = {
  title: "PickleIQ — Recomendações Inteligentes de Raquetes de Pickleball",
  description: "Encontre a raquete de pickleball perfeita com IA. Compare preços, veja especificações técnicas e receba recomendações personalizadas em português.",
};
```

## FR-03: Quiz Profile Storage Mismatch

### Two Profile Modules (CRITICAL MISMATCH)

**`@/lib/quiz-profile.ts`:**
- Storage key: `pickleiq_player_profile`
- Type: `QuizProfile` (7 fields: level, style, priority, budget, weightPreference, location, targetPaddle)
- Exports: `saveQuizProfile`, `loadQuizProfile`, `clearQuizProfile`, `hasQuizProfile`, `getProfileSummary`
- Used BY (writes): `quiz/page.tsx`
- Used BY (reads): `chat/page.tsx`, `compare/page.tsx`, `player-profile-sidebar.tsx`

**`@/lib/profile.ts`:**
- Storage key: `pickleiq:profile:{uid}` (user-specific via getOrCreateUserId)
- Type: `UserProfile` (3 fields: level, style, budget_max) — simpler shape
- Auth-aware: tries Clerk JWT first, falls back to localStorage
- Exports: `getProfile`, `saveProfile`, `clearProfile`, `getOrCreateUserId`, `migrateProfileOnLogin`
- Used BY (writes): `quiz-widget.tsx`, `home-client.tsx`
- Used BY (reads): `quiz/results/page.tsx`, `catalog-client.tsx`, `home-client.tsx`

### The Bug
1. User completes quiz on `/quiz` → `saveQuizProfile()` writes to key `pickleiq_player_profile`
2. User is redirected to `/quiz/results` → `getProfile()` reads from key `pickleiq:profile:{uid}`
3. Different keys → results page sees no profile → redirect loop or empty results

### Fix Strategy
Change `quiz/results/page.tsx` to import from `@/lib/quiz-profile` instead of `@/lib/profile`:
- Replace `import { getProfile, clearProfile } from '@/lib/profile'`
- With `import { loadQuizProfile, clearQuizProfile } from '@/lib/quiz-profile'`
- Update usage: `getProfile()` → `loadQuizProfile()`, `clearProfile()` → `clearQuizProfile()`
- Adjust type references from `UserProfile` to `QuizProfile`

**Do NOT delete `@/lib/profile.ts`** — other components legitimately use it (catalog-client, home-client). The two modules serve different purposes:
- `quiz-profile.ts` = quiz-specific rich profile (7 fields)
- `profile.ts` = minimal user profile with auth awareness (3 fields)

## FR-14: English Strings in UI

### Known English Strings
| File | Line | Current | Fix |
|------|------|---------|-----|
| `product-card.tsx` | 156 | "Details" | "Detalhes" |
| `product-card.tsx` | 165 | "Compare" | "Comparar" |

### Scan Results (other potential English)
- `home-client.tsx` has `wg-button-coral` but text is already Portuguese
- `quiz-profile.ts` has English labels in `getProfileSummary()` (e.g., "Beginner", "Priority: Power") — but these are internal/developer-facing, not user-facing. Still should be noted.
- Landing page CTAs: "VER MAIS OPÇÕES →" is Portuguese but uses ALL CAPS (not sentence case per design system)

## Common Pitfalls

1. **Don't use `var(--warm-white)`** — it was from the old light theme. Doesn't exist in current CSS.
2. **Don't mix light/dark colors** — all pages must use `bg-base` as root, never light backgrounds.
3. **Don't delete `@/lib/profile.ts`** — used by catalog, home, quiz-widget. Only fix the import in quiz/results.
4. **Don't forget `font-display`** — headings should use `font-display` (Bebas Neue) for consistent brand feel.
5. **wg- classes are NOT defined anywhere** — they were from a legacy CSS file that was removed during the v2.1 redesign. All replacements must be Tailwind utility classes or shadcn Button components.
6. **home-client.tsx also has wg- classes** — but that's Phase 29 scope (Core UX), not Phase 28.

## Out of Scope for Phase 28

- `home-client.tsx` wg- class cleanup (Phase 29)
- Landing page visual overhaul (Phase 29, FR-09)
- Quiz profile `getProfileSummary()` English labels (internal, non-blocking)
- Full i18n system setup (Phase 30+)
- Price alerts frontend flow (Phase 29, FR-13)
