---
phase: 02-full-data-pipeline
verified: 2026-03-28T14:15:00Z
status: gaps_found
score: 4/7 truths verified
re_verification: false
gaps:
  - truth: "Crawlers running via GH Actions schedule every 24h"
    status: failed
    reason: "GitHub Actions job references mercadolivre_expansion but actual file is mercado_livre.py — module import will fail"
    artifacts:
      - path: ".github/workflows/scrape.yml"
        issue: "Line with 'python -m pipeline.crawlers.mercadolivre_expansion' will fail — module not found"
      - path: "pipeline/crawlers/mercado_livre.py"
        issue: "File exists but GitHub Actions imports wrong module name"
    missing:
      - "Rename file OR fix GitHub Actions import"
      - "Verify all 6 crawler jobs run successfully"

  - truth: "FastAPI 5 endpoints return 200 with real data"
    status: failed
    reason: "API endpoints implement mock db_fetch functions that always return empty results — not wired to database"
    artifacts:
      - path: "backend/app/api/paddles.py"
        issue: "Mock functions will return [] forever: 'Fetch all rows (mock implementation)' comment on lines 21-22 and 27-28"
      - path: "backend/app/api/paddles.py"
        issue: "All 5 endpoints call db_fetch_all/db_fetch_one which return empty lists — endpoints will always return empty paginated responses"
    missing:
      - "Wire API endpoints to real psycopg async connection"
      - "Replace mock db_fetch functions with actual database queries"
      - "Test endpoints return non-empty responses"

  - truth: "Railway provisioned for API staging"
    status: failed
    reason: "Railway deployment references backend/Dockerfile which does not exist in repository"
    artifacts:
      - path: "railway.toml"
        issue: "Dockerfile set to 'backend/Dockerfile' but file not found"
      - path: "backend/Dockerfile"
        issue: "Missing — required by railway.toml build configuration"
    missing:
      - "Create backend/Dockerfile with Python 3.12 + FastAPI + dependencies"
      - "Verify Railway can build and deploy successfully"
---

# Phase 02: Full Data Pipeline — Verification Report

**Phase Goal:** Pipeline completo cobrindo todos os varejistas BR, com deduplicação, spec enrichment e embeddings pgvector.

**Verified:** 2026-03-28T14:15:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement Summary

**Score:** 4/7 observable truths verified

Three critical gaps prevent goal achievement:
1. **Crawler execution will fail** — GitHub Actions references wrong module name
2. **API endpoints return empty data** — Mock implementations not wired to database
3. **Railway deployment will fail** — Missing Dockerfile

---

## Observable Truths Verification

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Crawlers (Drop Shot Brasil + ML expansion) running via GH Actions schedule every 24h | ✗ FAILED | GitHub Actions imports `mercadolivre_expansion` module but actual file is `mercado_livre.py` — module will not load |
| 2 | 3-tier deduplication (SKU/hash/RapidFuzz) prevents duplicate paddles | ✓ VERIFIED | `pipeline/dedup/normalizer.py` has `tier1_match`, `tier2_match` functions; `pipeline/dedup/spec_matcher.py` has RapidFuzz token_set_ratio (4 matches) |
| 3 | Review queue flags fuzzy matches <0.85 for manual review | ✓ VERIFIED | `pipeline/dedup/spec_matcher.py` has threshold logic; `pipeline/dedup/review_queue.py` exists (documented in PHASE-2-COMPLETE.md line 45) |
| 4 | pgvector embeddings (text-embedding-3-small, HNSW) with async re-embedding | ⚠️ PARTIAL | text-embedding-3-small found in `pipeline/embeddings/batch_embedder.py` (lines 61, 109); batch_embedder has write-side working (INSERT/UPDATE paddle_embeddings); but no test confirms real OpenAI calls work |
| 5 | Async re-embedding via needs_reembed flag | ✓ VERIFIED | `pipeline/embeddings/batch_embedder.py` has `re_embed_changed_paddles()` function reading needs_reembed=true flag and resetting after batch (lines 41-109) |
| 6 | FastAPI 5 endpoints return 200 with real data | ✗ FAILED | Endpoints exist (`@router.get`) but use mock `db_fetch_all/db_fetch_one` functions that return empty results. Lines 21-22: "mock implementation" comment. All data will be empty. |
| 7 | Railway provisioned for API staging | ✗ FAILED | railway.toml references `backend/Dockerfile` which does not exist in repository |

---

