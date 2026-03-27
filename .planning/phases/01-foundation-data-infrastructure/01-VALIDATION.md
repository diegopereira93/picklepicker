---
phase: 1
slug: foundation-data-infrastructure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-asyncio 1.3.0 |
| **Config file** | `pipeline/pyproject.toml` — `[tool.pytest.ini_options]` |
| **Quick run command** | `cd pipeline && pytest tests/test_brazil_store_crawler.py -x` |
| **Full suite command** | `cd pipeline && pytest --cov=crawlers --cov=db --cov=alerts --cov-report=term-missing` |

---

## Sampling Rate

- **Per task commit:** `cd pipeline && pytest tests/ -x --tb=short`
- **Per wave merge:** `cd pipeline && pytest --cov=crawlers --cov=db --cov=alerts --cov-report=term-missing`
- **Phase gate:** Full suite green + coverage ≥ 80% before `/gsd:verify-work`

---

## Per-Task Verification Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| R1.1 | Docker Compose starts PostgreSQL (pgvector image) successfully | manual | `docker compose up -d && docker compose ps` | N/A |
| R1.1 | Supabase staging project reachable | manual | `psql $SUPABASE_URL -c "\dt"` | N/A |
| R1.2 | All 8 tables + materialized view exist in DB | automated | `psql $DATABASE_URL -c "\dt" \| grep -E 'paddles\|retailers\|price_snapshots\|paddle_specs\|paddle_embeddings\|review_queue\|users\|price_alerts'` | N/A |
| R1.2 | latest_prices materialized view exists | automated | `psql $DATABASE_URL -c "\dm" \| grep latest_prices` | N/A |
| R1.3 | Happy path: Firecrawl /extract → saves to price_snapshots | unit (mock Firecrawl + DB) | `pytest tests/test_brazil_store_crawler.py::test_happy_path -x` | Wave 0 |
| R1.3 | Retry: 3 attempts with growing backoff on 5xx | unit (mock 5xx × 3 then success) | `pytest tests/test_brazil_store_crawler.py::test_retry_backoff -x` | Wave 0 |
| R1.3 | Persistent failure: after 3 retries → Telegram alert fired | unit (mock 5xx × 3, mock Telegram) | `pytest tests/test_brazil_store_crawler.py::test_persistent_failure_telegram -x` | Wave 0 |
| R1.3 | Partial data: missing price/image → defined behavior (skip) | unit | `pytest tests/test_brazil_store_crawler.py::test_partial_data -x` | Wave 0 |
| R1.4 | ML search returns items + affiliate URL correctly tagged | unit (mock httpx) | `pytest tests/test_mercado_livre_crawler.py::test_affiliate_url_tagged -x` | Wave 0 |
| R1.4 | ML items saved to price_snapshots with currency=BRL | unit (mock httpx + DB) | `pytest tests/test_mercado_livre_crawler.py::test_saves_to_db -x` | Wave 0 |

---

## Wave 0 Requirements

These files MUST be created before any plan in this phase is executed (they are referenced by test commands above but do not yet exist):

- [ ] `pipeline/tests/test_brazil_store_crawler.py` — covers R1.3 (4 test cases: happy path, retry backoff, persistent failure + Telegram, partial data)
- [ ] `pipeline/tests/test_mercado_livre_crawler.py` — covers R1.4 (affiliate URL tagging, saves to DB)
- [ ] `pipeline/tests/conftest.py` — shared fixtures: mock Firecrawl response, mock psycopg pool, mock Telegram bot, mock httpx client
- [ ] `pipeline/pyproject.toml` — pytest + asyncio_mode = "auto" config

**Wave 0 is satisfied by Plan 01-03 and 01-04 creating test files alongside production code.**

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ≥ 50 raquetes indexed total | R1.1 | Requires live Firecrawl + ML API calls | Run crawlers manually, query `SELECT COUNT(*) FROM price_snapshots` |
| Supabase staging pgvector available | R1.1 | Requires Supabase account provisioning | `psql $SUPABASE_URL -c "SELECT * FROM pg_extension WHERE extname='vector'"` |
| ML Afiliados tag active in affiliate_url | R1.4 | Requires approved ML Afiliados account | Inspect `SELECT affiliate_url FROM price_snapshots LIMIT 5` — must contain `matt_id` or equivalent |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
