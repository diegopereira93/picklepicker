---
phase: 12-data-pipeline-quality
plan: 04
type: execute
wave: 3
depends_on: ["12-02", "12-03"]
files_modified:
  - .github/workflows/scraper.yml
  - pipeline/db/quality_metrics.py
  - pipeline/db/dead_letter_queue.py
  - pipeline/alerts/freshness.py
  - prisma/migrations/add_quality_tables.sql
autonomous: true
requirements:
  - PIPE-08
  - PIPE-09
  - PIPE-10
  - PIPE-11
  - PIPE-12
must_haves:
  truths:
    - "GitHub Actions workflow has retry on failure with jittered cron schedule"
    - "Data quality metrics tracked for null rates and validation failures"
    - "Dead letter queue stores failed extractions for reprocessing"
    - "Freshness alerts sent via Telegram when data is >48h old"
    - "Cron schedule has jitter to prevent thundering herd"
  artifacts:
    - path: ".github/workflows/scraper.yml"
      provides: "Workflow-level retry and jittered schedule"
      changes: ["strategy.max-attempts: 3", "cron with jitter"]
    - path: "pipeline/db/quality_metrics.py"
      provides: "Data quality tracking functions"
      exports: ["record_validation_failure", "get_null_rate_metrics"]
    - path: "pipeline/db/dead_letter_queue.py"
      provides: "Failed extraction storage and retry"
      exports: ["queue_failed_extraction", "retry_dead_letter_items"]
    - path: "pipeline/alerts/freshness.py"
      provides: "Data freshness monitoring"
      exports: ["check_data_freshness", "send_freshness_alert"]
  key_links:
    - from: "GitHub Actions cron schedule"
      to: "jittered timing"
      via: "random offset in minutes"
      pattern: "cron.*[0-9].*[0-9]"
    - from: "crawler failures"
      to: "dead_letter_queue"
      via: "queue_failed_extraction()"
      pattern: "INSERT INTO dead_letter_queue"
    - from: "GitHub Actions schedule"
      to: "freshness check"
      via: "freshness alert job"
      pattern: "pipeline.alerts.freshness"
---

<objective>
Build observability infrastructure: workflow retries, data quality metrics, dead letter queue, and freshness alerts.

