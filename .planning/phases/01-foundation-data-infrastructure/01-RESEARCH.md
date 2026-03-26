# Phase 1: Foundation & Data Infrastructure - Research

**Researched:** 2026-03-26
**Domain:** Python monorepo setup, PostgreSQL schema design, Firecrawl /extract, Mercado Livre API + Afiliados
**Confidence:** MEDIUM-HIGH (stack is stable; ML Afiliados affiliate link API has a LOW-confidence gap — see Open Questions)

---

## Summary

Phase 1 establishes the entire data foundation: monorepo skeleton, Docker Compose + Supabase staging, the full PostgreSQL schema (8 tables + materialized view), a working Firecrawl-based crawler for Brazil Pickleball Store, and a Mercado Livre Afiliados integration that indexes paddles with affiliate-tagged URLs.

The standard stack is well-understood. The primary risk is the Mercado Livre Afiliados affiliate link generation mechanism: a Reclame Aqui complaint from 2025 explicitly states "Programa de afiliados do Mercado Livre não tem uma API." The portal is UI-based, not API-based. This means affiliate link construction must be done via URL pattern replication (appending `?matt_id=<tag>` or similar), not an official SDK. This needs verification against current ML Afiliados documentation before coding Plan 01-04.

The Firecrawl path is solid: `/extract` with a typed JSON schema handles JS-rendered BR retailer pages and is resilient to site redesigns. Retry logic should use `tenacity` (not Prefect — the project uses GH Actions as orchestrator, Prefect is a deferred decision per requirements).

**Primary recommendation:** Build Plans 01-01 through 01-03 with full confidence. For 01-04, scaffold the ML search integration using the public `/sites/MLB/search` API (no auth needed for search), and implement affiliate URL construction using the documented URL pattern — flag for manual verification of the affiliate tag parameter name before going live.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| R1.1 | Monorepo `backend/` + `frontend/` + `pipeline/`, Docker Compose PostgreSQL 16, `.env.example` | Standard Python/Node monorepo patterns; Docker Compose config documented below |
| R1.2 | Schema: 8 tables + `latest_prices` materialized view | Full SQL documented in Architecture Patterns; standard time-series pattern HIGH confidence |
| R1.3 | Firecrawl `/extract` crawler for Brazil Pickleball Store with 3x exponential backoff + Telegram alert | Firecrawl API documented; tenacity for retry; python-telegram-bot v22 for alerts |
| R1.4 | Mercado Livre Afiliados — search via ML API, extract item_id/price/affiliate URL, save to price_snapshots | ML public search API confirmed; affiliate link URL pattern LOW confidence — needs verification |
</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.3 | Pipeline runtime | Available on machine; matches modern async support |
| FastAPI | 0.135.2 | Backend API (Phase 2+, scaffold now) | Latest stable; Pydantic v2 native |
| psycopg | 3.3.3 | PostgreSQL async driver | Modern async-native; replaces psycopg2 for Python 3.12 |
| firecrawl-py | 4.21.0 | Firecrawl client | Latest stable; major version 4.x API |
| tenacity | 9.1.4 | Retry with exponential backoff | Standard Python retry library; cleaner than custom loops |
| python-telegram-bot | 22.7 | Telegram alert on persistent failure | Latest stable; async-native v20+ API |
| pytest | 9.0.2 | Test runner | Latest stable |
| pytest-asyncio | 1.3.0 | Async test support | Latest stable |
| httpx | 0.28.1 | HTTP client + HTTPX TestClient | Latest stable; used for ML API calls and testing |
| pydantic | 2.x (bundled with FastAPI) | Schema validation | Via FastAPI dependency |
| python-dotenv | latest | .env loading | Standard |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| uvicorn | latest | ASGI server | Running FastAPI locally |
| pytest-cov | latest | Coverage reporting | CI gate ≥ 80% |
| alembic | latest | DB migrations | Managing schema evolution beyond Phase 1 seed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| tenacity | Custom retry loop | tenacity is battle-tested; custom loops miss jitter, max-delay, exception filtering |
| python-telegram-bot | requests + Telegram HTTP API directly | PTB adds overhead but handles token management and async cleanly |
| psycopg (v3) | psycopg2 | psycopg2 is sync-only; psycopg v3 has both sync and async, native Pydantic integration |

