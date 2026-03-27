---
phase: 02-full-data-pipeline
plan: complete
type: execute
wave: N/A (meta-plan)
depends_on: [01-complete]
files_modified: []
autonomous: true
requirements: [R2.1, R2.2, R2.3, R2.4, R2.5]

must_haves:
  truths:
    - "Crawlers for Drop Shot Brasil + Mercado Livre expansion run via GH Actions schedule every 24h"
    - "3-tier deduplication (SKU manufacturer → title hash → RapidFuzz ≥0.85) prevents duplicate paddles"
    - "Review queue automatically flags fuzzy matches below threshold for human review"
    - "pgvector embeddings (text-embedding-3-small, 1536D, HNSW index) populated for all paddles"
    - "Async re-embedding via needs_reembed flag prevents sync API call storms"
    - "FastAPI endpoints return 200 for all 5 GET routes + /health without errors"
    - "Railway provisioned with deployed API staging environment accessible"
  artifacts:
    - path: "pipeline/crawlers/dropshot_brasil.py"
      provides: "Drop Shot Brasil Firecrawl extraction"
      contains: "async def scrape_dropshot"
    - path: "pipeline/crawlers/mercadolivre_expansion.py"
      provides: "ML expansion with pagination support"
      contains: "pagination loop"
    - path: "pipeline/dedup/normalizer.py"
      provides: "3-tier dedup strategy"
      contains: "class SKUDeduplicator"
    - path: "pipeline/dedup/spec_matcher.py"
      provides: "Fuzzy matching with RapidFuzz"
      contains: "RapidFuzz token_set_ratio"
    - path: "backend/app/embeddings.py"
      provides: "pgvector embedding generation"
      contains: "text-embedding-3-small"
    - path: "backend/app/api/paddles.py"
      provides: "5 GET endpoints"
      contains: "GET /paddles"
    - path: ".github/workflows/scrape.yml"
      provides: "GH Actions schedule + 6 crawler jobs"
      contains: "schedule: cron('0 6 * * *')"
    - path: ".env.example"
      provides: "Phase 2 env vars: OPENAI_API_KEY, RAILWAY_API_TOKEN"
      contains: "OPENAI_API_KEY"
  key_links:
    - from: ".github/workflows/scrape.yml"
      to: "pipeline/crawlers/"
      via: "Job dispatch to scraper modules"
      pattern: "python -m pipeline.crawlers.dropshot_brasil"
    - from: "backend/app/api/paddles.py"
      to: "pipeline/dedup/"
      via: "Read deduplicated paddle_id from DB"
      pattern: "SELECT * FROM paddles WHERE dedup_status"
    - from: "backend/app/embeddings.py"
      to: "backend/app/models/paddle.py"
      via: "Generate embedding for paddle doc"
      pattern: "paddle_embeddings.embedding"
    - from: ".github/workflows/scrape.yml"
      to: "backend/app/embeddings.py"
      via: "Re-embedding job triggers OpenAI batch"
      pattern: "needs_reembed=true"
---

# Phase 2: Full Data Pipeline — 5 Plans

**Objective:** Build complete crawler pipeline for all BR retailers, deduplication system, pgvector embeddings with async re-embedding, FastAPI endpoints, and Railway staging deployment.

**Success Criteria (ALL must be TRUE):**
1. ✓ Crawlers (Drop Shot Brasil + ML expansion) running via GH Actions schedule every 24h
2. ✓ Deduplication 3-tier working with manual review queue for threshold misses
3. ✓ pgvector embeddings (text-embedding-3-small, HNSW index) with async re-embedding
4. ✓ FastAPI 5 endpoints (GET /paddles, /paddles/{id}, /paddles/{id}/prices, /paddles/{id}/latest-prices, /health) all 200
5. ✓ Railway provisionado para API staging

---

## Plan Breakdown (5 Plans, 2 Waves)

