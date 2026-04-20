-- Migration 002: Add missing tables, title_hash column, replace ML retailer with JOOLA
-- Run on existing databases: psql -d pickleiq -f pipeline/db/migrations/002_missing_tables.sql

-- Add title_hash column to paddles
ALTER TABLE paddles ADD COLUMN IF NOT EXISTS title_hash TEXT;
CREATE INDEX IF NOT EXISTS idx_paddles_title_hash ON paddles(title_hash);

-- Backfill title_hash for existing paddles
UPDATE paddles SET title_hash = encode(digest(lower(regexp_replace(regexp_replace(name, '[^\w\s]', '', 'g'), '\s+', ' ', 'g')), 'sha256'), 'hex')
WHERE title_hash IS NULL;

-- Add dead_letter_queue table
CREATE TABLE IF NOT EXISTS dead_letter_queue (
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

CREATE INDEX IF NOT EXISTS idx_dlq_status ON dead_letter_queue(status);

-- Add data_quality_checks table
CREATE TABLE IF NOT EXISTS data_quality_checks (
    id              BIGSERIAL PRIMARY KEY,
    source          TEXT NOT NULL,
    field           TEXT NOT NULL,
    reason          TEXT NOT NULL,
    raw_value       TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dqc_source ON data_quality_checks(source);
CREATE INDEX IF NOT EXISTS idx_dqc_created ON data_quality_checks(created_at);

-- Update retailers: replace Mercado Livre with JOOLA
UPDATE retailers SET
    name = 'JOOLA',
    base_url = 'https://www.joola.com.br',
    integration_type = 'shopify_json'
WHERE id = 2;

-- Update integration_type CHECK constraint to include shopify_json
ALTER TABLE retailers DROP CONSTRAINT IF EXISTS retailers_integration_type_check;
ALTER TABLE retailers ADD CONSTRAINT retailers_integration_type_check
    CHECK (integration_type IN ('firecrawl', 'ml_api', 'pa_api', 'shopify_json'));