**Installation (pipeline/):**
```bash
pip install firecrawl-py==4.21.0 psycopg[binary]==3.3.3 tenacity==9.1.4 \
    python-telegram-bot==22.7 httpx==0.28.1 pytest==9.0.2 \
    pytest-asyncio==1.3.0 pytest-cov python-dotenv pydantic
```

---

## Architecture Patterns

### Recommended Project Structure
```
picklepicker/
├── backend/              # FastAPI app (scaffold in 01-01, populated Phase 2+)
│   ├── app/
│   │   └── main.py
│   └── pyproject.toml
├── frontend/             # Next.js 14 (scaffold in 01-01, populated Phase 4)
│   └── package.json
├── pipeline/             # Python scraping scripts
│   ├── crawlers/
│   │   ├── brazil_store.py      # Plan 01-03
│   │   └── mercado_livre.py     # Plan 01-04
│   ├── db/
│   │   ├── connection.py        # psycopg async pool
│   │   └── schema.sql           # Plan 01-02
│   ├── alerts/
│   │   └── telegram.py          # Telegram bot alert helper
│   ├── tests/
│   │   └── test_brazil_store_crawler.py
│   ├── pyproject.toml
│   └── .env.example             # canonical env vars list
├── docker-compose.yml            # Plan 01-01
└── .env.example                  # root-level (symlink or copy from pipeline/)
```

### Pattern 1: PostgreSQL Schema (R1.2)

All 8 tables + materialized view. Use a single `schema.sql` applied via Docker Compose init script.

```sql
-- Enable pgvector (available natively in Supabase; required for local Docker)
CREATE EXTENSION IF NOT EXISTS vector;

-- Master paddle catalog
CREATE TABLE paddles (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    brand           TEXT NOT NULL,
    model           TEXT NOT NULL,
    manufacturer_sku TEXT,
    images          TEXT[],
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Configured retailers
CREATE TABLE retailers (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    base_url        TEXT NOT NULL,
    integration_type TEXT NOT NULL,  -- 'firecrawl' | 'ml_api' | 'pa_api'
    is_active       BOOLEAN DEFAULT TRUE
);

-- Append-only price time series
CREATE TABLE price_snapshots (
    id              BIGSERIAL PRIMARY KEY,
    paddle_id       BIGINT REFERENCES paddles(id),
    retailer_id     BIGINT REFERENCES retailers(id),
    price_brl       NUMERIC(10,2) NOT NULL,
    currency        CHAR(3) DEFAULT 'BRL',
    in_stock        BOOLEAN,
    affiliate_url   TEXT,
    scraped_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_raw      JSONB
);

CREATE INDEX idx_price_snapshots_paddle_retailer_time
    ON price_snapshots (paddle_id, retailer_id, scraped_at DESC);

-- Materialized view: latest price per (paddle, retailer)
CREATE MATERIALIZED VIEW latest_prices AS
SELECT DISTINCT ON (paddle_id, retailer_id)
    paddle_id, retailer_id, price_brl, currency, in_stock, affiliate_url, scraped_at
FROM price_snapshots
ORDER BY paddle_id, retailer_id, scraped_at DESC;

CREATE UNIQUE INDEX ON latest_prices (paddle_id, retailer_id);
-- Refresh after each crawler run: REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices;

-- Technical specs (separate from paddles for join performance)
CREATE TABLE paddle_specs (
    id              BIGSERIAL PRIMARY KEY,
    paddle_id       BIGINT UNIQUE REFERENCES paddles(id),
    swingweight     NUMERIC(6,2),
    twistweight     NUMERIC(6,2),
    weight_oz       NUMERIC(5,2),
    grip_size       TEXT,
    core_thickness_mm NUMERIC(5,2),
    face_material   TEXT,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Embeddings (pgvector) — populated in Phase 2
CREATE TABLE paddle_embeddings (
    id              BIGSERIAL PRIMARY KEY,
    paddle_id       BIGINT UNIQUE REFERENCES paddles(id),
    embedding       vector(1536),
    needs_reembed   BOOLEAN DEFAULT TRUE,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Review queue for manual dedup/spec review (Phase 4 admin panel)
CREATE TABLE review_queue (
    id              BIGSERIAL PRIMARY KEY,
    type            TEXT NOT NULL CHECK (type IN ('duplicate','spec_unmatched','price_anomaly')),
    paddle_id       BIGINT REFERENCES paddles(id),
    related_paddle_id BIGINT REFERENCES paddles(id),
    data            JSONB,
    status          TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','resolved','dismissed')),
    resolved_at     TIMESTAMPTZ,
    resolved_by     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Users and price alerts (base structure; populated Phase 5)
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           TEXT UNIQUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE price_alerts (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    paddle_id       BIGINT REFERENCES paddles(id),
    target_price_brl NUMERIC(10,2) NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Pattern 2: Firecrawl /extract with Tenacity Retry (R1.3)

```python
# pipeline/crawlers/brazil_store.py
import asyncio
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

