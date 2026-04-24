"""CLI tool for listing and managing review queue items.

Usage:
    python -m pipeline.dedup.review list [--all]
    python -m pipeline.dedup.review approve <id>
"""

import argparse
import asyncio
import json
import sys

from pipeline.db.connection import get_pool, close_pool


async def list_pending(show_all: bool = False, limit: int = 50) -> list[dict]:
    pool = await get_pool()
    async with pool.connection() as conn:
        if show_all:
            result = await conn.execute(
                """
                SELECT rq.id, p.name AS paddle_name,
                       rq.data->>'score' AS match_score,
                       rq.review_status, rq.status, rq.type,
                       rq.created_at
                FROM review_queue rq
                LEFT JOIN paddles p ON p.id = rq.paddle_id
                ORDER BY rq.created_at DESC
                LIMIT %(limit)s
                """,
                {"limit": limit},
            )
        else:
            result = await conn.execute(
                """
                SELECT rq.id, p.name AS paddle_name,
                       rq.data->>'score' AS match_score,
                       rq.review_status, rq.status, rq.type,
                       rq.created_at
                FROM review_queue rq
                LEFT JOIN paddles p ON p.id = rq.paddle_id
                WHERE rq.review_status = 'pending'
                ORDER BY rq.created_at DESC
                LIMIT %(limit)s
                """,
                {"limit": limit},
            )
        rows = await result.fetchall()

    return [
        {
            "id": r[0],
            "paddle_name": r[1] or "(unknown)",
            "match_score": r[2] or "-",
            "review_status": r[3] or "pending",
            "status": r[4],
            "type": r[5],
            "created_at": r[6].isoformat() if r[6] else "-",
        }
        for r in rows
    ]


async def approve_item(queue_id: int) -> bool:
    pool = await get_pool()
    async with pool.connection() as conn:
        result = await conn.execute(
            """
            UPDATE review_queue
            SET review_status = 'manually_reviewed'
            WHERE id = %(id)s
            """,
            {"id": queue_id},
        )
        status = await result.fetchone()
        await conn.commit()

    affected = int(status[0].split()[-1]) if status else 0
    if affected == 0:
        print(f"No review_queue item found with id={queue_id}")
        return False

    print(f"Item {queue_id} marked as manually_reviewed")
    return True


def _print_table(items: list[dict]) -> None:
    if not items:
        print("No items found.")
        return

    header = f"{'ID':>5}  {'Type':<16} {'Paddle Name':<40} {'Score':>6} {'Review':<20} {'Status':<10} {'Created At'}"
    print(header)
    print("-" * len(header))
    for it in items:
        print(
            f"{it['id']:>5}  {it['type']:<16} "
            f"{it['paddle_name'][:40]:<40} {str(it['match_score']):>6} "
            f"{it['review_status']:<20} {it['status']:<10} {it['created_at']}"
        )
    print(f"\nTotal: {len(items)} item(s)")


async def _run(args: argparse.Namespace) -> None:
    try:
        if args.command == "list":
            items = await list_pending(show_all=args.all, limit=args.limit)
            _print_table(items)
        elif args.command == "approve":
            await approve_item(args.id)
        else:
            print("Unknown command. Use: list [--all] | approve <id>")
            sys.exit(1)
    finally:
        await close_pool()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pipeline.dedup.review",
        description="Manage review queue items",
    )
    sub = parser.add_subparsers(dest="command")

    list_cmd = sub.add_parser("list", help="List review queue items")
    list_cmd.add_argument("--all", action="store_true", help="Show all items (not just pending)")
    list_cmd.add_argument("--limit", type=int, default=50, help="Max items to show")

    approve_cmd = sub.add_parser("approve", help="Mark item as manually_reviewed")
    approve_cmd.add_argument("id", type=int, help="Review queue item ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
