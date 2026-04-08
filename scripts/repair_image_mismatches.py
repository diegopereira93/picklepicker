#!/usr/bin/env python3
"""
Repair script for paddle image mismatches.

Smart repair: only clears images that are likely wrong by cross-referencing
with source_raw data. Preserves images that match their paddle name exactly.

Strategy:
1. For each paddle with an image, check if source_raw has a DIFFERENT image
   for the same paddle name — if so, the current image is likely wrong
2. Clear only the mismatched images (not all images)
3. Re-associate cleared paddles with correct images from source_raw

Usage:
    python scripts/repair_image_mismatches.py        # Dry run
    python scripts/repair_image_mismatches.py --apply # Apply fixes
"""

import sys
sys.path.insert(0, '/home/diego/Documentos/picklepicker')

import os
import argparse
import asyncio
from dotenv import load_dotenv
load_dotenv('/home/diego/Documentos/picklepicker/.env.local')

from pipeline.db.connection import get_connection, close_pool


async def find_mismatched_images(conn):
    """Find paddles where source_raw has a different image for the same name.

    Only flags images as wrong if source_raw contains a different URL for the
    exact same paddle name. This avoids clearing correctly matched images.
    """
    result = await conn.execute("""
        SELECT
            p.id,
            p.name,
            p.brand,
            p.image_url as current_image,
            src.source_image,
            src.source_name
        FROM paddles p
        INNER JOIN (
            SELECT
                source_raw->>'name' as sname,
                source_raw->>'name' as source_name,
                source_raw->>'image_url' as source_image
            FROM price_snapshots
            WHERE source_raw->>'image_url' IS NOT NULL
              AND source_raw->>'image_url' != ''
              AND source_raw->>'image_url' NOT LIKE '%%placehold.co%%'
              AND source_raw->>'image_url' NOT LIKE '%%unsplash%%'
              AND source_raw->>'image_url' NOT LIKE '%%example%%'
            GROUP BY source_raw->>'name', source_raw->>'image_url'
        ) src ON LOWER(TRIM(src.sname)) = LOWER(TRIM(p.name))
        WHERE p.image_url IS NOT NULL
          AND p.image_url != ''
          AND p.image_url != src.source_image
        ORDER BY p.brand, p.name
    """)
    rows = await result.fetchall()

    mismatches = []
    for row in rows:
        mismatches.append({
            'paddle_id': row[0],
            'paddle_name': row[1],
            'brand': row[2],
            'current_image': row[3],
            'correct_image': row[4],
            'source_name': row[5],
        })

    return mismatches


async def clear_mismatched_images(conn, mismatches, dry_run=True):
    """Clear only the images that are confirmed wrong."""
    if dry_run:
        print(f"  [DRY RUN] Would clear {len(mismatches)} mismatched images")
        for m in mismatches[:10]:
            print(f"    {m['brand']} - {m['paddle_name'][:50]}")
            print(f"      Current: {m['current_image'][:70]}...")
            print(f"      Correct: {m['correct_image'][:70]}...")
        if len(mismatches) > 10:
            print(f"    ... and {len(mismatches) - 10} more")
    else:
        cleared = 0
        for m in mismatches:
            await conn.execute(
                "UPDATE paddles SET image_url = NULL, updated_at = NOW() WHERE id = %s",
                (m['paddle_id'],)
            )
            cleared += 1
        await conn.commit()
        print(f"  Cleared {cleared} mismatched images")

    return len(mismatches)


async def reassociate_images(conn, dry_run=True):
    """Re-associate cleared images from source_raw using exact name matching."""
    result = await conn.execute("""
        SELECT id, name, brand FROM paddles
        WHERE image_url IS NULL OR image_url = ''
        ORDER BY brand, name
    """)
    paddles_no_image = await result.fetchall()

    reassociated = 0
    no_source = 0

    for paddle_id, paddle_name, paddle_brand in paddles_no_image:
        img_result = await conn.execute("""
            SELECT DISTINCT source_raw->>'image_url' as image_url,
                   source_raw->>'name' as source_name
            FROM price_snapshots
            WHERE LOWER(TRIM(source_raw->>'name')) = LOWER(TRIM(%s))
              AND source_raw->>'image_url' IS NOT NULL
              AND source_raw->>'image_url' != ''
              AND source_raw->>'image_url' NOT LIKE '%%placehold.co%%'
              AND source_raw->>'image_url' NOT LIKE '%%unsplash%%'
              AND source_raw->>'image_url' NOT LIKE '%%example%%'
            LIMIT 1
        """, (paddle_name,))

        img_row = await img_result.fetchone()
        if img_row:
            image_url = img_row[0]
            if dry_run:
                print(f"  [DRY RUN] {paddle_brand} - {paddle_name[:50]}: {image_url[:70]}...")
            else:
                await conn.execute(
                    "UPDATE paddles SET image_url = %s, updated_at = NOW() WHERE id = %s",
                    (image_url, paddle_id)
                )
                reassociated += 1
        else:
            no_source += 1

    if not dry_run:
        await conn.commit()

    print(f"\n  Re-associated: {reassociated}")
    print(f"  No source image found: {no_source}")

    return reassociated, no_source


async def main():
    parser = argparse.ArgumentParser(description='Repair paddle image mismatches')
    parser.add_argument('--apply', action='store_true', help='Apply fixes (default: dry run)')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 60)
    print(f"{'DRY RUN' if dry_run else 'APPLY MODE'} - Repairing paddle image mismatches")
    print("=" * 60)

    async with get_connection() as conn:
        # Phase 1: Find mismatches
        print("\nPhase 1: Finding mismatched images...")
        mismatches = await find_mismatched_images(conn)
        print(f"Found {len(mismatches)} mismatches")

        if not mismatches:
            print("No mismatches found. All images appear correct.")
            return

        # Phase 2: Clear mismatched images
        print(f"\nPhase 2: {'Would clear' if dry_run else 'Clearing'} mismatched images...")
        cleared = await clear_mismatched_images(conn, mismatches, dry_run)

        # Phase 3: Re-associate
        print(f"\nPhase 3: {'Would re-associate' if dry_run else 'Re-associating'} images from source_raw...")
        reassociated, no_source = await reassociate_images(conn, dry_run)

        # Summary
        print(f"\n{'=' * 60}")
        print(f"Summary: {len(mismatches)} mismatches found, {cleared} cleared, {reassociated} re-associated, {no_source} without source")
        print(f"{'=' * 60}")

    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
