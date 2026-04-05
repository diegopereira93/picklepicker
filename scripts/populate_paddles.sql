-- Populate paddles table with realistic data.
-- Images: Run scripts/migrate_real_images.py after seeding to populate image_url
--   with real product photos from retailers. Paddles without real images will
--   have image_url = NULL, triggering the "Foto" placeholder in the UI.
--
-- NEVER use placehold.co, unsplash.com, or any non-product image URL.
-- Run with: docker compose exec -T postgres psql -U pickleiq -d pickleiq < scripts/populate_paddles.sql

-- First, update existing paddles — set all fabricated URLs to NULL
UPDATE paddles
SET image_url = NULL, updated_at = NOW()
WHERE image_url LIKE '%placehold.co%' OR image_url LIKE '%unsplash%' OR image_url LIKE '%example%';

-- Insert paddles with realistic data (model is required)
-- image_url is intentionally NULL — run migrate_real_images.py to populate with real photos
INSERT INTO paddles (name, brand, model, manufacturer_sku, image_url, skill_level, in_stock, model_slug, price_min_brl, created_at)
VALUES
    ('Vanguard Power Air', 'Selkirk', 'Vanguard Power Air', 'SLK-VPA-001', NULL, 'advanced', true, 'vanguard-power-air', 1299.00, NOW()),
    ('Ben Johns Hyperion', 'JOOLA', 'Ben Johns Hyperion', 'JOO-BJH-001', NULL, 'advanced', true, 'ben-johns-hyperion', 1499.00, NOW()),
    ('SLK Evo Soft', 'Selkirk', 'SLK Evo Soft', 'SLK-EVS-001', NULL, 'intermediate', true, 'slk-evo-soft', 799.00, NOW()),
    ('Vision CGS', 'JOOLA', 'Vision CGS', 'JOO-VIS-001', NULL, 'intermediate', true, 'vision-cgs', 999.00, NOW()),
    ('Outbreak', 'Onix', 'Outbreak', 'ONX-OUT-001', NULL, 'intermediate', true, 'outbreak', 899.00, NOW()),
    ('Sports Pro', 'Franklin', 'Sports Pro', 'FRK-PRO-001', NULL, 'beginner', true, 'sports-pro', 599.00, NOW()),
    ('Tempest Pro', 'Paddletek', 'Tempest Pro', 'PTK-TEM-001', NULL, 'advanced', true, 'tempest-pro', 1099.00, NOW()),
    ('Encore Pro', 'Engage', 'Encore Pro', 'ENG-ENC-001', NULL, 'advanced', true, 'encore-pro', 1199.00, NOW()),
    ('Needle', 'Gamma', 'Needle', 'GAM-NDL-001', NULL, 'beginner', true, 'needle', 499.00, NOW()),
    ('Response Pro', 'Prince', 'Response Pro', 'PRI-RSP-001', NULL, 'intermediate', true, 'response-pro', 649.00, NOW()),
    ('Radical Pro', 'Head', 'Radical Pro', 'HD-RAD-001', NULL, 'advanced', true, 'radical-pro', 1399.00, NOW()),
    ('Drive Pro', 'Adidas', 'Drive Pro', 'ADI-DRV-001', NULL, 'advanced', false, 'drive-pro', 1299.00, NOW()),
    ('Vanguard Control', 'Selkirk', 'Vanguard Control', 'SLK-VCT-001', NULL, 'intermediate', true, 'vanguard-control', 1199.00, NOW()),
    ('S2', 'Selkirk', 'S2', 'SLK-S2-001', NULL, 'intermediate', true, 's2', 899.00, NOW())
ON CONFLICT DO NOTHING;

-- Verify results
SELECT 'Total paddles: ' || COUNT(*) as status FROM paddles;
SELECT 'Sample image URLs:';
SELECT id, name, image_url FROM paddles LIMIT 5;
