---
status: partial
phase: 01-foundation-data-infrastructure
source: [01-VERIFICATION.md]
started: 2026-03-26T23:55:00.000Z
updated: 2026-03-26T23:55:00.000Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Supabase staging provisioned with pgvector
expected: Supabase project created at staging URL, pgvector extension available (`SELECT * FROM pg_extension WHERE extname='vector'` returns 1 row), SUPABASE_URL and SUPABASE_ANON_KEY set in .env
result: [pending]

### 2. ML Afiliados affiliate parameter confirmed
expected: ML Afiliados dashboard confirms affiliate tag parameter name (matt_id or equivalent), affiliate_url in price_snapshots rows contains the correct parameter when crawler runs with real credentials
result: [pending]

### 3. ≥50 paddles indexed from live crawl
expected: `SELECT COUNT(*) FROM price_snapshots` returns ≥ 50 after running both crawlers with real API keys (FIRECRAWL_API_KEY, ML_AFFILIATE_TAG set)
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
