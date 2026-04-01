#!/usr/bin/env python3
"""
Extract real product images from Brazil Pickleball Store.

This script:
1. Extracts all products from the category page using Firecrawl extract()
2. For each product, scrapes the product page to get the image URL
3. Updates the database with the real image URLs
"""

import os
import sys
import re
import time
import asyncio
from typing import Optional
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add parent to path
sys.path.insert(0, '/home/diego/Documentos/picklepicker')

from pipeline.db.connection import get_connection

# Configuration
BRAZIL_STORE_URL = "https://www.brazilpickleballstore.com.br/raquete/"
BATCH_SIZE = 5  # Process in batches to avoid rate limiting


def get_firecrawl_app():
    """Initialize Firecrawl app with API key."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")
    return FirecrawlApp(api_key=api_key)


def extract_products_from_category(app: FirecrawlApp) -> list[dict]:
    """Extract products from category page using search."""
    print("📦 Extracting products using Firecrawl search...")

    # Use search to find product URLs
    result = app.search("site:brazilpickleballstore.com.br/produtos/ raquete pickleball")

    products = []
    if hasattr(result, 'web'):
        for item in result.web:
            if '/produtos/' in item.url.lower():
                products.append({
                    'name': item.title,
                    'product_url': item.url
                })

    print(f"✅ Found {len(products)} products")
    return products


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def extract_image_from_product_page(app: FirecrawlApp, product_url: str) -> Optional[str]:
    """Scrape product page and extract image URL."""
    try:
        result = app.scrape(product_url)

        if hasattr(result, 'markdown'):
            md = result.markdown
        elif isinstance(result, dict):
            md = result.get('markdown', '')
        else:
            return None

        # Look for mitiendanube image URLs
        img_pattern = r'(https?://[^\s\)]+\.mitiendanube\.com[^\s\)]*\.(?:jpg|jpeg|png|webp))'
        matches = re.findall(img_pattern, md, re.IGNORECASE)

        if matches:
            # Return first match, transformed to smaller size
            img_url = matches[0]
            return img_url.replace('-1024-1024', '-480-0')

        return None
    except Exception as e:
        print(f"  ⚠️ Error scraping {product_url}: {e}")
        return None


async def insert_product_with_image(conn, product: dict, image_url: str) -> bool:
    """Insert new product with image URL into database."""
    try:
        name = product.get('name', 'Unknown Product')

        # Extract brand and model from name
        words = name.split()
        brand = words[0] if words else 'Unknown'

        # Use remaining words as model (or same as name if only one word)
        model = ' '.join(words[1:]) if len(words) > 1 else name

        # Create model_slug from name
        import re
        model_slug = re.sub(r'[^\w\s-]', '', name.lower())
        model_slug = re.sub(r'[-\s]+', '-', model_slug)

        # Insert new paddle with all required fields
        result = await conn.execute(
            """
            INSERT INTO paddles (name, brand, model, model_slug, image_url, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id, name
            """,
            (name, brand, model, model_slug, image_url)
        )

        inserted = await result.fetchone()
        if inserted:
            await conn.commit()
            return True
        return False
    except Exception as e:
        print(f"  ⚠️ Error inserting into database: {e}")
        return False


async def extract_and_update_images():
    """Main function to extract images and update database."""
    print("🚀 Starting image extraction process...")
    print(f"📍 Category URL: {BRAZIL_STORE_URL}")
    print()

    # Initialize Firecrawl
    app = get_firecrawl_app()

    # Extract products
    products = extract_products_from_category(app)

    if not products:
        print("❌ No products found")
        return 0

    # Process all products found
    print(f"\n⚡ Processing all {len(products)} products")

    # Track statistics
    stats = {
        'total': len(products),
        'with_images': 0,
        'updated': 0,
        'failed': 0
    }

    # Connect to database
    async with get_connection() as conn:
        print("\n🖼️ Extracting images from product pages...")
        print(f"⏱️ This will take approximately {len(products)} seconds due to rate limiting")
        print()

        for i, product in enumerate(products):
            name = product.get('name', 'Unknown')
            product_url = product.get('product_url', '')

            print(f"[{i+1}/{len(products)}] {name[:50]}...")

            if not product_url:
                print("  ⚠️ No product URL")
                stats['failed'] += 1
                continue

            # Extract image from product page
            image_url = extract_image_from_product_page(app, product_url)

            if image_url:
                print(f"  ✅ Image found: {image_url[:60]}...")
                stats['with_images'] += 1

                # Insert into database
                if await insert_product_with_image(conn, product, image_url):
                    print(f"  ✅ Database updated")
                    stats['updated'] += 1
                else:
                    print(f"  ⚠️ Could not update database (product not found or already has image)")
            else:
                print(f"  ❌ No image found")
                stats['failed'] += 1

            # Rate limiting
            if i < len(products) - 1:
                time.sleep(1)

    # Print summary
    print("\n" + "="*60)
    print("📊 EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total products: {stats['total']}")
    print(f"Images found: {stats['with_images']}")
    print(f"Database updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    print(f"Success rate: {(stats['with_images'] / stats['total'] * 100):.1f}%")
    print("="*60)

    return stats['updated']


if __name__ == "__main__":
    try:
        count = asyncio.run(extract_and_update_images())
        print(f"\n✅ Successfully updated {count} products with real images")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
