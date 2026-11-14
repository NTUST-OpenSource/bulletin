"""The operator's commands, run in the app container: `bulletin <command>`."""

import argparse
import asyncio
import logging
import os
import signal
import sys
from typing import TYPE_CHECKING, TextIO, cast

from psycopg import AsyncConnection

from bulletin.registry import (
    CATEGORIES,
    TIERS,
    accept,
    list_boards,
    pending_boards,
    set_tier,
    tier_history,
)
from bulletin.schedule import enqueue
from bulletin.service import Settings, serve

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from bulletin.registry import Category, Tier

DATABASE_URL = "BULLETIN_DATABASE_URL"


def board_key(text: str) -> tuple[int, int]:
    """Read `<site>-<board>`, such as `1045-1391`."""
    site, _, rcg = text.partition("-")
    if not (site.isdigit() and rcg.isdigit()):
        msg = f"expected <site>-<board>, such as 1045-1391, not {text!r}"
        raise argparse.ArgumentTypeError(msg)
    return int(site), int(rcg)


def parser() -> argparse.ArgumentParser:
    """The command line."""
    root = argparse.ArgumentParser(prog="bulletin")
    commands = root.add_subparsers(dest="command", required=True)

    boards = commands.add_parser("boards", help="list the registry's boards")
    boards.add_argument("--tier", choices=TIERS)
    boards.add_argument("--pending", action="store_true", help="only boards pending review")

    tier = commands.add_parser("tier", help="change a board's tier or show its changes")
    tier_commands = tier.add_subparsers(dest="action", required=True)
    tier_set = tier_commands.add_parser("set", help="set a board's tier")
    tier_set.add_argument("board", type=board_key)
    tier_set.add_argument("tier", choices=TIERS)
    tier_set.add_argument("--by", default="cli", help="who makes the change (default: cli)")
    tier_commands.add_parser("history", help="a board's tier changes").add_argument(
        "board", type=board_key
    )

    review = commands.add_parser("review", help="review discovered boards")
    review_commands = review.add_subparsers(dest="action", required=True)
    review_accept = review_commands.add_parser("accept", help="clear a board's review mark")
    review_accept.add_argument("board", type=board_key)
    review_accept.add_argument("--tier", choices=TIERS)
    review_accept.add_argument("--category", choices=CATEGORIES)
    review_accept.add_argument("--by", default="cli", help="who makes the change (default: cli)")

    commands.add_parser("discover", help="queue a re-discovery of every site now")
    commands.add_parser("serve", help="run the service: both listeners and the worker")
    return root


async def _boards(conn: AsyncConnection, args: argparse.Namespace, out: TextIO) -> None:
    if args.pending:
        for p in await pending_boards(conn):
            found = p.found_at.date().isoformat()
            print(f"{p.site_id}-{p.rcg}\t{p.category}\t{found}\t{p.name}", file=out)
        return
    for b in await list_boards(conn, tier=cast("Tier | None", args.tier)):
        print(f"{b.site_id}-{b.rcg}\t{b.tier}\t{b.category}\t{b.name}", file=out)


async def _tier(conn: AsyncConnection, args: argparse.Namespace, out: TextIO) -> None:
    site, rcg = cast("tuple[int, int]", args.board)
    if args.action == "set":
        await set_tier(conn, site, rcg, cast("Tier", args.tier), by=args.by)
        return
    for c in await tier_history(conn, site, rcg):
        when = c.changed_at.isoformat(timespec="seconds")
        print(f"{when}\t{c.old_tier} -> {c.new_tier}\t{c.changed_by}", file=out)


async def _review(conn: AsyncConnection, args: argparse.Namespace) -> None:
    site, rcg = cast("tuple[int, int]", args.board)
    await accept(
        conn,
        site,
        rcg,
        tier=cast("Tier | None", args.tier),
        category=cast("Category | None", args.category),
        by=args.by,
    )


async def _discover(conn: AsyncConnection, now: datetime) -> None:
    cur = await conn.execute("SELECT site_id FROM site ORDER BY site_id")
    for (site_id,) in await cur.fetchall():
        await enqueue(conn, "discovery", str(site_id), now)


async def run(conn: AsyncConnection, args: argparse.Namespace, out: TextIO, now: datetime) -> int:
    """Run a parsed command against the database; return the exit status."""
    try:
        match args.command:
            case "boards":
                await _boards(conn, args, out)
            case "tier":
                await _tier(conn, args, out)
            case "review":
                await _review(conn, args)
            case _:
                await _discover(conn, now)
    except LookupError as error:
        print(f"bulletin: {error}", file=sys.stderr)
        return 1
    return 0


async def _main(argv: Sequence[str]) -> int:
    from datetime import UTC, datetime  # noqa: PLC0415 - only the command line reads the clock

    args = parser().parse_args(argv)
    if args.command == "serve":
        return await _serve()
    url = os.environ.get(DATABASE_URL)
    if not url:
        print(f"bulletin: {DATABASE_URL} is not set", file=sys.stderr)
        return 2
    async with await AsyncConnection.connect(url, autocommit=True) as conn:
        return await run(conn, args, sys.stdout, datetime.now(UTC))


async def _serve() -> int:
    try:
        settings = Settings.from_env(os.environ)
    except ValueError as error:
        print(f"bulletin: {error}", file=sys.stderr)
        return 2
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    stop = asyncio.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_running_loop().add_signal_handler(sig, stop.set)
    await serve(settings, stop)
    return 0


def main() -> None:
    """The `bulletin` command."""
    raise SystemExit(asyncio.run(_main(sys.argv[1:])))
