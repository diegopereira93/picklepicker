---
phase: 12-data-pipeline-quality
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - pipeline/db/connection.py
  - pipeline/crawlers/dropshot_brasil.py
  - pipeline/utils/__init__.py
  - pipeline/utils/security.py
autonomous: true
requirements:
  - PIPE-01
  - PIPE-02
must_haves:
  truths:
    - "Pool initialization is thread-safe with asyncio.Lock (no duplicate pools)"
    - "Firecrawl API key never appears in logs or exception messages"
    - "Sensitive data is scrubbed from all error outputs before propagation"
  artifacts:
    - path: "pipeline/db/connection.py"
      provides: "Thread-safe connection pool with asyncio.Lock"
      min_lines: 50
      exports: ["get_pool", "get_connection", "close_pool"]
    - path: "pipeline/crawlers/dropshot_brasil.py"
      provides: "Scrubbed exception handling for API key protection"
      changes: ["Exception wrapping with scrubbing", "Safe error logging"]
    - path: "pipeline/utils/security.py"
      provides: "Reusable sensitive data scrubbing utilities"
      exports: ["scrub_sensitive_data", "SensitiveDataFilter"]
  key_links:
    - from: "pipeline/db/connection.py"
      to: "_pool global"
      via: "asyncio.Lock()"
      pattern: "async with _pool_lock:"
    - from: "pipeline/crawlers/dropshot_brasil.py"
      to: "pipeline/utils/security.py"
      via: "import scrub_sensitive_data"
      pattern: "scrub_sensitive_data"
---

<objective>
Fix P0 production blockers: race condition in pool initialization and API key exposure risk.

