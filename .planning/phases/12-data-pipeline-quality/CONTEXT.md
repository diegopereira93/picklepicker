# Phase 12: Data Pipeline Quality & Reliability

## Context from Engineering Review

This phase addresses critical operational issues identified in the `/plan-eng-review` of the data pipeline.

### Background
The PickleIQ data pipeline (Phase 2) successfully implements:
- Firecrawl-based scrapers for Drop Shot Brasil
- Mercado Livre API integration
- PostgreSQL time-series storage with pgvector
- GitHub Actions scheduled crawlers (24h)

However, the engineering review identified **production-critical issues** that need resolution before scaling.

## Critical Issues to Address

### P0 — Production Blockers

1. **Race Condition in Pool Initialization** (`pipeline/db/connection.py`)
   - Two concurrent calls can create duplicate connection pools
   - Missing lock around check-then-act pattern

2. **API Key Exposure Risk** (`pipeline/crawlers/dropshot_brasil.py`)
   - Firecrawl API key can leak via exception messages
   - No scrubbing of sensitive data from logs

### P1 — High Priority

3. **Missing Transaction Rollback**
   - If save throws mid-transaction, connection returned to pool with uncommitted state
   - Can poison the connection pool

4. **Connection Pool Exhaustion**
   - Parallel GitHub Actions jobs hit `max_size=5` pool simultaneously
   - No coordination between jobs

5. **Unbounded Memory Growth**
   - `fetch_all=True` loads ALL ML products into memory
   - Risk of OOM with large datasets

6. **TOCTOU Race in Upsert**
   - `ON CONFLICT DO NOTHING` + separate `SELECT` can fail if row deleted between statements

7. **No Retry on ML API**
   - Unlike Drop Shot, ML crawler lacks retry logic
   - Single transient failure causes full job failure

### P2 — Medium Priority

8. **Cron Thundering Herd** — All jobs run at same minute (no jitter)
9. **No Workflow-Level Retry** in GitHub Actions
10. **Missing Data Quality Metrics** — No tracking of null rates, validation failures
11. **No Dead Letter Queue** — Failed records lost forever
12. **Data Freshness Monitoring** — No alerts for stale data

## Success Criteria

All must be TRUE:
- [ ] Pool initialization is thread-safe with asyncio.Lock
- [ ] No sensitive data exposed in logs/exceptions
- [ ] Transaction rollback on all crawler exceptions
- [ ] Connection pool has max_waiting and backpressure
- [ ] ML pagination has memory limit (max 1000 items)
- [ ] ML crawler has retry logic with exponential backoff
- [ ] GitHub Actions has workflow-level retry
- [ ] Data quality metrics table exists and is populated
- [ ] Dead letter queue for failed extractions
- [ ] Freshness alerts via Telegram if data > 48h old

## Technical Stack
- Python 3.12 + asyncpg/psycopg_pool
- PostgreSQL 15 + pgvector
- GitHub Actions
- Tenacity (retry library)

## Notes
- Based on recommendations from `/plan-eng-review` + outside voice
- Original reviewer + independent AI both flagged these issues
- Focus on correctness before adding features