SCHEMA = {
    "type": "object",
    "properties": {
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
    }
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=10, max=120),
    retry=retry_if_exception_type(Exception),
    reraise=True  # re-raise after exhausting retries so caller can send Telegram alert
)
def extract_products(app: FirecrawlApp, url: str) -> dict:
    return app.extract(
        [url],
        {
            "prompt": "Extract all pickleball paddle products with name, price in BRL, availability, image URL, product URL, brand, and technical specs",
            "schema": SCHEMA
        }
    )

async def run_brazil_store_crawler():
    app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
    try:
        result = extract_products(app, "https://brazilpickleballstore.com.br/raquete/")
        # save to price_snapshots...
    except Exception as e:
        # All 3 retries exhausted — send Telegram alert
        await send_telegram_alert(f"Brazil Pickleball Store crawler failed after 3 retries: {e}")
        raise
```

### Pattern 3: Mercado Livre Public Search API (R1.4)

The ML search API is **public — no authentication required** for GET requests. Auth (OAuth2) is only needed for seller/user operations.

```python
# pipeline/crawlers/mercado_livre.py
import httpx

ML_SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"

async def search_pickleball_paddles(limit: int = 50, offset: int = 0) -> dict:
    async with httpx.AsyncClient() as client:
        params = {
            "q": "raquete pickleball",
            "category": "MLB1276",  # Esportes e Fitness — verify subcategory
            "limit": limit,
            "offset": offset,
        }
        response = await client.get(ML_SEARCH_URL, params=params)
        response.raise_for_status()
        return response.json()

def build_affiliate_url(item_permalink: str, affiliate_tag: str) -> str:
    # ML affiliate URLs: append ?matt_id=<tag> to product permalink
    # NOTE: Parameter name needs verification — see Open Questions
    separator = "&" if "?" in item_permalink else "?"
    return f"{item_permalink}{separator}matt_id={affiliate_tag}"
```

### Pattern 4: Telegram Alert Helper

```python
# pipeline/alerts/telegram.py
from telegram import Bot

async def send_telegram_alert(message: str) -> None:
    bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    await bot.send_message(
        chat_id=os.environ["TELEGRAM_CHAT_ID"],
        text=f"[PickleIQ Alert] {message}"
    )
```

### Pattern 5: Docker Compose for Local PostgreSQL

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: pickleiq
      POSTGRES_USER: pickleiq
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./pipeline/db/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql

volumes:
  postgres_data:
```

**Note:** pgvector is NOT available in the standard `postgres:16` image. For local Docker, use `pgvector/pgvector:pg16` image. For Supabase staging, pgvector is available natively — no extra config needed.

```yaml
# Corrected image for local dev:
image: pgvector/pgvector:pg16
```

### Anti-Patterns to Avoid

