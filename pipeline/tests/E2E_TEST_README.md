# E2E Test Suite — Pipeline Scrapers

## Overview

This test suite validates the three PickleIQ pipeline scrapers end-to-end using mocked Firecrawl and ML API responses. It de-risks production scraper deployment by testing:

- Schema compliance of extracted product data
- Retry/backoff behavior on Firecrawl failures
- Error mode handling (timeout, rate limit, parse error, HTTP 4xx/5xx)
- Data integrity: price validation, URL format, deduplication
- Performance: all scrapers complete within time limits
- Concurrent execution: all 3 scrapers run in parallel

**Coverage results:**
| Scraper | Coverage |
|---------|----------|
| `brazil_store.py` | 80% |
| `dropshot_brasil.py` | 93% |
| `mercado_livre.py` | 94% |
| **Combined** | **90%** |

---

## Running E2E Tests

### Prerequisites

Install all dependencies via the root `venv`:

```bash
venv/bin/pip install -e pipeline/ pyyaml rapidfuzz
```

### Run All Tests

```bash
venv/bin/python3 -m pytest pipeline/tests/ -v
```

### Run With Coverage Report

```bash
# Terminal output
venv/bin/python3 -m pytest pipeline/tests/ --cov=pipeline.crawlers --cov-report=term-missing

# HTML report (opens in browser)
venv/bin/python3 -m pytest pipeline/tests/ --cov=pipeline.crawlers --cov-report=html
open htmlcov/index.html
```

### Run Specific Test Files

```bash
# Brazil Store scraper tests
venv/bin/python3 -m pytest pipeline/tests/test_brazil_store_scraper.py -v

# Drop Shot Brasil tests
venv/bin/python3 -m pytest pipeline/tests/test_dropshot_brasil_scraper.py -v

# Mercado Livre tests
venv/bin/python3 -m pytest pipeline/tests/test_mercado_livre_scraper.py -v

# Firecrawl error handling tests
venv/bin/python3 -m pytest pipeline/tests/test_firecrawl_integration.py -v

# Data integrity + performance benchmarks
venv/bin/python3 -m pytest pipeline/tests/test_data_integrity.py -v
```

### Run By Test Category

```bash
# Only error mode tests
venv/bin/python3 -m pytest pipeline/tests/ -k "error or retry or timeout" -v

# Only performance tests
venv/bin/python3 -m pytest pipeline/tests/ -k "benchmark or under_30s or under_45s" -v

# Only fuzzy dedup tests
venv/bin/python3 -m pytest pipeline/tests/ -k "fuzzy" -v

# Only concurrent execution tests
venv/bin/python3 -m pytest pipeline/tests/ -k "concurrent" -v
```

---

## Test Organization

| File | Tests | What it Covers |
|------|-------|----------------|
| `test_brazil_store_scraper.py` | 18 | Schema, price/URL validation, retry, parse error, DB persistence |
| `test_dropshot_brasil_scraper.py` | 19 | Schema, retry, performance, retailer_id=3, end-to-end crawl |
| `test_mercado_livre_scraper.py` | 24 | Affiliate URLs, pagination, RapidFuzz dedup, DB save logic |
| `test_firecrawl_integration.py` | 17 | Timeout/429/4xx/5xx error modes, concurrent execution, retry config |
| `test_data_integrity.py` | 23 | Cross-scraper schema, dedup, affiliate URLs, perf benchmarks |
| **Total** | **101** | |

### Shared Infrastructure

| File | Purpose |
|------|---------|
| `conftest.py` | `mock_firecrawl_app`, `scraper_db_connection`, `staging_config`, mock ML responses |
| `test_utils.py` | `assert_schema_valid`, `measure_crawl_time`, `load_staging_config`, `AsyncMockFirecrawl` |
| `fixtures/staging_config.yaml` | Retailer URLs, timeouts, performance thresholds |
| `fixtures/mock_responses/` | Sample JSON for Brazil Store, Drop Shot, and ML responses |

---

## Error Modes

See [FIRECRAWL_ERROR_HANDLING.md](./FIRECRAWL_ERROR_HANDLING.md) for the full error mode reference table.

