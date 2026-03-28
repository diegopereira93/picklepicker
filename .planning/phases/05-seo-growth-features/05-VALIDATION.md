---
name: Phase 05 Test Validation Architecture
description: Documents Nyquist test coverage for Phase 5 requirements. Confirms all Wave 0 test files exist and coverage is complete.
type: validation
---

# Phase 05: SEO & Growth Features — Test Validation Architecture

**Date:** 2026-03-28
**Status:** COMPLETE ✓
**Coverage Level:** Nyquist Compliance

---

## Executive Summary

All 7 required Wave 0 test files **exist in the codebase**. Coverage is **complete** for all Phase 5 requirements (R5.1–R5.4). Test locations align with project conventions (`frontend/src/tests/` + `backend/tests/`).

**Validation Status:** [PASS] — No Wave 0 gaps. Plans may proceed to execution.

---

## Wave 0 Test Files — Requirement Mapping

| Requirement | Test File | Location | Status | Coverage |
|---|---|---|---|---|
| **R5.1: Product pages** | product-metadata.test.ts | `frontend/src/tests/unit/product-metadata.test.ts` | ✓ EXISTS | generateMetadata(), SSR safety |
| **R5.1: Product pages** | product-schema.test.tsx | `frontend/src/tests/unit/product-schema.test.tsx` | ✓ EXISTS | ld+json Schema.org hydration |
| **R5.2: Clerk auth** | clerk-middleware.test.ts | `frontend/src/tests/unit/clerk-middleware.test.ts` | ✓ EXISTS | clerkMiddleware(), auth context |
| **R5.2: Price alerts** | test_price_alert_worker.py | `backend/tests/test_price_alert_worker.py` | ✓ EXISTS | 24h worker, Resend email trigger |
| **R5.3: Price history** | test_price_history.py | `backend/tests/test_price_history.py` | ✓ EXISTS | 90/180-day endpoint, data retrieval |
| **R5.3: Percentile** | test_price_percentile.py | `backend/tests/test_price_percentile.py` | ✓ EXISTS | P20 calculation logic |
| **R5.3: Chart rendering** | price-history-chart.test.tsx | `frontend/src/tests/price-history-chart.test.tsx` | ✓ EXISTS | Recharts dynamic import, SSR safety |

**Supporting tests:**
- `frontend/src/tests/unit/price-alerts.test.ts` — R5.2 alert creation/management
- `frontend/src/tests/unit/session-upgrade.test.ts` — Session upgrade for Clerk integration
- `frontend/src/tests/blog-metadata.test.tsx` — R5.4 blog metadata
- `frontend/src/tests/ftc-disclosure.test.tsx` — R5.4 FTC compliance component

---

## Test Architecture by Requirement

### R5.1: Product Pages (generateMetadata + Schema.org + ISR)

**Frontend Tests:**
```
frontend/src/tests/unit/product-metadata.test.ts
  ├─ generateMetadata() returns title with brand + model
  ├─ OG image set from paddle.image_url
  ├─ Canonical URL correct
  └─ ISR revalidate set to 3600s

frontend/src/tests/unit/product-schema.test.tsx
  ├─ ld+json Schema.org/Product renders without hydration mismatch
  ├─ price field matches latest_prices.current_price
  ├─ availability set to InStock if in_stock = true
  └─ image array includes all product images
```

**Verification Command:**
```bash
npm run test -- --grep="product-metadata|product-schema"
```

---

### R5.2: Clerk Auth + Price Alerts

**Frontend Tests:**
```
frontend/src/tests/unit/clerk-middleware.test.ts
  ├─ clerkMiddleware() exports from middleware.ts
  ├─ auth() call in /api/price-alerts/route.ts succeeds for authenticated user
  ├─ Returns 401 for unauthenticated request
  └─ user_id extracted and passed to backend

frontend/src/tests/unit/session-upgrade.test.ts
  ├─ Session storage persists user_id after Clerk login
  └─ Profile data merged into session context

frontend/src/tests/unit/price-alerts.test.ts
  ├─ User can POST /api/price-alerts with paddle_id + price_target
  ├─ price_alerts table INSERT succeeds
  └─ Resend API key present for email send
```

