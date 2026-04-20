# Codebase Concerns

**Analysis Date:** 2026-04-20

---

## Summary

This document identifies technical concerns, risks, debt, and improvement opportunities in the PickleIQ (picklepicker) codebase. Concerns are prioritized by severity and include specific file locations and recommendations.

---

## 1. Technical Debt

### T1 — Infrastructure Not Provisioned in Production

- **Severity:** High
- **Category:** Technical Debt
- **Description:** Production infrastructure (Supabase, Railway) not yet provisioned. The system runs locally but lacks production deployment.
- **Location:** `TODOS.md` T1 — pending since project inception
- **Recommendation:** Create Supabase project and Railway deployment early in development to catch dev/prod divergencies (RLS, extensions, permissions) before launch.

---

### T2 — Eval Gate Returns Mocked Scores

- **Severity:** High
- **Category:** Technical Debt
- **Description:** The eval gate (`backend/app/agents/eval_gate.py`) returns hardcoded scores arrays instead of testing real LLMs. This means model selection is not actually validated.
- **Location:** `backend/app/agents/eval_gate.py`
- **Recommendation:** Implement actual LLM evaluation using Groq/Claude APIs with real query sets and score computation.

---

### T3 — Legal Risk from Scraping US Retailers

- **Severity:** Medium
- **Category:** Legal / Compliance
- **Description:** Crawlers scrape specs from PickleballCentral and Johnkew (US retailers) whose ToS likely prohibits scraping. Risk: C&D letter or IP blocking.
- **Location:** `pipeline/crawlers/` (spec crawlers planned in Phase 2)
- **Recommendation:** Before implementing spec crawlers, verify ToS of target sites. Consider alternative sources: manufacturer press kits, WPT/PPA specifications, or direct manufacturer contact (Selkirk, JOOLA, Head).

---

### T4 — Review Queue Monitoring Not Implemented

- **Severity:** Medium
- **Category:** Operational
- **Description:** Dedup logging to review_queue is wired into crawlers, but dashboard monitoring for queue volume is not implemented.
- **Location:** `TODOS.md` T4
- **Recommendation:** Add volume metric to observability dashboard. Implement threshold alerts (e.g., >50 pending items triggers Telegram alert).

---

### T5 — Load Test Not Performed on /chat

- **Severity:** Medium
- **Category:** Performance
- **Description:** No load testing performed on the /chat endpoint. Performance target is P95 <3s but untested.
- **Location:** `TODOS.md` T5
- **Recommendation:** Run k6 or Locust simulation with 50 concurrent users against Railway staging before beta launch.

---

### T6 — Zero-Paddle Alert Not Implemented

- **Severity:** Low
- **Category:** Monitoring
- **Description:** No automated alert when a retailer's scraper returns zero paddles. Silent failures can cause stale pricing data.
- **Location:** `TODOS.md` T6
- **Recommendation:** Add post-scraper SQL check: `SELECT COUNT(*) FROM price_snapshots WHERE DATE(scraped_at) = CURRENT_DATE`. Alert if zero.

---

### T7 — Firecrawl Self-Hosted Runbook Not Written

- **Severity:** Low
- **Category:** Documentation
- **Description:** Runbook for migrating to Firecrawl self-hosted (when free tier exceeded) not documented.
- **Location:** `TODOS.md` T7
- **Recommendation:** Document migration steps: Docker image, proxy rotation config, Railway env vars, cost estimate ($20-50/month).

---

## 2. Code Quality Concerns

### C1 — Large Files Requiring Refactoring

- **Severity:** Medium
- **Category:** Code Quality
- **Description:** Several Python files exceed 500 lines, indicating potential for decomposition:
  - `pipeline/crawlers/brazil_store.py` (572 lines)
  - `pipeline/crawlers/dropshot_brasil.py` (567 lines)
  - `pipeline/crawlers/joola.py` (484 lines)
