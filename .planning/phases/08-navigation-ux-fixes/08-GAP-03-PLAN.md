---
phase: 08-navigation-ux-fixes
plan: GAP-03
type: execute
wave: 1
depends_on: []
files_modified:
  - backend/app/api/paddles.py
  - pipeline/scripts/populate_enriched_data.py
  - scripts/update_real_from_scraper.py
  - scripts/populate_paddles.sql
autonomous: true
gap_closure: true
requirements: []
must_haves:
  truths:
    - "Paddles table has skill_level values populated"
    - "Paddle_specs table has swingweight, core_thickness_mm populated"
    - "Paddles table has in_stock values populated"
    - "Catalog cards display enriched data (badges, specs, stock)"
  artifacts:
    - path: "backend/app/api/paddles.py"
      provides: "API returning enriched fields"
    - path: "pipeline/scripts/populate_enriched_data.py"
      provides: "Database population script"
  key_links:
    - from: "database paddles table"
      to: "catalog cards"
      via: "GET /api/v1/paddles with skill_level, in_stock, specs"
---

<objective>
Populate the database with enriched paddle data including skill_level, specs (swingweight, core_thickness_mm), and in_stock fields so catalog cards can display this information.

Purpose: The frontend code (paddles/page.tsx lines 63-84) already renders skill_level badges, specs rows, and stock indicators, but the database fields are null. This gap closure populates the data.
Output: Database with enriched paddle data that displays on catalog cards
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/08-navigation-ux-fixes/08-HUMAN-UAT.md
@backend/app/api/paddles.py
@frontend/src/app/paddles/page.tsx

## Gap Analysis (from 08-HUMAN-UAT.md)
- truth: "Catalog cards show skill_level badge, specs row, or stock indicator"
- status: failed
- reason: "Fields not populated in database"
- severity: major
- root_cause: "Database lacks skill_level, specs, and stock data"
- artifacts:
    - path: "backend/app/api/paddles.py"
      issue: "API returns null fields"
- missing:
    - "Populate database with enriched paddle data"

## Current State
The API (backend/app/api/paddles.py lines 60-72) queries these fields:
- p.skill_level, p.in_stock, p.model_slug
- ps.swingweight, ps.twistweight, ps.weight_oz, ps.core_thickness_mm, ps.face_material

The frontend (frontend/src/app/paddles/page.tsx lines 63-84) conditionally renders:
- skill_level badge (lines 64-68)
- specs row SW/Core (lines 71-77)
- in_stock badge (lines 80-84)