**Backend Tests:**
```
backend/tests/test_price_alert_worker.py
  ├─ GitHub Actions workflow scheduled 24h via cron
  ├─ Worker queries price_alerts WHERE last_triggered < NOW() - 24h
  ├─ Compares current price vs price_target
  ├─ Sends Resend email if current_price <= target
  ├─ Updates last_triggered timestamp
  ├─ Email includes unsubscribe link (RFC 8058)
  └─ Worker logs to stdout for GH Actions
```

**Verification Commands:**
```bash
npm run test -- --grep="clerk-middleware|session-upgrade|price-alerts"
pytest backend/tests/test_price_alert_worker.py -xvs
```

---

### R5.3: Price History + Percentile + Chart

**Backend Tests:**
```
backend/tests/test_price_history.py
  ├─ GET /paddles/{id}/price-history?days=90 returns 90-day data
  ├─ Returns [{ date, retailer, price }, ...] sorted by date
  ├─ Filters to paddle_id only (no cross-paddle leakage)
  └─ Returns empty array if no price history exists

backend/tests/test_price_percentile.py
  ├─ percentile20(prices) returns 20th percentile value
  ├─ Handles edge case: single price (returns that price)
  ├─ Handles edge case: identical prices (returns same value)
  └─ Calculation matches numpy/scipy percentile definition
```

**Frontend Tests:**
```
frontend/src/tests/price-history-chart.test.tsx
  ├─ Price history chart renders without SSR hydration mismatch (dynamic import)
  ├─ Chart fetches from /api/paddles/{id}/price-history?days=90
  ├─ Recharts LineChart renders 2+ price series (retailer lines)
  ├─ P20 indicator badge shows only when price <= percentile20
  ├─ Legend displays retailer names correctly
  └─ Handles empty data gracefully (no error)
```

**Verification Commands:**
```bash
pytest backend/tests/test_price_history.py -xvs
pytest backend/tests/test_price_percentile.py -xvs
npm run test -- --grep="price-history-chart"
```

---

### R5.4: Blog + FTC Compliance

**Frontend Tests:**
```
frontend/src/tests/blog-metadata.test.tsx
  ├─ Pillar page /blog/best-pickleball-paddles-beginners renders
  ├─ generateMetadata() returns title with keyword
  ├─ Schema.org/BlogPosting ld+json renders
  └─ ISR revalidate set to 86400s (24h)

frontend/src/tests/ftc-disclosure.test.tsx
  ├─ FTC disclosure badge renders above first affiliate link
  ├─ Badge text: "We earn affiliate commissions"
  ├─ Footer includes detailed disclaimer
  ├─ All product pages include FTC component
  └─ Disclosure wording meets FTC 16 CFR Part 255 requirements
```

**Verification Commands:**
```bash
npm run test -- --grep="blog-metadata|ftc-disclosure"
npm run build  # Verify blog pages build without errors
```

---

## Cross-Phase Integration

### Data Contracts

| Phase | Data Source | Test Coverage |
|---|---|---|
| Phase 01 | paddles, price_snapshots (created) | Existing integration tests verify schema |
| Phase 02 | embeddings, latest_prices (created) | test_paddles_endpoints.py verifies fetch |
| Phase 03 | Chat API, Langfuse (created) | test_chat_endpoint.py verifies integration |
| Phase 05 | users (Clerk), price_alerts (create) | test_price_alert_worker.py verifies INSERT |

**No data conflicts.** All Phase 05 tests assume Phase 1-4 tables exist and are populated.

---

## Execution Readiness

### Pre-Execution Verification (Wave 0 Complete)

- [x] Test files exist in codebase
- [x] All 4 requirements have test coverage
- [x] Test commands specified (npm run test + pytest)
- [x] Data contracts verified
- [x] No Wave 0 gaps identified

### Recommended Execution Order

1. **Wave 1 (Parallel):** Plans 01 + 02 + 03 (auth, product pages, price alerts)
2. **Wave 2:** Plan 04 (blog/SEO, depends on product pages from Wave 1)

### Test Coverage Summary

| Dimension | Count | Status |
|---|---|---|
| Frontend test files | 4 | ✓ Complete |
| Backend test files | 4 | ✓ Complete |
| Requirements covered | 4/4 | ✓ 100% |
| Plans ready for execution | 4/4 | ✓ Ready |

---

## Confidence Assessment

**Nyquist Compliance: [PASS]**

All required Wave 0 test files exist. Requirement coverage is complete. No gaps identified. Plans may proceed to execution immediately without additional Wave 0 setup.

---

*Last updated: 2026-03-28 — All Wave 0 gaps resolved*
