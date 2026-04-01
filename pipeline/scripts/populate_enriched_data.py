#!/usr/bin/env python3
"""Populate paddles with enriched data for testing."""
import asyncio
import os
import sys

sys.path.insert(0, '/home/diego/Documentos/picklepicker')

from dotenv import load_dotenv
load_dotenv('/home/diego/Documentos/picklepicker/.env.local')

import psycopg
from psycopg import AsyncConnection

SKILL_LEVELS = ['beginner', 'intermediate', 'advanced']


async def populate():
    """Populate database with enriched paddle data."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    async with await AsyncConnection.connect(database_url) as conn:
        # First, update existing paddles with skill_level and in_stock if NULL
        async with conn.cursor() as cur:
            await cur.execute("""
                UPDATE paddles
                SET skill_level = CASE
                        WHEN id % 3 = 1 THEN 'beginner'
                        WHEN id % 3 = 2 THEN 'intermediate'
                        ELSE 'advanced'
                    END,
                    in_stock = CASE WHEN id % 7 != 0 THEN true ELSE false END
                WHERE skill_level IS NULL OR in_stock IS NULL
            """)
            print(f"Updated {cur.rowcount} paddles with skill_level/in_stock")

            # Insert paddle_specs for paddles that don't have them
            await cur.execute("""
                INSERT INTO paddle_specs (paddle_id, swingweight, twistweight, weight_oz, core_thickness_mm, face_material)
                SELECT p.id,
                       floor(random() * 50 + 100)::int,  -- swingweight 100-150
                       floor(random() * 20 + 10)::int,   -- twistweight 10-30
                       floor(random() * 20 + 210)::int / 10.0,  -- weight 21.0-23.0 oz
                       floor(random() * 6 + 12)::int,    -- core 12-18mm
                       CASE WHEN p.id % 2 = 0 THEN 'carbon fiber' ELSE 'fiberglass' END
                FROM paddles p
                LEFT JOIN paddle_specs ps ON p.id = ps.paddle_id
                WHERE ps.paddle_id IS NULL
            """)
            print(f"Inserted {cur.rowcount} paddle_specs")

        await conn.commit()

        # Verify results
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM paddles WHERE skill_level IS NOT NULL")
            skill_count = (await cur.fetchone())[0]

            await cur.execute("SELECT COUNT(*) FROM paddles WHERE in_stock IS NOT NULL")
            stock_count = (await cur.fetchone())[0]

            await cur.execute("SELECT COUNT(*) FROM paddle_specs WHERE swingweight IS NOT NULL")
            specs_count = (await cur.fetchone())[0]

        print(f"\n✅ Database populated successfully:")
        print(f"   - Paddles with skill_level: {skill_count}")
        print(f"   - Paddles with in_stock: {stock_count}")
        print(f"   - Paddle specs with swingweight: {specs_count}")


if __name__ == "__main__":
    asyncio.run(populate())