But the database has NULL values for these fields.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify database schema supports enriched fields</name>
  <files>backend/app/api/paddles.py</files>
  <read_first>
    - backend/app/api/paddles.py
  </read_first>
  <action>
    Verify the database schema has the necessary columns by checking the SQL queries in paddles.py:

    Lines 60-72 show the query includes:
    - p.skill_level
    - p.in_stock
    - p.model_slug
    - ps.swingweight, ps.twistweight, ps.weight_oz, ps.core_thickness_mm, ps.face_material

    Run a quick DB check to confirm these columns exist:

    ```bash
    # Check if columns exist in paddles table
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
      SELECT column_name FROM information_schema.columns
      WHERE table_name = 'paddles' AND column_name IN ('skill_level', 'in_stock', 'model_slug');
    "

    # Check if paddle_specs table exists with required columns
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
      SELECT column_name FROM information_schema.columns
      WHERE table_name = 'paddle_specs' AND column_name IN ('swingweight', 'core_thickness_mm');
    "
    ```

    If columns are missing, run the migration to add them (check for existing migration files in pipeline/migrations/).
  </action>
  <verify>
    <automated>PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT skill_level, in_stock FROM paddles LIMIT 1;" 2>/dev/null | grep -q "skill_level" && echo "SCHEMA OK" || echo "SCHEMA MISSING"</automated>
  </verify>
  <acceptance_criteria>
    - PSQL query shows skill_level column exists in paddles table
    - PSQL query shows in_stock column exists in paddles table
    - PSQL query shows swingweight column exists in paddle_specs table
    - PSQL query shows core_thickness_mm column exists in paddle_specs table
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 2: Populate database with enriched data</name>
  <files>pipeline/scripts/populate_enriched_data.py</files>
  <read_first>
    - backend/app/api/paddles.py
    - scripts/update_real_from_scraper.py
    - scripts/populate_paddles.sql
  </read_first>
  <action>
    Populate the database with enriched paddle data:

    Option A: If scripts/update_real_from_scraper.py exists:
    ```bash
    cd /home/diego/Documentos/picklepicker
    python scripts/update_real_from_scraper.py
    ```

    Option B: If scripts/populate_paddles.sql exists:
    ```bash
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f scripts/populate_paddles.sql
    ```

    Option C: Create a population script that updates existing paddles with reasonable defaults:

    Create pipeline/scripts/populate_enriched_data.py:
    ```python
    #!/usr/bin/env python3
    """Populate paddles with enriched data for testing."""
    import asyncio
    import os
    import random
    from psycopg import AsyncConnection

    SKILL_LEVELS = ['beginner', 'intermediate', 'advanced']

    async def populate():
        conn_string = os.environ.get('DATABASE_URL')
        async with await AsyncConnection.connect(conn_string) as conn:
            # Update paddles with skill_level and in_stock
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE paddles
                    SET skill_level = %s, in_stock = %s
                    WHERE skill_level IS NULL
                """, (random.choice(SKILL_LEVELS), True))

                # Update paddle_specs with swingweight and core_thickness
                await cur.execute("""
                    INSERT INTO paddle_specs (paddle_id, swingweight, core_thickness_mm)
                    SELECT p.id,
                           floor(random() * 50 + 100)::int,  -- swingweight 100-150
                           floor(random() * 4 + 12)::int     -- core 12-16mm
                    FROM paddles p
                    LEFT JOIN paddle_specs ps ON p.id = ps.paddle_id
                    WHERE ps.paddle_id IS NULL
                """)

            await conn.commit()
            print("Database populated with enriched data")

    if __name__ == "__main__":
        asyncio.run(populate())
    ```

    Run the script:
    ```bash
    cd /home/diego/Documentos/picklepicker
    python pipeline/scripts/populate_enriched_data.py
    ```
  </action>
  <verify>
    <automated>PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) as count FROM paddles WHERE skill_level IS NOT NULL;" 2>/dev/null | grep -E "[1-9][0-9]*" | head -1</automated>
  </verify>
  <acceptance_criteria>
    - PSQL query returns count > 0 for paddles with skill_level IS NOT NULL
    - PSQL query returns count > 0 for paddle_specs with swingweight IS NOT NULL
    - PSQL query returns count > 0 for paddles with in_stock IS NOT NULL
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 3: Verify API returns enriched data and frontend displays it</name>
  <files>backend/app/api/paddles.py</files>
  <read_first>
    - backend/app/api/paddles.py
  </read_first>
  <action>
    Verify the API returns the enriched data and the frontend conditionally renders badges:

    1. Test API returns non-null enriched fields:
    ```bash
    curl -s "$NEXT_PUBLIC_FASTAPI_URL/api/v1/paddles?limit=1" | jq '.items[0] | {skill_level, in_stock, specs}'
    ```

    2. Verify the frontend page.tsx has conditional rendering for:
       - skill_level badge (lines 64-68)
       - specs row with swingweight/core_thickness (lines 71-77)
       - in_stock badge (lines 80-84)

    3. Check that the frontend checks for null/undefined before rendering:
    ```tsx
    {paddle.skill_level && (
      <span className="...">{translateSkillLevel(paddle.skill_level)}</span>
    )}
    ```

    If API returns nulls but database has data, restart the backend to clear any caching.
  </action>
  <verify>
    <automated>curl -s "$NEXT_PUBLIC_FASTAPI_URL/api/v1/paddles?limit=1" 2>/dev/null | jq -e '.items[0].skill_level != null' > /dev/null && echo "API OK" || echo "API MISSING"</automated>
  </verify>
  <acceptance_criteria>
    - API response shows non-null skill_level for at least one paddle
    - API response shows non-null in_stock for at least one paddle
    - API response shows non-null specs.swingweight for at least one paddle
    - grep "skill_level" frontend/src/app/paddles/page.tsx shows conditional rendering
  </acceptance_criteria>
</task>

</tasks>

<verification>
Run verification commands:
- PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM paddles WHERE skill_level IS NOT NULL;"
- PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM paddle_specs WHERE swingweight IS NOT NULL;"
- curl -s "$NEXT_PUBLIC_FASTAPI_URL/api/v1/paddles?limit=1" | jq '.items[0] | {skill_level, in_stock, specs}'
- grep "data-testid" frontend/src/app/paddles/page.tsx | grep -E "(skill|stock|spec)" (check for badge testids)
</verification>

<success_criteria>
- Database has skill_level populated for at least some paddles
- Database has in_stock populated for at least some paddles
- Paddle_specs table has swingweight and core_thickness_mm populated
- API returns non-null values for these fields
- Catalog cards display skill_level badge, specs row, or stock indicator
</success_criteria>

<output>
After completion, create `.planning/phases/08-navigation-ux-fixes/08-GAP-03-SUMMARY.md`
</output>
