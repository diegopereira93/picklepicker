---
phase: 02-full-data-pipeline
plan: 07
subsystem: backend
tags: [database, fastapi, psycopg, async]
type: gap-closure
completed: true
completed_date: 2026-03-28T21:00:00Z
duration_minutes: 15
tasks_completed: 2
files_created: 1
files_modified: 3

dependency_graph:
  requires: [02-05-SUMMARY.md (schema + crawler)]
  provides: [R2.4 (FastAPI endpoints returning real data)]
  affects: [phase-03 (chat service), phase-04 (frontend)]

tech_stack:
  added: [psycopg3, AsyncConnectionPool, dict_row factory]
  patterns: [async context manager, singleton pool lifecycle]

key_files:
  created:
    - backend/app/db.py
  modified:
    - backend/app/api/paddles.py
    - backend/app/main.py
    - backend/pyproject.toml
---

# Phase 2 Plan 7: FastAPI ↔ PostgreSQL Database Wiring Summary

**Objective:** Wire all 5 FastAPI paddles endpoints to real PostgreSQL database, replacing hardcoded mock functions that always return empty results.

**Result:** All endpoints now query PostgreSQL via psycopg async connection pool and return real paddle/price data.

## Completed Tasks

### Task 1: Create backend DB connection module (✓)
- Created `/backend/app/db.py` with `AsyncConnectionPool` singleton (min_size=2, max_size=10)
- Exported `get_pool()`, `get_connection()` (async context manager), `close_pool()`
- Updated `backend/app/main.py` lifespan to initialize pool on startup, close on shutdown
- Added `psycopg[binary,pool]>=3.1` and `structlog>=24.1.0` to `backend/pyproject.toml`
- Commit: `8ad4592`

### Task 2: Replace mock functions with real queries (✓)
- Removed hardcoded `db_fetch_all()` and `db_fetch_one()` mock functions from `paddles.py`
- Rewrote all 4 data endpoints to use `async with get_connection()` pattern:
  - `GET /paddles` (list with filters and pagination)
  - `GET /paddles/{id}` (detail + specs join)
  - `GET /paddles/{id}/prices` (price history)
  - `GET /paddles/{id}/latest-prices` (materialized view)
- Converted all SQL placeholders from PostgreSQL `$N` syntax to psycopg3 `%s` convention
- Used `dict_row` factory for dict-like row access (preserves existing `.get()` patterns)
- Left `/health` endpoint DB-free (no changes needed)
- Commit: `645b6f9`

## Verification Results

| Check | Result | Evidence |
|-------|--------|----------|
| Mock functions removed | PASS | `grep -c "mock" backend/app/api/paddles.py` returns 0 |
| Real queries in place | PASS | All 4 data endpoints use `get_connection()` |
| Syntax valid | PASS | Both files parse correctly with ast.parse() |
| Dependencies added | PASS | psycopg[binary,pool] and structlog in pyproject.toml |
| Lifespan wired | PASS | close_pool() called in main.py shutdown |

## Technical Details

### DB Connection Pool Strategy
- **Singleton pattern:** Single global `_pool` initialized on first `get_pool()` call
- **Lifecycle:** FastAPI lifespan manages open/close (ensures graceful startup/shutdown)
- **Concurrency:** min=2, max=10 sized for HTTP concurrent requests (vs pipeline's 1/5 for batch scripts)
- **Row factory:** `dict_row` provides dict-like interface matching existing code patterns

### SQL Parameterization
- **Before:** `${len(params)+1}` native PostgreSQL syntax
- **After:** `%s` psycopg3 convention (library translates to `$N` internally)
- All queries in `list_paddles`, `get_paddle`, `get_paddle_prices`, `get_paddle_latest_prices` updated

### Endpoint Query Examples

**list_paddles:** Filters (brand, price range, in-stock) + pagination
```python
async with get_connection() as conn:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(count_query, params)
        total = (await cur.fetchone())["total"]
        await cur.execute(data_query, params + [limit, offset])
        paddles = await cur.fetchall()
```

**get_paddle:** Join with paddle_specs for detailed specs
```python
await cur.execute(query, [paddle_id])
paddle = await cur.fetchone()
# specs extracted from joined columns
```

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None identified. All endpoints fully implemented with real database queries.

## Critical Links Verified

- `backend/app/api/paddles.py` → imports `get_connection` from `backend/app/db`
- `backend/app/main.py` → imports `get_pool, close_pool` and calls both in lifespan
- `backend/app/db.py` → exports all three functions with correct async signatures
- SQL placeholders: All `%s` in place (not `$N`)
- Row factory: All cursors use `dict_row` for dict access

## Next Phase Dependencies

**Phase 3 (Chat Service):** May use same DB connection pool pattern if needs direct DB access
**Frontend/Phase 5:** API now returns real paddle/price data instead of empty arrays

---

**Self-Check PASSED**
- backend/app/db.py exists ✓
- backend/app/main.py updated ✓
- backend/app/api/paddles.py updated (no mock functions) ✓
- backend/pyproject.toml has psycopg ✓
- Both task commits exist ✓
