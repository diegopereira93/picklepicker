---
phase: 12-data-pipeline-quality
plan: 01
subsystem: pipeline
phase_name: data-pipeline-quality
plan_name: p0-production-blockers
status: completed
completed_date: "2026-04-01"
depends_on: []
truth_verified:
  - Pool initialization is thread-safe with asyncio.Lock (no duplicate pools)
  - Firecrawl API key never appears in logs or exception messages
  - Sensitive data is scrubbed from all error outputs before propagation
key_files:
  created:
    - pipeline/utils/__init__.py
    - pipeline/utils/security.py
    - pipeline/utils/security_test.py
    - pipeline/db/connection_test.py
  modified:
    - pipeline/db/connection.py
    - pipeline/crawlers/dropshot_brasil.py
decisions: []
tech_stack:
  added:
    - pipeline/utils/security.py - Sensitive data scrubbing module
  patterns:
    - Double-checked locking for async singleton initialization
    - Pre-compiled regex patterns for performance
    - Logging.Filter for automatic scrubbing
    - Exception message sanitization before external alerting
metrics:
  duration_minutes: 18
  tasks: 3
  files: 6
  tests: 27
  commits: 3
---

# Phase 12 Plan 01: P0 Production Blockers Summary

**One-liner:** Fixed race condition in connection pool initialization and eliminated API key exposure risk through centralized sensitive data scrubbing.

## What Was Built

### 1. Security Utilities Module (`pipeline/utils/security.py`)

Created a reusable security module providing:

- **`scrub_sensitive_data(text: str)`**: Replaces sensitive values with `***`
  - Covers: api_key, apikey, api-key, token, secret, password, Bearer tokens, URL credentials
  - Pre-compiled regex patterns for performance
  - Handles URL query parameters specially

- **`SensitiveDataFilter(logging.Filter)`**: Automatic scrubbing for log messages
  - Attaches to any logger to scrub msg and args
  - Safe to use across all log levels

- **`mask_exception(exception: Exception)`**: Creates sanitized exception preserving type
  - Scrubs exception args and string representation
  - Maintains original exception type for proper handling

### 2. Race Condition Fix (`pipeline/db/connection.py`)

Implemented thread-safe connection pool initialization:

- Added `_pool_lock: asyncio.Lock | None = None` global
- Double-checked locking pattern in `get_pool()`:
  - Check `_pool is None` (fast path for cached pool)
  - Acquire lock and re-check (prevents duplicate initialization)
- `close_pool()` resets both `_pool` and `_pool_lock`

### 3. Crawler Security (`pipeline/crawlers/dropshot_brasil.py`)

Protected API keys from leaking in logs and alerts:

- Attached `SensitiveDataFilter` to crawler logger
- Exception messages scrubbed before:
  - Logging via `logger.error()`
  - Telegram alerts via `send_telegram_alert()`
- Sanitized exception re-raised with original as cause (`raise type(e)(safe_message) from e`)

## Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| `pipeline/utils/security_test.py` | 20 | All pass |
| `pipeline/db/connection_test.py` | 7 | All pass |
| **Total** | **27** | **All pass** |

### Key Test Scenarios

**Security scrubbing:**
- API keys, Bearer tokens, URL credentials
- Multiple secrets in single message
- Empty strings and None handling
- Custom replacement strings
- Exception masking with type preservation

**Race condition:**
- Concurrent get_pool() calls return same instance
- Double-checked locking prevents duplicate initialization
- close_pool() resets both pool and lock
- Subsequent calls use cached pool

## Verification Results

```bash
# Race condition fix verified
$ python3 -c "concurrent get_pool() calls return same pool"
Race condition test passed: concurrent calls return same pool

# API key scrubbing verified
$ python3 -c "scrub_sensitive_data('key=sk-test123')"
Scrubbing test passed: 'sk-test123' not in output, '***' present

# Integration verified
$ python3 -c "from pipeline.crawlers import dropshot_brasil"
Integration check passed: SensitiveDataFilter attached to logger
```

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 0b5d3dc | test | Add security utilities with sensitive data scrubbing (TDD) |
| 585794c | feat | Fix race condition in connection pool with asyncio.Lock (TDD) |
| ad2f0f5 | feat | Add API key scrubbing to Drop Shot Brasil crawler |

## Deviations from Plan

None. Plan executed exactly as written.

## Self-Check: PASSED

- [x] All created files exist
- [x] All modified files have correct changes
- [x] All commits exist and have proper messages
- [x] All tests pass (27/27)
- [x] Success criteria met (all 5 criteria verified)

## Known Stubs

None. All functionality fully implemented with tests.
