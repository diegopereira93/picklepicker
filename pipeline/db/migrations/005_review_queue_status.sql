-- Migration 005: Add review_status column to review_queue
-- Tracks dedup review workflow: pending → auto_approved | manually_reviewed

-- Add column with default
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS review_status TEXT DEFAULT 'pending';

-- Add check constraint
ALTER TABLE review_queue ADD CONSTRAINT review_status_check
    CHECK (review_status IN ('pending', 'auto_approved', 'manually_reviewed'));

-- Backfill existing rows
UPDATE review_queue SET review_status = 'pending' WHERE review_status IS NULL;
