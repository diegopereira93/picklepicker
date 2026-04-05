-- Remove paddles from brands never scraped with product images.
-- These brands have no retailer-sourced photos, only "Foto" placeholder.
-- Run: docker compose exec -T postgres psql -U pickleiq -d pickleiq < scripts/remove_unscraped_brands.sql

BEGIN;

-- Show what will be deleted (dry-run preview)
SELECT id, name, brand, model_slug, image_url
FROM paddles
WHERE brand IN (
    'Asics', 'Babolat', 'Diadem', 'Nox', 'Royal Padel',
    'Vulcan', 'Yonex', 'Netset', 'Dropshot', 'Gearbox'
)
ORDER BY brand, name;

-- Delete price history for these paddles (cascade would handle, but explicit for safety)
DELETE FROM price_snapshots
WHERE paddle_id IN (
    SELECT id FROM paddles
    WHERE brand IN (
        'Asics', 'Babolat', 'Diadem', 'Nox', 'Royal Padel',
        'Vulcan', 'Yonex', 'Netset', 'Dropshot', 'Gearbox'
    )
);

-- Delete specs for these paddles
DELETE FROM paddle_specs
WHERE paddle_id IN (
    SELECT id FROM paddles
    WHERE brand IN (
        'Asics', 'Babolat', 'Diadem', 'Nox', 'Royal Padel',
        'Vulcan', 'Yonex', 'Netset', 'Dropshot', 'Gearbox'
    )
);

-- Delete embeddings for these paddles
DELETE FROM paddle_embeddings
WHERE paddle_id IN (
    SELECT id FROM paddles
    WHERE brand IN (
        'Asics', 'Babolat', 'Diadem', 'Nox', 'Royal Padel',
        'Vulcan', 'Yonex', 'Netset', 'Dropshot', 'Gearbox'
    )
);

-- Delete price alerts for these paddles
DELETE FROM price_alerts
WHERE paddle_id IN (
    SELECT id FROM paddles
    WHERE brand IN (
        'Asics', 'Babolat', 'Diadem', 'Nox', 'Royal Padel',
        'Vulcan', 'Yonex', 'Netset', 'Dropshot', 'Gearbox'
    )
);

-- Delete review queue entries for these paddles
DELETE FROM review_queue
WHERE paddle_id IN (
    SELECT id FROM paddles
    WHERE brand IN (
        'Asics', 'Babolat', 'Diadem', 'Nox', 'Royal Padel',
        'Vulcan', 'Yonex', 'Netset', 'Dropshot', 'Gearbox'
    )
);

-- Finally, delete the paddles themselves
DELETE FROM paddles
WHERE brand IN (
    'Asics', 'Babolat', 'Diadem', 'Nox', 'Royal Padel',
    'Vulcan', 'Yonex', 'Netset', 'Dropshot', 'Gearbox'
);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices;

-- Verify
SELECT 'Remaining paddles: ' || COUNT(*) as status FROM paddles;

COMMIT;
