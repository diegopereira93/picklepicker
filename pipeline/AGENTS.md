# Pipeline — AGENTS.md

Scraping + data pipeline. Firecrawl/httpx crawlers, 3-tier dedup, OpenAI embeddings, pgvector. Separate venv.

## Structure

```
pipeline/
├── crawlers/
│   ├── brazil_store.py      # Firecrawl. tenacity 3x, 1-10s. No __main__.
│   ├── dropshot_brasil.py   # Firecrawl. tenacity 3x, 1-10s. No __main__.
│   └── mercado_livre.py     # httpx + ML API. tenacity 3x. HAS __main__.
├── db/
│   ├── schema.sql           # 8 tables + 2 MVs. pgvector. Seed retailers.
│   ├── schema-updates.sql   # Schema evolution
│   ├── connection.py        # AsyncConnectionPool, double-checked locking
│   ├── dead_letter_queue.py # Failed item storage + retry (max_retries)
│   └── quality_metrics.py   # Data quality tracking
├── dedup/
│   ├── normalizer.py        # normalize_title, title_hash, get_or_create_paddle
│   └── spec_matcher.py      # RapidFuzz fuzzy (threshold 0.85). Tier-3 dedup.
├── embeddings/
│   ├── batch_embedder.py    # OpenAI text-embedding-3-small → paddle_embeddings
│   └── document_generator.py # Narrative text from specs for embedding
├── alerts/freshness.py      # Price freshness alerts
├── migrations/              # add_enriched_columns.py (skill_level, in_stock, model_slug)
├── scripts/                 # populate_enriched_data.py
├── tests/                   # Mock Firecrawl, mock DB, mock Telegram. conftest.py fixtures.
└── pyproject.toml           # firecrawl-py, psycopg, tenacity, openai, httpx
```

## Where to Look

| Task | Location |
|------|----------|
| Add new scraper | `crawlers/` — use tenacity + Firecrawl pattern |
| Change DB schema | `db/schema.sql` (init) + `db/schema-updates.sql` (evolution) |
| Modify dedup logic | `dedup/normalizer.py` (tier 1-2) + `dedup/spec_matcher.py` (tier 3 fuzzy) |
| Change embeddings | `embeddings/batch_embedder.py` + `embeddings/document_generator.py` |
| Handle failed items | `db/dead_letter_queue.py` — retry tracking, max_retries |
| Add alert logic | `alerts/freshness.py` |
| Tests | `tests/` — conftest.py has mock_firecrawl_app, mock_db_connection |

## Conventions

- **Firecrawl only** — Brazil Store and Dropshot use Firecrawl API. No BeautifulSoup/Scrapy/Selenium.
- **Mercado Livre** — uses httpx for ML public API. `build_affiliate_url()` adds affiliate tag.
- **tenacity retry** — all crawlers. 3 attempts, exponential backoff. Params vary (1-10s vs 5-120s).
- **Data flow** — extract → price_snapshots (append-only) → REFRESH MATERIALIZED VIEW latest_prices.
- **3-tier dedup** — SKU exact → title hash → RapidFuzz fuzzy (0.85 threshold).
- **Embeddings** — OpenAI text-embedding-3-small → `paddle_embeddings` (vector(1536)).
- **Separate venv** — `pipeline/.venv/`. Own `pyproject.toml`. NOT shared with backend.
- **Invoked via GitHub Actions** — cron schedules in `.github/workflows/scraper.yml` and `scrape.yml`.

## Anti-Patterns

- Do NOT add BeautifulSoup/Scrapy — project uses Firecrawl/httpx intentionally.
- Do NOT share dependencies with backend — pipeline has its own venv and pyproject.toml.
- Do NOT assume `__main__` guard — only `mercado_livre.py` has it. Others are library modules.
- Do NOT hardcode DB credentials — use `DATABASE_URL` env var.
- Do NOT skip `REFRESH MATERIALIZED VIEW` after crawler writes — latest_prices must stay fresh.