Purpose: Prevent duplicate connection pools from concurrent access and eliminate sensitive data leakage in logs/exceptions. These are critical security and reliability issues that could cause data corruption or credential exposure.
Output: Thread-safe connection pool and secure error handling across crawlers.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/12-data-pipeline-quality/CONTEXT.md
@pipeline/db/connection.py
@pipeline/crawlers/dropshot_brasil.py
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Create security utilities module with sensitive data scrubbing</name>
  <files>pipeline/utils/__init__.py, pipeline/utils/security.py, pipeline/utils/security_test.py</files>
  <behavior>
    - scrub_sensitive_data("Error: key=sk-abc123") → "Error: key=***"
    - scrub_sensitive_data("url?token=secret&other=value") → "url?token=***&other=value"
    - SensitiveDataFilter masks API keys in logging
    - Handles common patterns: api_key, token, secret, password
  </behavior>
  <action>
    Create `pipeline/utils/__init__.py` (empty) and `pipeline/utils/security.py` with:

    1. `SENSITIVE_PATTERNS`: List of regex patterns to match sensitive data
       - api_key, apikey, api-key variants
       - token, secret, password variants
       - Environment variable patterns for common secrets

    2. `scrub_sensitive_data(text: str, replacement: str = "***") -> str`:
       - Iterate through SENSITIVE_PATTERNS
       - Replace matches with replacement string
       - Handle URL query parameters specially

    3. `SensitiveDataFilter(logging.Filter)`:
       - Filters LogRecord messages
       - Applies scrubbing to msg and args
       - Safe to attach to any logger

    4. `mask_exception(exception: Exception) -> Exception`:
       - Creates new exception with scrubbed message
       - Preserves original exception type where possible
       - Scrubs both args and string representation

    Use re.compile for performance. Include docstrings and type hints.
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/utils/security_test.py -v</automated>
  </verify>
  <done>
    - security.py exports scrub_sensitive_data and SensitiveDataFilter
    - Tests pass covering API keys, tokens, URLs, and exceptions
    - Module can be imported from pipeline.utils.security
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Fix race condition in pool initialization with asyncio.Lock</name>
  <files>pipeline/db/connection.py, pipeline/db/connection_test.py</files>
  <behavior>
    - Two concurrent get_pool() calls must return same pool instance
    - Pool created exactly once even with racing threads
    - Lock released properly after initialization
    - Lock acquired non-blocking for subsequent calls
  </behavior>
  <action>
    Modify `pipeline/db/connection.py` to fix race condition:

    1. Add `import asyncio` at top

    2. Add `_pool_lock: asyncio.Lock | None = None` global alongside `_pool`

    3. Update `get_pool()` with double-checked locking pattern:
       ```python
       async def get_pool() -> AsyncConnectionPool:
           global _pool, _pool_lock
           if _pool_lock is None:
               _pool_lock = asyncio.Lock()
           if _pool is None:
               async with _pool_lock:
                   if _pool is None:  # Double-check after acquiring lock
                       _pool = AsyncConnectionPool(...)
                       await _pool.open()
           return _pool
       ```

    4. Update `close_pool()` to reset `_pool_lock` too:
       ```python
       async def close_pool():
           global _pool, _pool_lock
           if _pool is not None:
               await _pool.close()
               _pool = None
               _pool_lock = None
       ```

    5. Ensure type hints remain accurate for Python 3.12
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/db/connection_test.py -v</automated>
  </verify>
  <done>
    - _pool_lock global exists and is initialized
    - Double-checked locking pattern implemented
    - Tests verify concurrent access returns same pool
    - close_pool resets both _pool and _pool_lock
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Add API key scrubbing to Drop Shot Brasil crawler</name>
  <files>pipeline/crawlers/dropshot_brasil.py</files>
  <behavior>
    - Exception messages never contain FIRECRAWL_API_KEY value
    - Logger messages scrubbed before output
    - Original exception preserved but message sanitized
    - Telegram alerts show scrubbed error messages
  </behavior>
  <action>
    Update `pipeline/crawlers/dropshot_brasil.py`:

    1. Add imports:
       ```python
       from pipeline.utils.security import scrub_sensitive_data, SensitiveDataFilter
       ```

    2. Attach filter to logger at module level:
       ```python
       logger = logging.getLogger(__name__)
       logger.addFilter(SensitiveDataFilter())
       ```

    3. Update `run_dropshot_brasil_crawler()` exception handling:
       ```python
       try:
           result = extract_products(app, DROPSHOT_BRASIL_URL)
       except Exception as e:
           # Scrub any sensitive data from error message
           safe_message = scrub_sensitive_data(str(e))
           await send_telegram_alert(
               f"Drop Shot Brasil crawler failed after 3 retries: {safe_message}"
           )
           # Re-raise sanitized exception
           raise type(e)(safe_message) from e
       ```

    4. Ensure error logging also uses scrubbing:
       - Any logger.warning/error calls with external data should be scrubbed
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -c "
import os
os.environ['FIRECRAWL_API_KEY'] = 'sk-test123'
os.environ['DATABASE_URL'] = 'postgresql://test'
from pipeline.utils.security import scrub_sensitive_data
msg = 'Error connecting with key=sk-test123'
scrubbed = scrub_sensitive_data(msg)
assert 'sk-test123' not in scrubbed, 'Key not scrubbed'
assert '***' in scrubbed, 'Replacement missing'
print('Scrubbing test passed')
"</automated>
  </verify>
  <done>
    - SensitiveDataFilter attached to crawler logger
    - Exception messages scrubbed before Telegram alert
    - No raw API key can appear in logs or alerts
    - Import statements added for security utilities
  </done>
</task>

</tasks>

<verification>
1. **Race Condition Fixed:**
   - `python -c "import asyncio; from pipeline.db.connection import get_pool; async def test(): p1 = await get_pool(); p2 = await get_pool(); assert p1 is p2; asyncio.run(test())"`

2. **API Key Scrubbing Works:**
   - Run `python -c "from pipeline.utils.security import scrub_sensitive_data; print(scrub_sensitive_data('key=secret123'))"`
   - Verify output contains `***` not `secret123`

3. **Integration Check:**
   - Import `pipeline.crawlers.dropshot_brasil` without errors
   - Verify `SensitiveDataFilter` in logger.filters
</verification>

<success_criteria>
All must be TRUE:
- [ ] Pool initialization uses asyncio.Lock with double-checked locking
- [ ] Concurrent get_pool() calls return same pool instance (tested)
- [ ] Security utilities module exists with scrub_sensitive_data function
- [ ] Drop Shot Brasil crawler scrubs exceptions before logging/alerts
- [ ] No API key patterns can leak through error messages
</success_criteria>

<output>
After completion, create `.planning/phases/12-data-pipeline-quality/12-01-p0-production-blockers-SUMMARY.md`
</output>
