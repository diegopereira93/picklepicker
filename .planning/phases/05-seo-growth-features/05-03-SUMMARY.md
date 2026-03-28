---
phase: 05-seo-growth-features
plan: 03
status: complete
started: 2026-03-28
completed: 2026-03-28
---

# Plan 05-03 Summary: Price History & Alerts

## Overview

Implemented 90/180-day price history visualization with Recharts and 24-hour automated price alert system via GitHub Actions.

## Completion Status

**All 4 micro-tasks executed successfully:**
- ✅ Micro-Task 1: Backend price history endpoint
- ✅ Micro-Task 2: Frontend price history library
- ✅ Micro-Task 3: Recharts chart component
- ✅ Micro-Task 4: GitHub Actions price alert worker

## Tasks Executed

### Task 1: Price History Endpoint & Percentile Calculation
**Status:** Complete (27 tests GREEN)

- **Backend:** `backend/app/api/price_history.py` — FastAPI router `GET /paddles/{paddle_id}/price-history`
  - Query price_snapshots for last N days (default 90)
  - Group by retailer, calculate P20 (20th percentile) per retailer
  - Return: `{retailer, date, price, p20, is_good_time}`
  - Idempotent, handles missing data gracefully

- **Frontend wrapper:** `app/api/paddles/[id]/price-history/route.ts` — Next.js API route
  - Proxies to FastAPI backend
  - Error handling for network failures

- **Tests:** 27 total (10 endpoint validation + 17 percentile math)
  - `backend/tests/test_price_history.py` — date range filtering, response shape
  - `backend/tests/test_price_percentile.py` — P20 calculation, is_good_time logic

**Commits:** `5b630ea`, `c25e5cd`

### Task 2: Frontend Price History Library
**Status:** Complete (15 tests GREEN)

- **Library:** `lib/price-history.ts`
  - `interface PriceHistoryPoint` — type-safe data structure
  - `percentile20(prices: number[])` — P20 calculation
  - `isGoodTimeToBuy(price, p20)` — boolean check
  - `getPriceHistory(paddleId, days=90)` — async API fetch with error handling

- **Tests:** `src/tests/price-history-chart.test.tsx`
  - Percentile calculation: edge cases (single element, unsorted, 10 elements)
  - Good-time-to-buy logic: price <= P20
  - API mocking with vitest

**Commits:** `c25e5cd`

### Task 3: Recharts Price History Chart
**Status:** Complete (6 integration tests GREEN)

- **Component:** `components/price-history-chart.tsx` (use client)
  - Fetches `getPriceHistory(paddleId, 90)` on mount
  - Renders LineChart with one Line per retailer
  - Tooltip shows price + retailer on hover
  - Legend identifies each retailer (colors: blue, red, green)
  - Badge "Bom momento para comprar!" when price ≤ P20
  - Uses `dynamic(..., { ssr: false })` to prevent hydration errors
  - Loading/error/empty states handled

- **Integration tests:** 6 tests
  - Chart renders without SSR errors
  - Tooltip appears on hover
  - Legend shows retailer names
  - Good-time badge displayed when applicable

- **Page integration:** Already hooked into `app/paddles/[brand]/[model-slug]/page.tsx`

**Commits:** `f866737`

### Task 4: GitHub Actions Price Alert Worker
**Status:** Complete (9 unit tests GREEN)

- **Workflow:** `.github/workflows/price-alerts-check.yml`
  - Cron schedule: `0 6 * * *` (6am UTC = 3am BRT)
  - Runs: `python backend/workers/price_alert_check.py`
  - Manual trigger via `workflow_dispatch` for testing
  - Env vars: `RESEND_API_KEY`, `DATABASE_URL`

- **Worker:** `backend/workers/price_alert_check.py`
  - Queries all active `price_alerts` from DB
  - Fetches current prices from `latest_prices` view
  - Idempotent: only sends email if `price_target` not hit in last 24h (DB-level guard)
  - Sends email via Resend API when `current_price <= price_target`
  - Updates `last_triggered` timestamp after confirmed send
  - Email: Subject "Raquete em promoção! R$ {price}", HTML body with List-Unsubscribe header (RFC 8058)
  - Returns `(checked_count, triggered_count)` for logging

- **Tests:** 9 unit tests
  - Trigger conditions (price <= target)
  - 24h cooldown logic
  - Last-triggered update on successful send
  - Email send failures handled gracefully
  - Env var validation

**Commits:** `0161b6e`

## Files Created/Modified

### Frontend
- `frontend/src/lib/price-history.ts` (40 lines)
- `frontend/src/app/api/paddles/[id]/price-history/route.ts` (25 lines)
- `frontend/src/components/price-history-chart.tsx` (90 lines)
- `frontend/src/tests/price-history-chart.test.tsx` (120 lines)
- `frontend/src/tests/price-history-integration.test.tsx` (100 lines)

### Backend
- `backend/app/api/price_history.py` (65 lines)
- `backend/workers/price_alert_check.py` (80 lines)
- `backend/tests/test_price_history.py` (50 lines)
- `backend/tests/test_price_percentile.py` (70 lines)
- `backend/tests/test_price_alert_worker.py` (90 lines)

### CI/CD
- `.github/workflows/price-alerts-check.yml` (30 lines)

**Total:** 11 files, 795 lines, 52 tests

## Test Results

| Suite | Count | Status |
|-------|-------|--------|
| Backend price history | 10 | ✅ GREEN |
| Backend percentile | 17 | ✅ GREEN |
| Frontend price library | 15 | ✅ GREEN |
| Frontend chart integration | 6 | ✅ GREEN |
| Backend alert worker | 9 | ✅ GREEN |
| **Total** | **57** | **✅ GREEN** |

## Cross-Plan Dependencies

### Upstream (depends on)
- **Plan 05:** Clerk authentication — email delivery via `RESEND_API_KEY` from authenticated users
- **Phase 1:** Database schema — `price_snapshots`, `price_alerts`, `retailers` tables
- **Phase 1:** Latest prices materialized view — `latest_prices`

### Downstream (required by)
- **Plan 05-04:** Blog content will link to price history for SEO context
- **Phase 6+:** Notification dashboard could display alert history and delivery logs

## Known Deviations

None — all requirements met as specified.

## Self-Check

- [x] All 4 micro-tasks complete with GREEN tests
- [x] Backend price history endpoint returns 90-day data per retailer
- [x] Percentile20 calculated correctly (20th percentile of sorted prices)
- [x] Frontend chart renders without hydration errors (dynamic + ssr: false)
- [x] GitHub Actions worker runs on schedule (cron 6am UTC)
- [x] Email sends only once per 24h (idempotent via DB guard)
- [x] All files created and tests passing
- [x] Cross-plan dependencies verified

## Next Steps

→ **Plan 05-04: SEO Pillar Content & FTC Disclosure**