- **Location:** `pipeline/crawlers/`
- **Recommendation:** Extract shared logic (retry decorators, parsing helpers, validation) into reusable modules. Consider a base crawler class.

---

### C2 — Broad Exception Handling

- **Severity:** Low
- **Category:** Code Quality
- **Description:** Several locations use bare `except Exception:` without specific handling or logging:
  - `pipeline/utils/security.py` lines 153, 160
  - `pipeline/db/connection.py` line 54
  - `backend/app/api/embeddings.py` lines 50, 57, 64
- **Location:** Multiple files
- **Recommendation:** Add specific exception handling with logging. Consider letting unexpected exceptions propagate with context.

---

### C3 — Duplicate vercel.json Configurations

- **Severity:** Low
- **Category:** Code Quality
- **Description:** Two `vercel.json` files exist: root-level (comprehensive security headers) and `frontend/vercel.json` (minimal subset).
- **Location:** `vercel.json`, `frontend/vercel.json`
- **Recommendation:** Consolidate to single root-level configuration or document why duplicates are needed.

---

### C4 — No ORM — Raw SQL Risks

- **Severity:** Low
- **Category:** Code Quality
- **Description:** Database queries use raw psycopg with string formatting. While parameterized queries are used (safe from SQL injection), column references aren't validated at compile time.
- **Location:** `backend/app/api/paddles.py`, `pipeline/db/`
- **Recommendation:** Add compile-time validation via SQL linter or type-checked query builder. Current approach is documented in AGENTS.md as intentional.

---

## 3. Security Concerns

### S1 — Hardcoded Database Password in Docker Compose

- **Severity:** Medium
- **Category:** Security
- **Description:** `docker-compose.yml` uses hardcoded default password `changeme` in POSTGRES_PASSWORD.
- **Location:** `docker-compose.yml` line 7
- **Recommendation:** Require POSTGRES_PASSWORD from environment: `${POSTGRES_PASSWORD}` (already partially implemented with fallback).

---

### S2 — Admin Secret Validation

- **Severity:** Medium
- **Category:** Security
- **Description:** Admin endpoints protected via Bearer token (`ADMIN_SECRET`), but no rate limiting or IP allowlisting on these endpoints.
- **Location:** `backend/app/api/` admin routes
- **Recommendation:** Consider adding rate limiting and IP allowlisting for sensitive admin endpoints in production.

---

### S3 — No .env Files Committed

- **Severity:** None
- **Category:** Security
- **Description:** Confirmed - no `.env` files committed to repository. Correctly gitignored.
- **Location:** Verified via glob
- **Recommendation:** No action needed. Maintain current `.gitignore` patterns.

---

## 4. Performance Concerns

### P1 — N+1 Query in Paddles List

- **Severity:** Medium
- **Category:** Performance
- **Description:** `list_paddles` endpoint uses correlated subqueries for retailer_count and latest_scraped_at per paddle:
  ```sql
  (SELECT COUNT(DISTINCT lp.retailer_id) FROM latest_prices lp WHERE lp.paddle_id = p.id)
  (SELECT MAX(lp.scraped_at) FROM latest_prices lp WHERE lp.paddle_id = p.id)
  ```
- **Location:** `backend/app/api/paddles.py` lines 141-142
- **Recommendation:** Add retailer_count and latest_scraped_at columns to paddles table, updated via triggers or materialized view refresh.

---

### P2 — Redis Cache Dependency

- **Severity:** Low
- **Category:** Performance
- **Description:** `/paddles` endpoint depends on Redis cache. If Redis is unavailable, all requests hit the database.
- **Location:** `backend/app/cache.py`, `backend/app/api/paddles.py`
- **Recommendation:** Add fallback to direct DB query if cache unavailable.

---

## 5. Testing Gaps

### G1 — Eval Gate Not Tested with Real LLMs

