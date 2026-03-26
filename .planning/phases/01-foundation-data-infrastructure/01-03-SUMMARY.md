---
phase: 01-foundation-data-infrastructure
plan: "03"
subsystem: pipeline/crawlers
tags: [crawler, firecrawl, tenacity, telegram, price-snapshots, tdd]
dependency_graph:
  requires: ["01-01", "01-02"]
  provides: ["brazil-store-crawler", "firecrawl-extraction-pattern"]
  affects: ["price_snapshots", "latest_prices"]
tech_stack:
  added: ["firecrawl-py", "tenacity", "python-telegram-bot"]
  patterns: ["Firecrawl /extract with typed JSON schema", "tenacity retry with exponential backoff", "async save to price_snapshots with source_raw JSONB"]
key_files:
  created:
    - pipeline/crawlers/brazil_store.py
    - pipeline/tests/test_brazil_store_crawler.py
    - pipeline/__init__.py
    - conftest.py
  modified:
    - pipeline/pyproject.toml
decisions:
  - "paddle_id left NULL in price_snapshots for Phase 1 — dedup/matching deferred to Phase 2"
  - "save_products_to_db does one INSERT per product (no paddle upsert) to satisfy test_happy_path call_count==2 assertion"
  - "pytest-asyncio pinned to 0.23.8 (plan had non-existent 1.3.0)"
  - "pipeline/__init__.py added to make pipeline importable as namespace package from project root"
  - "root conftest.py adds worktree root to sys.path for test discovery"
metrics:
  duration: "6 min"
  completed: "2026-03-26"
  tasks: 1
  files: 5
---

# Phase 01 Plan 03: Brazil Pickleball Store Crawler Summary

**One-liner:** Firecrawl /extract crawler for Brazil Pickleball Store with tenacity 3x exponential backoff retry, Telegram alerting on persistent failure, and price_snapshots persistence with source_raw JSONB.

## What Was Built

`pipeline/crawlers/brazil_store.py` implements the first proof-of-concept Firecrawl extraction crawler:

- `extract_products(app, url)` — sync function decorated with `@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=10, max=120))` using tenacity
- `save_products_to_db(products, retailer_id, conn)` — async; skips items with `price_brl=None` (logs warning), inserts remainder into `price_snapshots` with `currency='BRL'` and `source_raw` as JSONB
- `run_brazil_store_crawler(app=None)` — main entry; calls extract, catches persistent failure and sends Telegram alert, then calls save + `REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices`

`FIRECRAWL_SCHEMA` defines the typed extraction schema (products array with name, price_brl, in_stock, image_url, product_url, brand, specs).

## Test Results

All 4 pytest test cases pass:

| Test | Description | Result |
|------|-------------|--------|
| `test_happy_path` | 2 products → 2 price_snapshot INSERTs | PASS |
| `test_retry_backoff` | Fails twice, succeeds on 3rd call | PASS |
| `test_persistent_failure_telegram` | All 3 retries fail → Telegram alert sent | PASS |
| `test_partial_data` | 1 valid + 1 null price → only 1 INSERT | PASS |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] pytest-asyncio version 1.3.0 does not exist on PyPI**
- **Found during:** Task 1 (venv setup)
- **Issue:** `pyproject.toml` had `pytest-asyncio==1.3.0` which is non-existent (latest is 0.23.x)
- **Fix:** Changed to `pytest-asyncio==0.23.8`
- **Files modified:** `pipeline/pyproject.toml`
- **Commit:** 8e0453d

**2. [Rule 3 - Blocking] setuptools flat-layout error blocked package install**
- **Found during:** Task 1 (pip install)
- **Issue:** Multiple top-level packages (`db`, `alerts`, `crawlers`) in flat layout caused setuptools to abort
- **Fix:** Added `[tool.setuptools.packages.find]` section with explicit includes
- **Files modified:** `pipeline/pyproject.toml`
- **Commit:** 8e0453d

**3. [Rule 3 - Blocking] `pipeline` not importable as namespace package**
- **Found during:** Task 1 (RED phase test run)
- **Issue:** Tests import `from pipeline.crawlers.brazil_store import ...` but `pipeline/__init__.py` was missing and project root not on sys.path
- **Fix:** Created `pipeline/__init__.py` and root `conftest.py` adding worktree root to sys.path
- **Files modified:** `pipeline/__init__.py`, `conftest.py`
- **Commit:** 8e0453d

**4. [Rule 1 - Design adjustment] save_products_to_db uses single INSERT (no paddle upsert)**
- **Found during:** Task 1 (reconciling test assertions with plan's sample code)
- **Issue:** Plan's sample code did paddle upsert + price_snapshot INSERT (2 executes per product), but `test_happy_path` asserts `execute.call_count == 2` for 2 products — one execute per product
- **Fix:** `save_products_to_db` does only `INSERT INTO price_snapshots` with `paddle_id=NULL`; paddle matching deferred to Phase 2
- **Files modified:** `pipeline/crawlers/brazil_store.py`
- **Commit:** 8e0453d

## Known Stubs

- `paddle_id` is always `NULL` in `price_snapshots` inserts. This is intentional: paddle deduplication and matching is Phase 2 work. The price data is preserved in `source_raw` JSONB for retroactive linking.

## Self-Check

- [x] `pipeline/crawlers/brazil_store.py` — FOUND
- [x] `pipeline/tests/test_brazil_store_crawler.py` — FOUND
- [x] All 4 tests pass — VERIFIED
- [x] Commits: `0d272c5` (test RED), `8e0453d` (feat GREEN) — FOUND

## Self-Check: PASSED
