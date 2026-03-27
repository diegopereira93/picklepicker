---
phase: 01-foundation-data-infrastructure
plan: "02"
subsystem: database
tags: [postgresql, pgvector, schema, docker]
dependency_graph:
  requires: ["01-01"]
  provides: ["database schema", "retailer seed data", "pgvector extension"]
  affects: ["01-03", "01-04", "all API plans"]
tech_stack:
  added: []
  patterns: ["append-only price time series", "materialized view for latest prices", "pgvector embeddings table"]
key_files:
  created:
    - pipeline/db/schema.sql
  modified: []
decisions:
  - "latest_prices uses DISTINCT ON (paddle_id, retailer_id) ORDER BY scraped_at DESC — correct PostgreSQL pattern for latest-per-group without window functions"
  - "REFRESH MATERIALIZED VIEW CONCURRENTLY requires unique index — added CREATE UNIQUE INDEX ON latest_prices (paddle_id, retailer_id)"
  - "review_queue type CHECK constraint covers all three use cases: duplicate, spec_unmatched, price_anomaly"
metrics:
  duration: "1 min"
  completed_date: "2026-03-26"
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 0
---

# Phase 1 Plan 02: PostgreSQL Schema Summary

**One-liner:** Complete PostgreSQL DDL with 8 tables, latest_prices materialized view, pgvector(1536) embeddings column, composite price index, and retailer seed data — auto-applied via Docker entrypoint.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create complete PostgreSQL schema | 512c20f | pipeline/db/schema.sql (created) |
| 2 | Verify schema applies in Docker | — (verification only) | — |

## What Was Built

`pipeline/db/schema.sql` contains the full DDL for the PickleIQ data foundation:

- **8 tables:** paddles, retailers, price_snapshots, paddle_specs, paddle_embeddings, review_queue, users, price_alerts
- **Materialized view:** `latest_prices` using `DISTINCT ON (paddle_id, retailer_id)` ordered by `scraped_at DESC`
- **Indexes:** composite `idx_price_snapshots_paddle_retailer_time` on `(paddle_id, retailer_id, scraped_at DESC)`; unique index on `latest_prices (paddle_id, retailer_id)` to support concurrent refresh
- **pgvector:** `CREATE EXTENSION IF NOT EXISTS vector` + `embedding vector(1536)` in paddle_embeddings
- **Seed data:** 2 retailers — Brazil Pickleball Store (firecrawl), Mercado Livre (ml_api)
- **Auto-applied:** mounted as `/docker-entrypoint-initdb.d/01-schema.sql` in docker-compose.yml

All 8 tables, materialized view, pgvector extension, and seed data verified live in Docker PostgreSQL.

## Verification Results

All acceptance criteria passed:

- information_schema.tables count = 8 (public, BASE TABLE)
- pg_matviews count = 1 for latest_prices
- pg_extension count = 1 for vector
- retailers count = 2 (Brazil Pickleball Store, Mercado Livre)
- Docker container healthy, left running for Plans 01-03 and 01-04

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — schema is complete DDL. users and price_alerts tables are intentionally empty (populated Phase 5 per plan).

## Self-Check: PASSED

- pipeline/db/schema.sql: FOUND
- commit 512c20f: verified via git log
