# Frontend — AGENTS.md

Next.js 14 App Router + Tailwind CSS + Clerk auth. PT-BR locale. Read DESIGN.md before any UI change.

## Structure

```
frontend/src/
├── app/
│   ├── layout.tsx        # ClerkProvider, Inter + JetBrains Mono, Header/Footer
│   ├── page.tsx          # Landing page
│   ├── paddles/          # Paddle listing/detail
│   ├── chat/             # Chat page (SSE streaming)
│   ├── admin/            # Admin pages
│   ├── blog/             # Blog pages
│   └── api/              # Route Handlers (admin/catalog)
├── components/
│   ├── layout/           # Header, Footer
│   ├── ui/               # 12 shared components (button, card, etc.)
│   ├── chat/             # Chat widget
│   ├── quiz/             # quiz-flow, step-level, step-budget, step-style
│   ├── products/         # Product cards/grids
│   ├── admin/            # Admin components
│   └── schema/           # Schema components
├── lib/
│   ├── api.ts            # API client (NEXT_PUBLIC_FASTAPI_URL/api/v1)
│   ├── admin-api.ts      # Admin API with Bearer auth
│   ├── clerk.ts          # Clerk config
│   ├── tracking.ts       # Affiliate click tracking
│   └── seo.ts, utils.ts, etc.
├── types/paddle.ts       # Paddle, PaddleListResponse, LatestPriceResponse
├── hooks/use-announcer.ts # Accessibility
├── tests/                # Vitest (jsdom), 12 unit test files
└── middleware.ts          # Clerk middleware
```

## Where to Look

| Task | Location |
|------|----------|
| Add page/route | `src/app/` — follow App Router convention |
| Fix UI component | `src/components/` — read DESIGN.md first |
| Change API client | `src/lib/api.ts` — all backend calls go here |
| Modify quiz flow | `src/components/quiz/` — quiz-flow.tsx orchestrates steps |
| Auth changes | `src/middleware.ts` + `src/lib/clerk.ts` |
| Add TypeScript type | `src/types/paddle.ts` |
| Admin functionality | `src/app/admin/` + `src/lib/admin-api.ts` |

## Conventions

- **DESIGN.md is law** — Lime (#84CC16) on dark only. Green (#76b900) for data. 2px border-radius.
- **Fonts** — Inter (body), JetBrains Mono (data/specs), loaded via `next/font`.
- **PT-BR** — `lang="pt-BR"` on html. Portuguese UI copy.
- **API** — all calls through `src/lib/api.ts`. Backend at `NEXT_PUBLIC_FASTAPI_URL`.
- **Auth** — Clerk. Admin uses Bearer token (`ADMIN_SECRET`).
- **Tests** — Vitest with jsdom. `npm run test`.
- **No CSS modules** — Tailwind CSS only.

## Anti-Patterns

- Do NOT use lime (#84CC16) on white/light backgrounds — fails WCAG AA.
- Do NOT bypass Clerk middleware — all auth flows through `src/middleware.ts`.
- Do NOT hardcode API URLs — use `NEXT_PUBLIC_FASTAPI_URL` env var.
- Do NOT add rounded corners (8px+) — design system uses 2px only.
- Do NOT use `@ts-ignore` or `as any` — fix types properly.