- **Severity:** High
- **Category:** Testing
- **Description:** `backend/app/agents/eval_gate.py` returns hardcoded scores - no actual LLM testing.
- **Location:** `backend/app/agents/eval_gate.py`
- **Recommendation:** Add integration tests that call real Groq/Claude APIs with test queries.

---

### G2 — Load Testing Not Performed

- **Severity:** Medium
- **Category:** Testing
- **Description:** No load/stress tests for /chat endpoint. Performance under concurrent load unknown.
- **Location:** N/A — not implemented
- **Recommendation:** Add k6 or Locust tests targeting P95 <3s, P99 <8s with 50 concurrent users.

---

### G3 — E2E Scraper Tests Require DB

- **Severity:** Low
- **Category:** Testing
- **Description:** `pipeline/test_e2e_scraper.py` requires running database, limiting CI flexibility.
- **Location:** `pipeline/test_e2e_scraper.py`
- **Recommendation:** Consider test fixtures with mock DB responses for faster unit test runs.

---

## 6. Documentation Gaps

### D1 — Missing Production Runbook

- **Severity:** Medium
- **Category:** Documentation
- **Description:** No runbook for common production operations: rollback, scaling, debug commands.
- **Location:** `docs/DEPLOYMENT.md` (partial)
- **Recommendation:** Expand DEPLOYMENT.md with rollback procedures, debug commands, scaling guidelines.

---

### D2 — API Documentation Not Exposed

- **Severity:** Low
- **Category:** Documentation
- **Description:** FastAPI auto-generated `/docs` endpoint not linked from frontend or deployment docs.
- **Location:** `backend/app/main.py`
- **Recommendation:** Add `/docs` link to developer documentation.

---

## 7. Dependency Risks

### R1 — Firecrawl Free Tier Dependency

- **Severity:** Medium
- **Category:** Dependencies
- **Description:** Pipeline depends on Firecrawl free tier (500 credits/month). Exceeding limit breaks scraping silently.
- **Location:** `pipeline/crawlers/`
- **Recommendation:** Monitor usage via Firecrawl dashboard. Prepare self-hosted migration runbook (TODOS.md T7).

---

### R2 — Single Embedding Provider (Jina AI)

- **Severity:** Low
- **Category:** Dependencies
- **Description:** Primary embedding provider is Jina AI. If service is down, fallback to HuggingFace may be slower or less accurate.
- **Location:** `backend/app/services/embedding.py`
- **Recommendation:** Document fallback chain and monitor latency differences between providers.

---

## 8. Configuration Concerns

### Cf1 — No Environment Validation at Startup

- **Severity:** Medium
- **Category:** Configuration
- **Description:** Backend doesn't validate required environment variables at startup. Missing keys cause runtime errors.
- **Location:** `backend/app/main.py`
- **Recommendation:** Add startup validation: check DATABASE_URL, GROQ_API_KEY, JINA_API_KEY exist and are non-empty. Fail fast with clear error message.

---

### Cf2 — Default Values in Examples May Leak

- **Severity:** Low
- **Category:** Configuration
- **Description:** `.env.example` files contain placeholder comments but no actual secrets. However, docker-compose.yml has hardcoded fallback.
- **Location:** `docker-compose.yml`, `.env.example`
- **Recommendation:** Remove default passwords entirely; require explicit environment setup.

---

## Priority Summary

| Priority | Count | Items |
|----------|-------|-------|
| **High** | 3 | T1 (infra), T2 (eval mock), G1 (eval test) |
| **Medium** | 9 | T3 (legal), T4 (monitoring), T5 (load test), C1 (large files), S1 (docker password), P1 (N+1), Cf1 (env validation), R1 (Firecrawl) |
| **Low** | 7 | T6 (zero-paddle), T7 (runbook), C2 (exceptions), C3 (vercel.json), C4 (raw SQL), D1/D2 (docs), R2 (embeddings), Cf2 (defaults) |

---

*Concerns audit: 2026-04-20*
