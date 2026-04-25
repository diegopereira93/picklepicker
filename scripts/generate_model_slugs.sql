-- Generate model_slug for all paddles where model_slug IS NULL
-- Format: lowercase, spaces→hyphens, consecutive hyphens collapsed, special chars removed
-- Preserves existing non-null model_slug values

UPDATE paddles
SET model_slug = LOWER(
    REGEXP_REPLACE(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(name, '[^\w\s-]', '', 'g'),
                '\s+', '-', 'g'
            ),
            '-+', '-', 'g'
        ),
        '^-|-$', '', 'g'
    )
)
WHERE model_slug IS NULL
  AND name IS NOT NULL
  AND name != '';

-- Verify: check for any remaining NULLs
-- SELECT COUNT(*) FROM paddles WHERE model_slug IS NULL;