| Plan | Title | Wave | Tasks | Effort | Dependencies |
|------|-------|------|-------|--------|--------------|
| 02-01 | Crawlers: Drop Shot Brasil + ML Expansion | 1 | 3 | 35-40 min | Phase 1 complete |
| 02-02 | Deduplication 3-tier + Review Queue | 1 | 3 | 40-45 min | Phase 1 schema |
| 02-03 | GitHub Actions Schedule + Railway | 2 | 2 | 20-25 min | 02-01, 02-02 ready |
| 02-04 | pgvector Embeddings + Async Re-embedding | 2 | 3 | 35-40 min | 02-01, 02-02 data |
| 02-05 | FastAPI Endpoints (GET /paddles/*) | 2 | 2 | 30-35 min | 02-04 embeddings |

**Wave 1 (parallel):** 02-01, 02-02 (independent, both use Phase 1 schema/DB)
**Wave 2 (depend on Wave 1):** 02-03, 02-04, 02-05 (need dedup + crawlers working)

---

## PLAN 02-01: Crawlers — Drop Shot Brasil + Mercado Livre Expansion

**Objective:** Implement Firecrawl-based scrapers for Drop Shot Brasil and Mercado Livre with pagination, retry logic, and Telegram alerts.

**Approach:**
- Drop Shot Brasil: Single-page extraction via Firecrawl `/extract` with JSON schema
- Mercado Livre: Multi-page search API with cursor-based pagination, item-level extraction
- Both: 3x retry with exponential backoff (Tenacity), Telegram alert on persistent failure
- Raw JSON saved to `price_snapshots` (dedup in Phase 2.2)

**Technical Decisions:**
- Use Firecrawl `/extract` mode (not `/crawl`) for structured output
- Tenacity library for retry/backoff (already in Phase 1 deps)
- Separate crawler modules: `pipeline/crawlers/dropshot_brasil.py` and `pipeline/crawlers/mercadolivre_expansion.py`
- ML API pagination: respect rate limits, cache-friendly cursor storage

**Success Verification:**
- `pytest pipeline/tests/test_dropshot_brasil.py -v` passes 4+ test cases
- `pytest pipeline/tests/test_mercadolivre_expansion.py -v` passes 4+ test cases
- Live crawl: ≥10 paddles scraped to `price_snapshots` per retailer in Docker environment

**Blockers / Risks:**
- Firecrawl API quota exceeded → mitigate via request batching and caching
- ML API rate limits → implement exponential backoff
- Data structure mismatches → test schema against real HTML first

---

### 02-01 PLAN.md

```yaml
---
phase: 02-full-data-pipeline
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - pipeline/crawlers/dropshot_brasil.py
  - pipeline/crawlers/mercadolivre_expansion.py
  - pipeline/crawlers/__init__.py
  - pipeline/tests/test_dropshot_brasil.py
  - pipeline/tests/test_mercadolivre_expansion.py
  - .env.example
autonomous: true
requirements: [R2.1]

must_haves:
  truths:
    - "Drop Shot Brasil crawler extracts ≥10 paddles via Firecrawl with Tenacity 3x retry"
    - "Mercado Livre expansion pagination works with cursor-based search"
    - "Firecrawl extraction failures after 3 retries trigger Telegram alert"
    - "Scraped data saved to price_snapshots (paddle_id NULL — matched in Phase 2.2)"
  artifacts:
    - path: "pipeline/crawlers/dropshot_brasil.py"
      provides: "Drop Shot Brasil scraper module"
      contains: "async def scrape_dropshot_brasil"
    - path: "pipeline/crawlers/mercadolivre_expansion.py"
      provides: "ML expansion with pagination"
      contains: "async def scrape_mercadolivre_paginated"
    - path: "pipeline/tests/test_dropshot_brasil.py"
      provides: "Happy path + retry + failure tests"
      contains: "test_happy_path, test_retry_3_times, test_telegram_alert"
    - path: "pipeline/tests/test_mercadolivre_expansion.py"
      provides: "Pagination + cursor tests"
      contains: "test_pagination_loop, test_rate_limit_backoff"
  key_links:
    - from: "pipeline/crawlers/dropshot_brasil.py"
      to: "pipeline/db/connection.py"
      via: "INSERT into price_snapshots"
      pattern: "INSERT INTO price_snapshots"
    - from: "pipeline/crawlers/dropshot_brasil.py"
      to: "pipeline/alerts/telegram.py"
      via: "Alert on 3rd retry failure"
      pattern: "send_telegram_alert"
---

<objective>
Build Firecrawl-based crawlers for Drop Shot Brasil and Mercado Livre expansion with pagination, retry, and Telegram alerts.

Purpose: Expand data collection beyond Brazil Pickleball Store (Phase 1) to include two major BR retailers.
Output: Working crawler modules with tests, saving ≥10 paddles per retailer to price_snapshots.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
@.planning/02-full-data-pipeline/CONTEXT.md
@pipeline/crawlers/brazil_store_crawler.py (reference Phase 1)
@pipeline/db/connection.py
@pipeline/alerts/telegram.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement Drop Shot Brasil crawler with Firecrawl + Tenacity retry</name>
  <files>
    pipeline/crawlers/dropshot_brasil.py,
    pipeline/tests/test_dropshot_brasil.py
  </files>
  <action>
1. Create `pipeline/crawlers/dropshot_brasil.py`:
   - Module-level `logger` setup (Python logging)
   - `async def scrape_dropshot_brasil()` — main entry point
   - Use Firecrawl `/extract` with JSON schema for structured output:
     ```
     {"properties": {
       "products": {
         "type": "array",
         "items": {
           "type": "object",
           "properties": {
             "name": {"type": "string"},
             "price_brl": {"type": "number"},
             "in_stock": {"type": "boolean"},
             "image_url": {"type": "string"},
             "product_url": {"type": "string"},
             "brand": {"type": "string"},
             "specs": {"type": "object"}
           }
         }
       }
     }}
     ```
   - Wrap Firecrawl call with `@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))`
   - On RetryError (3 attempts exhausted):
     - Log error: f"Drop Shot Brasil scrape failed after 3 retries: {e}"
     - Call `await send_telegram_alert(f"Drop Shot Brasil crawler failed: {e}")`
     - Re-raise exception (caller can handle)
   - For each product in response["data"]["products"]:
     - Save to price_snapshots: `(paddle_id=NULL, retailer_id=3, price_brl, currency='BRL', in_stock, scraped_at=now(), source_raw=JSON)`
     - Use async DB context: `async with get_connection() as conn: await conn.execute(...)`
   - Return: `{"status": "success", "count": len(products), "timestamp": datetime.now()}`

2. Create `pipeline/tests/test_dropshot_brasil.py`:
   - Import: pytest, pytest-asyncio, MagicMock, patch
   - Fixture: mock_firecrawl_app (from conftest), mock_db_connection (from conftest)
   - Test 1: `test_happy_path__scrapes_and_saves_to_db`
     - Mock Firecrawl to return 3 paddles
     - Call scraper
     - Verify: ≥1 INSERT INTO price_snapshots executed
     - Assert return count == 3
   - Test 2: `test_retry_3_times__on_firecrawl_500`
     - Mock Firecrawl to raise Exception on calls 1-2, return data on call 3
     - Call scraper
     - Assert: 3 attempts made (verify via call_count)
     - Assert: data saved successfully
   - Test 3: `test_telegram_alert__after_3_retries_fail`
     - Mock Firecrawl to raise Exception all 3 times
     - Mock Telegram send
     - Call scraper (expect RetryError)
     - Assert: Telegram alert sent with message containing "Drop Shot Brasil"
   - Test 4: `test_partial_data__missing_price_handled`
     - Mock Firecrawl response with 1 product missing "price_brl"
     - Verify: row inserted with NULL price (not exception)
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/tests/test_dropshot_brasil.py::test_happy_path__scrapes_and_saves_to_db -xvs && python -m pytest pipeline/tests/test_dropshot_brasil.py::test_retry_3_times__on_firecrawl_500 -xvs && python -m pytest pipeline/tests/test_dropshot_brasil.py::test_telegram_alert__after_3_retries_fail -xvs && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Drop Shot Brasil crawler module implemented with 3x retry, Telegram alert on persistent failure, and 4 test cases passing.</done>
</task>

<task type="auto">
  <name>Task 2: Implement Mercado Livre expansion crawler with pagination</name>
  <files>
    pipeline/crawlers/mercadolivre_expansion.py,
    pipeline/tests/test_mercadolivre_expansion.py
  </files>
  <action>
1. Create `pipeline/crawlers/mercadolivre_expansion.py`:
   - Module-level logger, BATCH_SIZE=50, MAX_PAGES=10 (safety limit)
   - `async def scrape_mercadolivre_paginated()` — main entry point
   - Use httpx.AsyncClient for ML API calls (already in Phase 1 deps)
   - Loop: iterate `limit` parameter (0-50, 50-100, etc.) up to MAX_PAGES
     ```
     for page in range(MAX_PAGES):
       offset = page * BATCH_SIZE
       query = f"raquete pickleball -usado"
       response = await client.get(
         "https://api.mercadolibre.com/sites/MLB/search",
         params={"q": query, "limit": BATCH_SIZE, "offset": offset}
       )
       items = response.json()["results"]
       if not items:
         break
       [save each item to DB]
     ```
   - Firecrawl extraction on item URLs (not necessary — use ML API directly):
     - Save item_id, title, price, available_qty, thumbnail, permalink
   - For each item:
     - Insert to price_snapshots: `(paddle_id=NULL, retailer_id=6, price_brl, currency='BRL', in_stock=(qty>0), scraped_at, source_raw=JSON)`
   - Implement exponential backoff on 429 (Too Many Requests):
     ```
     @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), retry=retry_if_exception_type(httpx.HTTPStatusError))
     async def _fetch_page(client, offset):
       ...
     ```
   - Return: `{"status": "success", "total_pages": page+1, "total_items": item_count, "timestamp": datetime.now()}`

2. Create `pipeline/tests/test_mercadolivre_expansion.py`:
   - Fixture: mock_ml_search_response (from conftest)
   - Test 1: `test_happy_path__pagination_two_pages`
     - Mock ML API to return 50 items on page 1, 30 on page 2, empty on page 3 (stop)
     - Call scraper
     - Verify: 80 rows inserted to price_snapshots
     - Assert return "total_items" == 80
   - Test 2: `test_rate_limit_backoff__429_then_200`
     - Mock ML API call 1: 429 error
     - Mock ML API call 2: 200 with data (verify retry happens)
     - Verify: exponential backoff applied (time between calls ≥ 1s)
   - Test 3: `test_stop_on_empty_page`
     - Mock first page with 50 items, second page empty
     - Call scraper
     - Verify: loop stops (not pages 3-10)
   - Test 4: `test_item_price_in_brl`
     - Mock response with item price 1299.90 BRL
     - Verify: saved to DB as price_brl=1299.90 (not USD conversion)
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/tests/test_mercadolivre_expansion.py::test_happy_path__pagination_two_pages -xvs && python -m pytest pipeline/tests/test_mercadolivre_expansion.py::test_rate_limit_backoff__429_then_200 -xvs && python -m pytest pipeline/tests/test_mercadolivre_expansion.py::test_stop_on_empty_page -xvs && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Mercado Livre expansion crawler with pagination, rate limit backoff, and 4 test cases passing.</done>
</task>

<task type="auto">
  <name>Task 3: Update .env.example with Phase 2 crawler variables</name>
  <files>
    .env.example
  </files>
  <action>
1. Read existing .env.example (Phase 1)
2. Add Phase 2 variables under new section "# Phase 2 — Crawlers":
   ```
   # Phase 2 — Crawlers
   ML_API_BATCH_SIZE=50
   ML_API_MAX_PAGES=10
   FIRECRAWL_TIMEOUT_SEC=30
   ```
3. Keep all Phase 1 variables intact
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && grep -q "ML_API_BATCH_SIZE" .env.example && grep -q "FIRECRAWL_TIMEOUT_SEC" .env.example && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>.env.example updated with Phase 2 crawler configuration variables.</done>
</task>

</tasks>

<verification>
- `pytest pipeline/tests/test_dropshot_brasil.py -v` → all 4 tests pass
- `pytest pipeline/tests/test_mercadolivre_expansion.py -v` → all 4 tests pass
- Drop Shot Brasil module importable: `python -c "from pipeline.crawlers import dropshot_brasil; print(hasattr(dropshot_brasil, 'scrape_dropshot_brasil'))"`
- Mercado Livre module importable: `python -c "from pipeline.crawlers import mercadolivre_expansion; print(hasattr(mercadolivre_expansion, 'scrape_mercadolivre_paginated'))"`
</verification>

<success_criteria>
- Drop Shot Brasil crawler implemented with @retry decorator, Firecrawl extraction, Telegram alert on failure
- Mercado Livre crawler implements pagination with exponential backoff
- Both modules save data to price_snapshots with paddle_id=NULL (dedup in Phase 2.2)
- 8 test cases total (4 per crawler) all passing
- .env.example documents Phase 2 crawler variables
</success_criteria>

<output>
After completion, create `.planning/phases/02-full-data-pipeline/02-01-SUMMARY.md`
</output>
```

---

## PLAN 02-02: Deduplication 3-Tier + Manual Review Queue

**Objective:** Implement SKU deduplication strategy (manufacturer SKU → title hash → RapidFuzz) with automatic review queue flagging.

**Approach:**
- Tier 1: Match by manufacturer SKU (exact match, when available)
- Tier 2: Title normalization + hash-based matching (lowercase, remove punctuation, compare)
- Tier 3: RapidFuzz token_set_ratio ≥ 0.85 (fuzzy string matching)
- Matches < 0.85 flagged to `review_queue` (type: `duplicate`) for manual decision
- Update `paddle_id` in `price_snapshots` for matched items

**Technical Decisions:**
- RapidFuzz library (faster Levenshtein than fuzzywuzzy, in Phase 1 deps)
- Separate modules: `pipeline/dedup/normalizer.py`, `pipeline/dedup/spec_matcher.py`
- Post-crawler job (Phase 2.3 GH Actions) runs dedup + spec matching nightly
- No auto-merge: all matches require human review initially (conservative)

**Success Verification:**
- Exact SKU matches correctly identified (test case calibrated)
- Fuzzy ≥0.85 matches accepted; <0.85 matches flagged to review_queue
- RapidFuzz threshold calibration: include test cases with scores 0.84, 0.85, 0.86

**Blockers / Risks:**
- Title normalization too aggressive → false negatives
- Threshold 0.85 too high/low → adjust via test calibration
- Review queue explosion → implement priority scoring

---

### 02-02 PLAN.md

```yaml
---
phase: 02-full-data-pipeline
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - pipeline/dedup/__init__.py
  - pipeline/dedup/normalizer.py
  - pipeline/dedup/spec_matcher.py
  - pipeline/dedup/review_queue.py
  - pipeline/tests/test_dedup_normalizer.py
  - pipeline/tests/test_spec_matcher.py
  - backend/app/models/paddle.py (extend with dedup fields)
  - backend/tests/test_admin_queue.py
autonomous: true
requirements: [R2.2]

must_haves:
  truths:
    - "3-tier dedup strategy (SKU exact → title hash → RapidFuzz) identifies duplicates"
    - "Fuzzy matches ≥0.85 automatically merged (same paddle_id)"
    - "Fuzzy matches <0.85 flagged to review_queue (type: duplicate) for human decision"
    - "Review queue records include: match_score, candidate_ids, suggested_action"
  artifacts:
    - path: "pipeline/dedup/normalizer.py"
      provides: "Title normalization + hash-based tier-2 matching"
      contains: "def normalize_title"
    - path: "pipeline/dedup/spec_matcher.py"
      provides: "RapidFuzz fuzzy matching tier-3"
      contains: "def fuzzy_match_paddles"
    - path: "pipeline/dedup/review_queue.py"
      provides: "Review queue management"
      contains: "INSERT INTO review_queue"
    - path: "pipeline/tests/test_dedup_normalizer.py"
      provides: "Normalization test cases"
      contains: "test_normalize__removes_punctuation"
    - path: "pipeline/tests/test_spec_matcher.py"
      provides: "Fuzzy match calibration tests"
      contains: "test_fuzzy_match__score_085__accepted, test_fuzzy_match__score_084__rejected"
  key_links:
    - from: "pipeline/dedup/"
      to: "pipeline/db/connection.py"
      via: "Query price_snapshots, update paddle_id"
      pattern: "SELECT * FROM price_snapshots"
    - from: "pipeline/dedup/"
      to: "review_queue table"
      via: "Flag mismatches <0.85"
      pattern: "INSERT INTO review_queue"
    - from: "backend/tests/test_admin_queue.py"
      to: "backend/app/api/admin.py"
      via: "GET /admin/queue, PATCH /admin/queue/{id}/resolve"
      pattern: "GET /admin/queue"
---

<objective>
Implement 3-tier SKU deduplication (manufacturer SKU → title hash → RapidFuzz) with automatic review queue flagging for fuzzy matches below threshold.

Purpose: Prevent duplicate paddle entries while allowing manual verification of ambiguous matches.
Output: Working dedup modules with calibrated RapidFuzz threshold, review_queue populated with flagged items.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md
@.planning/02-full-data-pipeline/CONTEXT.md
@REQUIREMENTS.md (R2.2 section for 3-tier strategy)
@pipeline/db/schema.sql (review_queue table)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement title normalization + tier-1/2 dedup matching</name>
  <files>
    pipeline/dedup/__init__.py,
    pipeline/dedup/normalizer.py,
    pipeline/tests/test_dedup_normalizer.py
  </files>
  <action>
1. Create `pipeline/dedup/normalizer.py`:
   - `def normalize_title(title: str) -> str`:
     - Convert to lowercase
     - Strip leading/trailing whitespace
     - Remove all punctuation (regex: `[^\w\s]`)
     - Replace multiple spaces with single space
     - Return normalized string
   - `def title_hash(title: str) -> str`:
     - Normalize title
     - Return SHA256 hex digest (for quick comparison)
   - `async def tier1_match(sku: str, retailer_id: int) -> int | None`:
     - Query DB: `SELECT paddle_id FROM paddles WHERE manufacturer_sku = $1`
     - If found, return paddle_id; else return None
   - `async def tier2_match(title: str) -> int | None`:
     - Calculate hash = title_hash(title)
     - Query DB: `SELECT paddle_id FROM paddles WHERE title_hash = $1`
     - Return first match or None

2. Create `pipeline/tests/test_dedup_normalizer.py`:
   - Test 1: `test_normalize__removes_punctuation`
     - Input: "Selkirk Vanguard Power Air™ (Pro)"
     - Expected: "selkirk vanguard power air pro"
   - Test 2: `test_normalize__strips_whitespace`
     - Input: "  JOOLA Ben Johns  "
     - Expected: "joola ben johns"
   - Test 3: `test_title_hash__deterministic`
     - Normalize same title twice, hashes must match
   - Test 4: `test_tier1_match__finds_by_sku`
     - Mock: paddle with manufacturer_sku="SLK-2024-001"
     - Call: tier1_match("SLK-2024-001", retailer_id=1)
     - Assert: returns paddle_id
   - Test 5: `test_tier2_match__finds_by_hash`
     - Mock: paddle with title_hash (of normalized "selkirk vanguard")
     - Query: tier2_match("Selkirk Vanguard")
     - Assert: returns paddle_id
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/tests/test_dedup_normalizer.py -xvs && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Title normalization and tier-1/2 dedup matching implemented with 5 test cases passing.</done>
</task>

<task type="auto">
  <name>Task 2: Implement RapidFuzz fuzzy matching (tier-3) with review queue flagging</name>
  <files>
    pipeline/dedup/spec_matcher.py,
    pipeline/tests/test_spec_matcher.py
  </files>
  <action>
1. Create `pipeline/dedup/spec_matcher.py`:
   - Import: RapidFuzz `token_set_ratio`, logger
   - `FUZZY_THRESHOLD = 0.85` (constant, adjustable)
   - `async def fuzzy_match_candidates(title: str, retailer_id: int, max_candidates: int = 10) -> list[tuple[int, float]]`:
     - Query: `SELECT paddle_id, name FROM paddles WHERE retailer_id != $1 ORDER BY RANDOM() LIMIT $2`
     - For each candidate:
       - score = token_set_ratio(title.lower(), candidate_name.lower()) / 100.0
       - Collect (paddle_id, score) pairs with score ≥ 0.70 (lower bound for fuzzy detection)
     - Return sorted by score descending
   - `async def process_dedup_for_price_snapshot(snapshot_id: int, title: str, retailer_id: int)`:
     - Try tier1 (SKU): if found, link to paddle_id
     - Try tier2 (hash): if found, link to paddle_id
     - Try tier3 (fuzzy):
       - candidates = fuzzy_match_candidates(title, retailer_id)
       - if top_score ≥ FUZZY_THRESHOLD:
         - Link to top candidate paddle_id
         - Log: f"Fuzzy match accepted: {title} → {candidate_id} (score: {top_score})"
       - elif top_score >= 0.70 and top_score < FUZZY_THRESHOLD:
         - Insert to review_queue: type='duplicate', score=top_score, paddle_id=None (new), related_paddle_id=top_candidate_id
         - Log: f"Fuzzy match flagged: {title} vs {candidate_name} (score: {top_score} < {FUZZY_THRESHOLD})"
       - else:
         - Create new paddle_id (no match found)

2. Create `pipeline/tests/test_spec_matcher.py`:
   - Test 1: `test_fuzzy_match__score_086__accepted`
     - Mock paddles: "Selkirk Vanguard Power Air" vs "Selkirk Vanguard Power Air Pro"
     - RapidFuzz will score ≈0.86+
     - Assert: matched, no review_queue entry
   - Test 2: `test_fuzzy_match__score_085__boundary_accepted`
     - Mock exact boundary: score = 0.85
     - Assert: matched (≥ threshold)
   - Test 3: `test_fuzzy_match__score_084__rejected_to_queue`
     - Mock: score = 0.84 (just below threshold)
     - Assert: no match, review_queue type='duplicate' inserted with score=0.84
   - Test 4: `test_fuzzy_match__score_070__flagged_not_auto_merged`
     - Mock: score = 0.70 (minimal detection threshold)
     - Assert: flagged to queue, not auto-merged
   - Test 5: `test_fuzzy_match__score_050__no_match_new_paddle`
     - Mock: score = 0.50 (too low)
     - Assert: new paddle_id created, no queue entry
   - Test 6: `test_fuzzy_match__multiple_candidates__best_selected`
     - Mock 3 candidates with scores [0.92, 0.80, 0.75]
     - Assert: matched to 0.92 candidate
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/tests/test_spec_matcher.py::test_fuzzy_match__score_086__accepted -xvs && python -m pytest pipeline/tests/test_spec_matcher.py::test_fuzzy_match__score_084__rejected_to_queue -xvs && python -m pytest pipeline/tests/test_spec_matcher.py::test_fuzzy_match__score_085__boundary_accepted -xvs && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>RapidFuzz fuzzy matching (tier-3) with calibrated 0.85 threshold and review queue flagging, 6 test cases passing.</done>
</task>

<task type="auto">
  <name>Task 3: Extend Paddle model with dedup fields + implement admin queue endpoints</name>
  <files>
    backend/app/models/paddle.py (extend),
    backend/app/api/admin.py,
    backend/tests/test_admin_queue.py
  </files>
  <action>
1. Read existing `backend/app/models/paddle.py` and extend with dedup tracking:
   - Add optional field: `dedup_status: str = "pending"` (pending | merged | rejected | manual)
   - Add optional field: `merged_into_paddle_id: int | None = None`
   - Add optional field: `title_hash: str | None = None` (for tier-2 quick lookup)
   - Create migration: ALTER TABLE paddles ADD COLUMN dedup_status VARCHAR(20) DEFAULT 'pending' (Phase 6)

2. Create `backend/app/api/admin.py`:
   - `GET /admin/queue?type=duplicate&status=pending`:
     - Require: Authorization header with ADMIN_SECRET
     - Query: `SELECT id, type, paddle_id, related_paddle_id, data, score FROM review_queue WHERE status=$1 AND type=$2 ORDER BY created_at DESC LIMIT 50`
     - Response: `[{id, type, score, candidates: [paddle1, paddle2], action_suggested: "merge"}]`
   - `PATCH /admin/queue/{id}/resolve`:
     - Require: Authorization header with ADMIN_SECRET
     - Body: `{action: "merge" | "reject", related_paddle_id?: int}`
     - If action="merge": UPDATE paddles SET dedup_status='merged', merged_into_paddle_id=$1 WHERE paddle_id=$2
     - If action="reject": UPDATE paddles SET dedup_status='rejected'
     - UPDATE review_queue SET status='resolved', resolved_at=now()
     - Response: `{status: "resolved", action_taken: "merge" | "reject"}`

3. Create `backend/tests/test_admin_queue.py`:
   - Fixture: mock ADMIN_SECRET in os.environ
   - Test 1: `test_get_queue__200_with_token`
     - Mock: 2 items in review_queue (type='duplicate')
     - GET /admin/queue with Authorization: Bearer <TOKEN>
     - Assert: 200, returns 2 items with scores
   - Test 2: `test_get_queue__401_without_token`
     - GET /admin/queue without Authorization header
     - Assert: 401 Unauthorized
   - Test 3: `test_patch_queue_resolve__merge`
     - Mock: review_queue item with paddle_id=1, related_paddle_id=2
     - PATCH /admin/queue/1/resolve with {action: "merge", related_paddle_id: 2}
     - Assert: 200, DB updated with merged_into_paddle_id
   - Test 4: `test_patch_queue_resolve__reject`
     - Mock: review_queue item
     - PATCH /admin/queue/1/resolve with {action: "reject"}
     - Assert: 200, dedup_status='rejected'
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest backend/tests/test_admin_queue.py::test_get_queue__200_with_token -xvs && python -m pytest backend/tests/test_admin_queue.py::test_get_queue__401_without_token -xvs && python -m pytest backend/tests/test_admin_queue.py::test_patch_queue_resolve__merge -xvs && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Paddle model extended with dedup fields, admin queue endpoints (GET /admin/queue, PATCH /admin/queue/{id}/resolve) with auth, 4 test cases passing.</done>
</task>

</tasks>

<verification>
- `pytest pipeline/tests/test_dedup_normalizer.py -v` → all 5 tests pass
- `pytest pipeline/tests/test_spec_matcher.py -v` → all 6 tests pass
- `pytest backend/tests/test_admin_queue.py -v` → all 4 tests pass
- RapidFuzz threshold calibration: scores 0.084, 0.085, 0.086 tested explicitly
</verification>

<success_criteria>
- 3-tier dedup strategy implemented (SKU → title hash → RapidFuzz)
- RapidFuzz threshold ≥0.85 for auto-merge, <0.85 flagged to review_queue
- Admin endpoints GET /admin/queue and PATCH /admin/queue/{id}/resolve operational
- 15 test cases total across normalizer, spec_matcher, admin tests all passing
</success_criteria>

<output>
After completion, create `.planning/phases/02-full-data-pipeline/02-02-SUMMARY.md`
</output>
```

---

## PLAN 02-03: GitHub Actions Schedule + Railway Provisioning

**Objective:** Configure GH Actions workflow for 24h crawler schedule with separate jobs per retailer, and provision Railway staging environment for API.

**Approach:**
- GH Actions workflow `.github/workflows/scrape.yml` with `schedule: cron('0 6 * * *')` (6h BRT = daily midnight UTC)
- 6 separate jobs: dropshot_brasil, mercadolivre, franklin_br, head_br, joola_br, enrich_specs (Phase 2.4)
- Each job: 3x retry via `uses: nick-inverson/retry@v2` or native Python Tenacity
- Failure: Telegram alert after job failure, structured logging to stdout (JSON)
- Railway: Dockerfile for FastAPI, environment variables from Railway dashboard, exposed port 8000

**Technical Decisions:**
- No Prefect (yet) — GH Actions sufficient for 6 independent jobs per REQUIREMENTS.md
- Railway over Heroku: simpler Dockerfile, cheaper, native env var support
- JSON structured logging for Railway observability (Phase 2.5 and beyond)

**Success Verification:**
- GH Actions workflow validates syntax (`ghas` tool or manual check)
- Live schedule test: trigger manual run, verify all jobs complete
- Railway app created, FastAPI startup successful, /health endpoint 200

**Blockers / Risks:**
- GH Actions job timeout (6h default) — crawlers should complete in < 30min
- Telegram rate limiting — aggregate alerts instead of per-job
- Railway free tier quotas — monitor usage

---

### 02-03 PLAN.md

```yaml
---
phase: 02-full-data-pipeline
plan: 03
type: execute
wave: 2
depends_on: [02-01, 02-02]
files_modified:
  - .github/workflows/scrape.yml
  - Dockerfile.railway
  - railway.toml
  - backend/app/main.py (extend with startup/shutdown)
  - .env.example (add RAILWAY_API_TOKEN)
autonomous: true
requirements: [R2.3]

must_haves:
  truths:
    - "GitHub Actions workflow scrape.yml runs daily at 6h UTC via cron schedule"
    - "6 separate jobs (dropshot, mercadolivre, franklin, head, joola, enrich) execute in parallel"
    - "Job failure triggers Telegram alert (aggregate, not per-job)"
    - "Railway staging environment provisioned and FastAPI accessible"
  artifacts:
    - path: ".github/workflows/scrape.yml"
      provides: "GH Actions daily schedule"
      contains: "schedule: cron('0 6 * * *')"
    - path: "Dockerfile.railway"
      provides: "Railway container config"
      contains: "FROM python:3.12"
    - path: "railway.toml"
      provides: "Railway deploy config"
      contains: "[build]"
    - path: "backend/app/main.py"
      provides: "FastAPI with startup/shutdown hooks"
      contains: "@app.on_event('startup')"
  key_links:
    - from: ".github/workflows/scrape.yml"
      to: "pipeline/crawlers/"
      via: "Job: python -m pipeline.crawlers.dropshot_brasil"
      pattern: "python -m pipeline.crawlers"
    - from: "Dockerfile.railway"
      to: "backend/app/main.py"
      via: "CMD: uvicorn backend.app.main:app"
      pattern: "uvicorn"
---

<objective>
Set up GitHub Actions schedule for 24h crawler orchestration and Railway staging environment for API deployment.

Purpose: Automate daily data collection and provide staging API accessible for testing.
Output: Working GH Actions workflow, Railway app deployed with FastAPI, daily schedule validated.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md (R2.3 section)
@.planning/02-full-data-pipeline/CONTEXT.md
@pipeline/crawlers/ (ref module names for jobs)
@.env.example
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create GitHub Actions workflow with daily cron schedule and 6 crawler jobs</name>
  <files>
    .github/workflows/scrape.yml
  </files>
  <action>
1. Create `.github/workflows/scrape.yml`:
```yaml
name: Scrape Paddles (24h Schedule)

on:
  schedule:
    - cron: '0 6 * * *'  # 6h UTC = midnight BRT
  workflow_dispatch:     # Manual trigger for testing

env:
  DATABASE_URL: ${{ secrets.SUPABASE_DATABASE_URL }}
  FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
  TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
  ML_API_BATCH_SIZE: 50

jobs:
  scrape-dropshot-brasil:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: |
          cd pipeline && pip install -e . 2>&1 | tail -10
      - name: Scrape Drop Shot Brasil
        run: |
          cd pipeline && python -m pipeline.crawlers.dropshot_brasil 2>&1 | tee /tmp/dropshot.log
      - name: Alert on failure
        if: failure()
        run: |
          python -c "
import asyncio, os
from pipeline.alerts.telegram import send_telegram_alert
asyncio.run(send_telegram_alert('Drop Shot Brasil crawler FAILED. Check logs.'))
"

  scrape-mercadolivre:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: |
          cd pipeline && pip install -e .
      - name: Scrape Mercado Livre
        run: |
          cd pipeline && python -m pipeline.crawlers.mercadolivre_expansion 2>&1 | tee /tmp/ml.log
      - name: Alert on failure
        if: failure()
        run: |
          python -c "
import asyncio, os
from pipeline.alerts.telegram import send_telegram_alert
asyncio.run(send_telegram_alert('Mercado Livre crawler FAILED. Check logs.'))
"

  scrape-franklin-br:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: cd pipeline && pip install -e .
      - name: Scrape Franklin BR
        run: cd pipeline && python -m pipeline.crawlers.franklin_br 2>&1 || echo "Franklin BR not yet implemented"
      - name: Alert on failure
        if: failure()
        run: |
          python -c "
import asyncio
from pipeline.alerts.telegram import send_telegram_alert
asyncio.run(send_telegram_alert('Franklin BR crawler FAILED.'))
"

  scrape-head-br:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: cd pipeline && pip install -e .
      - name: Scrape Head BR
        run: cd pipeline && python -m pipeline.crawlers.head_br 2>&1 || echo "Head BR not yet implemented"
      - name: Alert on failure
        if: failure()
        run: |
          python -c "
import asyncio
from pipeline.alerts.telegram import send_telegram_alert
asyncio.run(send_telegram_alert('Head BR crawler FAILED.'))
"

  scrape-joola-br:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: cd pipeline && pip install -e .
      - name: Scrape JOOLA BR
        run: cd pipeline && python -m pipeline.crawlers.joola_br 2>&1 || echo "JOOLA BR not yet implemented"
      - name: Alert on failure
        if: failure()
        run: |
          python -c "
import asyncio
from pipeline.alerts.telegram import send_telegram_alert
asyncio.run(send_telegram_alert('JOOLA BR crawler FAILED.'))
"

  enrich-specs:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    needs: [scrape-dropshot-brasil, scrape-mercadolivre]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: cd pipeline && pip install -e .
      - name: Enrich specs from international sources
        run: cd pipeline && python -m pipeline.crawlers.spec_enrichment 2>&1 || echo "Spec enrichment not yet implemented"
      - name: Alert on failure
        if: failure()
        run: |
          python -c "
import asyncio
from pipeline.alerts.telegram import send_telegram_alert
asyncio.run(send_telegram_alert('Spec enrichment FAILED.'))
"

  notify-success:
    runs-on: ubuntu-latest
    needs: [scrape-dropshot-brasil, scrape-mercadolivre, enrich-specs]
    if: success()
    steps:
      - name: Send success alert
        run: |
          python -c "
import asyncio, os, sys
sys.path.insert(0, 'pipeline')
from pipeline.alerts.telegram import send_telegram_alert
asyncio.run(send_telegram_alert('✓ All crawlers completed successfully.'))
"
```

2. Validate syntax: `gha validate .github/workflows/scrape.yml` (or manual review)
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && test -f .github/workflows/scrape.yml && grep -q "schedule: cron" .github/workflows/scrape.yml && grep -q "workflow_dispatch" .github/workflows/scrape.yml && grep -q "scrape-dropshot" .github/workflows/scrape.yml && grep -q "scrape-mercadolivre" .github/workflows/scrape.yml && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>GitHub Actions workflow created with daily 6h UTC schedule, 6 separate jobs with Telegram alerts on failure.</done>
</task>

<task type="auto">
  <name>Task 2: Create Railway Dockerfile + railway.toml config + FastAPI startup/shutdown hooks</name>
  <files>
    Dockerfile.railway,
    railway.toml,
    backend/app/main.py (extend)
  </files>
  <action>
1. Create `Dockerfile.railway`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy backend
COPY backend/ /app/backend/

# Copy pipeline (for shared modules if needed)
COPY pipeline/ /app/pipeline/

# Install backend deps
RUN pip install --no-cache-dir fastapi uvicorn psycopg[binary] httpx pydantic python-dotenv openai

# Expose port (Railway will route via $PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Start FastAPI
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Create `railway.toml`:
```toml
[build]
dockerfile = "Dockerfile.railway"

[deploy]
startCommand = "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"

[[services]]
name = "api"
```

3. Update `backend/app/main.py`:
   - Import: `from contextlib import asynccontextmanager`
   - Add FastAPI lifespan context manager (v0.93+):
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI startup — initializing...")
    # Could initialize DB pool, cache, etc. here
    yield
    # Shutdown
    logger.info("FastAPI shutdown — cleaning up...")
    # Close DB pool, cache, etc. here

app = FastAPI(title="PickleIQ", version="0.1.0", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}
```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && test -f Dockerfile.railway && grep -q "python:3.12" Dockerfile.railway && grep -q "uvicorn" Dockerfile.railway && test -f railway.toml && grep -q "Dockerfile.railway" railway.toml && grep -q "lifespan" backend/app/main.py && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Dockerfile.railway, railway.toml, and FastAPI startup/shutdown hooks created. Ready for Railway deployment.</done>
</task>

</tasks>

<verification>
- `.github/workflows/scrape.yml` contains daily schedule, 6 jobs, Telegram alerts
- `Dockerfile.railway` uses python:3.12-slim, installs deps, exposes 8000
- `railway.toml` references correct Dockerfile
- `backend/app/main.py` has @asynccontextmanager lifespan hook
</verification>

<success_criteria>
- GH Actions workflow runs daily at 6h UTC
- 6 crawler jobs configured (even if not yet implemented — job will skip gracefully)
- Manual workflow_dispatch available for testing
- Railway Dockerfile valid and startable
- FastAPI responds to /health endpoint
</success_criteria>

<output>
After completion, create `.planning/phases/02-full-data-pipeline/02-03-SUMMARY.md`
</output>
```

---

## PLAN 02-04: pgvector Embeddings + Async Re-embedding

**Objective:** Generate text embeddings for all paddles using text-embedding-3-small, create HNSW index, and implement async re-embedding via needs_reembed flag.

**Approach:**
- Document generation: 200-400 tokens per paddle (specs + name + translated metrics)
- OpenAI API `text-embedding-3-small` batch processing (5 concurrent requests max)
- Store in `paddle_embeddings(paddle_id, embedding vector(1536), updated_at)`
- Create HNSW index: `CREATE INDEX ON paddle_embeddings USING hnsw (embedding vector_cosine_ops)`
- Async re-embedding: trigger on `paddle_specs` UPDATE → set `needs_reembed=true`
- Nightly GH Actions job: `SELECT WHERE needs_reembed=true` → batch OpenAI → reset flag

**Technical Decisions:**
- text-embedding-3-small: cost-effective (0.02/MTok), sufficient for 1536D vectors
- HNSW over IVFFlat: better accuracy, PostgreSQL 16 supports it natively
- Async batch: avoid 500 synchronous API calls during bulk updates
- Threshold 0.65 for similarity (in Phase 3 RAG)

**Success Verification:**
- All paddles have embeddings (no NULLs in paddle_embeddings.embedding)
- HNSW index created and queryable via `<-> cosine distance operator`
- Async re-embedding test: mock OpenAI, verify batch processing without blocking

**Blockers / Risks:**
- OpenAI API quota exceeded → use batch API for cost savings (Phase 3)
- Document generation too short/long → calibrate token count
- Embedding dimension mismatch (1536 vs 3072) → test schema compatibility

---

### 02-04 PLAN.md

```yaml
---
phase: 02-full-data-pipeline
plan: 04
type: execute
wave: 2
depends_on: [02-01, 02-02]
files_modified:
  - backend/app/embeddings.py
  - backend/app/models/paddle.py (extend)
  - pipeline/embeddings/__init__.py
  - pipeline/embeddings/document_generator.py
  - pipeline/embeddings/batch_embedder.py
  - pipeline/tests/test_embeddings.py
  - .github/workflows/scrape.yml (add re-embedding job)
  - .env.example (add OPENAI_API_KEY)
autonomous: true
requirements: [R2.4]

must_haves:
  truths:
    - "All paddles have 1536-dimensional embeddings from text-embedding-3-small"
    - "HNSW index on paddle_embeddings.embedding enables fast cosine similarity search"
    - "Async re-embedding job processes needs_reembed=true batches nightly"
    - "Document per paddle: 200-400 tokens (specs + translated metrics + name)"
  artifacts:
    - path: "pipeline/embeddings/document_generator.py"
      provides: "Paddle → narrative document conversion"
      contains: "def generate_paddle_document"
    - path: "pipeline/embeddings/batch_embedder.py"
      provides: "OpenAI batch embedding with retry"
      contains: "async def batch_embed_paddles"
    - path: "backend/app/embeddings.py"
      provides: "Embedding service (read-only for Phase 2)"
      contains: "async def get_similar_paddles"
    - path: "backend/app/models/paddle.py"
      provides: "Extended with needs_reembed flag"
      contains: "needs_reembed: bool"
  key_links:
    - from: "pipeline/embeddings/batch_embedder.py"
      to: "paddle_embeddings table"
      via: "INSERT/UPDATE vector column"
      pattern: "INSERT INTO paddle_embeddings"
    - from: ".github/workflows/scrape.yml"
      to: "pipeline/embeddings/batch_embedder.py"
      via: "Re-embedding job triggered post-crawl"
      pattern: "python -m pipeline.embeddings.batch_embedder"
    - from: "backend/app/embeddings.py"
      to: "paddle_embeddings table"
      via: "pgvector similarity search"
      pattern: "<-> vector_cosine_ops"
---

<objective>
Generate text embeddings for all paddles using text-embedding-3-small, create HNSW index for fast similarity search, and implement async re-embedding for spec updates.

Purpose: Enable semantic search in Phase 3 RAG agent for personalized paddle recommendations.
Output: paddle_embeddings table fully populated, HNSW index created, async re-embedding job operational.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md (R2.4 section for embedding architecture)
@.planning/02-full-data-pipeline/CONTEXT.md
@backend/app/models/paddle.py
@pipeline/db/schema.sql (paddle_embeddings table structure)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement document generation + batch embedding service</name>
  <files>
    pipeline/embeddings/__init__.py,
    pipeline/embeddings/document_generator.py,
    pipeline/embeddings/batch_embedder.py,
    pipeline/tests/test_embeddings.py
  </files>
  <action>
1. Create `pipeline/embeddings/document_generator.py`:
   - `def generate_paddle_document(paddle: PaddleWithSpecs) -> str`:
     - Input: paddle dict with: name, brand, retailer, price_min, specs {swingweight, twistweight, weight_oz, core_thickness_mm, face_material}
     - Generate narrative (200-400 tokens):
       ```
       "{brand} {name} pickleball paddle.

       Specifications:
       - Weight: {weight_oz} oz
       - Swingweight: {swingweight}
       - Twistweight: {twistweight}
       - Core thickness: {core_thickness_mm}mm ({material_description})
       - Face material: {face_material}

       Performance profile:
       {swingweight_interpretation} — ideal for {swingweight_recommended_style}
       {twistweight_interpretation} — {twistweight_recommended_skill}
       Core {core_thickness_mm}mm provides {core_feel_description}

       Available at {retailer_name} from R$ {price_min}
       ```
     - Use helper functions:
       - `def swingweight_to_description(swingweight: float) -> str` — maps to "ágil", "equilibrado", "potência"
       - `def twistweight_to_description(twistweight: float) -> str` — maps to "precisão", "tolerância"
       - `def core_to_description(core_mm: float) -> str` — maps to "resposta viva", "controle e absorção"
     - Ensure output is 200-400 tokens (use tiktoken estimate, fallback to len(words)/1.3)

2. Create `pipeline/embeddings/batch_embedder.py`:
   - Import: OpenAI client, asyncio, psycopg
   - `async def batch_embed_paddles(paddle_ids: list[int] = None, batch_size: int = 5)`:
     - If paddle_ids is None: SELECT all paddles with NULL embedding (first run)
     - Fetch paddle docs for each ID
     - For each batch (size 5):
       - Call OpenAI `Embedding.create(model="text-embedding-3-small", input=[docs...])` (batch mode available in v1.3+)
       - Extract embedding vector
       - INSERT/UPDATE paddle_embeddings(paddle_id, embedding, updated_at)
       - Log: f"Embedded {len(batch)} paddles, tokens: {usage.total_tokens}"
     - Return: `{"status": "success", "total_embedded": count, "tokens": total_tokens, "cost_usd": total_tokens * 0.02 / 1_000_000}`
   - `async def re_embed_flagged_paddles()`:
     - SELECT paddle_id FROM paddles WHERE needs_reembed=true
     - Call batch_embed_paddles(paddle_ids)
     - UPDATE paddles SET needs_reembed=false WHERE paddle_id IN (...)
     - Return result

3. Create `pipeline/tests/test_embeddings.py`:
   - Test 1: `test_document_generation__contains_specs`
     - Mock paddle: name="Selkirk Vanguard", swingweight=115, core_13mm
     - Generate doc
     - Assert: doc contains "Selkirk Vanguard", "115", "13mm"
     - Assert: 200 < len(doc.split()) < 400
   - Test 2: `test_batch_embed__first_run__embeds_all`
     - Mock: 3 paddles, no embeddings yet
     - Mock OpenAI to return vectors
     - Call batch_embed_paddles(None)
     - Assert: 3 rows inserted to paddle_embeddings
     - Assert: each embedding is 1536 dimensions
   - Test 3: `test_batch_embed__batching__respects_batch_size_5`
     - Mock: 12 paddles
     - Track OpenAI calls (should be ceil(12/5)=3 batches)
     - Assert: 3 API calls made (not 12)
   - Test 4: `test_re_embed_flagged__only_flagged_paddles`
     - Mock: 5 paddles, 2 with needs_reembed=true
     - Call re_embed_flagged_paddles()
     - Assert: only 2 embedded
     - Assert: needs_reembed=false for those 2 after
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest pipeline/tests/test_embeddings.py::test_document_generation__contains_specs -xvs && python -m pytest pipeline/tests/test_embeddings.py::test_batch_embed__first_run__embeds_all -xvs && python -m pytest pipeline/tests/test_embeddings.py::test_batch_embed__batching__respects_batch_size_5 -xvs && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Document generation and batch embedding service implemented with 4 test cases passing.</done>
</task>

<task type="auto">
  <name>Task 2: Create embedding index + extend Paddle model + add re-embedding to GH Actions</name>
  <files>
    pipeline/db/schema-updates.sql,
    backend/app/models/paddle.py (extend),
    backend/app/embeddings.py,
    .github/workflows/scrape.yml (extend)
  </files>
  <action>
1. Create `pipeline/db/schema-updates.sql` (to be applied post-Phase 1):
   ```sql
   -- Add needs_reembed flag to paddles table
   ALTER TABLE paddles ADD COLUMN needs_reembed boolean DEFAULT false;

   -- Create HNSW index for cosine similarity search
   CREATE INDEX paddles_embedding_hnsw_idx
   ON paddle_embeddings USING hnsw (embedding vector_cosine_ops)
   WITH (m=16, ef_construction=200);

   -- Trigger: mark paddle for re-embedding when specs update
   CREATE OR REPLACE FUNCTION mark_for_reembed()
   RETURNS TRIGGER AS $$
   BEGIN
     UPDATE paddles SET needs_reembed=true WHERE id=NEW.paddle_id;
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER paddle_specs_update_reembed
   AFTER UPDATE ON paddle_specs
   FOR EACH ROW
   EXECUTE FUNCTION mark_for_reembed();
   ```

2. Update `backend/app/models/paddle.py`:
   - Add field: `needs_reembed: bool = False`
   - Add optional field: `embedding: Optional[list[float]] = None` (for full retrieval, optional)

3. Create `backend/app/embeddings.py`:
   - `async def get_similar_paddles(query_embedding: list[float], top_k: int = 5, threshold: float = 0.65) -> list[int]`:
     - Use psycopg connection
     - Query: `SELECT paddle_id, (embedding <-> $1::vector) AS distance FROM paddle_embeddings WHERE (embedding <-> $1::vector) <= (1 - $2) ORDER BY distance LIMIT $3`
     - Return list of paddle_ids with similarity ≥ threshold
   - (This function will be called by Phase 3 RAG agent)

4. Update `.github/workflows/scrape.yml`:
   - Add new job `re-embed-flagged`:
     ```yaml
     re-embed-flagged:
       runs-on: ubuntu-latest
       needs: [scrape-dropshot-brasil, scrape-mercadolivre]
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: '3.12'
         - name: Install deps
           run: cd pipeline && pip install -e .
         - name: Re-embed flagged paddles
           env:
             OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
           run: |
             cd pipeline && python -c "
     import asyncio
     from pipeline.embeddings.batch_embedder import re_embed_flagged_paddles
     result = asyncio.run(re_embed_flagged_paddles())
     print(f'Re-embedding result: {result}')
     "
     ```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && test -f pipeline/db/schema-updates.sql && grep -q "HNSW\|hnsw" pipeline/db/schema-updates.sql && grep -q "needs_reembed" pipeline/db/schema-updates.sql && grep -q "get_similar_paddles" backend/app/embeddings.py && grep -q "vector_cosine_ops" backend/app/embeddings.py && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Embedding index (HNSW) created, Paddle model extended, similarity search endpoint prepared, re-embedding job added to GH Actions.</done>
</task>

</tasks>

<verification>
- `pytest pipeline/tests/test_embeddings.py -v` → all tests pass
- Document generation produces 200-400 token narratives
- Batch embedding respects batch_size=5 concurrency
- HNSW index creation script valid SQL
- Re-embedding job integrated into GH Actions workflow
</verification>

<success_criteria>
- All paddles have embeddings (1536D vectors) in paddle_embeddings table
- HNSW index on embedding column enables < 50ms cosine similarity queries
- async re_embed_flagged_paddles() processes needs_reembed=true batches correctly
- Trigger on paddle_specs UPDATE sets needs_reembed=true automatically
- Document generation 200-400 tokens per paddle
- 4 embedding tests passing
</success_criteria>

<output>
After completion, create `.planning/phases/02-full-data-pipeline/02-04-SUMMARY.md`
</output>
```

---

## PLAN 02-05: FastAPI Endpoints (GET /paddles/*)

**Objective:** Implement 5 GET endpoints for paddle retrieval: /paddles, /paddles/{id}, /paddles/{id}/prices, /paddles/{id}/latest-prices, /health.

**Approach:**
- Shared filtering: brand, price_range, skill_level, in_stock query params
- /paddles — list all (paginated: limit=50, offset=0)
- /paddles/{id} — single paddle + latest specs + translated metrics
- /paddles/{id}/prices — historical price data (all snapshots)
- /paddles/{id}/latest-prices — current price from each retailer
- /health — simple 200 OK

**Technical Decisions:**
- Response models via Pydantic
- SQL queries optimized (indices in schema from Phase 1)
- No authentication (anon-first)
- Pagination via limit/offset (limit max 100)

**Success Verification:**
- pytest: 100% happy path + error cases (404, validation)
- Manual: curl endpoints, verify schema matches response

**Blockers / Risks:**
- N+1 queries on /paddles — mitigate with JOIN
- Large datasets slow — implement pagination
- Schema evolution — version endpoints if necessary

---

### 02-05 PLAN.md

```yaml
---
phase: 02-full-data-pipeline
plan: 05
type: execute
wave: 2
depends_on: [02-04]
files_modified:
  - backend/app/api/__init__.py
  - backend/app/api/paddles.py
  - backend/app/schemas.py (response models)
  - backend/tests/test_paddles_endpoints.py
  - backend/app/main.py (add routes)
autonomous: true
requirements: [R2.5]

must_haves:
  truths:
    - "GET /paddles returns list of paddles with optional filters (brand, price_range, in_stock, limit, offset)"
    - "GET /paddles/{id} returns single paddle with full specs + translated metrics"
    - "GET /paddles/{id}/prices returns historical price_snapshots (all time)"
    - "GET /paddles/{id}/latest-prices returns current prices per retailer (from latest_prices view)"
    - "GET /health returns 200 OK {status: ok}"
  artifacts:
    - path: "backend/app/api/paddles.py"
      provides: "5 paddle endpoints"
      contains: "@router.get('/paddles')"
    - path: "backend/app/schemas.py"
      provides: "Response Pydantic models"
      contains: "class PaddleResponse"
    - path: "backend/tests/test_paddles_endpoints.py"
      provides: "Happy path + error tests"
      contains: "test_get_paddles__200"
  key_links:
    - from: "backend/app/api/paddles.py"
      to: "backend/app/models/paddle.py"
      via: "Pydantic response schema conversion"
      pattern: "PaddleResponse.from_orm"
    - from: "backend/app/main.py"
      to: "backend/app/api/paddles.py"
      via: "app.include_router(paddles_router)"
      pattern: "include_router"
---

<objective>
Implement 5 FastAPI GET endpoints for paddle catalog browsing: list, detail, prices, latest-prices, and health check.

Purpose: Provide API surface for frontend (Phase 4) and RAG agent (Phase 3) to query paddle data.
Output: All 5 endpoints operational, tested, fully specified in OpenAPI schema.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md (R2.5 section)
@.planning/02-full-data-pipeline/CONTEXT.md
@backend/app/models/paddle.py (schema)
@backend/app/main.py (FastAPI app)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create Pydantic response schemas + paddle listing/detail endpoints</name>
  <files>
    backend/app/schemas.py,
    backend/app/api/__init__.py,
    backend/app/api/paddles.py,
    backend/tests/test_paddles_endpoints.py
  </files>
  <action>
1. Create `backend/app/schemas.py`:
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SpecsResponse(BaseModel):
    swingweight: Optional[float] = None
    twistweight: Optional[float] = None
    weight_oz: Optional[float] = None
    grip_size: Optional[str] = None
    core_thickness_mm: Optional[float] = None
    face_material: Optional[str] = None
    model_config = {"from_attributes": True}

class PaddleResponse(BaseModel):
    id: int
    name: str
    brand: str
    sku: Optional[str] = None
    image_url: Optional[str] = None
    specs: Optional[SpecsResponse] = None
    price_min_brl: Optional[float] = None
    created_at: datetime
    model_config = {"from_attributes": True}

class PaddleListResponse(BaseModel):
    items: List[PaddleResponse]
    total: int
    limit: int
    offset: int

class PriceSnapshot(BaseModel):
    retailer_name: str
    price_brl: float
    currency: str
    in_stock: bool
    scraped_at: datetime
    model_config = {"from_attributes": True}

class PriceHistoryResponse(BaseModel):
    paddle_id: int
    paddle_name: str
    prices: List[PriceSnapshot]

class LatestPriceResponse(BaseModel):
    paddle_id: int
    paddle_name: str
    latest_prices: List[PriceSnapshot]

class HealthResponse(BaseModel):
    status: str
```

2. Create `backend/app/api/__init__.py` (empty or with exports).

3. Create `backend/app/api/paddles.py`:
```python
from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
import logging
from backend.app.schemas import (
    PaddleResponse, PaddleListResponse, PriceHistoryResponse, LatestPriceResponse, HealthResponse
)
from backend.app.db import get_db_connection  # TBD: DB helper
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/paddles", tags=["paddles"])

@router.get("", response_model=PaddleListResponse, status_code=status.HTTP_200_OK)
async def list_paddles(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    price_min: Optional[float] = Query(None, description="Min price BRL"),
    price_max: Optional[float] = Query(None, description="Max price BRL"),
    in_stock: Optional[bool] = Query(None, description="Only in-stock items"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """List all paddles with optional filters."""
    # Build SQL with WHERE clauses based on filters
    where_clauses = ["dedup_status IN ('pending', 'merged')"]  # Exclude rejected
    params = []

    if brand:
        where_clauses.append("brand = $" + str(len(params)+1))
        params.append(brand)
    if price_min:
        where_clauses.append("price_min_brl >= $" + str(len(params)+1))
        params.append(price_min)
    if price_max:
        where_clauses.append("price_min_brl <= $" + str(len(params)+1))
        params.append(price_max)
    if in_stock is not None:
        where_clauses.append("in_stock = $" + str(len(params)+1))
        params.append(in_stock)

    where = " AND ".join(where_clauses)

    # Count query
    count_query = f"SELECT COUNT(*) as total FROM paddles WHERE {where}"
    count_result = await db_fetch_one(count_query, params)
    total = count_result["total"]

    # Data query with pagination
    data_query = f"SELECT * FROM paddles WHERE {where} ORDER BY created_at DESC LIMIT ${len(params)+1} OFFSET ${len(params)+2}"
    paddles = await db_fetch_all(data_query, params + [limit, offset])

    items = [PaddleResponse.model_validate(p) for p in paddles]
    return PaddleListResponse(items=items, total=total, limit=limit, offset=offset)

@router.get("/{paddle_id}", response_model=PaddleResponse, status_code=status.HTTP_200_OK)
async def get_paddle(paddle_id: int):
    """Get single paddle with full details."""
    query = """
    SELECT p.*, ps.swingweight, ps.twistweight, ps.weight_oz, ps.core_thickness_mm, ps.face_material
    FROM paddles p
    LEFT JOIN paddle_specs ps ON p.id = ps.paddle_id
    WHERE p.id = $1 AND p.dedup_status IN ('pending', 'merged')
    """
    paddle = await db_fetch_one(query, [paddle_id])
    if not paddle:
        raise HTTPException(status_code=404, detail="Paddle not found")

    # Combine specs
    specs_data = {k: v for k, v in paddle.items() if k in ["swingweight", "twistweight", "weight_oz", "core_thickness_mm", "face_material"]}
    paddle["specs"] = specs_data if any(specs_data.values()) else None

    return PaddleResponse.model_validate(paddle)

@router.get("/{paddle_id}/prices", response_model=PriceHistoryResponse, status_code=status.HTTP_200_OK)
async def get_paddle_prices(paddle_id: int):
    """Get price history for a paddle across all retailers."""
    # Verify paddle exists
    query = "SELECT id, name FROM paddles WHERE id = $1"
    paddle = await db_fetch_one(query, [paddle_id])
    if not paddle:
        raise HTTPException(status_code=404, detail="Paddle not found")

    # Get prices
    prices_query = """
    SELECT r.name AS retailer_name, ps.price_brl, ps.currency, ps.in_stock, ps.scraped_at
    FROM price_snapshots ps
    JOIN retailers r ON ps.retailer_id = r.id
    WHERE ps.paddle_id = $1
    ORDER BY ps.scraped_at DESC
    """
    prices = await db_fetch_all(prices_query, [paddle_id])

    return PriceHistoryResponse(
        paddle_id=paddle_id,
        paddle_name=paddle["name"],
        prices=[PriceSnapshot.model_validate(p) for p in prices]
    )

@router.get("/{paddle_id}/latest-prices", response_model=LatestPriceResponse, status_code=status.HTTP_200_OK)
async def get_paddle_latest_prices(paddle_id: int):
    """Get latest price from each retailer for a paddle."""
    # Verify paddle exists
    query = "SELECT id, name FROM paddles WHERE id = $1"
    paddle = await db_fetch_one(query, [paddle_id])
    if not paddle:
        raise HTTPException(status_code=404, detail="Paddle not found")

    # Get latest prices (from materialized view)
    prices_query = """
    SELECT r.name AS retailer_name, lp.price_brl, lp.currency, lp.in_stock, lp.scraped_at
    FROM latest_prices lp
    JOIN retailers r ON lp.retailer_id = r.id
    WHERE lp.paddle_id = $1
    """
    prices = await db_fetch_all(prices_query, [paddle_id])

    return LatestPriceResponse(
        paddle_id=paddle_id,
        paddle_name=paddle["name"],
        latest_prices=[PriceSnapshot.model_validate(p) for p in prices]
    )

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="ok")
```

4. Create `backend/tests/test_paddles_endpoints.py`:
```python
import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_get_paddles__200():
    """Test GET /paddles returns list."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/paddles")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

@pytest.mark.asyncio
async def test_get_paddle__200():
    """Test GET /paddles/{id} returns single paddle."""
    # Assume paddle_id=1 exists from Phase 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/paddles/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "name" in data
        assert "brand" in data

@pytest.mark.asyncio
async def test_get_paddle__404():
    """Test GET /paddles/{id} returns 404 for invalid ID."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/paddles/99999")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_paddle_prices__200():
    """Test GET /paddles/{id}/prices returns history."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/paddles/1/prices")
        assert response.status_code == 200
        data = response.json()
        assert data["paddle_id"] == 1
        assert "prices" in data

@pytest.mark.asyncio
async def test_get_paddle_latest_prices__200():
    """Test GET /paddles/{id}/latest-prices returns current prices."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/paddles/1/latest-prices")
        assert response.status_code == 200
        data = response.json()
        assert data["paddle_id"] == 1
        assert "latest_prices" in data

@pytest.mark.asyncio
async def test_health__200():
    """Test GET /health returns ok."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -m pytest backend/tests/test_paddles_endpoints.py::test_health__200 -xvs && python -m pytest backend/tests/test_paddles_endpoints.py::test_get_paddles__200 -xvs && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Response schemas created, 5 paddle endpoints implemented, health check operational.</done>
</task>

<task type="auto">
  <name>Task 2: Wire routes into FastAPI app + validation test</name>
  <files>
    backend/app/main.py (extend)
  </files>
  <action>
1. Update `backend/app/main.py`:
   - Import: `from backend.app.api.paddles import router as paddles_router`
   - Add: `app.include_router(paddles_router)`
   - Verify /health route is already there (Phase 1 had it)

2. Manual validation:
   - Run: `cd /home/diego/Documentos/picklepicker && python -m uvicorn backend.app.main:app --reload`
   - Visit: http://localhost:8000/docs
   - Verify: All 5 endpoints visible in Swagger UI
   - Test manual requests to confirm schema
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && grep -q "include_router.*paddles" backend/app/main.py && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>Routes integrated into FastAPI app, OpenAPI schema includes all 5 paddle endpoints.</done>
</task>

</tasks>

<verification>
- `pytest backend/tests/test_paddles_endpoints.py -v` → all 6+ tests pass
- FastAPI /docs page shows 5 paddle endpoints + /health
- GET /paddles returns PaddleListResponse with pagination
- GET /paddles/{id} returns PaddleResponse with specs nested
- GET /paddles/{id}/prices returns historical data
- GET /paddles/{id}/latest-prices returns current prices from latest_prices view
- GET /health returns {status: ok}
</verification>

<success_criteria>
- All 5 endpoints return 200 on happy path
- All endpoints properly paginated or parameterized
- Error handling: 404 for invalid IDs, validation errors for bad params
- Response schemas match Pydantic models
- OpenAPI spec valid and accessible at /docs
- 6 test cases passing (health, list, detail, 404, prices, latest-prices)
</success_criteria>

<output>
After completion, create `.planning/phases/02-full-data-pipeline/02-05-SUMMARY.md`
</output>
```

---

## Summary

**Phase 2: Full Data Pipeline** consists of 5 independent, executable plans delivering:

1. **02-01 (Wave 1):** Drop Shot Brasil + Mercado Livre crawlers via Firecrawl with retry + Telegram alerts
2. **02-02 (Wave 1):** 3-tier deduplication (SKU → hash → RapidFuzz 0.85) + review queue
3. **02-03 (Wave 2):** GH Actions daily schedule (6 jobs) + Railway staging deployment
4. **02-04 (Wave 2):** pgvector embeddings (text-embedding-3-small, 1536D, HNSW index) + async re-embedding
5. **02-05 (Wave 2):** FastAPI endpoints: GET /paddles, /paddles/{id}, /paddles/{id}/prices, /paddles/{id}/latest-prices, /health

**Execution Timeline:** ~170-185 min total (35-40 min each × 5 plans, parallelized in 2 waves)

**Testing:** 40+ test cases across all modules, all passing before merging.

**Go/No-Go Verification:**
- [ ] All 5 plans executed
- [ ] All tests passing
- [ ] GH Actions workflow validates
- [ ] Railway app deployable
- [ ] ≥200 paddles indexed (from crawlers)
- [ ] Dedup review_queue populated (fuzzy matches <0.85)
- [ ] pgvector index queryable
- [ ] FastAPI /health responds 200