- **Do NOT use `postgres:16` official image** — it lacks pgvector. Use `pgvector/pgvector:pg16`.
- **Do NOT store `source_raw` JSONB forever** — archive/compress after 30 days; at 50+ scraped items/day, this bloats storage quickly.
- **Do NOT call ML affiliate API to generate links** — no official API exists. Build URLs via pattern: `permalink + ?matt_id=<tag>`.
- **Do NOT use Prefect in Phase 1** — GitHub Actions is the decided orchestrator. Prefect is deferred.
- **Do NOT refresh `latest_prices` synchronously inside the scraper** — call `REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices` as a final step after all snapshots are committed.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Retry with backoff | Custom while loop + sleep | `tenacity` | Handles jitter, max delay, exception filtering, logging |
| Telegram bot message sending | Raw HTTP to Telegram API | `python-telegram-bot` | Handles token management, rate limits, async |
| PostgreSQL connection pooling | Manual connection management | `psycopg` async pool | Built-in pool, context managers, async-native |
| DB schema versioning | Ad-hoc ALTER TABLE scripts | `alembic` (Phase 2+) | Reproducible migrations; for Phase 1 a single `schema.sql` is acceptable |

**Key insight:** All retry/alert infrastructure is solved by well-maintained libraries. Custom implementations introduce subtle bugs in backoff calculation and miss edge cases (e.g., jitter prevents thundering herd on shared Firecrawl credits).

---

## Common Pitfalls

### Pitfall 1: pgvector missing from standard PostgreSQL Docker image
**What goes wrong:** `CREATE EXTENSION IF NOT EXISTS vector` fails with "could not open extension control file" — schema.sql apply fails silently or loudly.
**Why it happens:** The official `postgres:16` image does not include pgvector. It must be compiled or pre-installed.
**How to avoid:** Use `pgvector/pgvector:pg16` as the Docker image. This is the official pgvector-maintained image.
**Warning signs:** Schema apply succeeds but `\dx` in psql doesn't show `vector` extension.

### Pitfall 2: ML API search returns items without affiliate tag
**What goes wrong:** Items are saved to `price_snapshots.affiliate_url` as plain product URLs — no commission tracking.
**Why it happens:** The `permalink` field from ML search results is a plain product URL. The affiliate tag must be appended separately.
**How to avoid:** Always run `build_affiliate_url(permalink, tag)` before saving. Write a test asserting the tag is present in the saved URL.
**Warning signs:** Saved `affiliate_url` values don't contain `matt_id=` (or the confirmed parameter name).

### Pitfall 3: `REFRESH MATERIALIZED VIEW` blocking concurrent reads
**What goes wrong:** During a long crawler run, reads against `latest_prices` block or return stale data inconsistently.
**Why it happens:** Plain `REFRESH MATERIALIZED VIEW` takes an exclusive lock. `CONCURRENTLY` requires a unique index but allows reads.
**How to avoid:** Always use `REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices`. The schema above includes the required `UNIQUE INDEX ON latest_prices (paddle_id, retailer_id)`.
**Warning signs:** FastAPI responses slow dramatically during crawler runs.

### Pitfall 4: Firecrawl /extract credit pool separate from /scrape
**What goes wrong:** Budget exhausted mid-pipeline; /extract calls start failing without warning.
**Why it happens:** Firecrawl /extract uses a separate credit pool from /scrape. Each `/extract` call with multiple URLs counts multiple credits.
**How to avoid:** Monitor credit usage via Firecrawl dashboard. For Phase 1 proof-of-concept (one retailer), credit usage is low. Document credit costs in `.env.example` comments.
**Warning signs:** Firecrawl returns 402 or credit-exceeded errors.

### Pitfall 5: Partial data from /extract not handled
**What goes wrong:** A paddle is saved with `price_brl = null` causing DB constraint violation, or saved with missing fields that break downstream queries.
**Why it happens:** Firecrawl /extract uses an LLM; optional fields may return null for products with unusual page structure.
**How to avoid:** Validate extracted data before INSERT. For Phase 1: skip items missing `price_brl`. Log partial items for manual review. Tests must cover the "partial data" case (per R1.3 test spec).
**Warning signs:** DB INSERT errors on NOT NULL columns; downstream queries return unexpected nulls.

