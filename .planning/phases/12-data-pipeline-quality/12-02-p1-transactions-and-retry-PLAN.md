---
phase: 12-data-pipeline-quality
plan: 02
type: execute
wave: 2
depends_on: ["12-01"]
files_modified:
  - pipeline/db/connection.py
  - pipeline/crawlers/dropshot_brasil.py
  - pipeline/crawlers/mercado_livre.py
autonomous: true
requirements:
  - PIPE-03
  - PIPE-04
  - PIPE-07
must_haves:
  truths:
    - "All database transactions rollback on exception (no poisoned connections)"
    - "Connection pool has max_waiting with proper backpressure handling"
    - "Mercado Livre crawler has retry logic with exponential backoff"
    - "No transient ML API failures cause full job failure"
  artifacts:
    - path: "pipeline/db/connection.py"
      provides: "Transaction-safe connection context with automatic rollback"
      changes: ["@asynccontextmanager with try/except/rollback", "max_waiting configuration"]
    - path: "pipeline/crawlers/mercado_livre.py"
      provides: "Retry-wrapped ML API calls"
      changes: ["@retry decorator on search_pickleball_paddles", "Tenacity integration"]
    - path: "pipeline/crawlers/dropshot_brasil.py"
      provides: "Transaction rollback on all exceptions"
      changes: ["try/except with rollback in async context"]
  key_links:
    - from: "get_connection() context manager"
      to: "conn.rollback()"
      via: "except block in @asynccontextmanager"
      pattern: "try: yield conn; except: await conn.rollback(); raise"
    - from: "search_pickleball_paddles()"
      to: "@retry decorator"
      via: "tenacity.retry"
      pattern: "@retry(stop=stop_after_attempt(3), wait=wait_exponential(...)"
---

<objective>
Implement transaction rollback protection and add retry logic to Mercado Livre crawler.

Purpose: Prevent connection pool poisoning from uncommitted transactions and ensure transient ML API failures don't cause full job failures. These reliability improvements prevent data corruption and reduce manual intervention.
Output: Transaction-safe database connections and resilient ML API calls.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/12-data-pipeline-quality/CONTEXT.md
@pipeline/db/connection.py
@pipeline/crawlers/dropshot_brasil.py
@pipeline/crawlers/mercado_livre.py
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add transaction rollback to connection context manager</name>
  <files>pipeline/db/connection.py, pipeline/db/connection_test.py</files>
  <behavior>
    - Exception in get_connection context triggers automatic rollback
    - Connection returned to pool in clean state
    - Rollback logged at debug level
    - Original exception re-raised after rollback
  </behavior>
  <action>
    Modify `pipeline/db/connection.py`:

    1. Update `get_connection()` context manager:
       ```python
       @asynccontextmanager
       async def get_connection():
           pool = await get_pool()
           async with pool.connection() as conn:
               try:
                   yield conn
               except Exception:
                   # Rollback on any exception to prevent pool poisoning
                   try:
                       await conn.rollback()
                   except Exception as rollback_err:
                       logger.warning(f"Rollback failed: {rollback_err}")
                   raise  # Re-raise original exception
       ```

    2. Add logger import and setup at module level:
       ```python
       import logging
       logger = logging.getLogger(__name__)
       ```

    3. Update `get_pool()` to add connection pool configuration:
       ```python
       _pool = AsyncConnectionPool(
           conninfo=os.environ["DATABASE_URL"],
           min_size=1,
           max_size=5,
           max_waiting=10,  # Queue up to 10 waiting connections
           max_idle=300,    # Close idle connections after 5 minutes
       )
       ```

    4. Add docstring explaining rollback behavior
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/db/connection_test.py::test_transaction_rollback -v</automated>
  </verify>
  <done>
    - get_connection() has try/except with rollback on Exception
    - max_waiting=10 added to AsyncConnectionPool
    - Rollback failures logged but don't suppress original exception
    - Tests verify rollback occurs on simulated errors
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Add retry logic to Mercado Livre API calls</name>
  <files>pipeline/crawlers/mercado_livre.py</files>
  <behavior>
    - search_pickleball_paddles retries up to 3 times on transient failures
    - Exponential backoff: 1s, 2s, 4s (max 10s)
    - Retries on httpx.HTTPStatusError (5xx, timeouts, connection errors)
    - Does NOT retry on 4xx client errors (bad request, auth)
    - Final failure raises after all retries exhausted
  </behavior>
  <action>
    Update `pipeline/crawlers/mercado_livre.py`:

    1. Add tenacity imports at top:
       ```python
       from tenacity import (
           retry,
           stop_after_attempt,
           wait_exponential,
           retry_if_exception_type,
           before_sleep_log,
       )
       ```

    2. Add retry decorator to `search_pickleball_paddles()`:
       ```python
       @retry(
           stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((
               httpx.HTTPStatusError,
               httpx.ConnectError,
               httpx.TimeoutException,
           )),
           before_sleep=before_sleep_log(logger, logging.WARNING),
           reraise=True,
       )
       async def search_pickleball_paddles(
           limit: int = 50,
           offset: int = 0,
           fetch_all: bool = False,
       ) -> dict:
       ```

    3. Update exception handling in `run_mercado_livre_crawler()`:
       - Remove redundant try/except since retry handles transient failures
       - Keep final exception handling for Telegram alert after all retries
       - Use scrub_sensitive_data on error message (import from security module)

    4. Add import for security utilities:
       ```python
       from pipeline.utils.security import scrub_sensitive_data, SensitiveDataFilter
       logger.addFilter(SensitiveDataFilter())
       ```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -c "
