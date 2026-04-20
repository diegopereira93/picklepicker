-- PickleIQ Schema v1.1 — Phase 1 Foundation + Pipeline Fixes
-- Applied via docker-entrypoint-initdb.d/01-schema.sql

-- Enable pgvector extension (available in pgvector/pgvector:pg16 image)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- Table 1: paddles — Master paddle catalog
-- ============================================================
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
    title_hash        TEXT,
    needs_reembed     BOOLEAN DEFAULT false,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_paddle_name UNIQUE (name)
);

CREATE INDEX idx_paddles_title_hash ON paddles(title_hash);

-- ============================================================
-- Table 2: retailers — Configured retailer sources
-- ============================================================
CREATE TABLE retailers (
    id               BIGSERIAL PRIMARY KEY,
    name             TEXT NOT NULL,
    base_url         TEXT NOT NULL,
    integration_type TEXT NOT NULL CHECK (integration_type IN ('firecrawl', 'ml_api', 'pa_api', 'shopify_json')),
    is_active        BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- Table 3: price_snapshots — Append-only price time series
-- ============================================================
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

-- ============================================================
-- Materialized View: latest_prices — Latest price per (paddle, retailer)
-- ============================================================
CREATE MATERIALIZED VIEW latest_prices AS
SELECT DISTINCT ON (paddle_id, retailer_id)
    paddle_id, retailer_id, price_brl, currency, in_stock, affiliate_url, scraped_at
FROM price_snapshots
ORDER BY paddle_id, retailer_id, scraped_at DESC;

CREATE UNIQUE INDEX ON latest_prices (paddle_id, retailer_id);
-- Refresh after each crawler run: REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices;

-- ============================================================
-- Table 4: paddle_specs — Technical specifications
-- ============================================================
CREATE TABLE paddle_specs (
    id                BIGSERIAL PRIMARY KEY,
    paddle_id         BIGINT UNIQUE REFERENCES paddles(id),
    swingweight       NUMERIC(6,2),
    twistweight       NUMERIC(6,2),
    weight_oz         NUMERIC(5,2),
    grip_size         TEXT,
    core_thickness_mm NUMERIC(5,2),
    face_material     TEXT,
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Table 5: paddle_embeddings — pgvector embeddings (populated Phase 2)
-- ============================================================
CREATE TABLE paddle_embeddings (
    id              BIGSERIAL PRIMARY KEY,
    paddle_id       BIGINT UNIQUE REFERENCES paddles(id),
    embedding       vector(768),
    needs_reembed   BOOLEAN DEFAULT TRUE,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Table 6: review_queue — Items flagged for manual review
-- ============================================================
CREATE TABLE review_queue (
    id                BIGSERIAL PRIMARY KEY,
    type              TEXT NOT NULL CHECK (type IN ('duplicate', 'spec_unmatched', 'price_anomaly')),
    paddle_id         BIGINT REFERENCES paddles(id),
    related_paddle_id BIGINT REFERENCES paddles(id),
    data              JSONB,
    status            TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'resolved', 'dismissed')),
    resolved_at       TIMESTAMPTZ,
    resolved_by       TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Table 7: users — Base user table (populated Phase 5)
-- ============================================================
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           TEXT UNIQUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Table 8: price_alerts — Price alert subscriptions (populated Phase 5)
-- ============================================================
CREATE TABLE price_alerts (
    id               BIGSERIAL PRIMARY KEY,
    user_id          BIGINT REFERENCES users(id),
    paddle_id        BIGINT REFERENCES paddles(id),
    target_price_brl NUMERIC(10,2) NOT NULL,
    is_active        BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Table 9: user_profiles — Persisted user quiz profiles
-- ============================================================
CREATE TABLE user_profiles (
    id              BIGSERIAL PRIMARY KEY,
    user_id         TEXT UNIQUE NOT NULL,
    level           TEXT NOT NULL CHECK (level IN ('beginner', 'intermediate', 'advanced')),
    style           TEXT CHECK (style IN ('control', 'power', 'balanced')),
    budget_max      NUMERIC(10,2) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Table 10: affiliate_clicks — Affiliate click tracking
-- ============================================================
CREATE TABLE affiliate_clicks (
    id              BIGSERIAL PRIMARY KEY,
    paddle_id       BIGINT REFERENCES paddles(id),
    retailer        TEXT,
    source          TEXT DEFAULT 'organic',
    campaign        TEXT DEFAULT 'general',
    medium          TEXT DEFAULT 'affiliate',
    page            TEXT,
    affiliate_url   TEXT,
    user_agent      TEXT,
    ip_address      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_affiliate_clicks_paddle ON affiliate_clicks(paddle_id);
CREATE INDEX idx_affiliate_clicks_created ON affiliate_clicks(created_at);

-- ============================================================
-- Seed data: Retailers for Phase 1
-- ============================================================
INSERT INTO retailers (name, base_url, integration_type, is_active) VALUES
    ('Brazil Pickleball Store', 'https://brazilpickleballstore.com.br', 'firecrawl', TRUE),
    ('JOOLA', 'https://www.joola.com.br', 'shopify_json', TRUE),
    ('Drop Shot Brasil', 'https://www.dropshotbrasil.com.br', 'firecrawl', TRUE);

-- ============================================================
-- Table 11: dead_letter_queue — Failed extraction storage
-- ============================================================
CREATE TABLE dead_letter_queue (
    id              BIGSERIAL PRIMARY KEY,
    source          TEXT NOT NULL,
    payload         JSONB,
    error_message   TEXT,
    retry_count     INT DEFAULT 0,
    max_retries     INT DEFAULT 3,
    status          TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'resolved', 'failed')),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

CREATE INDEX idx_dlq_status ON dead_letter_queue(status);

-- ============================================================
-- Table 12: data_quality_checks — Validation failure tracking
-- ============================================================
CREATE TABLE data_quality_checks (
    id              BIGSERIAL PRIMARY KEY,
    source          TEXT NOT NULL,
    field           TEXT NOT NULL,
    reason          TEXT NOT NULL,
    raw_value       TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_dqc_source ON data_quality_checks(source);
CREATE INDEX idx_dqc_created ON data_quality_checks(created_at);

-- Backfill title_hash for existing paddles
UPDATE paddles SET title_hash = encode(digest(lower(regexp_replace(regexp_replace(name, '[^\w\s]', '', 'g'), '\s+', ' ', 'g')), 'sha256'), 'hex')
WHERE title_hash IS NULL;
