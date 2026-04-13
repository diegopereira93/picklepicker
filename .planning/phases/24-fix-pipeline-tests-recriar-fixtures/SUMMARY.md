# Phase 24 — Fix Pipeline Tests

## Overview
Fixed pipeline test suite — updated tests to match crawler migration from `app.extract()` to `app.scrape()` with markdown parsing.

## Results
- **Before**: 115 passed, 38 failed
- **After**: 151 passed, 2 failed (pre-existing placeholder tests requiring DB)

## Root Cause
All crawlers (Brazil Store, Dropshot Brasil) migrated from Firecrawl's `app.extract()` structured API to `app.scrape()` markdown-based parsing. Tests still mocked `app.extract` which was never called.

## Changes Made

### Mock Pattern Change
All tests updated from:
```python
app.extract = MagicMock(return_value={"data": {"products": [...]}})
```
to:
```python
app.scrape = MagicMock(return_value=MagicMock(markdown=MOCK_MARKDOWN))
```

### DB Operation Count Fix
`save_products_to_db()` does 2 DB operations per product (paddle INSERT + snapshot INSERT):
- `call_count == N` → `call_count == 2 * N`

### Other Fixes
- `in_stock` defaults to `True` (not `False`): `product.get("in_stock", True)`
- Dropshot retry config: `wait_exponential(min=10, max=120)` (was min=1, max=10)
- Price regex requires no space after `R$`: `R$1.299,90` not `R$ 1.299,90`
- ML scraper upsert: no SELECT fallback on conflict (logs error + continues)

### Files Modified
| File | Fixes |
|------|-------|
| `pipeline/tests/test_brazil_store_crawler.py` | 4 tests: mock, call_count, retry |
| `pipeline/tests/test_brazil_store_scraper.py` | 7 tests: mock, markdown, assertions |
| `pipeline/tests/test_dropshot_brasil_crawler.py` | 4 tests: mock, call_count, retry |
| `pipeline/tests/test_dropshot_brasil_scraper.py` | 7 tests: mock, markdown, assertions |
| `pipeline/tests/test_firecrawl_integration.py` | 13 tests: helper func, all mocks |
| `pipeline/tests/test_mercado_livre_scraper.py` | 1 test: upsert conflict behavior |

### Pre-existing Failures (Not Fixed)
- `test_embeddings.py::test_batch_embed__placeholder` — requires running DB
- `test_embeddings.py::test_re_embed_flagged__placeholder` — requires running DB
