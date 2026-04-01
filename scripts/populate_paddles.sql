-- Populate paddles table with more realistic data and valid image URLs
-- Run with: docker compose exec -T postgres psql -U pickleiq -d pickleiq < scripts/populate_paddles.sql

-- First, update existing paddles with proper image URLs
UPDATE paddles
SET image_url = CASE
    WHEN name LIKE '%Selkirk%' THEN 'https://placehold.co/600x400/1e3a8a/white?text=Selkirk+Vanguard'
    WHEN name LIKE '%JOOLA%' THEN 'https://placehold.co/600x400/dc2626/white?text=JOOLA+Hyperion'
    WHEN name LIKE '%PaddleTech%' THEN 'https://placehold.co/600x400/16a34a/white?text=PaddleTech+Pro'
    WHEN name LIKE '%Wilson%' THEN 'https://placehold.co/600x400/ca8a04/white?text=Wilson+Camo'
    WHEN name LIKE '%Gearbox%' THEN 'https://placehold.co/600x400/7c3aed/white?text=Gearbox+Pro'
    ELSE 'https://placehold.co/600x400/374151/white?text=Pickleball+Paddle'
END
WHERE image_url LIKE '%example.com%' OR image_url IS NULL;

-- Insert more paddles with realistic data (model is required)
INSERT INTO paddles (name, brand, model, manufacturer_sku, image_url, skill_level, in_stock, model_slug, price_min_brl, created_at)
VALUES
    ('Vanguard Power Air', 'Selkirk', 'Vanguard Power Air', 'SLK-VPA-001', 'https://placehold.co/600x400/1e3a8a/white?text=Selkirk+Vanguard', 'advanced', true, 'vanguard-power-air', 1299.00, NOW()),
    ('Ben Johns Hyperion', 'JOOLA', 'Ben Johns Hyperion', 'JOO-BJH-001', 'https://placehold.co/600x400/dc2626/white?text=JOOLA+Hyperion', 'advanced', true, 'ben-johns-hyperion', 1499.00, NOW()),
    ('SLK Evo Soft', 'Selkirk', 'SLK Evo Soft', 'SLK-EVS-001', 'https://placehold.co/600x400/2563eb/white?text=Selkirk+Evo', 'intermediate', true, 'slk-evo-soft', 799.00, NOW()),
    ('Vision CGS', 'JOOLA', 'Vision CGS', 'JOO-VIS-001', 'https://placehold.co/600x400/db2777/white?text=JOOLA+Vision', 'intermediate', true, 'vision-cgs', 999.00, NOW()),
    ('Outbreak', 'Onix', 'Outbreak', 'ONX-OUT-001', 'https://placehold.co/600x400/ea580c/white?text=Onix+Outbreak', 'intermediate', true, 'outbreak', 899.00, NOW()),
    ('Sports Pro', 'Franklin', 'Sports Pro', 'FRK-PRO-001', 'https://placehold.co/600x400/0891b2/white?text=Franklin+Pro', 'beginner', true, 'sports-pro', 599.00, NOW()),
    ('Tempest Pro', 'Paddletek', 'Tempest Pro', 'PTK-TEM-001', 'https://placehold.co/600x400/65a30d/white?text=Paddletek+Tempest', 'advanced', true, 'tempest-pro', 1099.00, NOW()),
    ('Encore Pro', 'Engage', 'Encore Pro', 'ENG-ENC-001', 'https://placehold.co/600x400/9333ea/white?text=Engage+Encore', 'advanced', true, 'encore-pro', 1199.00, NOW()),
    ('Needle', 'Gamma', 'Needle', 'GAM-NDL-001', 'https://placehold.co/600x400/be123c/white?text=Gamma+Needle', 'beginner', true, 'needle', 499.00, NOW()),
    ('Response Pro', 'Prince', 'Response Pro', 'PRI-RSP-001', 'https://placehold.co/600x400/4f46e5/white?text=Prince+Response', 'intermediate', true, 'response-pro', 649.00, NOW()),
    ('Radical Pro', 'Head', 'Radical Pro', 'HD-RAD-001', 'https://placehold.co/600x400/059669/white?text=Head+Radical', 'advanced', true, 'radical-pro', 1399.00, NOW()),
    ('Drive Pro', 'Adidas', 'Drive Pro', 'ADI-DRV-001', 'https://placehold.co/600x400/dc2626/white?text=Adidas+Drive', 'advanced', false, 'drive-pro', 1299.00, NOW()),
    ('Speed Pro', 'Asics', 'Speed Pro', 'ASC-SPD-001', 'https://placehold.co/600x400/2563eb/white?text=Asics+Speed', 'intermediate', true, 'speed-pro', 849.00, NOW()),
    ('MNSTR Power', 'Babolat', 'MNSTR Power', 'BAB-MNS-001', 'https://placehold.co/600x400/eab308/black?text=Babolat+MNSTR', 'advanced', true, 'mnstr-power', 1599.00, NOW()),
    ('Warrior V2', 'Diadem', 'Warrior V2', 'DIA-WAR-001', 'https://placehold.co/600x400/c2410c/white?text=Diadem+Warrior', 'advanced', true, 'warrior-v2', 1349.00, NOW()),
    ('Power Pro', 'Dropshot', 'Power Pro', 'DSP-PWR-001', 'https://placehold.co/600x400/0284c7/white?text=Dropshot+Power', 'intermediate', true, 'power-pro', 749.00, NOW()),
    ('AT10 Genius', 'Nox', 'AT10 Genius', 'NOX-AT10-001', 'https://placehold.co/600x400/7c2d12/white?text=Nox+AT10', 'advanced', true, 'at10-genius', 1699.00, NOW()),
    ('RP790', 'Royal Padel', 'RP790', 'RP-RP790-001', 'https://placehold.co/600x400/1e40af/white?text=Royal+Padel', 'beginner', true, 'rp790', 579.00, NOW()),
    ('Vanguard Control', 'Selkirk', 'Vanguard Control', 'SLK-VCT-001', 'https://placehold.co/600x400/4338ca/white?text=Selkirk+Control', 'intermediate', true, 'vanguard-control', 1199.00, NOW()),
    ('V730', 'Vulcan', 'V730', 'VLC-V730-001', 'https://placehold.co/600x400/b91c1c/white?text=Vulcan+V730', 'advanced', true, 'v730', 1099.00, NOW()),
    ('EZONE Plus', 'Yonex', 'EZONE Plus', 'YNX-EZP-001', 'https://placehold.co/600x400/15803d/white?text=Yonex+EZONE', 'intermediate', true, 'ezone-plus', 949.00, NOW()),
    ('Pro XR', 'Gearbox', 'Pro XR', 'GBX-PXR-001', 'https://placehold.co/600x400/7c3aed/white?text=Gearbox+XR', 'advanced', true, 'pro-xr', 1249.00, NOW()),
    ('S2', 'Selkirk', 'S2', 'SLK-S2-001', 'https://placehold.co/600x400/1d4ed8/white?text=Selkirk+S2', 'intermediate', true, 's2', 899.00, NOW()),
    ('Carbon 1', 'Netset', 'Carbon 1', 'NTS-C1-001', 'https://placehold.co/600x400/0e7490/white?text=Netset+Carbon', 'beginner', true, 'carbon-1', 349.00, NOW())
ON CONFLICT DO NOTHING;

-- Verify results
SELECT 'Total paddles: ' || COUNT(*) as status FROM paddles;
SELECT 'Sample image URLs:';
SELECT id, name, image_url FROM paddles LIMIT 5;