Purpose: Enable monitoring, debugging, and recovery from pipeline failures. Provide visibility into data quality and pipeline health.
Output: Complete observability stack with metrics, DLQ, and alerting.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/12-data-pipeline-quality/CONTEXT.md
@.github/workflows/scraper.yml
@pipeline/alerts/telegram.py
@prisma/schema.prisma
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add workflow-level retry and cron jitter to GitHub Actions</name>
  <files>.github/workflows/scraper.yml</files>
  <action>
    Update `.github/workflows/scraper.yml`:

    1. Add strategy block for workflow-level retry:
       ```yaml
       jobs:
         crawl:
           runs-on: ubuntu-latest
           strategy:
             fail-fast: false
             max-parallel: 1
           # Retry entire workflow on failure
           timeout-minutes: 30
       ```

    2. Add job-level retry using GitHub Actions syntax:
       ```yaml
       jobs:
         crawl:
           runs-on: ubuntu-latest
           steps:
             # ... existing steps ...

           # Add retry logic for the entire job
           outputs:
             status: ${{ job.status }}
       ```

    3. Actually, GitHub Actions doesn't have native job-level retry.
       Use a workaround with reusable workflow or step-level retry:
       ```yaml
       - name: Run crawlers with retry
         uses: nick-fields/retry@v3
         with:
           timeout_minutes: 30
           max_attempts: 3
           retry_on: error
           command: |
             cd backend
             python -m pipeline.crawlers.brazil_pickleball_store
             python -m pipeline.crawlers.mercado_livre
             python -m pipeline.crawlers.drop_shot_brasil
         continue-on-error: false
       ```

    4. Update cron schedule to add jitter:
       Change from:
       ```yaml
       schedule:
         - cron: '0 2 * * *'  # 2 AM UTC
       ```
       To a staggered schedule:
       ```yaml
       schedule:
         # Stagger jobs: 2:00, 2:05, 2:10 UTC to prevent thundering herd
         - cron: '0 2 * * *'
         - cron: '5 2 * * *'
         - cron: '10 2 * * *'
       ```

    5. Alternatively, use dynamic jitter in workflow (simpler):
       Keep single schedule, add sleep with random offset in job:
       ```yaml
       - name: Add jitter delay
         run: |
           # Random sleep 0-120 seconds to prevent thundering herd
           sleep $((RANDOM % 120))
       ```

    6. Implement the simpler jitter approach + step retry
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && grep -E "(retry|sleep|jitter)" .github/workflows/scraper.yml</automated>
  </verify>
  <done>
    - Workflow has retry mechanism (nick-fields/retry or similar)
    - Jitter added via random sleep step
    - No longer using continue-on-error: true
    - All three crawlers run in single retry-wrapped step
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Create data quality metrics tracking module</name>
  <files>pipeline/db/quality_metrics.py, pipeline/db/quality_metrics_test.py</files>
  <behavior>
    - record_validation_failure logs source, field, reason, timestamp
    - get_null_rate_metrics returns percentage null per field
    - get_validation_summary aggregates failures by source/field
    - Metrics persisted to data_quality_checks table
  </behavior>
  <action>
    Create `pipeline/db/quality_metrics.py`:

    1. Define Pydantic models for quality checks:
       ```python
       from datetime import datetime
       from typing import Optional
       from pydantic import BaseModel

       class ValidationFailure(BaseModel):
           source: str  # crawler name
           field: str   # field that failed validation
           reason: str  # why it failed
           raw_value: Optional[str]
           created_at: datetime = datetime.utcnow()

       class NullRateMetric(BaseModel):
           source: str
           field: str
           total_records: int
           null_count: int
           null_rate_pct: float
           checked_at: datetime = datetime.utcnow()
       ```

    2. Create tracking functions:
       ```python
       from pipeline.db.connection import get_connection

       async def record_validation_failure(
           source: str,
           field: str,
           reason: str,
           raw_value: Optional[str] = None,
       ) -> None:
           """Record a validation failure for later analysis."""
           async with get_connection() as conn:
               await conn.execute(
                   """
                   INSERT INTO data_quality_checks
                       (source, field, reason, raw_value, created_at)
                   VALUES (%(source)s, %(field)s, %(reason)s, %(raw_value)s, NOW())
                   """,
                   {
                       "source": source,
                       "field": field,
                       "reason": reason,
                       "raw_value": raw_value,
                   },
               )
               await conn.commit()

       async def get_null_rate_metrics(
           source: str,
           table: str,
           fields: list[str],
       ) -> list[NullRateMetric]:
           """Calculate null rate for specified fields."""
           # Implementation queries table for null counts
           pass
       ```

    3. Add SQL migration in `prisma/migrations/add_quality_tables.sql`:
       ```sql
       CREATE TABLE IF NOT EXISTS data_quality_checks (
           id SERIAL PRIMARY KEY,
           source VARCHAR(100) NOT NULL,
           field VARCHAR(100) NOT NULL,
           reason TEXT NOT NULL,
           raw_value TEXT,
           created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
       );

       CREATE INDEX idx_quality_checks_source ON data_quality_checks(source);
       CREATE INDEX idx_quality_checks_created_at ON data_quality_checks(created_at);
       ```

    4. Add usage in crawlers (update existing crawlers):
       ```python
       # In mercado_livre.py where we skip items
       if not price:
           await record_validation_failure(
               source="mercado_livre",
               field="price",
               reason="missing_or_zero",
               raw_value=str(item.get("price")),
           )
       ```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/db/quality_metrics_test.py -v</automated>
  </verify>
  <done>
    - quality_metrics.py exists with record_validation_failure
    - SQL migration creates data_quality_checks table
    - Tests pass for validation recording and metrics calculation
    - At least one crawler updated to use quality tracking
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Create dead letter queue for failed extractions</name>
  <files>pipeline/db/dead_letter_queue.py, pipeline/db/dead_letter_queue_test.py, prisma/migrations/add_dlq_table.sql</files>
  <behavior>
    - Failed extractions stored with full context (source, payload, error)
    - DLQ items can be retried via retry_dead_letter_items()
    - Max retry count tracked to prevent infinite loops
    - Processed items marked as resolved or max-retried
  </behavior>
  <action>
    Create `pipeline/db/dead_letter_queue.py`:

    1. Define DLQ models:
       ```python
       from datetime import datetime
       from enum import Enum
       from typing import Optional
       from pydantic import BaseModel

       class DLQStatus(str, Enum):
           PENDING = "pending"
           PROCESSING = "processing"
           RESOLVED = "resolved"
           FAILED = "failed"  # Max retries exceeded

       class DeadLetterItem(BaseModel):
           id: Optional[int]
           source: str  # Which crawler
           payload: dict  # The data that failed
           error_message: str
           retry_count: int = 0
           max_retries: int = 3
           status: DLQStatus = DLQStatus.PENDING
           created_at: datetime = datetime.utcnow()
           updated_at: Optional[datetime]
       ```

    2. Create DLQ functions:
       ```python
       from pipeline.db.connection import get_connection

       async def queue_failed_extraction(
           source: str,
           payload: dict,
           error_message: str,
           max_retries: int = 3,
       ) -> int:
           """Add a failed extraction to the DLQ. Returns DLQ item ID."""
           async with get_connection() as conn:
               result = await conn.execute(
                   """
                   INSERT INTO dead_letter_queue
                       (source, payload, error_message, max_retries, status, created_at)
                   VALUES (%(source)s, %(payload)s, %(error_message)s, %(max_retries)s, 'pending', NOW())
                   RETURNING id
                   """,
                   {
                       "source": source,
                       "payload": json.dumps(payload),
                       "error_message": error_message,
                       "max_retries": max_retries,
                   },
               )
               row = await result.fetchone()
               await conn.commit()
               return row[0]

       async def get_pending_dlq_items(limit: int = 100) -> list[DeadLetterItem]:
           """Get pending DLQ items for retry processing."""
           async with get_connection() as conn:
               result = await conn.execute(
                   """
                   SELECT id, source, payload, error_message, retry_count, max_retries, status, created_at, updated_at
                   FROM dead_letter_queue
                   WHERE status = 'pending' AND retry_count < max_retries
                   ORDER BY created_at
                   LIMIT %(limit)s
                   """,
                   {"limit": limit},
               )
               rows = await result.fetchall()
               return [DeadLetterItem(**dict(row)) for row in rows]

       async def update_dlq_status(
           item_id: int,
           status: DLQStatus,
           increment_retry: bool = False,
       ) -> None:
           """Update DLQ item status and retry count."""
           async with get_connection() as conn:
               await conn.execute(
                   """
                   UPDATE dead_letter_queue
                   SET status = %(status)s,
                       retry_count = retry_count + %(increment)s,
                       updated_at = NOW()
                   WHERE id = %(id)s
                   """,
                   {"status": status.value, "increment": 1 if increment_retry else 0, "id": item_id},
               )
               await conn.commit()
       ```

    3. Add SQL migration:
       ```sql
       CREATE TABLE IF NOT EXISTS dead_letter_queue (
           id SERIAL PRIMARY KEY,
           source VARCHAR(100) NOT NULL,
           payload JSONB NOT NULL,
           error_message TEXT NOT NULL,
           retry_count INTEGER DEFAULT 0,
           max_retries INTEGER DEFAULT 3,
           status VARCHAR(20) DEFAULT 'pending',
           created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
           updated_at TIMESTAMP WITH TIME ZONE
       );

       CREATE INDEX idx_dlq_status ON dead_letter_queue(status, retry_count);
       CREATE INDEX idx_dlq_created_at ON dead_letter_queue(created_at);
       ```

    4. Update crawlers to use DLQ on failure:
       ```python
       from pipeline.db.dead_letter_queue import queue_failed_extraction

       # In crawler exception handler
       except Exception as e:
           await queue_failed_extraction(
               source="dropshot_brasil",
               payload=product,
               error_message=str(e),
           )
       ```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/db/dead_letter_queue_test.py -v</automated>
  </verify>
  <done>
    - dead_letter_queue.py exists with queue_failed_extraction
    - SQL migration creates dead_letter_queue table
    - get_pending_dlq_items and update_dlq_status implemented
    - Tests pass for DLQ operations
  </done>
