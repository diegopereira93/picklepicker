---
phase: 01-foundation-data-infrastructure
plan: "04"
subsystem: pipeline/crawlers
tags: [mercado-livre, affiliate, crawler, ml-api, tdd]
dependency_graph:
  requires: ["01-01", "01-02"]
  provides: ["pipeline/crawlers/mercado_livre.py", "ML affiliate URL construction", "price_snapshots ML rows"]
  affects: ["latest_prices materialized view", "price_snapshots table"]
tech_stack:
  added: ["httpx.AsyncClient for ML API", "psycopg[pool] extra"]
  patterns: ["TDD red-green", "async httpx pagination", "ON CONFLICT DO NOTHING upsert"]
key_files:
  created:
    - pipeline/crawlers/mercado_livre.py
    - pipeline/tests/test_mercado_livre_crawler.py
    - pipeline/__init__.py
  modified:
    - pipeline/pyproject.toml
decisions:
  - "matt_id is the affiliate parameter name for ML Afiliados (needs verification against ML portal)"
  - "psycopg[binary,pool] required — pool extra was missing from pyproject.toml"
  - "httpx response.json() is synchronous — test mocks must use MagicMock not AsyncMock"
  - "build-system section added to pyproject.toml with setuptools backend"
  - "pipeline/__init__.py created to make the pipeline directory importable as a package"
metrics:
  duration: "7 min"
  completed_date: "2026-03-26"
  tasks_completed: 1
  tasks_total: 1
  files_created: 3
  files_modified: 1
---

# Phase 01 Plan 04: Mercado Livre Crawler Summary

**One-liner:** ML public search API crawler with matt_id affiliate URL tagging, pagination, and price_snapshots persistence using httpx async client.

## What Was Built

A complete Mercado Livre integration crawler (`pipeline/crawlers/mercado_livre.py`) that:

- Queries the public ML search API at `https://api.mercadolibre.com/sites/MLB/search` with `q=raquete pickleball` and `category=MLB1276`
- Constructs affiliate URLs by appending `matt_id={ML_AFFILIATE_TAG}` (using `?` or `&` separator correctly)
- Paginates through all results when `total > limit` via `fetch_all=True`
- Persists items to `price_snapshots` with `retailer_id=2` (Mercado Livre), `currency='BRL'`, `affiliate_url`, and `source_raw` JSONB
- Skips items where `price` is `None` or `0`
- Refreshes `latest_prices` materialized view after each run
- Falls back gracefully when `ML_AFFILIATE_TAG` is not set (logs warning, saves plain permalink)

## Test Results

7/7 tests passing:
- `test_affiliate_url_tagged` — matt_id appended with ? separator
- `test_affiliate_url_with_existing_params` — & separator when URL has existing params
- `test_affiliate_url_empty_tag_returns_plain` — empty tag returns unchanged permalink
- `test_search_returns_items` — httpx AsyncClient called with ML_SEARCH_URL
- `test_saves_to_db` — 2 items saved with affiliate_url containing tag
- `test_pagination` — 2 API calls made for total=75, limit=50
- `test_partial_data_skipped` — only 1/3 items saved (price=None and price=0 skipped)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Missing build-system in pyproject.toml**
- **Found during:** Task 1 (GREEN phase setup)
- **Issue:** `pyproject.toml` had no `[build-system]` table; pip install -e failed
- **Fix:** Added `[build-system]` with `setuptools>=45` and `wheel`; set `where = [".."]` for package find
- **Files modified:** `pipeline/pyproject.toml`
- **Commit:** ed9d2f1

**2. [Rule 3 - Blocking] psycopg pool extra not installed**
- **Found during:** Task 1 (GREEN phase — import error)
- **Issue:** `psycopg[binary]` does not include `psycopg_pool`; `connection.py` imports from it
- **Fix:** Changed dependency to `psycopg[binary,pool]==3.3.3`
- **Files modified:** `pipeline/pyproject.toml`
- **Commit:** 86ff145

**3. [Rule 1 - Bug] Test mock type mismatch for httpx response**
- **Found during:** Task 1 (GREEN phase — first test run)
- **Issue:** `AsyncMock()` for response makes `.json()` return a coroutine; httpx `.json()` is synchronous
- **Fix:** Changed response mocks in `TestSearch` and `TestPagination` from `AsyncMock()` to `MagicMock()`
- **Files modified:** `pipeline/tests/test_mercado_livre_crawler.py`
- **Commit:** 86ff145

**4. [Rule 3 - Blocking] Missing pipeline/__init__.py**
- **Found during:** Task 1 (venv import test)
- **Issue:** `pipeline/` directory had no `__init__.py` so Python couldn't import it as a package
- **Fix:** Created empty `pipeline/__init__.py`
- **Files modified:** `pipeline/__init__.py`
- **Commit:** ed9d2f1

## Known Stubs

- `brand: ""` in paddle insert — ML search API does not reliably provide a separate brand field. The `brand` field will be populated by the spec enrichment pipeline in Phase 2.

## Decisions Made

1. `matt_id` used as the ML Afiliados affiliate parameter — this name needs confirmation against the ML Afiliados portal before production use. Fallback (plain permalink) is implemented.
2. `retailer_id = 2` hardcoded per schema seed data — Mercado Livre is always the second inserted retailer.
3. Paddle dedup is intentionally deferred to Phase 2 — ON CONFLICT DO NOTHING avoids duplicates at the name level but proper brand/model matching will happen later.

## Self-Check: PASSED

- [x] `pipeline/crawlers/mercado_livre.py` — created and contains all required functions
- [x] `pipeline/tests/test_mercado_livre_crawler.py` — 7 tests, all passing
- [x] Commits: ed9d2f1 (RED), 86ff145 (GREEN) — both confirmed in git log
- [x] `grep "matt_id" pipeline/crawlers/mercado_livre.py` — found
- [x] `grep "api.mercadolibre.com" pipeline/crawlers/mercado_livre.py` — found
- [x] `grep "INSERT INTO price_snapshots" pipeline/crawlers/mercado_livre.py` — found
