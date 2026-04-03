---
phase: 12-data-pipeline-quality
plan: 03
plan_name: Memory and Concurrency Fixes
subsystem: pipeline
tags: [memory, concurrency, atomic-upsert, toctou, pagination]
requires: [12-01]
provides: [memory-bounded-crawler, atomic-upsert]
affects: [pipeline/crawlers/mercado_livre.py, pipeline/db/schema.sql]
tech-stack:
  added: []
  patterns: [MAX_ITEMS limit, ON CONFLICT DO UPDATE RETURNING]
key-files:
  created: []
  modified:
    - pipeline/crawlers/mercado_livre.py
    - pipeline/db/schema.sql
decisions:
  - "Use MAX_ITEMS=1000 as hard limit to prevent unbounded memory growth"
  - "Atomic upsert with ON CONFLICT DO UPDATE ... RETURNING eliminates TOCTOU race"
  - "Fail-fast with PostgreSQL error if UNIQUE constraint missing (safer than silent data loss)"
metrics:
  duration: 15m
  completed_date: 2026-04-01
---

# Phase 12 Plan 03: Memory and Concurrency Fixes Summary

Fixed memory exhaustion and TOCTOU race condition in Mercado Livre crawler to make it production-ready for large datasets.

## Changes Made

### Task 1: Memory-Bounded Pagination
- Added `MAX_ITEMS = 1000` constant to prevent unbounded memory growth
- Updated `search_pickleball_paddles()` to track `items_fetched` counter
- Added early break condition when `items_fetched >= MAX_ITEMS`
- Logs warning when pagination limit is reached
- Updated docstring to document MAX_ITEMS behavior

### Task 2: Atomic Upsert (TOCTOU Fix)
- Replaced `ON CONFLICT DO NOTHING` with `ON CONFLICT (name) DO UPDATE SET`
- Uses `EXCLUDED.*` pattern to update existing rows atomically
- Removed vulnerable separate `SELECT id FROM paddles WHERE name = ...` query
- Single query with `RETURNING id` gets paddle_id atomically
- Updated docstring with upsert behavior and constraint requirement

### Task 3: Database Constraint
- Added `CONSTRAINT unique_paddle_name UNIQUE (name)` to paddles table
- Required for `ON CONFLICT (name)` clause to work correctly
- Code fails safely with PostgreSQL error if constraint missing

## Verification Results

| Criterion | Status |
|-----------|--------|
| MAX_ITEMS = 1000 constant defined | PASS |
| Pagination stops at items_fetched >= MAX_ITEMS | PASS |
| Warning logged when limit reached | PASS |
| ON CONFLICT DO UPDATE pattern | PASS |
| Single query with RETURNING id | PASS |
| TOCTOU-vulnerable code removed | PASS |
| UNIQUE constraint on paddles.name | PASS |

## Commits

1. `b6baa54` feat(12-03): add MAX_ITEMS memory limit to ML pagination
2. `be7ca22` feat(12-03): fix TOCTOU race with atomic upsert
3. `96031f1` feat(12-03): add UNIQUE constraint on paddles.name for atomic upsert

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- All modified files exist and contain expected changes
- All commits recorded with correct hashes
- Verification commands confirm all success criteria met
