#!/usr/bin/env python3
"""
Extract real product images from scraped product pages
and update the paddles table.
"""

import sys
import re
sys.path.insert(0, '/home/diego/Documentos/picklepicker')

import os
import asyncio
from dotenv import load_dotenv
load_dotenv('/home/diego/Documentos/picklepicker/.env.local')

from firecrawl import FirecrawlApp
from pipeline.db.connection import get_connection, close_pool

app = FirecrawlApp(api_key=os.environ['FIRECRAWL_API_KEY'])


def extract_image_from_markdown(markdown: str) -> str | None:
    """Extract the first image URL from markdown."""
    # Look for image markdown pattern: ![alt](url)
    pattern = r'!\[.*?\]\((https?://[^)]+)\)'
    matches = re.findall(pattern, markdown)

    for match in matches:
        # Filter for actual product images (not logos, icons, etc)
        if any(ext in match.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
            if 'mitiendanube.com' in match or 'cdn' in match or 'product' in match:
                return match

    return None


async def update_paddle_image(paddle_id: int, product_url: str, name: str):
    """Scrape product page and update paddle with real image."""
    try:
        print(f"Scraping: {name[:50]}...")
        result = app.scrape(product_url)

        if hasattr(result, 'markdown') and result.markdown:
            image_url = extract_image_from_markdown(result.markdown)

            if image_url:
                print(f"  ✅ Found image: {image_url[:80]}...")

                # Update database
                async with get_connection() as conn:
                    await conn.execute(
                        "UPDATE paddles SET image_url = $1, updated_at = NOW() WHERE id = $2",
                        image_url, paddle_id
                    )
                    await conn.commit()
                print(f"  ✅ Updated paddle {paddle_id}")
                return True
            else:
                print(f"  ❌ No image found in markdown")
        else:
            print(f"  ❌ No markdown in result")

    except Exception as e:
        print(f"  ❌ Error: {e}")

    return False


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Extracting REAL product images from scraped data")
    print("=" * 60)

    # Get products from price_snapshots with URLs
    async with get_connection() as conn:
        # Phase 1: Exact name matching (normalized, trimmed)
        result = await conn.execute("""
            SELECT DISTINCT ON (ps.id)
                p.id as paddle_id,
                ps.source_raw->>'name' as product_name,
                ps.affiliate_url as product_url,
                'exact' as match_type
            FROM price_snapshots ps
            JOIN paddles p ON LOWER(TRIM(ps.source_raw->>'name')) = LOWER(TRIM(p.name))
            WHERE ps.affiliate_url IS NOT NULL
              AND ps.affiliate_url != ''
              AND (p.image_url LIKE '%example%' OR p.image_url IS NULL)
            LIMIT 20
        """)

        rows = list(await result.fetchall())
        exact_count = len(rows)
        print(f"Exact matches: {exact_count}")

        # Phase 2: Fuzzy matching for paddles without exact matches
        fuzzy_result = await conn.execute("""
            SELECT DISTINCT ON (ps.id)
                p.id as paddle_id,
                ps.source_raw->>'name' as product_name,
                ps.affiliate_url as product_url,
                'fuzzy' as match_type
            FROM price_snapshots ps
            JOIN paddles p ON LOWER(ps.source_raw->>'name') LIKE '%' || LOWER(p.name) || '%'
                AND LOWER(p.name) LIKE '%' || LOWER(SPLIT_PART(TRIM(ps.source_raw->>'name'), ' ', 1)) || '%'
            WHERE ps.affiliate_url IS NOT NULL
              AND ps.affiliate_url != ''
              AND (p.image_url LIKE '%example%' OR p.image_url IS NULL)
              AND NOT EXISTS (
                  SELECT 1 FROM paddles p2
                  WHERE LOWER(TRIM(ps.source_raw->>'name')) = LOWER(TRIM(p2.name))
              )
            LIMIT 10
        """)

        fuzzy_rows = await fuzzy_result.fetchall()
        rows.extend(fuzzy_rows)
        fuzzy_count = len(fuzzy_rows)
        print(f"Fuzzy matches: {fuzzy_count}")
        print(f"Total products to scrape: {len(rows)}\n")

        for row in rows:
            match_type = row['match_type']
            product_name = row['product_name']
            paddle_id = row['paddle_id']
            label = "EXACT" if match_type == 'exact' else "FUZZY"
            print(f"  [{label}] Paddle {paddle_id}: {product_name[:60]}")
        print()

        updated = 0
        for row in rows:
            paddle_id = row['paddle_id']
            name = row['product_name']
            url = row['product_url']

            if await update_paddle_image(paddle_id, url, name):
                updated += 1

        print(f"\n{'=' * 60}")
        print(f"Updated {updated} paddles with real images ({exact_count} exact, {fuzzy_count} fuzzy)")
        print(f"{'=' * 60}")

    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
