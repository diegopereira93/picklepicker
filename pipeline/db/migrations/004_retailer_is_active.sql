-- Migration 004: Add is_active column to retailers table
-- Allows disabling retailers without removing them from the database.
-- Crawlers should check is_active = TRUE before scraping.
-- Run: psql -d pickleiq -f pipeline/db/migrations/004_retailer_is_active.sql

-- Add is_active column (idempotent — safe to run on fresh or existing databases)
ALTER TABLE retailers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Ensure all existing retailers are active (idempotent)
UPDATE retailers SET is_active = TRUE WHERE is_active IS NULL;

-- Comment on column for documentation
COMMENT ON COLUMN retailers.is_active IS 'Controle de ativação do varejista. FALSE = crawler ignora este varejista.';
