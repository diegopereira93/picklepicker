# Scraping Pipeline Research: PickleIQ Price Intelligence

**Domain:** Web scraping for e-commerce price monitoring using Firecrawl API
**Researched:** 2026-03-26
**Overall Confidence:** MEDIUM (based on training data through August 2025; Firecrawl is a fast-moving project — verify version-specific details against current docs at https://docs.firecrawl.dev)

---

## 1. Firecrawl API Capabilities for E-Commerce Product Scraping

### Core Capabilities (HIGH confidence)

Firecrawl provides three primary endpoints relevant to price monitoring:

**`/scrape` — Single-page extraction**
The workhorse for product page scraping. Key parameters:
- `url`: target URL
- `formats`: `["markdown", "html", "rawHtml", "json"]` — use `json` with a schema for structured output
- `actions`: list of browser actions (click, scroll, wait) executed before extraction — critical for JS-rendered prices
- `waitFor`: milliseconds to wait for dynamic content to load (e.g., price elements that appear after API calls)
- `headers`: pass custom headers (User-Agent, Accept-Language, etc.)
- `includeTags` / `excludeTags`: CSS selector filtering to reduce noise

**`/extract` — LLM-powered structured extraction**
The highest-value endpoint for price intelligence:
```json
{
  "urls": ["https://pickleballcentral.com/product/selkirk-vanguard-power-air"],
  "prompt": "Extract product name, brand, current price, original price, discount percentage, availability status, SKU, and all specifications",
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "brand": {"type": "string"},
      "sku": {"type": "string"},
      "price_current": {"type": "number"},
      "price_original": {"type": "number"},
      "in_stock": {"type": "boolean"},
      "specs": {"type": "object"}
    }
  }
}
```
This endpoint uses an LLM to interpret page structure, making it resilient to site redesigns. It handles variant pricing (different paddle weights/grips having different prices) better than CSS selectors.

**`/crawl` — Multi-page category scraping**
For scraping entire category pages (e.g., all paddles on PickleballCentral):
- `limit`: max pages to crawl
- `includePaths` / `excludePaths`: regex patterns to constrain crawl scope
- `scrapeOptions`: applies scrape config to each discovered page
- Returns a job ID; poll `/crawl/{id}` for results (async by design)

**`/map` — URL discovery**
Generates a sitemap of all URLs matching a pattern. Use this to pre-build your URL list before scheduling scrape jobs.

### What Firecrawl Handles Well (MEDIUM confidence)
- JavaScript-rendered prices (it uses a headless browser, Playwright-based)
- Lazy-loaded content with `waitFor` + `actions` (scroll-to-load patterns)
- Authentication flows via `actions` (click, type, wait sequences)
- Markdown output strips nav/footer clutter — cleaner than raw HTML for LLM extraction

### What Firecrawl Does NOT Handle (MEDIUM confidence)
- CAPTCHA solving is not guaranteed — Firecrawl rotates proxies and fingerprints, but hard CAPTCHAs still fail
- Real-time streaming of prices — batch/async only
- Session persistence across requests (each scrape is stateless unless you pass cookies manually)

**Gotcha:** The `/extract` endpoint counts against a separate credit pool from `/scrape`. Budget accordingly for 24h batch jobs across 4 retailers.

---

## 2. Anti-Bot Measures on Sports Retail Sites

### Threat Landscape by Retailer (MEDIUM confidence, based on known retailer tech stacks)

| Retailer | Likely Protection | Severity |
|----------|------------------|----------|
| PickleballCentral | Cloudflare (CDN + Bot Management) | Medium |
| Fromuth Pickleball | Basic rate limiting, possibly Cloudflare | Low-Medium |
| JustPaddles | Cloudflare or similar CDN | Medium |
| Amazon | AWS WAF + bot fingerprinting + CAPTCHA | Very High |

### How Firecrawl Addresses These (MEDIUM confidence)

**Proxy rotation:** Firecrawl's managed service routes through residential proxy pools by default. This defeats IP-based rate limiting and basic geo-blocks.

**Browser fingerprinting evasion:** The headless browser is configured with realistic User-Agent strings, WebGL fingerprints, and viewport sizes. This bypasses most Cloudflare JS challenges (5-second shield).

**Cloudflare Turnstile / hCAPTCHA:** Firecrawl does NOT reliably solve interactive CAPTCHAs. If a retailer requires CAPTCHA completion, expect failures. Mitigation: scrape during off-peak hours (3–6 AM local time) when challenge rates are lower.

**Rate limiting — your responsibility:** Firecrawl provides the request infrastructure, but you control request cadence. For a 24h pipeline:
- PickleballCentral: safe at 1 req/3–5 seconds per domain
- Amazon: DO NOT scrape Amazon product pages directly — use Amazon Product Advertising API or a dedicated Amazon scraping service (Rainforest API, DataForSEO). Amazon's bot detection is class-leading and blocks even residential proxies aggressively.

**Recommended approach for Amazon:** Use the Amazon Product Advertising API (PA-API 5.0) for pricing data. It's rate-limited but legal and reliable. Requires affiliate account.

### Anti-Bot Gotchas
- **Dynamic price injection:** Some retailers (JustPaddles pattern) load prices via XHR after page load. Use `waitFor: 3000` + `actions: [{"type": "wait", "milliseconds": 2000}]` to ensure price DOM is populated before extraction.
- **Session-based pricing:** Some sites show different prices based on login state or cookies. Firecrawl's stateless nature means you always get guest pricing — document this in your data model.
- **Honeypot links:** Some crawl-protection systems inject invisible links. Using `/crawl` without `includePaths` filtering can burn credits on trap URLs.

---

## 3. Scheduling Strategy for 24h Batch Scraping Jobs

### Recommendation: Prefect (MEDIUM-HIGH confidence)

For a price intelligence platform at PickleIQ's likely scale (hundreds to low thousands of SKUs, 4 retailers, daily cadence), **Prefect Cloud** or self-hosted Prefect is the right choice over Airflow.

**Why Prefect over Airflow:**
- Airflow's DAG model requires DAGs to be defined statically at deploy time — dynamic URL lists (adding new paddles) require DAG reloads or complex dynamic DAG patterns
- Prefect supports dynamic mapping natively: `.map()` over a URL list at runtime
- Prefect's deployment model (work pools + workers) fits a simple 24h job better than Airflow's heavyweight scheduler
- Prefect has native retry logic with exponential backoff — essential for flaky scraping
- Airflow is correct if you're already running it for other workloads (avoid two orchestrators)

**Why not cron:**
Simple cron + a Python script works for a proof of concept but breaks down when you need: retry logic per-URL, observability on which URLs failed, parallelism control, and alerting. Graduate past cron before production.

### Recommended Prefect Flow Structure

```python
@task(retries=3, retry_delay_seconds=exponential(60, max_delay=600))
def scrape_product(url: str, retailer: str) -> dict:
    # call Firecrawl /extract
    pass

@task
def fetch_active_skus() -> list[dict]:
    # query postgres for URLs needing refresh
    pass

@flow(name="price-refresh-24h")
def price_refresh_flow():
    skus = fetch_active_skus()
    # Prefect concurrent mapping — controls parallelism
    results = scrape_product.map(
        url=skus["url"],
        retailer=skus["retailer"]
    )
    # downstream: normalize, upsert, alert on >5% price changes
```

**Scheduling:** Prefect deployments support cron schedules. Run at `0 4 * * *` (4 AM) to hit retailers when traffic is lowest and anti-bot thresholds are least aggressive.

**Parallelism:** Limit to 3–5 concurrent Firecrawl requests per retailer to avoid triggering rate limits. Use Prefect's concurrency limits on task runners.

### Airflow — When to Use Instead
Use Airflow if PickleIQ already runs Airflow for other data pipelines (warehouse ETL, etc.) — consolidating orchestrators reduces ops burden. The dynamic DAG patterns have improved in Airflow 2.x with `@task.expand()`.

---

## 4. PostgreSQL Schema for Price History

### Core Schema Pattern (HIGH confidence — standard time-series pattern)

```sql
-- Products: one row per canonical product (deduplicated across retailers)
CREATE TABLE products (
    id              BIGSERIAL PRIMARY KEY,
    canonical_name  TEXT NOT NULL,
    brand           TEXT NOT NULL,
    model           TEXT NOT NULL,
    category        TEXT NOT NULL,  -- 'paddle', 'ball', 'bag', etc.
    specs           JSONB,          -- normalized specs after dedup
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Retailer listings: one row per (product, retailer) combination
CREATE TABLE retailer_listings (
    id              BIGSERIAL PRIMARY KEY,
    product_id      BIGINT REFERENCES products(id),
    retailer        TEXT NOT NULL,  -- 'pickleballcentral', 'fromuth', etc.
    retailer_url    TEXT NOT NULL UNIQUE,
    retailer_sku    TEXT,
    title_raw       TEXT,           -- raw title as scraped (for audit)
    is_active       BOOLEAN DEFAULT TRUE,
    first_seen_at   TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Price snapshots: append-only time series
CREATE TABLE price_snapshots (
    id              BIGSERIAL PRIMARY KEY,
    listing_id      BIGINT REFERENCES retailer_listings(id),
    scraped_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    price_current   NUMERIC(10,2) NOT NULL,
    price_original  NUMERIC(10,2),          -- strikethrough/MSRP price
    currency        CHAR(3) DEFAULT 'USD',
    in_stock        BOOLEAN,
    inventory_qty   INTEGER,                -- if exposed by retailer
    variant_label   TEXT,                  -- 'Lightweight / 4" Grip'
    source_raw      JSONB                  -- full Firecrawl JSON response
);

-- Indexes for efficient querying
CREATE INDEX idx_price_snapshots_listing_time
    ON price_snapshots (listing_id, scraped_at DESC);

CREATE INDEX idx_price_snapshots_scraped_at
    ON price_snapshots (scraped_at DESC);

CREATE INDEX idx_retailer_listings_product
    ON retailer_listings (product_id);
```

### TimescaleDB Consideration (MEDIUM confidence)

If price_snapshots grows beyond ~50M rows (scraping 1000 SKUs across 4 retailers daily = 4000 rows/day = ~1.5M rows/year), consider TimescaleDB's `CREATE TABLE ... USING timescaledb` with automatic chunk management. TimescaleDB integrates cleanly with standard PostgreSQL tooling but adds a layer of ops complexity. Defer until row counts justify it.

### Query Patterns to Optimize For

**Latest price per listing (materialized view pattern):**
```sql
CREATE MATERIALIZED VIEW latest_prices AS
SELECT DISTINCT ON (listing_id)
    listing_id, price_current, price_original, in_stock, scraped_at
FROM price_snapshots
ORDER BY listing_id, scraped_at DESC;

CREATE UNIQUE INDEX ON latest_prices (listing_id);
-- Refresh after each scrape batch: REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices;
```

**Price history for a product across retailers:**
```sql
SELECT rl.retailer, ps.scraped_at, ps.price_current
FROM price_snapshots ps
JOIN retailer_listings rl ON rl.id = ps.listing_id
WHERE rl.product_id = $1
  AND ps.scraped_at > NOW() - INTERVAL '30 days'
ORDER BY ps.scraped_at DESC;
```

**Gotcha — storage bloat:** Do NOT store `source_raw` JSONB in the main price_snapshots table long-term. Move it to a separate `scrape_audit` table or compress/archive after 7 days. The raw Firecrawl response per page can be 50–200KB; at 4000 snapshots/day that's 200–800MB/day.

---

## 5. Normalization Challenges: SKU Deduplication and Spec Inconsistencies

### The Core Problem (HIGH confidence)

The same paddle appears differently across retailers:

| Retailer | Title as Scraped |
|----------|-----------------|
| PickleballCentral | "Selkirk VANGUARD Power Air Invikta - Midnight Black" |
| Fromuth | "Selkirk Vanguard Power Air Invikta Paddle - Black" |
| JustPaddles | "Selkirk Sport VANGUARD Power Air - Invikta Shape" |
| Amazon | "Selkirk Sport Pickleball Paddle - VANGUARD Power Air Invikta" |

These are the same product. Deduplication without a canonical database requires significant work.

### SKU Deduplication Strategy

**Tier 1 — Manufacturer SKU matching (HIGH confidence, preferred)**
Most paddle manufacturers print a SKU on the product and include it in spec sheets. If Firecrawl extracts the manufacturer SKU from the page, use that as the primary dedup key. Store it in `retailer_listings.retailer_sku`. Map to canonical products via a `product_skus` lookup table.

Problem: Not all retailers expose the manufacturer SKU on product pages. JustPaddles and Fromuth are inconsistent.

**Tier 2 — Normalized title matching (MEDIUM confidence)**
Build a normalization pipeline:
1. Lowercase, strip punctuation
2. Extract brand from known brand list (Selkirk, Joola, Head, Paddletek, etc.)
3. Extract model tokens using regex patterns per brand
4. Block-hash the (brand, normalized_model_tokens) tuple
5. Match across retailers by hash

This gets ~85% accuracy. The remaining 15% requires manual review or fuzzy matching (RapidFuzz with token_sort_ratio > 90).

**Tier 3 — Embedding similarity (LOW confidence for production MVP)**
Encode product titles as embeddings (via OpenAI or a local model) and use cosine similarity. Effective but expensive per-query and adds infrastructure. Defer to a later phase.

### Spec Format Inconsistencies

Paddle specs vary wildly across retailers:

| Spec | PickleballCentral | Fromuth | JustPaddles |
|------|------------------|---------|-------------|
| Weight | "7.3 - 7.7 oz" | "7.5oz average" | "Mid Weight" |
| Grip Length | "5.25 inches" | '5.25"' | "5 1/4 in" |
| Core Thickness | "16mm" | ".63 inches" | "16 MM" |

**Normalization rules to implement:**

```python
# Weight: always store in ounces as a range [min, max]
def normalize_weight(raw: str) -> tuple[float, float]:
    # handles "7.3-7.7 oz", "7.5oz", "Mid Weight" -> None
    ...

# Grip length: always store in inches as float
def normalize_grip_length(raw: str) -> float | None:
    # handles '5.25"', "5.25 inches", "5 1/4 in"
    ...

# Core thickness: always store in mm as float
def normalize_thickness(raw: str) -> float | None:
    # handles "16mm", ".63 inches" -> 16.0, "16 MM" -> 16.0
    ...
```

**Store both raw and normalized:**
```sql
-- In products.specs JSONB:
{
  "weight_oz_min": 7.3,
  "weight_oz_max": 7.7,
  "grip_length_in": 5.25,
  "core_thickness_mm": 16.0,
  "core_material": "polypropylene",
  "surface_material": "carbon_fiber",
  "shape": "elongated"
}
```

Always keep the raw scraped specs in `retailer_listings` or `scrape_audit` — you will need to re-run normalization as rules improve.

### Variant Handling (MEDIUM confidence — significant complexity)

Paddles have variants (grip size, weight class). Retailers handle this differently:
- **Single URL per variant:** JustPaddles often gives each variant its own product URL
- **Single URL, variant selector:** PickleballCentral uses JS variant pickers, price changes on selection
- **Bundle listings:** Amazon groups variants under one ASIN with child ASINs

**Recommendation:** Model variants as separate `retailer_listings` rows pointing to the same `products.id`. Include `variant_label` in price_snapshots. Do not try to normalize variant structures in Phase 1 — capture raw data and normalize in Phase 2 once patterns are understood.

---

## Critical Gotchas Summary

| # | Gotcha | Impact | Mitigation |
|---|--------|--------|------------|
| 1 | Amazon blocks residential proxies aggressively | Data gap for largest retailer | Use Amazon PA-API instead of Firecrawl for Amazon |
| 2 | Dynamic price loading via XHR | Prices not captured | Use `waitFor` + `actions` with scroll in Firecrawl |
| 3 | `/extract` uses separate credit pool | Unexpected cost overrun | Budget credits separately; use `/scrape` + schema for high-volume runs |
| 4 | `source_raw` JSONB bloat | Disk cost explosion | Archive/compress raw responses after 7 days |
| 5 | Variant prices under one URL | Price history mixed across variants | Capture `variant_label` in every snapshot; model variants as separate listings |
| 6 | Session-based pricing (logged-in vs guest) | Inconsistent price data | Document: all prices are guest/unauthenticated |
| 7 | Normalization rules will change | Breaks historical queries | Store raw specs forever; re-run normalization on raw data |
| 8 | Manufacturer SKU not always on page | Dedup requires fuzzy matching | Build SKU extraction + fuzzy fallback; manual review queue for unmatched |

---

## Sources and Confidence Notes

- Firecrawl API structure: MEDIUM confidence — based on Firecrawl docs as of mid-2025; verify current endpoint names and parameter names at https://docs.firecrawl.dev
- Anti-bot patterns: MEDIUM confidence — based on known Cloudflare and retail security patterns; retailer-specific severity is an estimate
- Prefect vs Airflow: HIGH confidence — based on documented capabilities of both tools as of 2025
- PostgreSQL schema patterns: HIGH confidence — standard time-series and normalization patterns, well-established
- Spec normalization: HIGH confidence — common ETL challenge with known solutions
- Amazon scraping difficulty: HIGH confidence — well-documented; PA-API recommendation is standard industry practice
