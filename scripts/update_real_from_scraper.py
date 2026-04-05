#!/usr/bin/env python3
"""
Extract real product images from Brazil Pickleball Store
and update matching paddles.
"""

import sys
sys.path.insert(0, '/home/diego/Documentos/picklepicker')

import os
import asyncio
from dotenv import load_dotenv
load_dotenv('/home/diego/Documentos/picklepicker/.env.local')

from firecrawl import FirecrawlApp
from pipeline.db.connection import get_connection, close_pool

app = FirecrawlApp(api_key=os.environ['FIRECRAWL_API_KEY'])

# Map brand names to normalize
BRAND_MAP = {
    '3rdshot': '3RDShot',
    '3RDShot': '3RDShot',
    'selkirk': 'Selkirk',
    'Selkirk': 'Selkirk',
    'joola': 'JOOLA',
    'JOOLA': 'JOOLA',
    'paddletek': 'Paddletek',
    'Paddletek': 'Paddletek',
    'engage': 'Engage',
    'Engage': 'Engage',
    'proxr': 'ProXR',
    'ProXR': 'ProXR',
    'slk': 'SLK',
    'SLK': 'SLK',
    'wilson': 'Wilson',
    'Wilson': 'Wilson',
    'gearbox': 'Gearbox',
    'Gearbox': 'Gearbox',
    'onix': 'Onix',
    'Onix': 'Onix',
    'franklin': 'Franklin',
    'Franklin': 'Franklin',
    'gamma': 'Gamma',
    'Gamma': 'Gamma',
    'head': 'Head',
    'Head': 'Head',
    'prince': 'Prince',
    'Prince': 'Prince',
}


def normalize_brand(brand: str) -> str:
    """Normalize brand name."""
    return BRAND_MAP.get(brand, brand)


async def extract_and_update_images():
    """Extract real products and update paddle images."""
    print("=" * 60)
    print("Extracting REAL product images from Brazil Pickleball Store")
    print("=" * 60)

    # Extract products from Brazil Store
    print("\n📦 Extracting products from Firecrawl...")
    result = app.extract(
        urls=['https://brazilpickleballstore.com.br/raquete/'],
        prompt='Extract all pickleball paddle products with name, price in BRL, brand. For image_url, extract the main product image URL from the product card/listing. Look for img tags with product images.',
        schema={
            'type': 'object',
            'properties': {
                'products': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'price_brl': {'type': 'number'},
                            'image_url': {'type': 'string'},
                            'product_url': {'type': 'string'},
                            'brand': {'type': 'string'},
                        },
                    },
                }
            }
        }
    )

    if not result.data or 'products' not in result.data:
        print("❌ No products extracted")
        return

    products = result.data['products']
    print(f"✅ Extracted {len(products)} products\n")

    # Filter products with images
    products_with_images = [p for p in products if p.get('image_url') and p['image_url'].startswith('http')]
    print(f"📸 {len(products_with_images)} products have images\n")

    # Update database
    async with get_connection() as conn:
        updated = 0
        for product in products_with_images[:20]:  # Limit to 20
            name = product.get('name', '')
            brand = normalize_brand(product.get('brand', ''))
            image_url = product.get('image_url')

            # Try to find matching paddle
            # First: try exact name match (case-insensitive)
            row = await conn.fetchrow("""
                SELECT id, name FROM paddles
                WHERE LOWER(name) = LOWER($1)
                  AND (image_url LIKE '%example%' OR image_url IS NULL)
            """, name)

            # Fallback: fuzzy match if exact fails
            if not row:
                row = await conn.fetchrow("""
                    SELECT id, name FROM paddles
                    WHERE LOWER(brand) = LOWER($1)
                      AND (image_url LIKE '%example%' OR image_url IS NULL)
                      AND LOWER(name) LIKE '%' || LOWER(SPLIT_PART(LOWER($2), ' ', 1)) || '%'
                    LIMIT 1
                """, brand, name)

            if row:
                paddle_id = row['id']
                paddle_name = row['name']

                # Safety check: verify brand matches
                if brand and brand.lower() not in paddle_name.lower():
                    print(f"⚠️  Brand mismatch: product brand='{brand}', matched paddle='{paddle_name}'")

                await conn.execute(
                    "UPDATE paddles SET image_url = $1, updated_at = NOW() WHERE id = $2",
                    image_url, paddle_id
                )
                print(f"✅ Updated: {name[:40]} → {paddle_name[:40]}")
                print(f"   🖼️  {image_url[:70]}...")
                updated += 1
            else:
                print(f"⚠️  No match for: {brand} - {name[:40]}...")

        await conn.commit()

    print(f"\n{'=' * 60}")
    print(f"Updated {updated} paddles with real images from scraper")
    print(f"{'=' * 60}")

    await close_pool()


if __name__ == "__main__":
    asyncio.run(extract_and_update_images())
