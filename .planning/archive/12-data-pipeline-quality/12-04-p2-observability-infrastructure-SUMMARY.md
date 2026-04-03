---
phase: 12-data-pipeline-quality
plan: 04
subsystem: pipeline
tags: [observability, retry, dead-letter-queue, metrics, alerting, github-actions, cron]

# Dependency graph
requires:
  - phase: 12-02
    provides: Transaction and retry infrastructure for observability hooks
  - phase: 12-03
    provides: Atomic upsert patterns for DLQ and metrics integration

provides:
  - Workflow-level retry with nick-fields/retry@v3
  - Cron jitter to prevent thundering herd
  - Data quality metrics tracking (null rates, validation failures)
  - Dead letter queue for failed extractions with retry capability
  - Data freshness monitoring with 48h threshold and Telegram alerts
  - SQL migrations for data_quality_checks and dead_letter_queue tables

affects:
  - pipeline-extraction
  - pipeline-monitoring
  - alerts

tech-stack:
  added: [nick-fields/retry, pydantic]
  patterns:
    - TDD RED-GREEN-REFACTOR for database modules
    - Async context managers for database connections
    - Pydantic models for data validation and serialization

key-files:
  created:
    - pipeline/db/quality_metrics.py - Validation failure tracking and null rate metrics
    - pipeline/db/quality_metrics_test.py - TDD tests (7 passing)
    - pipeline/db/dead_letter_queue.py - Failed extraction storage and retry logic
    - pipeline/db/dead_letter_queue_test.py - TDD tests (10 passing)
    - pipeline/alerts/freshness.py - Data freshness monitoring and alerting
    - prisma/migrations/add_quality_tables.sql - SQL migrations for observability tables
  modified:
    - .github/workflows/scraper.yml - Added retry, jitter, staggered cron schedules

key-decisions:
  - "Used staggered cron schedules (2:00, 2:05, 2:10 UTC) combined with random sleep jitter to prevent thundering herd"
  - "Implemented nick-fields/retry@v3 for workflow-level retry with max_attempts=3"
  - "DLQ tracks retry_count and max_retries to prevent infinite loops"
  - "Freshness threshold set to 48 hours based on daily crawl schedule"

patterns-established:
  - "TDD for database modules: Write failing tests first, then implementation"
  - "Pydantic BaseModel for database entity validation and typing"
  - "Enum-based status management for DLQ states"
  - "Async/await patterns for database operations with proper connection pooling"

requirements-completed: [PIPE-08, PIPE-09, PIPE-10, PIPE-11, PIPE-12]

# Metrics
duration: 35min
completed: 2026-04-01
---

# Phase 12 Plan 04: Observability Infrastructure Summary

**Complete observability stack with workflow retry, cron jitter, data quality metrics, dead letter queue, and freshness alerting via Telegram**

## Performance

- **Duration:** 35 min
- **Started:** 2026-04-01T16:30:00Z
- **Completed:** 2026-04-01T17:05:00Z
- **Tasks:** 4/4
- **Files modified:** 7

## Accomplishments

- Added workflow-level retry with 3 attempts using nick-fields/retry@v3
- Implemented cron jitter with staggered schedules and random sleep to prevent thundering herd
- Created data quality metrics module for tracking validation failures and null rates (7 tests)
- Built dead letter queue for failed extractions with retry capability and status tracking (10 tests)
- Implemented freshness monitoring with 48h threshold and Telegram integration
- Created SQL migrations for data_quality_checks and dead_letter_queue tables with indexes

## Task Commits

Each task was committed atomically:

1. **Task 1: Add workflow-level retry and cron jitter** - `c59674c` (feat)
2. **Task 2: Create data quality metrics tracking module** - `93cb19f` (feat)
3. **Task 3: Create dead letter queue for failed extractions** - `59683ef` (feat)
4. **Task 4: Create data freshness monitoring and alerting** - `19d88c1` (feat)

**Plan metadata:** `docs-commit` (docs: complete plan)

_TDD tasks include both test and implementation commits per task_

## Files Created/Modified

- `.github/workflows/scraper.yml` - Staggered cron schedules (2:00, 2:05, 2:10 UTC), jitter delay (0-120s random sleep), nick-fields/retry@v3 with max_attempts=3, freshness check step
- `pipeline/db/quality_metrics.py` - ValidationFailure/NullRateMetric models, record_validation_failure(), get_null_rate_metrics(), get_validation_summary()
- `pipeline/db/quality_metrics_test.py` - 7 TDD tests for quality metrics
- `pipeline/db/dead_letter_queue.py` - DLQStatus enum, DeadLetterItem model, queue_failed_extraction(), get_pending_dlq_items(), update_dlq_status(), retry_dead_letter_items()
- `pipeline/db/dead_letter_queue_test.py` - 10 TDD tests for DLQ
- `pipeline/alerts/freshness.py` - FRESHNESS_THRESHOLD_HOURS=48, check_data_freshness(), send_freshness_alert(), Telegram integration
- `prisma/migrations/add_quality_tables.sql` - data_quality_checks and dead_letter_queue tables with indexes

## Decisions Made

- Combined staggered cron schedules (5-minute intervals) with random sleep jitter for robust thundering herd prevention
- Used nick-fields/retry@v3 for step-level retry instead of complex reusable workflow approach
- Set DLQ max_retries=3 default to match workflow retry count for consistency
- Used JSONB for DLQ payload storage to preserve full extraction context
- Chose 48-hour freshness threshold to accommodate weekend gaps in daily crawl schedule

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all components implemented smoothly with TDD approach.

## User Setup Required

None - no external service configuration required. Database migrations should be applied before first run.

## Self-Check

- [x] `.github/workflows/scraper.yml` exists with retry and jitter
- [x] `pipeline/db/quality_metrics.py` exists with record_validation_failure
- [x] `pipeline/db/dead_letter_queue.py` exists with queue_failed_extraction
- [x] `pipeline/alerts/freshness.py` exists with check_data_freshness
- [x] `prisma/migrations/add_quality_tables.sql` exists with both tables
- [x] All tests pass (17 total: 7 quality + 10 DLQ)
- [x] Commits c59674c, 93cb19f, 59683ef, 19d88c1 exist

**Self-Check: PASSED**

## Next Phase Readiness

- Observability infrastructure complete, ready for Phase 13 planning
- All pipeline failures can now be tracked in DLQ for retry
- Data quality metrics available for monitoring dashboard
- Freshness alerts will notify when crawlers fail to run
- No blockers - Phase 12 complete

---

*Phase: 12-data-pipeline-quality*
*Completed: 2026-04-01*
