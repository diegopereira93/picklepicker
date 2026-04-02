-- PickleIQ Schema v1.0 — Phase 1 Foundation
-- Applied via docker-entrypoint-initdb.d/01-schema.sql

-- Enable pgvector extension (available in pgvector/pgvector:pg16 image)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- Table 1: paddles — Master paddle catalog
-- ============================================================
CREATE TABLE paddles (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    brand           TEXT NOT NULL,
    model           TEXT NOT NULL,
    manufacturer_sku TEXT,
    images          TEXT[],
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_paddle_name UNIQUE (name)
);

-- ============================================================
-- Table 2: retailers — Configured retailer sources
-- ============================================================
CREATE TABLE retailers (
    id               BIGSERIAL PRIMARY KEY,
    name             TEXT NOT NULL,
    base_url         TEXT NOT NULL,
    integration_type TEXT NOT NULL CHECK (integration_type IN ('firecrawl', 'ml_api', 'pa_api')),
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
    embedding       vector(1536),
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
-- Seed data: Retailers for Phase 1
-- ============================================================
INSERT INTO retailers (name, base_url, integration_type, is_active) VALUES
    ('Brazil Pickleball Store', 'https://brazilpickleballstore.com.br', 'firecrawl', TRUE),
    ('Mercado Livre', 'https://www.mercadolivre.com.br', 'ml_api', TRUE);
