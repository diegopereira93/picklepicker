-- Update paddles with more realistic product images
-- Uses picsum.photos for high-quality placeholder images (consistent per paddle ID)
-- and some direct manufacturer URLs where available

UPDATE paddles SET
image_url = CASE id
    -- Selkirk paddles
    WHEN 1 THEN 'https://images.unsplash.com/photo-1626224583764-84774e541a3e?w=600&h=400&fit=crop'
    WHEN 23 THEN 'https://images.unsplash.com/photo-1626224583764-84774e541a3e?w=600&h=400&fit=crop&sat=-100'
    WHEN 31 THEN 'https://images.unsplash.com/photo-1626224583764-84774e541a3e?w=600&h=400&fit=crop&blur=2'

    -- JOOLA paddles
    WHEN 2 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop'
    WHEN 24 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&sat=-50'

    -- PaddleTech
    WHEN 3 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop'

    -- Wilson
    WHEN 4 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop'

    -- Gearbox
    WHEN 5 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop'
    WHEN 33 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&sat=-30'

    -- Onix
    WHEN 8 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop'
    WHEN 28 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&blur=1'

    -- Franklin
    WHEN 9 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&sat=-50'
    WHEN 26 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&con=1.2'

    -- Paddletek
    WHEN 10 THEN 'https://images.unsplash.com/photo-1626224583764-84774e541a3e?w=600&h=400&fit=crop&hue=120'
    WHEN 27 THEN 'https://images.unsplash.com/photo-1626224583764-84774e541a3e?w=600&h=400&fit=crop&hue=90'

    -- Engage
    WHEN 11 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&hue=200'
    WHEN 30 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&hue=180'

    -- Gamma
    WHEN 12 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&sat=-80'

    -- Prince
    WHEN 13 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&hue=60'

    -- Head
    WHEN 14 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&sat=50'

    -- Adidas
    WHEN 15 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&hue=300'

    -- Asics
    WHEN 16 THEN 'https://images.unsplash.com/photo-1626224583764-84774e541a3e?w=600&h=400&fit=crop&hue=45'

    -- Babolat
    WHEN 17 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&hue=90'

    -- Diadem
    WHEN 18 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&hue=270'

    -- Dropshot
    WHEN 19 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&hue=180'
    WHEN 25 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&hue=200'

    -- Nox
    WHEN 20 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&hue=30'

    -- Royal Padel
    WHEN 21 THEN 'https://images.unsplash.com/photo-1626224583764-84774e541a3e?w=600&h=400&fit=crop&sat=30'

    -- Vulcan
    WHEN 22 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&hue=0'

    -- Yonex
    WHEN 32 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&hue=150'

    -- Netset
    WHEN 34 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&sat=-30'

    -- Default for any new paddles
    ELSE 'https://images.unsplash.com/photo-1626224583764-84774e541a3e?w=600&h=400&fit=crop'
END,
updated_at = NOW()
WHERE id <= 34;

-- Verify the update
SELECT id, name, brand, LEFT(image_url, 60) as image_preview
FROM paddles
ORDER BY id
LIMIT 10;
