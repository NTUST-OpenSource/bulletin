"""Requirements of the tier-admin capability."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import pytest

from bulletin.registry import Board, get_board, import_seed, set_tier, tier_history
from bulletin.schedule import due_boards, mark_polled

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from bulletin.registry import Tier

WEDNESDAY = datetime(2026, 11, 18, 10, 0, tzinfo=ZoneInfo("Asia/Taipei"))


async def board_at(conn: AsyncConnection, tier: Tier, polled: datetime | None = None) -> None:
    await import_seed(conn, [Board(1053, 1435, "h", "u", "n", "announcement", tier)])
    if polled is not None:
        await mark_polled(conn, 1053, 1435, polled)


async def test_raising_a_board(migrated: AsyncConnection) -> None:
    """Change a tier: P4 polled at 09:58 and set to P1 at 10:00 is due by 10:03."""
    await board_at(migrated, "P4", WEDNESDAY - timedelta(minutes=2))

    await set_tier(migrated, 1053, 1435, "P1")

    assert await due_boards(migrated, WEDNESDAY + timedelta(minutes=2, seconds=59)) == []
    assert await due_boards(migrated, WEDNESDAY + timedelta(minutes=3)) == [(1053, 1435)]


async def test_turning_a_board_off(migrated: AsyncConnection) -> None:
    """Change a tier: an off board has no further poll scheduled."""
    await board_at(migrated, "P2", WEDNESDAY)

    await set_tier(migrated, 1053, 1435, "off")

    cur = await migrated.execute("SELECT next_poll_at FROM board")
    assert await cur.fetchall() == [(None,)]


async def test_an_unknown_board(migrated: AsyncConnection) -> None:
    """Change a tier: an unknown board is refused by name, and no tier changes."""
    await board_at(migrated, "P2")

    with pytest.raises(LookupError, match="1053-9999"):
        await set_tier(migrated, 1053, 9999, "P1")

    assert (await get_board(migrated, 1053, 1435)) == Board(
        1053, 1435, "h", "u", "n", "announcement", "P2"
    )


async def test_an_unknown_tier(migrated: AsyncConnection) -> None:
    """Change a tier: an unknown tier is refused, and the board keeps its tier."""
    await board_at(migrated, "P2")

    with pytest.raises(ValueError, match="P9"):
        await set_tier(migrated, 1053, 1435, "P9")  # pyright: ignore[reportArgumentType]

    board = await get_board(migrated, 1053, 1435)
    assert board is not None
    assert board.tier == "P2"


async def test_two_changes(migrated: AsyncConnection) -> None:
    """Tier audit: P4 to P2 by the CLI, then P1 through the API, listed newest first."""
    await board_at(migrated, "P4")

    await set_tier(migrated, 1053, 1435, "P2")
    await set_tier(migrated, 1053, 1435, "P1", by="owner-laptop")

    history = await tier_history(migrated, 1053, 1435)
    assert [(c.old_tier, c.new_tier, c.changed_by) for c in history] == [
        ("P2", "P1", "owner-laptop"),
        ("P4", "P2", "cli"),
    ]


@pytest.mark.xfail(strict=True, reason="Turning a board on")
async def test_an_off_board_turned_on(migrated: AsyncConnection) -> None:
    """Turning a board on: it counts as not backfilled and a backfill of it is queued."""
    await board_at(migrated, "off")
    await migrated.execute("UPDATE board SET backfilled_at = now(), backfill_page = 40")

    await set_tier(migrated, 1053, 1435, "P3")

    cur = await migrated.execute("SELECT backfilled_at, backfill_page FROM board")
    assert await cur.fetchall() == [(None, None)]
    cur = await migrated.execute("SELECT kind, ref FROM job")
    assert await cur.fetchall() == [("backfill", "1053-1435")]


async def test_a_change_between_tiers_queues_nothing(migrated: AsyncConnection) -> None:
    """Turning a board on: only a change from off queues a backfill."""
    await board_at(migrated, "P4")

    await set_tier(migrated, 1053, 1435, "P1")

    cur = await migrated.execute("SELECT count(*) FROM job")
    assert await cur.fetchone() == (0,)