## Required Artifacts Verification

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pipeline/crawlers/dropshot_brasil.py` | async def scrape_dropshot | ✓ EXISTS, NOT EXACT NAME | Has `run_dropshot_brasil_crawler()` instead; function works but PLAN expects `async def scrape_dropshot` |
| `pipeline/crawlers/mercadolivre_expansion.py` | pagination loop | ✗ MISSING | File named `mercado_livre.py` not `mercadolivre_expansion.py` — GitHub Actions will fail to import |
| `pipeline/dedup/normalizer.py` | class SKUDeduplicator | ✓ EXISTS, NOT EXACT NAME | Has functions `tier1_match()`, `tier2_match()` not a class; provides tier-1/2 matching |
| `pipeline/dedup/spec_matcher.py` | RapidFuzz token_set_ratio | ✓ VERIFIED | Imports rapidfuzz.fuzz; uses token_set_ratio (4 grep matches) |
| `backend/app/embeddings.py` | text-embedding-3-small | ⚠️ PARTIAL | File exists and has similarity search function but does NOT contain "text-embedding-3-small" — that's in `pipeline/embeddings/batch_embedder.py` instead. Split across files. |
| `backend/app/api/paddles.py` | GET /paddles endpoints | ✓ EXISTS, NOT WIRED | 5 endpoints defined: `@router.get("")`, `@router.get("/{paddle_id}")`, `/prices`, `/latest-prices`, `/health`. But all call mock `db_fetch_*` functions returning empty lists. |
| `.github/workflows/scrape.yml` | schedule cron 0 6 * * * | ✓ VERIFIED | Has `schedule:` with `cron: "0 6 * * *"` (6h UTC = midnight BRT) |
| `.env.example` | OPENAI_API_KEY, RAILWAY_API_TOKEN | ✗ MISSING | Grep found 0 matches for both keys. File has only 5 env vars total, missing required Phase 2 vars. |

---

## Key Link Verification (Wiring)

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `.github/workflows/scrape.yml` | `pipeline/crawlers/` | Job dispatch to scraper modules | ✗ NOT_WIRED | GitHub Actions runs `python -m pipeline.crawlers.mercadolivre_expansion` but file is `pipeline/crawlers/mercado_livre.py`. Module import will fail. |
| `backend/app/api/paddles.py` | `pipeline/dedup/` | Read deduplicated paddle_id from DB | ✗ HOLLOW | API has WHERE clause checking `dedup_status IN ('pending', 'merged')` but db_fetch functions are mocks returning []. No real DB connection. |
| `backend/app/embeddings.py` | `backend/app/models/paddle.py` | Generate embedding for paddle doc | ✗ NOT_FOUND | embeddings.py does NOT import or reference paddle models. Function `get_similar_paddles()` takes raw `query_embedding: List[float]` parameter — no integration. |
| `.github/workflows/scrape.yml` | `backend/app/embeddings.py` | Re-embedding job triggers OpenAI batch | ✗ PARTIAL | GitHub Actions has "Enrich specs" job but runs `python -m pipeline.crawlers.spec_enrichment` not embeddings. Spec enrichment module does not exist. |

---

## Data-Flow Trace (Level 4)

### Artifact: backend/app/api/paddles.py

**Truth:** "FastAPI endpoints return real paddle data"

**Data Variable:** `paddle` in `list_paddles()` → called via `db_fetch_all()`

**Source:** `db_fetch_all()` at line 21-22

**Produces Real Data:** ✗ NO
- Function marked "mock implementation"
- Returns hardcoded empty list `[]`
- No real database connection
- All 5 endpoints will return empty paginated responses

**Status:** ✗ HOLLOW — wired but data disconnected

---

### Artifact: pipeline/embeddings/batch_embedder.py

**Truth:** "pgvector embeddings populated for all paddles"

**Data Variable:** Embeddings returned from OpenAI API

**Source:** OpenAI batch processing via `client.embeddings.create(model="text-embedding-3-small", ...)`

**Produces Real Data:** ⚠️ UNCLEAR
- Code structure correct (batch processing, INSERT to paddle_embeddings)
- But tests mock OpenAI responses (per PHASE-2-COMPLETE.md line 279)
- Real OpenAI calls not verified in actual execution

**Status:** ⚠️ UNCERTAIN — structure ready but real data flow needs test

---

## Behavioral Spot-Checks

**Environment:** No runnable entry points tested (server not started)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| API /health endpoint | (requires server) | Not tested | ? SKIP |
| GitHub Actions schedule test | `grep -q "cron.*0 6.*\*.*\*.*\*" .github/workflows/scrape.yml` | Found cron | ✓ PASS (schedule syntax valid) |
| Dropshot scraper loads | `cd pipeline && python -c "from pipeline.crawlers.dropshot_brasil import run_dropshot_brasil_crawler; print('OK')"` | (not executed — would test import) | ? SKIP |
| Mercado Livre scraper import | `cd pipeline && python -c "from pipeline.crawlers.mercadolivre_expansion import *"` | (would fail — module name mismatch) | ✗ FAIL (expected) |

---

## Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| R2.1 | Crawlers running via GH Actions schedule | ✗ BLOCKED | GitHub Actions references wrong module name (mercadolivre_expansion vs mercado_livre.py) |
| R2.2 | Deduplication 3-tier working | ✓ SATISFIED | normalizer.py + spec_matcher.py + review_queue.py all present and substantive |
| R2.3 | pgvector embeddings with HNSW | ⚠️ PARTIAL | Structure correct, batch_embedder.py writes to paddle_embeddings, but real OpenAI integration not verified |
| R2.4 | FastAPI 5 endpoints all 200 | ✗ BLOCKED | Endpoints defined but return empty data (mock implementations) |
| R2.5 | Railway provisioned for staging | ✗ BLOCKED | Missing backend/Dockerfile required by railway.toml |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `backend/app/api/paddles.py` | 21-22 | Mock implementation returning empty list | 🛑 BLOCKER | All 5 endpoints return empty data instead of paddles |
| `backend/app/api/paddles.py` | 27-28 | Mock implementation returning empty result | 🛑 BLOCKER | Detail endpoints will fail to return single paddle |
| `.github/workflows/scrape.yml` | line with mercadolivre_expansion | Wrong module name in import | 🛑 BLOCKER | Crawler job will fail at runtime with ModuleNotFoundError |
| `backend/Dockerfile` | MISSING | Dockerfile does not exist | 🛑 BLOCKER | Railway deployment will fail — cannot build Docker image |
| `.env.example` | MISSING | OPENAI_API_KEY, RAILWAY_API_TOKEN not defined | ⚠️ WARNING | Phase 2 env vars documented but not in file |

---

## Human Verification Required

### 1. Mercado Livre Crawler Import

**Test:** Try to import the crawler in GitHub Actions context
**Expected:** Successful import from `pipeline.crawlers.mercado_livre` (actual name) OR file renamed to match GitHub Actions reference
**Why human:** Module naming mismatch — can auto-fix by renaming or updating import, but need to verify which is correct intent

### 2. API Endpoint Data Flow

**Test:** Start API server and call `GET /paddles` with Authorization headers
**Expected:** Return paginated list of paddles with names, brands, prices (non-empty array)
**Why human:** Requires database connection + migration + sample data — can't test without running environment

### 3. Embeddings Real Data

**Test:** Run `pipeline.embeddings.batch_embedder.embed_paddles()` with real OpenAI API key
**Expected:** paddle_embeddings table populated with 1536-dimensional vectors; no OpenAI errors
**Why human:** Requires live OpenAI API key and real database — can't test in sandbox

### 4. Railway Deployment

**Test:** Deploy to Railway with built Docker image
**Expected:** API accessible at Railway staging URL; /health returns 200
**Why human:** Requires Railway account + Docker registry — can't test in sandbox

---

## Gaps Summary

Phase 2 goal requires a **complete, runnable data pipeline**. Three critical blockers prevent this:

1. **GitHub Actions will not execute crawlers** (`mercadolivre_expansion` module does not exist)
2. **API endpoints return empty data** (mock db_fetch implementations never wired to real database)
3. **Railway deployment will fail** (backend/Dockerfile missing)

### Files to Fix (Priority Order)

**Blocker 1: Fix crawler module naming**
- Either rename `pipeline/crawlers/mercado_livre.py` → `mercadolivre_expansion.py`
- OR update `.github/workflows/scrape.yml` line to import from `pipeline.crawlers.mercado_livre`

**Blocker 2: Wire API to database**
- Replace mock `db_fetch_all()` and `db_fetch_one()` in `backend/app/api/paddles.py`
- Wire to real `get_connection()` async pool from `pipeline.db.connection`
- Test all 5 endpoints return non-empty responses

**Blocker 3: Create backend/Dockerfile**
- Python 3.12 image
- Install dependencies (FastAPI, psycopg, openai, etc.)
- Expose port defined in railway.toml
- Verify Railway can build and deploy

**Additional:** Add missing env vars to `.env.example`
- OPENAI_API_KEY
- RAILWAY_API_TOKEN
- All Phase 2 required variables

### Root Causes

- **Naming inconsistency:** File and GitHub Actions reference don't match (likely copy-paste during execution)
- **Mock implementations left in place:** API endpoints scaffolded but never wired to real DB connection
- **Incomplete deployment configuration:** Dockerfile referenced in railway.toml but never created

---

## Summary

**Phase 2 goal is NOT achieved.** Goal requires "Pipeline completo... com deduplicação, spec enrichment e embeddings pgvector" — emphasis on *completo* (complete, working end-to-end).

✓ **Working components:**
- Deduplication system (3-tier logic present and substantive)
- Embeddings infrastructure (batch_embedder.py with write-side)
- GitHub Actions scheduling (cron syntax valid)
- FastAPI schema design (5 endpoints defined)

✗ **Broken/incomplete components:**
- Crawler execution (module import mismatch)
- API data flow (mock implementations)
- Deployment infrastructure (Dockerfile missing)

**Recommendation:** Close all three gaps, then re-verify with `gsd:plan-phase --gaps`.

---

_Verified: 2026-03-28T14:15:00Z_
_Verifier: Claude (gsd-verifier)_
