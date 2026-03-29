# Firecrawl Error Handling Patterns

Documents how each error mode is handled across Brazil Store and Drop Shot Brasil scrapers.

## Error Mode Reference Table

| Error Type | HTTP Code | Retryable | Retries | Backoff | Alert Sent | Result |
|-----------|-----------|-----------|---------|---------|------------|--------|
| Timeout | N/A | Yes | 3 | Exponential | Yes (after 3) | Raises + Alert |
| Rate Limit | 429 | Yes | 3 | Exponential | Yes (after 3) | Raises + Alert |
| Parse Error / None data | N/A | N/A | 0 | N/A | No | Returns 0 gracefully |
| HTTP 4xx Client Error | 400-499 | Yes* | 3 | Exponential | Yes (after 3) | Raises + Alert |
| HTTP 5xx Server Error | 500-599 | Yes | 3 | Exponential | Yes (after 3) | Raises + Alert |
| Max Retries Exceeded | Any | No | 3 (done) | N/A | Yes | Raises |

> *Note: tenacity retries all Exception subclasses. HTTP 4xx errors (client-side) are technically retried
> because the @retry decorator uses `retry_if_exception_type(Exception)`. This may be refined in future
> to only retry 5xx/timeout errors.

## Retry Configuration

### Brazil Store (`brazil_store.py`)
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=10, max=120),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
```
- **Attempts:** 3 total (1 initial + 2 retries)
- **Backoff:** 10s → 20s → 40s (exponential, capped at 120s)
- **Re-raise:** Yes — final exception propagates to `run_brazil_store_crawler`

### Drop Shot Brasil (`dropshot_brasil.py`)
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
```
- **Attempts:** 3 total
- **Backoff:** 1s → 2s → 4s (exponential, capped at 10s)
- **Re-raise:** Yes

## Alert Behavior

When all retries are exhausted, `run_*_crawler()` catches the exception and calls:
```python
await send_telegram_alert(f"Brazil Pickleball Store crawler failed after 3 retries: {e}")
```

Alert messages include:
- Scraper name ("Brazil Pickleball Store", "Drop Shot Brasil")
- Error description from the exception
- Phrase "3 retries" to distinguish exhausted retries from transient errors

## Parse Error / Graceful Degradation

When Firecrawl returns `{"data": None}` (parse failure):
- `extract_products()` returns the raw response (no exception)
- `run_*_crawler()` handles `None` data via `(result.get("data") or {}).get("products", [])`
- Returns 0 (no products saved) — **does not send alert**
- Logged as warning: `"No products extracted from [Scraper Name]"`

## Circuit Breaker Pattern

There is no automatic circuit breaker in Phase 1. The Telegram alert acts as a manual circuit
signal — when an alert fires, operators can temporarily disable the scraper cron.

Phase 2 will implement an automated circuit breaker:
- Opens after 5 consecutive failures in a rolling 1-hour window
- Sends alert when circuit opens and closes
- Stores circuit state in Redis

## Concurrent Execution

All 3 scrapers can run concurrently via `asyncio.gather()`:
```python
results = await asyncio.gather(
    run_brazil_store_crawler(app=bs_app),
    run_dropshot_brasil_crawler(app=ds_app),
    run_mercado_livre_crawler(),
    return_exceptions=True,  # prevents one failure from canceling others
)
```

When one scraper fails under concurrent load, others continue independently.
Use `return_exceptions=True` to collect all results before checking for errors.

## Test Coverage

| Test File | Error Modes Covered |
|-----------|-------------------|
| `test_firecrawl_integration.py` | Timeout, 429, parse error, 4xx, 5xx, max retries, concurrent |
| `test_brazil_store_scraper.py` | Timeout retry, rate limit, parse error, alert on failure |
| `test_dropshot_brasil_scraper.py` | Timeout retry, parse error, alert on failure |
| `test_mercado_livre_scraper.py` | API timeout, crawler failure alert |
