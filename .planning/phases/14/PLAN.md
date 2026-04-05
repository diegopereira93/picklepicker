# Phase 14: Launch Readiness & Bug Fixes

**Status:** Ready for execution
**Milestone:** v1.4
**Dependencies:** None (bug-fix phase, no upstream phases)
**Created:** 2026-04-04
**Updated:** 2026-04-04 — v1.1: Real image pipeline (no fabricated images)

## Goal

Eliminate all console errors and broken flows across catalog, detail, and chat pages so the app is launch-ready. **All product images must be real photos from retailers — no fabricated/placeholder images.**

## Image Policy (NON-NEGOTIABLE)

| Source | Allowed? | Reason |
|--------|----------|--------|
| Real scraped images from retailers (mitiendanube.com, mlstatic.com, etc.) | ✅ YES | Actual product photos |
| NULL / "Foto" fallback | ✅ YES (last resort) | Honest "no image available" state |
| placehold.co | ❌ NEVER | Fabricated generated images |
| Unsplash stock photos | ❌ NEVER | Generic sports photos, not the actual product |
| Any other non-product URL | ❌ NEVER | Deceptive to users |

**Priority order:** Real scraped image → NULL ( Foto fallback ). Never invent an image.

## Requirements Coverage

| Requirement | Tasks | Notes |
|-------------|-------|-------|
| IMG-01 | 14.2a, 14.2b, 14.4 | Schema sync + real image migration + onError safety net |
| IMG-02 | 14.2a, 14.2b, 14.5 | Same pipeline + detail page onError |
| IMG-03 | 14.2b, 14.2c | Migration extracts real images; seed data uses NULL |
| IMG-04 | 14.7 | Already correct (no change needed) |
| RTE-01 | 14.1 | Backend model_slug filter |
| RTE-02 | 14.3 | Frontend slug match verification |
| RTE-03 | 14.1, 14.3 | Combined backend+frontend fix |
| CHT-01 | 14.6 | Budget, message, style edge cases |
| CHT-02 | 14.6 | End-to-end validation |
| CHT-03 | 14.6 | Error surfacing |
| QA-01 | 14.10 | Full test suite run |
| QA-02 | 14.8, 14.9 | New regression tests |
| QA-03 | 14.10 | Manual smoke test |

## Execution Waves

```
Wave 1 (parallel) ──── 14.1  Backend model_slug filter
                    ──── 14.2a Schema sync (add missing columns to schema.sql)

Wave 2 (sequential, after Wave 1) ──── 14.2b Image migration script (source_raw → paddles.image_url)
                                    ──── 14.2c Seed data cleanup (remove all fabricated URLs)

Wave 3 (parallel, after Wave 2) ──── 14.3 Frontend slug match verification
                                ──── 14.4 Catalog image onError (safety net)
                                ──── 14.5 Detail image onError (safety net)
                                ──── 14.6 Chat proxy edge cases
                                ──── 14.7 Product card (verify — no change)

Wave 4 (after Wave 3) ──── 14.8 Backend regression tests
                        ──── 14.9 Frontend regression tests
                        ──── 14.10 Full verification
```

---

## Task Details

### Task 14.1 — Add `model_slug` filter to backend paddles API

**Category:** `deep`
**Skills:** `[]`
**Files:** `backend/app/api/paddles.py`
**Dependencies:** None
**Requirements:** RTE-01, RTE-03

**Changes:**

1. Add `model_slug` parameter to `list_paddles` function signature (after line 25, alongside existing `brand` param):

```python
model_slug: Optional[str] = Query(None, description="Filter by model slug"),
```

2. Add WHERE clause filter (after the brand filter block, ~line 39). Follow the exact same pattern as brand:

```python
if model_slug:
    where_clauses.append("model_slug = %s")
    params.append(model_slug)
```

3. That's it. The SELECT query on lines 61-70 already includes `p.model_slug`. No other changes needed.

**QA Verification:**
- `curl "http://localhost:8000/api/v1/paddles?brand=selkirk&model_slug=vanguard-power-air"` → 200, 1 item
- `curl "http://localhost:8000/api/v1/paddles?brand=selkirk"` → 200, all Selkirk items

**Success Criteria:** Backend returns filtered results when `model_slug` provided, returns all brand paddles when omitted.

---

### Task 14.2a — Sync schema.sql with production reality

