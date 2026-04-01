#!/usr/bin/env python3
"""
Migration: Add skill_level and in_stock columns to paddles table
"""

import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load env BEFORE any pipeline imports
env_path = Path(__file__).parent.parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)

# Now import pipeline modules (they need DATABASE_URL)
from pipeline.db.connection import get_connection


async def migrate():
    """Add enriched columns to paddles table"""
    async with get_connection() as conn:
        async with conn.cursor() as cur:
            # Add skill_level column
            try:
                await cur.execute("""
                    ALTER TABLE paddles
                    ADD COLUMN IF NOT EXISTS skill_level VARCHAR(50)
                """)
                print("✅ Added skill_level column")
            except Exception as e:
                print(f"⚠️  skill_level column issue: {e}")

            # Add in_stock column
            try:
                await cur.execute("""
                    ALTER TABLE paddles
                    ADD COLUMN IF NOT EXISTS in_stock BOOLEAN DEFAULT NULL
                """)
                print("✅ Added in_stock column")
            except Exception as e:
                print(f"⚠️  in_stock column issue: {e}")

            # Add model_slug column for matching
            try:
                await cur.execute("""
                    ALTER TABLE paddles
                    ADD COLUMN IF NOT EXISTS model_slug VARCHAR(255)
                """)
                print("✅ Added model_slug column")
            except Exception as e:
                print(f"⚠️  model_slug column issue: {e}")

            # Verify schema
            await cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'paddles'
                AND column_name IN ('skill_level', 'in_stock', 'model_slug')
                ORDER BY column_name
            """)
            cols = await cur.fetchall()
            print("\n📊 Enriched columns in paddles table:")
            for c in cols:
                nullable = "NULL" if c[2] == "YES" else "NOT NULL"
                print(f"  - {c[0]}: {c[1]} ({nullable})")


if __name__ == "__main__":
    asyncio.run(migrate())
