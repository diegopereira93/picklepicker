-- Data quality metrics tables for pipeline observability
-- Created: Phase 12-04 Observability Infrastructure

-- Table for tracking validation failures
CREATE TABLE IF NOT EXISTS data_quality_checks (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    field VARCHAR(100) NOT NULL,
    reason TEXT NOT NULL,
    raw_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_quality_checks_source ON data_quality_checks(source);
CREATE INDEX IF NOT EXISTS idx_quality_checks_field ON data_quality_checks(field);
CREATE INDEX IF NOT EXISTS idx_quality_checks_created_at ON data_quality_checks(created_at);

-- Composite index for common query pattern (source + time range)
CREATE INDEX IF NOT EXISTS idx_quality_checks_source_created
    ON data_quality_checks(source, created_at);

-- Dead letter queue table for failed extraction handling
CREATE TABLE IF NOT EXISTS dead_letter_queue (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    error_message TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for DLQ queries
CREATE INDEX IF NOT EXISTS idx_dlq_status ON dead_letter_queue(status, retry_count);
CREATE INDEX IF NOT EXISTS idx_dlq_created_at ON dead_letter_queue(created_at);
CREATE INDEX IF NOT EXISTS idx_dlq_source ON dead_letter_queue(source);