**Category:** `deep`
**Skills:** `[]`
**Files:** `pipeline/db/schema.sql`, `pipeline/db/schema-updates.sql`
**Dependencies:** None
**Requirements:** IMG-01, IMG-02, RTE-01 (schema must be correct for all tasks)

**Context — schema.sql is severely stale:**
The `pipeline/db/schema.sql` `paddles` table is missing columns that the production DB and all API code rely on. The app works in production because these columns were added via manual ALTER TABLE or another untracked mechanism.

**Production DB has these columns (confirmed by API code + seed data):**

| Column | Type | Referenced by |
|--------|------|---------------|
| `image_url` | `TEXT` | `paddles.py` line 62, `schemas.py` line 26, `populate_paddles.sql` |
| `model_slug` | `TEXT` | `paddles.py` line 63, `schemas.py` line 30, `populate_paddles.sql` |
| `skill_level` | `TEXT` | `paddles.py` line 63, `schemas.py` line 31, `populate_paddles.sql` |
| `in_stock` | `BOOLEAN` | `paddles.py` line 63, `schemas.py` line 32, `populate_paddles.sql` |
| `price_min_brl` | `NUMERIC(10,2)` | `paddles.py` line 62, `schemas.py` line 28, `populate_paddles.sql` |

**Schema.sql currently has:**
```sql
CREATE TABLE paddles (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    brand           TEXT NOT NULL,
    model           TEXT NOT NULL,
    manufacturer_sku TEXT,
    images          TEXT[],          -- ← API never queries this
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_paddle_name UNIQUE (name)
);
```

**Changes to `pipeline/db/schema.sql`:**

Replace the `paddles` CREATE TABLE with:

```sql
CREATE TABLE paddles (
    id                BIGSERIAL PRIMARY KEY,
    name              TEXT NOT NULL,
    brand             TEXT NOT NULL,
    model             TEXT NOT NULL,
    manufacturer_sku  TEXT,
    image_url         TEXT,                          -- real product image URL (single)
    images            TEXT[],                         -- legacy: ML thumbnail array (kept for compat)
    model_slug        TEXT,                           -- URL-safe slug for routing
    skill_level       TEXT,                           -- beginner | intermediate | advanced
    in_stock          BOOLEAN DEFAULT true,
    price_min_brl     NUMERIC(10,2),
    needs_reembed     BOOLEAN DEFAULT false,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_paddle_name UNIQUE (name)
);
```

**Changes to `pipeline/db/schema-updates.sql`:**

Add a comment block at the top explaining these were applied separately. Remove the `ALTER TABLE paddles ADD COLUMN needs_reembed` line since it's now in the base schema.

**IMPORTANT:** Do NOT run this schema on production — it's a documentation sync only. The production DB already has these columns.

**QA Verification:**
- `grep -c "image_url" pipeline/db/schema.sql` → 1+
- `grep -c "model_slug" pipeline/db/schema.sql` → 1+
- `grep -c "skill_level" pipeline/db/schema.sql` → 1+
- `grep -c "in_stock" pipeline/db/schema.sql` → 2+ (CREATE TABLE + price_snapshots)
- `grep -c "price_min_brl" pipeline/db/schema.sql` → 1+
- Verify `images TEXT[]` is still present (kept for Mercado Livre compat)

**Success Criteria:** `schema.sql` accurately reflects the production DB schema. All columns referenced by the API are defined.

---

### Task 14.2b — Image migration: extract real images from source_raw

**Category:** `deep`
**Skills:** `[]`
**Files:** NEW `scripts/migrate_real_images.py` (rewrite of existing `scripts/extract_real_images.py`)
**Dependencies:** 14.2a (schema must be accurate)
**Requirements:** IMG-01, IMG-02, IMG-03

**Context — where real images actually live:**

| Retailer | Image Source | Storage Location | Reaches API? |
|----------|-------------|-----------------|-------------|
| **Brazil Store** | Phase 2 scrapes `mitiendanube.com` CDN | `price_snapshots.source_raw` JSONB | ❌ No — stuck in JSONB |
| **Mercado Livre** | `item.thumbnail` from ML API | `paddles.images` TEXT[] | ❌ No — API queries `image_url`, not `images` |
| **Dropshot** | Firecrawl extraction | `price_snapshots.source_raw` JSONB | ❌ No — stuck in JSONB |