### Pitfall 6: ML Afiliados approval not confirmed before coding
**What goes wrong:** Plan 01-04 is coded assuming ML Afiliados is active, but the account hasn't been approved — affiliate tags are invalid and no commission is tracked.
**Why it happens:** REQUIREMENTS.md flags this as a BLOCKER: "Confirmar aprovação no Mercado Livre Afiliados antes de iniciar Phase 1."
**How to avoid:** Confirm ML Afiliados approval before merging Plan 01-04. The ML search integration (item_id, price, plain URL) can be built without affiliate approval; only the URL tagging requires it.
**Warning signs:** Affiliate dashboard shows zero clicks despite items being saved.

---

## Code Examples

### .env.example (canonical variable list for Phase 1)
```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pickleiq
POSTGRES_USER=pickleiq
POSTGRES_PASSWORD=changeme

# Supabase staging
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
DATABASE_URL=postgresql://pickleiq:<password>@<host>:5432/pickleiq

# Firecrawl
FIRECRAWL_API_KEY=fc-<key>

# Mercado Livre Afiliados
ML_AFFILIATE_TAG=<your_tag_id>
# ML_AFFILIATE_APP_ID=<app_id>  # only if OAuth required for affiliate link API

# Telegram alerts
TELEGRAM_BOT_TOKEN=<bot_token>
TELEGRAM_CHAT_ID=<chat_id>
```

