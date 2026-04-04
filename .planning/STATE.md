# STATE.md — PickleIQ

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Requirements defined, ready for planning
Last activity: 2026-04-04 — Milestone v1.4 started

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-04)

**Core value:** Users can confidently choose the right pickleball paddle through AI-powered recommendations backed by real-time pricing and technical specs
**Current focus:** Phase 14 — Launch Readiness & Bug Fixes

## Accumulated Context

### Shipped Milestones

| Milestone | Version | Phases | Status |
|-----------|---------|--------|--------|
| MVP | v1.0.0 | 1–6 | ✅ Complete |
| Scraper & E2E | v1.1.0 | 7–9 | ✅ Complete |
| Core Web Vitals | v1.2.0 | 11 | ✅ Complete |
| Hybrid UI Redesign | v1.3.0 | 13 | ✅ Complete |
| Launch Readiness | v1.4.0 | 14 | 🔄 In progress |

### Known Issues (from v1.4 investigation)

1. **placehold.co images:** DB seed has invalid placeholder URLs. Next.js can't optimize them. Need to NULL them out and rely on "Foto" fallback.
2. **Paddle detail 404:** Backend missing `model_slug` filter on list endpoint. Root cause, not a frontend parsing issue.
3. **Chat 422:** `budget_max` edge case (0 bypasses fallback), empty message edge case.

### Pending TODOS (from TODOS.md)

T1–T7 deferred. Not in scope for v1.4. These are operational improvements for post-launch.

### Key Technical Notes

- Backend uses raw SQL (no ORM). Column names must match `pipeline/db/schema.sql`.
- Two separate Python venvs: `backend/venv/` and `pipeline/.venv/`.
- Frontend uses `next/image` with `remotePatterns: [{ hostname: '**' }]` — allows all hosts.
- Chat proxy at `frontend/src/app/api/chat/route.ts` transforms Vercel AI SDK format → FastAPI format.

---
*State updated: 2026-04-04*