**Additionally**, `extract_real_images.py` exists but has bugs:
- Line 52: Uses `$1`/`$2` parameter syntax (asyncpg) but `pipeline/db/connection.py` uses psycopg `%s` syntax
- Line 86: Filters `p.image_url LIKE '%example%'` — wrong placeholder pattern
- Only processes 10 items (LIMIT 10)
- Requires Firecrawl API key (re-scrapes pages) instead of using already-scraped `source_raw` data

**New script: `scripts/migrate_real_images.py`**

This script should:
1. Query `price_snapshots.source_raw` for existing image URLs (no re-scraping needed)
2. Match to `paddles` by name (since `paddle_id` is NULL for Brazil Store/Dropshot)
3. Update `paddles.image_url` with the real URL
4. Handle Mercado Livre: copy `paddles.images[1]` → `paddles.image_url` for ML-sourced paddles
5. Set `image_url = NULL` for paddles with no real image found
6. Report statistics: how many real images found, how many set to NULL

**Script logic (pseudocode):**

```python
"""
Migrate real product images from source_raw → paddles.image_url.

Priority order:
1. Brazil Store / Dropshot: extract from price_snapshots.source_raw JSONB
2. Mercado Livre: copy from paddles.images[1] (ML thumbnail)
3. No real image found → set image_url = NULL (triggers "Foto" fallback)

Usage:
  python scripts/migrate_real_images.py
  # or with DB URL:
  DATABASE_URL=postgresql://... python scripts/migrate_real_images.py
"""

# Step 1: Extract from source_raw (Brazil Store, Dropshot)
# SELECT source_raw->>'image_url' as image_url,
#        source_raw->>'name' as product_name
# FROM price_snapshots
# WHERE source_raw->>'image_url' IS NOT NULL
#   AND source_raw->>'image_url' NOT LIKE '%placehold.co%'
#   AND source_raw->>'image_url' NOT LIKE '%unsplash%'

# Step 2: Match to paddles by name (case-insensitive substring match)
# UPDATE paddles SET image_url = $real_url
# WHERE LOWER(name) LIKE '%' || LOWER($product_name) || '%'
#   AND (image_url IS NULL OR image_url LIKE '%placehold.co%' OR image_url LIKE '%unsplash%')

# Step 3: Handle Mercado Livre — copy images[1] to image_url
# UPDATE paddles SET image_url = images[1]
# WHERE images IS NOT NULL AND array_length(images, 1) > 0
#   AND (image_url IS NULL OR image_url LIKE '%placehold.co%' OR image_url LIKE '%unsplash%')

# Step 4: Clean remaining fabricated URLs
# UPDATE paddles SET image_url = NULL
# WHERE image_url LIKE '%placehold.co%' OR image_url LIKE '%unsplash%' OR image_url LIKE '%example%'

# Step 5: Report
# SELECT COUNT(*) as total_paddles FROM paddles;
# SELECT COUNT(*) as has_real_image FROM paddles WHERE image_url IS NOT NULL;
# SELECT COUNT(*) as null_image FROM paddles WHERE image_url IS NULL;
```

**IMPORTANT — URL validation:**
Only accept URLs from trusted retailer domains:
- `mitiendanube.com` (Brazil Store CDN)
- `mlstatic.com` (Mercado Livre CDN)
- `mercadolivre.com.br` (Mercado Livre)
- `dropshotbrasil.com.br` (Dropshot)
- Any `https://` URL from a known retailer

Reject:
- `placehold.co` — fabricated
- `unsplash.com` — generic stock
- `example.com` — placeholder
- Any URL with `?text=` query param (generated image indicator)

**QA Verification:**
- Run: `python scripts/migrate_real_images.py`
- Expected output: "Updated X paddles with real images, Y paddles set to NULL"
- Verify: `SELECT image_url FROM paddles WHERE image_url IS NOT NULL LIMIT 5;` — all real retailer URLs
- Verify: `SELECT COUNT(*) FROM paddles WHERE image_url LIKE '%placehold.co%';` → 0
- Verify: `SELECT COUNT(*) FROM paddles WHERE image_url LIKE '%unsplash%';` → 0

**Success Criteria:** All paddles have either a real retailer image URL or NULL. Zero fabricated URLs remain.

---

### Task 14.2c — Clean seed data (remove all fabricated URLs)

