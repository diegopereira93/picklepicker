---
phase: 12-data-pipeline-quality
plan: 03
type: execute
wave: 2
depends_on: ["12-01"]
files_modified:
  - pipeline/crawlers/mercado_livre.py
  - pipeline/db/connection.py
autonomous: true
requirements:
  - PIPE-05
  - PIPE-06
must_haves:
  truths:
    - "ML pagination stops at 1000 items to prevent OOM"
    - "Memory usage is bounded regardless of total result count"
    - "TOCTOU race in paddle upsert is eliminated with RETURNING clause"
    - "Upsert operation is atomic (no separate SELECT after INSERT)"
  artifacts:
    - path: "pipeline/crawlers/mercado_livre.py"
      provides: "Memory-bounded ML pagination with MAX_ITEMS limit"
      changes: ["MAX_ITEMS=1000 constant", "Counter before extend", "Early break condition"]
    - path: "pipeline/crawlers/mercado_livre.py"
      provides: "Atomic paddle upsert without TOCTOU race"
      changes: ["INSERT ... ON CONFLICT ... DO UPDATE SET", "Single query with RETURNING"]
  key_links:
    - from: "search_pickleball_paddles(fetch_all=True)"
      to: "MAX_ITEMS limit"
      via: "if len(all_results) >= MAX_ITEMS: break"
      pattern: "MAX_ITEMS = 1000"
    - from: "save_ml_items_to_db()"
      to: "atomic upsert query"
      via: "INSERT ... ON CONFLICT (name) DO UPDATE SET ... RETURNING id"
      pattern: "ON CONFLICT.*DO UPDATE"
---

<objective>
Fix memory exhaustion and TOCTOU race condition in Mercado Livre crawler.

Purpose: Prevent unbounded memory growth from fetch_all=True and eliminate the race condition where a row can be deleted between INSERT and SELECT. These changes make the ML crawler production-ready for large datasets.
Output: Memory-bounded pagination and atomic upsert operations.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/12-data-pipeline-quality/CONTEXT.md
@pipeline/crawlers/mercado_livre.py
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add memory limit to ML pagination</name>
  <files>pipeline/crawlers/mercado_livre.py</files>
  <behavior>
    - fetch_all=True stops after 1000 items maximum
    - Memory usage bounded regardless of total results
    - Logger warns when limit is hit
    - Existing behavior preserved for small result sets
    - Function returns partial results gracefully
  </behavior>
  <action>
    Modify `pipeline/crawlers/mercado_livre.py`:

    1. Add constant at module level:
       ```python
       MAX_ITEMS = 1000  # Prevent unbounded memory growth
       ```

    2. Update `search_pickleball_paddles()` pagination logic:
       ```python
       async def search_pickleball_paddles(
           limit: int = 50,
           offset: int = 0,
           fetch_all: bool = False,
       ) -> dict:
           """Search ML for pickleball paddles.

           If fetch_all=True, paginates through results up to MAX_ITEMS.
           Returns dict with 'results' list and 'paging' info.
           """
           all_results = []
           current_offset = offset
           items_fetched = 0

           # ... headers setup ...

           async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
               while True:
                   # ... params setup ...

                   response = await client.get(ML_SEARCH_URL, params=params)
                   response.raise_for_status()
                   data = response.json()

                   results = data.get("results", [])
                   all_results.extend(results)
                   items_fetched += len(results)

                   # Check memory limit
                   if items_fetched >= MAX_ITEMS:
                       logger.warning(
                           "Reached MAX_ITEMS limit (%d), stopping pagination. "
                           "Some results may be truncated.", MAX_ITEMS
                       )
                       break

                   if not fetch_all:
                       return data

                   # ... paging logic ...

                   if current_offset >= total or len(results) == 0:
                       break

           return {
               "results": all_results,
               "paging": {
                   "total": len(all_results),
                   "offset": 0,
                   "limit": len(all_results),
               },
           }
       ```

    3. Add warning log when limit is reached

    4. Update function docstring to document MAX_ITEMS behavior
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && python -c "
from pipeline.crawlers.mercado_livre import MAX_ITEMS, search_pickleball_paddles
assert MAX_ITEMS == 1000, f'Expected MAX_ITEMS=1000, got {MAX_ITEMS}'
print('MAX_ITEMS constant verified')
"</automated>
  </verify>
  <done>
    - MAX_ITEMS = 1000 constant defined at module level
    - Pagination loop checks items_fetched >= MAX_ITEMS
    - Warning logged when limit is reached
    - Function returns partial results gracefully
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Fix TOCTOU race with atomic upsert</name>
  <files>pipeline/crawlers/mercado_livre.py</files>
  <behavior>
    - Upsert uses single atomic query (no separate SELECT)
    - ON CONFLICT DO UPDATE pattern with RETURNING id
    - No race condition if row deleted between statements
    - Works with PostgreSQL unique constraint on name
    - Returns paddle_id reliably for all cases
  </behavior>
  <action>
    Update `pipeline/crawlers/mercado_livre.py` in `save_ml_items_to_db()`:

    1. Modify the upsert logic to use DO UPDATE:
       ```python
       # Atomic upsert: insert or update, always return id
       result = await conn.execute(
           """
           INSERT INTO paddles (name, brand, model, images)
           VALUES (%(name)s, %(brand)s, %(model)s, %(images)s)
           ON CONFLICT (name) DO UPDATE SET
               brand = EXCLUDED.brand,
               model = EXCLUDED.model,
               images = EXCLUDED.images,
               updated_at = NOW()
           RETURNING id
           """,
           {
               "name": title,
               "brand": "",  # ML search doesn't always have separate brand
               "model": title,
               "images": [item.get("thumbnail", "")],
           },
       )
       row = await result.fetchone()
       if row is None:
           logger.error("Upsert failed for paddle: %s", title)
           continue

       paddle_id = row[0]
       ```

    2. Remove the old TOCTOU-vulnerable pattern:
       - Remove the `ON CONFLICT DO NOTHING` query
       - Remove the separate `SELECT id FROM paddles WHERE name = ...`
       - Remove the error handling for "row already existed" case

    3. Ensure the paddles table has a UNIQUE constraint on name:
       - Add comment noting this requirement
       - If constraint doesn't exist, it will raise an error (good - alerts us)

    4. Add docstring explaining the upsert behavior:
       ```python
       """Save ML search items to price_snapshots.

       Uses atomic upsert for paddles (INSERT ... ON CONFLICT DO UPDATE)
       to avoid TOCTOU race conditions. Requires UNIQUE constraint on
       paddles.name.
       """
       ```
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && grep -n "ON CONFLICT.*DO UPDATE" pipeline/crawlers/mercado_livre.py</automated>
  </verify>
  <done>
    - ON CONFLICT DO UPDATE pattern implemented
    - Single query with RETURNING id (no separate SELECT)
    - TOCTOU-vulnerable code removed
    - Docstring updated with upsert behavior
  </done>
