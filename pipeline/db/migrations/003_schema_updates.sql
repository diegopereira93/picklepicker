-- Migration 003: Schema updates (HNSW index, reembed trigger)
-- Extracted from schema-updates.sql — active content only.

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
