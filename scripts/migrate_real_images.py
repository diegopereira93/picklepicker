#!/usr/bin/env python3
"""
Migrate real product images from price_snapshots.source_raw to paddles.image_url.

This script extracts real product images from previously scraped data in the
price_snapshots table and updates the paddles table with legitimate product images.
"""

import os
import sys
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import psycopg3 for database connections
import psycopg


def validate_image_url(url):
    """Validate if an image URL is from a trusted domain."""
    if not url or not url.startswith('http'):
        return False
    
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        # Trusted domains
        trusted_domains = [
            'mitiendanube.com',      # Brazil Store CDN
            'mlstatic.com',          # Mercado Livre CDN
            'mercadolivre.com.br',   # Mercado Livre
            'dropshotbrasil.com.br'  # Dropshot
        ]
        
        # Allow any HTTPS URL that isn't obviously placeholder
        if domain and not any(placeholder in domain for placeholder in ['placehold.co', 'unsplash.com', 'example.com']):
            return True
            
        # Or from trusted domains
        if any(trusted in domain for trusted in trusted_domains):
            return True
            
        return False
    except Exception:
        return False


def main():
    """Main entry point for migrating real product images."""
    print("=" * 60)
    print("Migrating REAL product images from source_raw to paddles")
    print("=" * 60)
    
    # Database connection
    try:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
            
        conn = psycopg.connect(database_url)
        cur = conn.cursor()
        print("✅ Connected to database successfully")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return 1
    
    try:
        # Statistics tracking
        stats = {
            'source_images_found': 0,
            'paddles_updated_source': 0,
            'paddles_updated_ml': 0,
            'paddles_cleaned': 0
        }
        
        # 1. Extract real images from price_snapshots.source_raw
        print("\n🔍 Extracting real images from price_snapshots.source_raw...")
        cur.execute("""
            SELECT source_raw->>'image_url' as image_url,
                   source_raw->>'thumbnail' as thumbnail,
                   source_raw->>'name' as product_name
            FROM price_snapshots
            WHERE source_raw->>'image_url' IS NOT NULL
              AND source_raw->>'image_url' NOT LIKE '%placehold.co%'
              AND source_raw->>'image_url' NOT LIKE '%unsplash%'
        """)
        
        source_images = cur.fetchall()
        stats['source_images_found'] = len(source_images)
        print(f"✅ Found {stats['source_images_found']} potential real images")
        
        # 2. For each source_raw image, match to paddles by name and update
        print("\n🔄 Updating paddles with source_raw images...")
        for image_url, thumbnail, product_name in source_images:
            # Prefer thumbnail if image_url is not valid
            url_to_use = image_url if validate_image_url(image_url) else thumbnail
            
            if not url_to_use:
                continue
                
            if validate_image_url(url_to_use):
                try:
                    # Use % for LIKE pattern matching
                    pattern = '%' + product_name.lower().replace('%', '') + '%'
                    
                    cur.execute("""
                        UPDATE paddles SET image_url = %s, updated_at = NOW()
                        WHERE LOWER(name) LIKE %s
                          AND (image_url IS NULL OR image_url LIKE '%%placehold.co%%' OR image_url LIKE '%%unsplash%%')
                    """, (url_to_use, pattern))
                    
                    if cur.rowcount > 0:
                        stats['paddles_updated_source'] += cur.rowcount
                        
                except Exception as e:
                    print(f"⚠️  Warning: Could not update paddle '{product_name}' - {e}")
        
        print(f"✅ Updated {stats['paddles_updated_source']} paddles from source_raw data")
        
        # 3. Handle Mercado Livre paddles - copy from images TEXT array
        print("\n🔄 Updating Mercado Livre paddles from images array...")
        cur.execute("""
            UPDATE paddles SET image_url = images[1], updated_at = NOW()
            WHERE images IS NOT NULL AND array_length(images, 1) > 0
              AND (image_url IS NULL OR image_url LIKE '%%placehold.co%%' OR image_url LIKE '%%unsplash%%')
        """)
        
        stats['paddles_updated_ml'] = cur.rowcount
        print(f"✅ Updated {stats['paddles_updated_ml']} Mercado Livre paddles")
        
        # 4. Clean remaining fabricated URLs
        print("\n🧹 Cleaning remaining placeholder URLs...")
        cur.execute("""
            UPDATE paddles SET image_url = NULL, updated_at = NOW()
            WHERE image_url LIKE '%%placehold.co%%' OR image_url LIKE '%%unsplash%%' OR image_url LIKE '%%example%%'
        """)
        
        stats['paddles_cleaned'] = cur.rowcount
        print(f"✅ Cleaned {stats['paddles_cleaned']} placeholder URLs")
        
        # 5. Commit all changes
        conn.commit()
        print("\n💾 All changes committed to database")
        
        # 6. Report statistics
        print("\n📊 Final Statistics:")
        cur.execute("SELECT COUNT(*) as total FROM paddles")
        total_paddles = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) as has_image FROM paddles WHERE image_url IS NOT NULL")
        paddles_with_image = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) as null_image FROM paddles WHERE image_url IS NULL")
        paddles_without_image = cur.fetchone()[0]
        
        print(f"   Total paddles: {total_paddles}")
        print(f"   Paddles with images: {paddles_with_image}")
        print(f"   Paddles without images: {paddles_without_image}")
        print(f"   Source images processed: {stats['source_images_found']}")
        print(f"   Updated from source_raw: {stats['paddles_updated_source']}")
        print(f"   Updated from ML images: {stats['paddles_updated_ml']}")
        print(f"   Cleaned placeholders: {stats['paddles_cleaned']}")
        
        print(f"\n{'=' * 60}")
        print("Migration completed successfully!")
        print(f"{'=' * 60}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        return 1
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("🔒 Database connection closed")


if __name__ == "__main__":
    sys.exit(main())