**Category:** `quick`
**Skills:** `[]`
**Files:** `scripts/populate_paddles.sql`
**Dependencies:** 14.2b (migration runs first to populate real images)
**Requirements:** IMG-03

**Changes to `scripts/populate_paddles.sql`:**

1. Replace ALL `placehold.co` URLs with NULL in the INSERT VALUES:

```sql
-- BEFORE:
'https://placehold.co/600x400/1e3a8a/white?text=Selkirk+Vanguard'
-- AFTER:
NULL
```

2. Add a header comment explaining the image strategy:

```sql
-- Populate paddles table with realistic data.
-- Images: Run scripts/migrate_real_images.py after seeding to populate image_url
--   with real product photos from retailers. Paddles without real images will
--   have image_url = NULL, triggering the "Foto" placeholder in the UI.
--
-- NEVER use placehold.co, unsplash.com, or any non-product image URL.
```

3. The UPDATE block (lines 5-14) references `image_url LIKE '%example.com%'` — this is fine as a legacy cleanup, but also add `OR image_url LIKE '%placehold.co%'`:

```sql
WHERE image_url LIKE '%example.com%' OR image_url LIKE '%placehold.co%' OR image_url IS NULL;
```

And change all the THEN values to NULL:

```sql
SET image_url = CASE
    WHEN name LIKE '%Selkirk%' THEN NULL
    WHEN name LIKE '%JOOLA%' THEN NULL
    ...
    ELSE NULL
END
```

4. Apply NULL to ALL 24 INSERT VALUES entries.

**QA Verification:**
- `grep -c "placehold.co" scripts/populate_paddles.sql` → 0
- `grep -c "unsplash" scripts/populate_paddles.sql` → 0
- `grep -c "NULL" scripts/populate_paddles.sql` → 24+ (one per INSERT row)

**Success Criteria:** Seed data contains zero fabricated image URLs. All image_url values are NULL.

---

### Task 14.3 — Verify slug match in `fetchProductData`

**Category:** `deep`
**Skills:** `[]`
**Files:** `frontend/src/lib/seo.ts`
**Dependencies:** 14.1 (backend must filter by model_slug first)
**Requirements:** RTE-02, RTE-03

**Current behavior (lines 7-29):**
```typescript
const paddle = data.data?.[0] ?? data.paddles?.[0] ?? data.items?.[0] ?? null
```
Takes first item regardless of slug match. If backend returns wrong first item, page 404s.

**Changes:**

After line 14 (the fallback chain), add slug verification. Replace the simple fallback with a slug-aware lookup:

```typescript
// Find items from response (handles different response shapes)
const items = data.data ?? data.paddles ?? data.items ?? []

// Find the item matching both brand and model_slug
const paddle = items.find(
  (item: Record<string, unknown>) =>
    item.model_slug === modelSlug || item.name?.toString().toLowerCase().replace(/\s+/g, '-') === modelSlug
) ?? null
```

Keep the existing numeric ID fallback (lines 16-22) unchanged — it's a valid secondary path.

**QA Verification:**
- Verify the function checks `model_slug` match instead of blindly taking `[0]`
- Ensure the numeric ID fallback still works for `/^\d+$/` slugs

**Success Criteria:** `fetchProductData('selkirk', 'vanguard-power-air')` returns the paddle with `model_slug === 'vanguard-power-air'`, not whatever `items[0]` happens to be.

---

