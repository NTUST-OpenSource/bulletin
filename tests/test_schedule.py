"""Requirements of the polling capability that decide when a board is due."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import pytest

from bulletin.registry import Board, import_seed
from bulletin.schedule import due_boards, interval, mark_polled

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from bulletin.registry import Tier

TAIPEI = ZoneInfo("Asia/Taipei")
WEDNESDAY = datetime(2026, 11, 18, 10, 0, tzinfo=TAIPEI)
SATURDAY = datetime(2026, 11, 21, 10, 0, tzinfo=TAIPEI)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Tier intervals")
@pytest.mark.parametrize(
    ("tier", "at", "minutes"),
    [
        ("P1", WEDNESDAY, 5),
        ("P1", SATURDAY, 20),
        ("P1", WEDNESDAY.replace(hour=7, minute=59), 20),
        ("P1", WEDNESDAY.replace(hour=18), 20),
        ("P2", WEDNESDAY, 15),
        ("P2", WEDNESDAY.replace(hour=22), 60),
        ("P3", WEDNESDAY, 60),
        ("P3", SATURDAY, 240),
        ("P4", WEDNESDAY, 24 * 60),
        ("P4", SATURDAY, 24 * 60),
    ],
)
def test_interval_by_tier_and_window(tier: Tier, at: datetime, minutes: int) -> None:
    """Tier intervals: the window that holds the last poll decides the interval."""
    assert interval(tier, at) == timedelta(minutes=minutes)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Tier intervals")
def test_off_boards_have_no_interval() -> None:
    """Tier intervals: an off board is never due."""
    assert interval("off", WEDNESDAY) is None


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Tier intervals")
async def test_office_hours(migrated: AsyncConnection) -> None:
    """Tier intervals: a P1 board polled at 10:00 on a Wednesday is due at 10:05."""
    await import_seed(migrated, [Board(1045, 1391, "h", "u", "n", "announcement", "P1")])

    await mark_polled(migrated, 1045, 1391, WEDNESDAY)

    assert await due_boards(migrated, WEDNESDAY + timedelta(minutes=4, seconds=59)) == []
    assert await due_boards(migrated, WEDNESDAY + timedelta(minutes=5)) == [(1045, 1391)]
