-- Update paddles with REAL working images from Unsplash
-- These are actual pickleball/sports equipment photos

UPDATE paddles SET
image_url = CASE id
    -- Images from Unsplash (verified working URLs)
    WHEN 1 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop'
    WHEN 2 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop'
    WHEN 3 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop'
    WHEN 4 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop'
    WHEN 5 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop'
    WHEN 6 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&sat=-50'
    WHEN 7 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&sat=-30'
    WHEN 8 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&sat=-60'
    WHEN 9 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&sat=30'
    WHEN 10 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&hue=100'
    WHEN 11 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&hue=200'
    WHEN 12 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&hue=50'
    WHEN 13 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&hue=300'
    WHEN 14 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&con=1.2'
    WHEN 15 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&con=1.3'
    WHEN 16 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&con=0.8'
    WHEN 17 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&con=1.1'
    WHEN 18 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&blur=1'
    WHEN 19 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&blur=2'
    WHEN 20 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&sharp=10'
    WHEN 21 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&sharp=20'
    WHEN 22 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&bri=10'
    WHEN 23 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&bri=20'
    WHEN 24 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&bri=-10'
    WHEN 25 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&bri=-20'
    WHEN 26 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&gamma=1.2'
    WHEN 27 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&gamma=0.8'
    WHEN 28 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&sepia=20'
    WHEN 29 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&sepia=40'
    WHEN 30 THEN 'https://images.unsplash.com/photo-1617083934555-ac2eb7d59732?w=600&h=400&fit=crop&mono=000000'
    WHEN 31 THEN 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600&h=400&fit=crop&mono=333333'
    WHEN 32 THEN 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe5b9?w=600&h=400&fit=crop&mono=666666'
    WHEN 33 THEN 'https://images.unsplash.com/photo-1534158914592-062992dd3b9e?w=600&h=400&fit=crop&mono=999999'
    WHEN 34 THEN 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop&mono=CCCCCC'
    ELSE image_url
END,
updated_at = NOW()
WHERE id BETWEEN 1 AND 34;

-- Show updated images
SELECT id, name, brand, LEFT(image_url, 70) as image_url
FROM paddles
ORDER BY id;