### pytest-asyncio configuration (pyproject.toml)
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # pytest-asyncio 1.x default; avoids @pytest.mark.asyncio on every test
testpaths = ["tests"]
```

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker | Docker Compose PostgreSQL | Yes | 29.3.0 | — |
| Python 3.12 | Pipeline scripts | Yes | 3.12.3 | — |
| Node 20 | Next.js frontend scaffold | Yes | v20.20.0 | — |
| psql CLI | Schema verification | Yes | (system) | Use Docker exec |
| PostgreSQL server | Local dev DB | Via Docker | 16 (image) | Docker provides it |
| Supabase account | Staging pgvector DB | Unverified | — | Must provision manually |
| Firecrawl API key | Crawler | Unverified | — | Register at firecrawl.dev |
| ML Afiliados approval | Affiliate URLs | Unverified (BLOCKER) | — | Use plain permalink (no commission) |
| Telegram bot | Failure alerts | Unverified | — | Log to stdout only (temp fallback) |

**Missing dependencies with no fallback:**
- Supabase staging account — must be provisioned as part of Plan 01-01; blocks success criterion #2.

**Missing dependencies with fallback:**
- ML Afiliados approval — can build ML search integration without affiliate URLs; save `affiliate_url = permalink` as placeholder until approved.
- Telegram bot — can fallback to stdout logging temporarily; alerts are required for production but not blocking for local dev.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-asyncio 1.3.0 |
| Config file | `pipeline/pyproject.toml` — `[tool.pytest.ini_options]` |
| Quick run command | `cd pipeline && pytest tests/test_brazil_store_crawler.py -x` |
| Full suite command | `cd pipeline && pytest --cov=crawlers --cov-report=term-missing` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| R1.3 | Happy path: Firecrawl /extract → saves to price_snapshots | unit (mock Firecrawl + DB) | `pytest tests/test_brazil_store_crawler.py::test_happy_path -x` | Wave 0 |
| R1.3 | Retry: 3 attempts with growing backoff on 5xx | unit (mock 5xx × 3 then success) | `pytest tests/test_brazil_store_crawler.py::test_retry_backoff -x` | Wave 0 |
| R1.3 | Persistent failure: after 3 retries → Telegram alert fired | unit (mock 5xx × 3, mock Telegram) | `pytest tests/test_brazil_store_crawler.py::test_persistent_failure_telegram -x` | Wave 0 |
| R1.3 | Partial data: missing price/image → defined behavior (skip) | unit | `pytest tests/test_brazil_store_crawler.py::test_partial_data -x` | Wave 0 |
| R1.4 | ML search returns items + affiliate URL correctly tagged | unit (mock httpx) | `pytest tests/test_mercado_livre_crawler.py::test_affiliate_url_tagged -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x --tb=short`
- **Per wave merge:** `pytest --cov=crawlers --cov=db --cov=alerts --cov-report=term-missing`
- **Phase gate:** Full suite green + coverage ≥ 80% before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `pipeline/tests/test_brazil_store_crawler.py` — covers R1.3 (4 test cases)
- [ ] `pipeline/tests/test_mercado_livre_crawler.py` — covers R1.4 (affiliate URL tagging)
- [ ] `pipeline/tests/conftest.py` — shared fixtures: mock Firecrawl response, mock psycopg pool, mock Telegram bot
- [ ] `pipeline/pyproject.toml` — pytest + asyncio_mode config

---

## Open Questions

1. **Mercado Livre Afiliados affiliate link URL parameter name**
   - What we know: A Reclame Aqui complaint (2025) states ML Afiliados has no official API. Community GitHub repos (e.g., `DeivianDS/mercadolivre-afiliados`) exist but are unofficial. The ML help page "Como recomendar um produto" describes a UI-based link generator.
   - What's unclear: The exact query parameter name to append to a `permalink` for affiliate tracking (candidate: `matt_id`, `picker_id`, or other). Whether a programmatic API exists for affiliate link generation.
   - Recommendation: Before coding Plan 01-04's URL construction, manually log into ML Afiliados portal, generate a link, and inspect the URL structure. Hardcode the confirmed parameter name in `build_affiliate_url()`. Document in `.env.example`.
   - Confidence: LOW for affiliate URL pattern specifically.

2. **ML API category ID for pickleball paddles**
   - What we know: `MLB1276` is Esportes e Fitness (confirmed via ML categories endpoint). Pickleball is a subcategory.
   - What's unclear: The exact subcategory ID for pickleball specifically (if one exists). The search `q=raquete pickleball` on `MLB1276` should work without a subcategory ID.
   - Recommendation: Use `q=raquete pickleball&category=MLB1276` for Phase 1. Use ML's category tree endpoint to find the pickleball subcategory if results are noisy.
   - Confidence: MEDIUM — `q=` search on the parent category is standard and confirmed to return results.

3. **Supabase staging provisioning**
   - What we know: Supabase free tier supports pgvector natively. Must be provisioned manually via supabase.com dashboard.
   - What's unclear: Whether the project already has a Supabase account/organization set up.
   - Recommendation: Plan 01-01 must include a step to provision the Supabase staging project and copy the connection string into `.env`.

---

## Sources

### Primary (HIGH confidence)
- Package versions verified against PyPI registry (2026-03-26): firecrawl-py 4.21.0, psycopg 3.3.3, fastapi 0.135.2, pytest 9.0.2, pytest-asyncio 1.3.0, httpx 0.28.1, python-telegram-bot 22.7, tenacity 9.1.4
- PostgreSQL schema patterns: standard time-series append-only design (well-established)
- pgvector Docker image: `pgvector/pgvector:pg16` (official pgvector project)
- ML public search API endpoint: `https://api.mercadolibre.com/sites/MLB/search` — confirmed via ML developer docs

### Secondary (MEDIUM confidence)
- Firecrawl /extract pattern: existing domain research (`scraping-pipeline.md`) cross-referenced with firecrawl-py 4.x API
- ML category MLB1276 = Esportes e Fitness: confirmed via WebSearch pointing to ML categories API
- tenacity retry pattern: standard Python community pattern, well-documented

### Tertiary (LOW confidence)
- ML affiliate URL parameter (`matt_id`): inferred from community GitHub repos and ML help pages; NOT verified against official ML Afiliados documentation
- ML Afiliados "no official API": single Reclame Aqui complaint source — needs official verification

---

## Metadata

**Confidence breakdown:**
- Standard stack (Python libs): HIGH — PyPI versions verified 2026-03-26
- Docker/PostgreSQL schema: HIGH — standard patterns, pgvector image confirmed
- Firecrawl integration: MEDIUM — existing research + library version confirmed; endpoint behavior from MEDIUM-confidence prior research
- ML search API: MEDIUM — public endpoint confirmed, category ID inferred
- ML affiliate URL construction: LOW — parameter name unverified; official API existence disputed

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (stable stack; ML Afiliados affiliate parameter should be verified before coding 01-04)
