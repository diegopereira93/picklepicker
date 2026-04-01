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