</task>

<task type="auto">
  <name>Task 3: Verify database constraint exists for upsert</name>
  <files>prisma/schema.prisma, schema.sql</files>
  <action>
    Check and document the UNIQUE constraint requirement:

    1. Read prisma/schema.prisma to check Paddle model:
       - Look for @@unique or @unique on name field

    2. If constraint is missing, document it in a migration task for future:
       - Create note: "Requires UNIQUE constraint on paddles.name"
       - Current code will fail safely if constraint absent

    3. Add defensive comment in mercado_livre.py:
       ```python
       # NOTE: Requires UNIQUE constraint on paddles.name
       # If this constraint doesn't exist, the upsert will fail
       # with a PostgreSQL error, which is safer than silent data loss
       ```

    4. Verify existing code doesn't break if constraint exists
  </action>
  <verify>
    <automated>cd /home/diego/Documentos/picklepicker && grep -n "unique" prisma/schema.prisma | grep -i paddle | head -5</automated>
  </verify>
  <done>
    - UNIQUE constraint on paddles.name verified or documented
    - Defensive comment added to code
    - Code fails safely if constraint is missing
  </done>
</task>

</tasks>

<verification>
1. **Memory Limit:**
   - `grep -n "MAX_ITEMS" pipeline/crawlers/mercado_livre.py`
   - Check pagination loop has early break condition

2. **Atomic Upsert:**
   - `grep -n "ON CONFLICT" pipeline/crawlers/mercado_livre.py`
   - Verify "DO UPDATE" not "DO NOTHING"
   - Confirm RETURNING clause present

3. **No TOCTOU:**
   - Verify no separate SELECT after INSERT
   - Check no fetchone() on conflict case (only on RETURNING)
</verification>

<success_criteria>
All must be TRUE:
- [ ] MAX_ITEMS = 1000 constant limits ML pagination
- [ ] Pagination stops when items_fetched >= MAX_ITEMS
- [ ] Warning logged when limit is reached
- [ ] Upsert uses ON CONFLICT DO UPDATE pattern
- [ ] Single query with RETURNING id (no separate SELECT)
- [ ] TOCTOU-vulnerable code completely removed
- [ ] UNIQUE constraint requirement documented
</success_criteria>

<output>
After completion, create `.planning/phases/12-data-pipeline-quality/12-03-p1-memory-and-concurrency-SUMMARY.md`
</output>