### Task 14.4 — Add image onError safety net to catalog page

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/app/paddles/page.tsx`
**Dependencies:** 14.2b (real images should be populated, but onError catches any future broken URLs)
**Requirements:** IMG-01, IMG-02

**Context — this is a SAFETY NET, not the primary image strategy.**
Task 14.2b populates real images. This task handles the edge case where a real retailer URL becomes broken (product delisted, CDN changes, etc.).

**Changes:**

Create a `SafeImage` component (inline or extracted to `frontend/src/components/ui/safe-image.tsx`). The pattern:

```tsx
function SafeImage({ src, alt, fallbackClassName, ...props }: {
  src: string | null | undefined
  alt: string
  fallbackClassName?: string
} & Omit<React.ComponentProps<typeof Image>, 'src'>) {
  const [errored, setErrored] = React.useState(false)

  if (!src || errored) {
    return (
      <div
        className={fallbackClassName ?? "w-full h-48 bg-muted/50 rounded-lg flex items-center justify-center text-muted-foreground text-xs mb-3"}
        aria-label={`${alt} — imagem indisponível`}
      >
        Foto
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      className={props.className}
      onError={() => setErrored(true)}
    />
  )
}
```

**NOTE:** Using native `<img>` instead of Next.js `<Image>` because:
1. `<Image>` doesn't reliably bubble `onError` events
2. Real retailer images come from varied CDNs — Next.js image optimization may fail on some
3. Native `<img>` with `loading="lazy"` provides adequate performance for catalog grids

Then replace the existing conditional render (lines 59-72) with:
```tsx
<SafeImage
  src={paddle.image_url}
  alt={`${paddle.brand} ${paddle.name} paddle`}
  className="w-full h-48 object-contain mb-3 hy-product-image"
/>
```

**If extracting to shared component** (`frontend/src/components/ui/safe-image.tsx`):
Both 14.4 and 14.5 should import from the same file to avoid duplication.

**QA Verification:**
- Render with a real `image_url` → image loads normally
- Render with `image_url = null` → "Foto" fallback immediately
- Render with a broken `image_url` → "Foto" fallback after load failure, no console error
- `grep -c "placehold.co" frontend/src/app/paddles/page.tsx` → 0

**Success Criteria:** No "not a valid image" console errors. Broken URLs gracefully fall back to "Foto" placeholder. Real images display normally.

---

### Task 14.5 — Add image onError safety net to detail page

**Category:** `visual-engineering`
**Skills:** `['frontend-ui-ux']`
**Files:** `frontend/src/app/paddles/[brand]/[model-slug]/page.tsx`
**Dependencies:** 14.2b (real images populated)
**Requirements:** IMG-02

**Changes:**

Same `SafeImage` pattern as Task 14.4 but for the detail page hero image (lines 54-68). Import the shared component if extracted in 14.4.

Detail page specifics:
- Fallback div: `w-full max-w-md mx-auto mb-6 h-[300px] bg-muted/50 rounded-lg flex items-center justify-center text-muted-foreground text-sm`
- Pass `fallbackClassName` prop to override default sizing

**QA Verification:**
- Navigate to `/paddles/selkirk/vanguard-power-air` with real image → image loads
- Navigate with `image_url = null` → "Foto" fallback, no console error
- Navigate with broken URL → "Foto" fallback, no console error

**Success Criteria:** Detail page never shows a broken image. Real images display. Graceful fallback for all error states.

---

### Task 14.6 — Fix chat proxy edge cases

**Category:** `deep`
**Skills:** `[]`
**Files:** `frontend/src/app/api/chat/route.ts`
**Dependencies:** None
**Requirements:** CHT-01, CHT-02, CHT-03

**Root causes:**

1. **`budget_max = 0` bypasses `?? 600`** (line ~39): `0 ?? 600` returns `0`, but FastAPI validator rejects `budget_brl <= 0`
2. **Empty message content** (line ~37): `lastUserMessage.content` can be empty string, FastAPI rejects empty messages
3. **Error responses not surfaced** (lines ~45-50): Non-200 responses from FastAPI are forwarded as-is without user-friendly error message

**Changes to `frontend/src/app/api/chat/route.ts`:**

1. **Fix budget (line ~39):** Replace:
```typescript
budget_brl: profile?.budget_max ?? 600,
```
With:
```typescript
budget_brl: Math.max(profile?.budget_max ?? 600, 1),
```
This ensures: `undefined → 600`, `null → 600`, `0 → 1`, `500 → 500`, `-10 → 1`.

2. **Fix empty message (after line ~27, before payload construction):** Add validation:
```typescript
const messageContent = lastUserMessage.content?.trim() ?? ''
if (!messageContent) {
  return new Response(JSON.stringify({ error: 'Mensagem vazia — por favor, descreva o que procura.' }), {
    status: 400,
    headers: { 'Content-Type': 'application/json' },
  })
}
```

3. **Fix error surfacing (after line ~50, after FastAPI fetch):** Add response status check:
```typescript
if (!fastapiResponse.ok) {
  const errorBody = await fastapiResponse.text().catch(() => '')
  console.error(`[chat proxy] Backend error ${fastapiResponse.status}:`, errorBody)
  return new Response(
    JSON.stringify({ error: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.' }),
    { status: fastapiResponse.status, headers: { 'Content-Type': 'application/json' } }
  )
}
```

4. **Style field:** `style: profile?.style` is already safe — backend `Optional[str]` accepts None. But ensure we send `null` instead of `undefined`:
```typescript
style: profile?.style ?? null,
```

**QA Verification:**
- `budget_max: 0` → `budget_brl: 1` (no 422)
- Empty message → 400 with PT-BR error message
- Whitespace-only message → 400 with PT-BR error message
- Valid data → 200 streaming response
- Backend unreachable → 503 with PT-BR error message

**Success Criteria:** Zero 422 errors from valid quiz flow. All edge cases handled with PT-BR error messages.

---

### Task 14.7 — Verify product card (no change)

**Category:** `quick`
**Skills:** `[]`
**Files:** `frontend/src/components/chat/product-card.tsx`
**Dependencies:** None
**Requirements:** IMG-04

**Action:** Read the file and confirm it already uses a hardcoded "Foto" placeholder div (lines 62-69). No external image URL is loaded. IMG-04 is already satisfied.

**Verification:** `grep -c "image_url\|<img\|<Image" frontend/src/components/chat/product-card.tsx` — Expected: 0

**Success Criteria:** Product card renders "Foto" placeholder. No change needed.

---

### Task 14.8 — Backend regression tests

**Category:** `deep`
**Skills:** `[]`
**Files:** `backend/tests/test_paddles_endpoints.py` (extend)
**Dependencies:** 14.1, 14.2a
**Requirements:** QA-02

**Test cases to add** (follow existing `test_paddles_endpoints.py` pattern with `TestClient(app)`):

1. **`test_list_paddles_with_model_slug_filter`**: `client.get("/api/v1/paddles?brand=selkirk&model_slug=vanguard-power-air")` → 200, items contain matching paddle
2. **`test_list_paddles_without_model_slug`**: `client.get("/api/v1/paddles?brand=selkirk")` → 200, returns all Selkirk paddles
3. **`test_list_paddles_model_slug_and_brand_combined`**: Both filters together → correct single paddle
4. **`test_list_paddles_model_slug_not_found`**: Non-existent slug → 200 with empty items (not 404)

**QA Verification:**
- `cd backend && python -m pytest tests/test_paddles_endpoints.py -v` → all pass

**Success Criteria:** 4+ new test cases covering model_slug filter. All tests green.

---

### Task 14.9 — Frontend regression tests

**Category:** `deep`
**Skills:** `[]`
**Files:** `frontend/src/tests/unit/product-metadata.test.ts` (extend), `frontend/src/tests/unit/route-handler-proxy.test.ts` (extend)
**Dependencies:** 14.3, 14.6
**Requirements:** QA-02

**Test cases for `fetchProductData` (in `product-metadata.test.ts`):**

1. **`returns correct paddle when multiple brand paddles exist`**: Mock returns `{paddles: [paddleA, paddleB]}` where only `paddleB` matches `modelSlug`. Verify `paddleB` returned.
2. **`returns null when no slug match found`**: Mock returns `{paddles: [paddleA]}` where neither matches. Verify `null`.
3. **`falls back to numeric ID lookup when slug is numeric`**: First fetch empty, second fetch by ID returns paddle. Verify paddle returned.

**Test cases for chat proxy (in `route-handler-proxy.test.ts`):**

4. **`handles budget_max=0 gracefully`**: Request with `profile.budget_max = 0`. Capture payload. Verify `budget_brl >= 1`.
5. **`rejects empty message with 400`**: Request with `messages: [{role: 'user', content: ''}]`. Verify 400.
6. **`rejects whitespace-only message with 400`**: Request with `messages: [{role: 'user', content: '   '}]`. Verify 400.
7. **`surfaces backend error with PT-BR message`**: Mock fetch returns 422. Verify proxy returns JSON error with PT-BR message.

**QA Verification:**
- `cd frontend && npx vitest run src/tests/unit/product-metadata.test.ts src/tests/unit/route-handler-proxy.test.ts` → all pass

**Success Criteria:** 7+ new test cases. All tests green.

---

### Task 14.10 — Full verification

**Category:** `deep`
**Skills:** `['qa']`
**Files:** All modified files
**Dependencies:** 14.1–14.9
**Requirements:** QA-01, QA-03

**Steps:**

1. **Backend tests:** `cd backend && python -m pytest tests/ -v` → all pass (167+ existing + new)
2. **Frontend tests:** `cd frontend && npx vitest run` → all pass (152+ existing + new)
3. **`make test`** → exit code 0
4. **LSP diagnostics** on all modified files → zero errors
5. **Image integrity check:**
   ```bash
   # Verify zero fabricated URLs in DB (if running against real DB)
   # SELECT COUNT(*) FROM paddles WHERE image_url LIKE '%placehold.co%' OR image_url LIKE '%unsplash%';
   # Expected: 0
   ```
6. **Manual smoke test** (if dev environment available):
   - Browse `/paddles` → real product images or "Foto" fallback, zero console errors
   - Click paddle → detail page loads (200), real image or "Foto", no broken images
   - Complete quiz → chat responds (200), no 422

**Success Criteria:** All checks pass. Zero regressions. Zero fabricated images in the application.

---

## Follow-up (NOT in scope for Phase 14)

These are important but not launch-blocking:

1. **Fix Brazil Store crawler** to populate `paddles.image_url` during normal scrape runs (currently only saves to `source_raw` JSONB)
2. **Fix Dropshot crawler** same as above
3. **Fix Mercado Livre crawler** to also populate `paddles.image_url` (currently only populates `paddles.images` TEXT[])
4. **Automate image migration** in the scrape GitHub Action workflow (run `migrate_real_images.py` after each crawl)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `source_raw` has no image data (crawlers never run) | Medium | Medium | Seed data uses NULL → "Foto" fallback. Migration script reports stats. Run crawlers to populate. |
| Name matching in migration is imprecise | Medium | Low | Use case-insensitive substring match with brand filter. Manual review of unmatched paddles. |
| `<img>` onError doesn't fire on some CDNs | Low | Low | "Foto" fallback for NULL covers this. Real CDN URLs from trusted domains should work. |
| Schema.sql changes break fresh DB setup | Low | High | Schema.sql is documentation — fresh DB uses docker-entrypoint-initdb.d which applies schema + updates. Test with `make db-clean && make db-up`. |
| `fetchProductData` slug match breaks existing routes | Low | Medium | Fix makes matching MORE precise. Existing valid routes still match. |
| Chat proxy change breaks quiz flow | Low | Medium | Fix is additive — adds validation BEFORE sending. Quiz sends valid data already. |

## Verification Checklist

- [ ] 14.1: `curl "/api/v1/paddles?brand=selkirk&model_slug=vanguard-power-air"` returns 1 matching paddle
- [ ] 14.1: `curl "/api/v1/paddles?brand=selkirk"` returns all Selkirk paddles
- [ ] 14.2a: `schema.sql` defines `image_url TEXT`, `model_slug TEXT`, `skill_level TEXT`, `in_stock BOOLEAN`, `price_min_brl NUMERIC(10,2)`
- [ ] 14.2b: `migrate_real_images.py` runs successfully, reports X real images found, Y set to NULL
- [ ] 14.2b: Zero `placehold.co`, `unsplash`, or `example.com` URLs in DB after migration
- [ ] 14.2c: `grep -c "placehold.co" scripts/populate_paddles.sql` → 0
- [ ] 14.2c: `grep -c "unsplash" scripts/populate_paddles.sql` → 0
- [ ] 14.3: `fetchProductData` finds correct paddle by slug, not first item
- [ ] 14.4: Real image displays, broken URL → "Foto" fallback, no console error
- [ ] 14.5: Same as 14.4 for detail page
- [ ] 14.6: `budget_max=0` → `budget_brl=1` (no 422)
- [ ] 14.6: Empty message → 400 with PT-BR error
- [ ] 14.7: Product card shows "Foto" (no change needed)
- [ ] 14.8: Backend regression tests pass
- [ ] 14.9: Frontend regression tests pass
- [ ] 14.10: `make test` passes with zero regressions
- [ ] 14.10: LSP diagnostics clean on all modified files
- [ ] 14.10: Manual smoke: catalog → detail → quiz → chat with zero errors
- [ ] 14.10: **ZERO fabricated images anywhere in the application**

---
*Plan created: 2026-04-04*
*Plan v1.1 — 2026-04-04: Real image pipeline (no fabricated images)*