</task>

<task type="auto">
  <name>Task 4: Create data freshness monitoring and alerting</name>
  <files>pipeline/alerts/freshness.py, .github/workflows/scraper.yml</files>
  <action>
    Create `pipeline/alerts/freshness.py`:

    1. Implement freshness checking:
       ```python
       import os
       from datetime import datetime, timedelta
       from typing import Optional
       from pipeline.db.connection import get_connection
       from pipeline.alerts.telegram import send_telegram_alert

       FRESHNESS_THRESHOLD_HOURS = 48

       async def get_latest_scrape_timestamp(source: str) -> Optional[datetime]:
           """Get the most recent scrape timestamp for a source."""
           async with get_connection() as conn:
               result = await conn.execute(
                   """
                   SELECT MAX(scraped_at) as latest
                   FROM price_snapshots
                   WHERE retailer_id = (
                       SELECT id FROM retailers WHERE name = %(source)s
                   )
                   """,
                   {"source": source},
               )
               row = await result.fetchone()
               return row[0] if row else None

       async def check_data_freshness() -> dict[str, bool]:
           """Check freshness for all data sources. Returns source -> is_fresh map."""
           sources = ["dropshot_brasil", "mercado_livre"]
           results = {}
           threshold = timedelta(hours=FRESHNESS_THRESHOLD_HOURS)

           for source in sources:
               latest = await get_latest_scrape_timestamp(source)
               if latest is None:
                   results[source] = False
                   await send_freshness_alert(source, None)
               elif datetime.utcnow() - latest > threshold:
                   results[source] = False
                   await send_freshness_alert(source, latest)
               else:
                   results[source] = True

           return results

       async def send_freshness_alert(source: str, latest: Optional[datetime]) -> None:
           """Send Telegram alert for stale data."""
           if latest is None:
               message = f"⚠️ Data Freshness Alert: No data found for {source}. Run crawlers immediately."
           else:
               hours_old = int((datetime.utcnow() - latest).total_seconds() / 3600)
               message = f"⚠️ Data Freshness Alert: {source} data is {hours_old}h old (threshold: {FRESHNESS_THRESHOLD_HOURS}h)"

           await send_telegram_alert(message)
       ```

    2. Add freshness check to GitHub Actions:
       ```yaml
       - name: Check data freshness
         run: |
           cd backend
           python -c "
           import asyncio
           from pipeline.alerts.freshness import check_data_freshness
           asyncio.run(check_data_freshness())
           "
         continue-on-error: true
       ```

    3. Add separate freshness alert workflow (optional):
       Create `.github/workflows/freshness-check.yml`:
       ```yaml
       name: Data Freshness Check
       on:
         schedule:
           - cron: '0 6 * * *'  # 6 AM UTC daily
         workflow_dispatch:
       jobs:
         check:
           runs-on: ubuntu-latest
           steps:
             - uses: actions/checkout@v4
             - name: Check freshness
               run: |
                 cd backend
                 python -c "import asyncio; from pipeline.alerts.freshness import check_data_freshness; asyncio.run(check_data_freshness())"
       ```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -c "