import asyncio
from unittest.mock import patch, AsyncMock
from pipeline.crawlers.mercado_livre import search_pickleball_paddles

# Test that retry decorator is present
assert hasattr(search_pickleball_paddles, '__wrapped__'), 'No retry decorator'
print('Retry decorator verified')
"</automated>
  </verify>
  <done>
    - @retry decorator added to search_pickleball_paddles
    - Retries on HTTPStatusError, ConnectError, TimeoutException
    - Exponential backoff with 3 attempts configured
    - Security filter attached to logger
  </done>
</task>

<task type="auto">
  <name>Task 3: Update Drop Shot Brasil to use transaction-safe pattern</name>
  <files>pipeline/crawlers/dropshot_brasil.py</files>
  <action>
    Update `pipeline/crawlers/dropshot_brasil.py` to rely on context manager rollback:

    1. Verify current `save_products_to_db` uses `conn` parameter directly

    2. In `run_dropshot_brasil_crawler()`, wrap save operation:
       ```python
       async with get_connection() as conn:
           try:
               saved = await save_products_to_db(products, retailer_id=3, conn=conn)
               await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices")
               await conn.commit()
           except Exception:
               # Rollback happens automatically via context manager
               # Just re-raise for proper error handling
               raise
       ```

    3. Actually, since `get_connection()` now handles rollback automatically,
       the existing code is already protected. Just verify the pattern:
       - Ensure `async with get_connection() as conn:` is used (it is)
       - Ensure we're not manually managing transactions elsewhere (we're not)

    4. Add comment explaining automatic rollback:
       ```python
       async with get_connection() as conn:
           # Note: get_connection() context manager automatically rolls back
           # on exception to prevent pool poisoning
           saved = await save_products_to_db(products, retailer_id=3, conn=conn)
           await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices")
           await conn.commit()
       ```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && grep -n "automatically rolls back" pipeline/crawlers/dropshot_brasil.py</automated>
  </verify>
  <done>
    - Drop Shot Brasil uses get_connection() context manager
    - Comment added explaining automatic rollback behavior
    - Code follows transaction-safe pattern
  </done>
</task>

</tasks>

<verification>
1. **Transaction Rollback Works:**
   - Check `pipeline/db/connection.py` has try/except/rollback pattern
   - Verify max_waiting=10 is in AsyncConnectionPool kwargs

2. **Retry Logic Active:**
   - `grep -n "@retry" pipeline/crawlers/mercado_livre.py`
   - Verify retry_if_exception_type includes httpx errors

3. **Integration Test:**
   - Import both crawlers successfully
   - Verify no circular imports with security module
</verification>

<success_criteria>
All must be TRUE:
- [ ] get_connection() context manager has automatic rollback on exception
- [ ] Connection pool configured with max_waiting=10 for backpressure
- [ ] Mercado Livre search_pickleball_paddles has @retry decorator
- [ ] Retry configured for 3 attempts with exponential backoff
- [ ] Both crawlers import and use security utilities
- [ ] No manual transaction management outside context manager
</success_criteria>

<output>
After completion, create `.planning/phases/12-data-pipeline-quality/12-02-p1-transactions-and-retry-SUMMARY.md`
</output>