**Quick summary:**

| Error | Retries | Backoff (Brazil Store) | Alert Sent |
|-------|---------|------------------------|------------|
| Timeout | 3 | 10s → 20s → 40s | Yes (after 3) |
| Rate Limit (429) | 3 | 10s → 20s → 40s | Yes (after 3) |
| Parse Error (`data=None`) | 0 | N/A | No (returns 0) |
| HTTP 4xx | 3* | 10s → 20s → 40s | Yes (after 3) |
| HTTP 5xx | 3 | 10s → 20s → 40s | Yes (after 3) |

> *HTTP 4xx are technically retried because tenacity uses `retry_if_exception_type(Exception)`.

---

## Performance Baselines

| Scraper | Target | Test |
|---------|--------|------|
| Brazil Store (single crawl) | < 30s | `test_brazil_store_crawl_under_30s` |
| Drop Shot Brasil (single crawl) | < 30s | `test_dropshot_brasil_crawl_under_30s` |
| Mercado Livre (3-page pagination) | < 30s | `test_mercado_livre_multi_page_under_30s` |
| All 3 concurrent | < 45s | `test_concurrent_all_3_scrapers_under_45s` |
| Memory growth (10 repeated calls) | < 5MB | `test_no_memory_leak_repeated_extraction` |

All tests run against mocked Firecrawl/httpx — no real network calls.

---

## Data Integrity Checks

### Schema Requirements (Firecrawl scrapers)

Every extracted product must have:
- `name` (str, non-empty)
- `price_brl` (float, > 0)
- `in_stock` (bool)
- `image_url` (str, starts with `https://`)
- `product_url` (str, starts with `https://`)
- `brand` (str, non-empty)
- `specs` (dict, may be empty `{}`)

### Deduplication Logic

Phase 1 does NOT perform deduplication — `paddle_id` is left NULL in `price_snapshots`. Phase 2 will implement:

| Strategy | Threshold | Description |
|----------|-----------|-------------|
| URL/SKU match | Exact | Same `product_url` = same product |
| Title hash | Exact | Same `name.lower() + brand.lower()` = duplicate |
| RapidFuzz | ≥ 85 | `token_sort_ratio` catches typos/order variations |

RapidFuzz threshold validated in tests — 85 correctly separates same-product variants from different paddles.

### Affiliate URL Format

Mercado Livre affiliate URLs follow the pattern:
```
{permalink}?matt_id={affiliate_tag}
{permalink}&matt_id={affiliate_tag}  (when permalink already has params)
```

If `ML_AFFILIATE_TAG` is empty, plain permalink is saved (no commission, but link works).

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'psycopg_pool'`

Install pipeline dependencies:
```bash
venv/bin/pip install -e pipeline/ psycopg[binary,pool]
```

### `ModuleNotFoundError: No module named 'rapidfuzz'`

```bash
venv/bin/pip install rapidfuzz
```

### `ModuleNotFoundError: No module named 'yaml'`

```bash
venv/bin/pip install pyyaml
```

### Tests take > 3 minutes

The `test_firecrawl_integration.py` tests that exercise tenacity retries with real backoff (10s min) will take ~3 minutes because tenacity actually sleeps between retries. This is expected behavior — the backoff validates real retry timing.

To skip slow tests:
```bash
venv/bin/python3 -m pytest pipeline/tests/ --ignore=pipeline/tests/test_firecrawl_integration.py -v
```

### `KeyError: 'DATABASE_URL'`

Set a dummy URL for test runs:
```bash
DATABASE_URL=postgresql://test:test@localhost/test venv/bin/python3 -m pytest pipeline/tests/ -v
```

Or add to your `.env.local` file (it's in `.gitignore`).

### Coverage Below 80%

Run with `--cov-report=term-missing` to see which lines are not covered:
```bash
venv/bin/python3 -m pytest pipeline/tests/test_brazil_store_scraper.py \
  --cov=pipeline.crawlers.brazil_store --cov-report=term-missing
```

Add tests for the missing lines shown in the `Missing` column.
