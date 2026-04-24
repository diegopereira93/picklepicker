"""Versioned migration runner for pipeline database schema."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

try:
    import structlog
    log = structlog.get_logger(__name__)
except ImportError:
    import logging
    log = logging.getLogger(__name__)
    if not log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        log.addHandler(handler)
        log.setLevel(logging.INFO)

from pipeline.db.connection import get_pool, close_pool


CREATE_MIGRATIONS_TABLE = """\
CREATE TABLE IF NOT EXISTS schema_migrations (
    version   VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW()
)
"""


async def discover_migrations(migrations_dir: str) -> list[str]:
    """Return sorted list of numbered .sql migration filenames in the given directory."""
    p = Path(migrations_dir)
    if not p.is_dir():
        return []
    return sorted(
        f.name for f in p.iterdir()
        if f.is_file() and f.suffix == ".sql" and f.name[0:3].isdigit()
    )


async def applied_versions(conn) -> set[str]:
    """Return the set of already-applied migration filenames."""
    await conn.execute(CREATE_MIGRATIONS_TABLE)
    cur = await conn.execute("SELECT version FROM schema_migrations")
    rows = await cur.fetchall()
    return {row[0] for row in rows}


async def apply_migration(conn, filename: str, sql: str) -> None:
    """Apply a single migration and record it."""
    await conn.execute(sql)
    await conn.execute(
        "INSERT INTO schema_migrations (version) VALUES (%s)", (filename,)
    )


async def run_migrations(migrations_dir: str, dry_run: bool = False) -> None:
    """Discover and apply pending migrations."""
    files = await discover_migrations(migrations_dir)
    if not files:
        print("No migrations found")
        return

    pool = await get_pool()
    try:
        async with pool.connection() as conn:
            already = await applied_versions(conn)

        pending = [f for f in files if f not in already]
        if not pending:
            print("All migrations already applied")
            return

        for filename in pending:
            filepath = os.path.join(migrations_dir, filename)
            sql = Path(filepath).read_text()

            if dry_run:
                print(f"[DRY RUN] Would apply: {filename}")
                continue

            async with pool.connection() as conn:
                await conn.execute("BEGIN")
                try:
                    await apply_migration(conn, filename, sql)
                    await conn.execute("COMMIT")
                    print(f"Applied: {filename}")
                except Exception as exc:
                    await conn.execute("ROLLBACK")
                    print(f"FAILED: {filename} — {exc}", file=sys.stderr)
                    sys.exit(1)
    finally:
        await close_pool()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be applied without executing",
    )
    parser.add_argument(
        "--dir",
        default=os.path.join(os.path.dirname(__file__), "migrations"),
        help="Migrations directory (default: pipeline/db/migrations/)",
    )
    args = parser.parse_args()
    asyncio.run(run_migrations(args.dir, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
