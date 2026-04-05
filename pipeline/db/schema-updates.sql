-- Phase 2+ Schema Updates
-- These columns are now in the base schema.sql (synced 2026-04-04).
-- Kept here for reference — do NOT re-run on fresh DBs.

-- ALTER TABLE paddles ADD COLUMN needs_reembed boolean DEFAULT false;
-- (Consolidated into base schema.sql)

-- Create HNSW index for cosine similarity search
CREATE INDEX paddles_embedding_hnsw_idx
ON paddle_embeddings USING hnsw (embedding vector_cosine_ops)
WITH (m=16, ef_construction=200);

-- Trigger: mark paddle for re-embedding when specs update
CREATE OR REPLACE FUNCTION mark_for_reembed()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE paddles SET needs_reembed=true WHERE id=NEW.paddle_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER paddle_specs_update_reembed
AFTER UPDATE ON paddle_specs
FOR EACH ROW
EXECUTE FUNCTION mark_for_reembed();