from pipeline.alerts.freshness import FRESHNESS_THRESHOLD_HOURS, check_data_freshness
assert FRESHNESS_THRESHOLD_HOURS == 48
import inspect
assert inspect.iscoroutinefunction(check_data_freshness)
print('Freshness module structure verified')
"</automated>
  </verify>
  <done>
    - freshness.py exists with check_data_freshness function
    - FRESHNESS_THRESHOLD_HOURS = 48 configured
    - get_latest_scrape_timestamp queries price_snapshots
    - send_freshness_alert sends Telegram notifications
    - Freshness check integrated into workflow
  </done>
</task>

</tasks>

<verification>
1. **Workflow Retry:**
   - `grep -n "nick-fields/retry" .github/workflows/scraper.yml`
   - Check max_attempts is set

2. **Cron Jitter:**
   - Verify random sleep in workflow steps

3. **Quality Metrics:**
   - Table exists: `data_quality_checks`
   - Index exists on source and created_at

4. **Dead Letter Queue:**
   - Table exists: `dead_letter_queue`
   - Module exports queue_failed_extraction

5. **Freshness Alerts:**
   - FRESHNESS_THRESHOLD_HOURS = 48
   - Telegram integration working
</verification>

<success_criteria>
All must be TRUE:
- [ ] Workflow has retry mechanism with max_attempts=3
- [ ] Cron schedule has jitter (random sleep or staggered schedules)
- [ ] data_quality_checks table exists and is populated
- [ ] dead_letter_queue table exists with retry_count tracking
- [ ] Freshness checking queries latest scrape timestamps
- [ ] Telegram alerts sent when data > 48h old
- [ ] All new modules have test files with passing tests
</success_criteria>

<output>
After completion, create `.planning/phases/12-data-pipeline-quality/12-04-p2-observability-infrastructure-SUMMARY.md`
</output>
