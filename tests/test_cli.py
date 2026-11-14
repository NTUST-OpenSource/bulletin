"""The operator's commands: Change a tier, Tier audit and Review new boards from a shell."""

import io
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from bulletin.cli import parser, run
from bulletin.registry import Board, Found, add_discovered, get_board, import_seed

if TYPE_CHECKING:
    from psycopg import AsyncConnection

NOW = datetime(2026, 11, 18, 2, 0, tzinfo=UTC)


async def bulletin(conn: AsyncConnection, *argv: str) -> tuple[int, str]:
    out = io.StringIO()
    status = await run(conn, parser().parse_args(argv), out, NOW)
    return status, out.getvalue()


async def test_tier_set_and_history(migrated: AsyncConnection) -> None:
    """Change a tier and Tier audit: `tier set` with --by, then `tier history`."""
    await import_seed(migrated, [Board(1053, 1435, "h", "u", "n", "announcement", "P4")])

    assert await bulletin(migrated, "tier", "set", "1053-1435", "P2") == (0, "")
    assert await bulletin(migrated, "tier", "set", "1053-1435", "P1", "--by", "owner") == (0, "")
    status, history = await bulletin(migrated, "tier", "history", "1053-1435")

    assert status == 0
    assert [line.split("\t")[1:] for line in history.splitlines()] == [
        ["P2 -> P1", "owner"],
        ["P4 -> P2", "cli"],
    ]
    status, listed = await bulletin(migrated, "boards", "--tier", "P1")
    assert listed == "1053-1435\tP1\tannouncement\tn\n"


async def test_unknown_boards_and_tiers(migrated: AsyncConnection) -> None:
    """Change a tier: unknown boards fail by name; unknown tiers never reach the database."""
    assert await bulletin(migrated, "tier", "set", "1053-9", "P1") == (1, "")
    with pytest.raises(SystemExit):
        parser().parse_args(["tier", "set", "1053-1435", "P9"])
    with pytest.raises(SystemExit):
        parser().parse_args(["tier", "set", "1053", "P1"])


async def test_review_and_discover(migrated: AsyncConnection) -> None:
    """Review new boards: list pending ones, accept one; `discover` queues every site."""
    await import_seed(migrated, [Board(1053, 1435, "h", "u", "n", "announcement", "P4")])
    await add_discovered(migrated, [Found(1053, 2000, "board 2000")])

    status, pending = await bulletin(migrated, "boards", "--pending")
    assert (status, pending.split("\t")[0]) == (0, "1053-2000")
    assert await bulletin(
        migrated, "review", "accept", "1053-2000", "--tier", "P3", "--category", "news"
    ) == (0, "")
    assert await bulletin(migrated, "discover") == (0, "")

    assert await get_board(migrated, 1053, 2000) == Board(
        1053, 2000, "h", "u", "board 2000", "news", "P3"
    )
    cur = await migrated.execute("SELECT kind, ref FROM job WHERE kind = 'discovery'")
    assert await cur.fetchall() == [("discovery", "1053")]
