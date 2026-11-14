"""Requirements of the polling capability that decide when a board is due."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import pytest

from bulletin.registry import Board, import_seed
from bulletin.schedule import (
    Job,
    Poll,
    due_boards,
    enqueue,
    interval,
    mark_polled,
    next_request,
)

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from bulletin.registry import Tier

TAIPEI = ZoneInfo("Asia/Taipei")
WEDNESDAY = datetime(2026, 11, 18, 10, 0, tzinfo=TAIPEI)
SATURDAY = datetime(2026, 11, 21, 10, 0, tzinfo=TAIPEI)


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


def test_off_boards_have_no_interval() -> None:
    """Tier intervals: an off board is never due."""
    assert interval("off", WEDNESDAY) is None


async def test_office_hours(migrated: AsyncConnection) -> None:
    """Tier intervals: a P1 board polled at 10:00 on a Wednesday is due at 10:05."""
    await import_seed(migrated, [Board(1045, 1391, "h", "u", "n", "announcement", "P1")])

    await mark_polled(migrated, 1045, 1391, WEDNESDAY)

    assert await due_boards(migrated, WEDNESDAY + timedelta(minutes=4, seconds=59)) == []
    assert await due_boards(migrated, WEDNESDAY + timedelta(minutes=5)) == [(1045, 1391)]


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Queue order")
async def test_backfill_yields(migrated: AsyncConnection) -> None:
    """Queue order: a backfill page and a P3 poll due at 02:00 send the poll first."""
    night = datetime(2026, 11, 18, 2, 0, tzinfo=TAIPEI)
    await enqueue(migrated, "backfill", "1045-1391", night - timedelta(hours=1))
    await import_seed(migrated, [Board(1045, 1391, "h", "u", "n", "announcement", "P3")])

    assert await next_request(migrated, night) == Poll(1045, 1391)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Queue order")
async def test_daytime_backfill_waits_until_one(migrated: AsyncConnection) -> None:
    """Queue order: a backfill queued at 14:00 waits until 01:00."""
    afternoon = datetime(2026, 11, 18, 14, 0, tzinfo=TAIPEI)
    job = await enqueue(migrated, "backfill", "1045-1391", afternoon)

    assert await next_request(migrated, afternoon) is None
    assert await next_request(migrated, afternoon.replace(hour=23, minute=59)) is None
    night = afternoon.replace(day=19, hour=1)
    assert await next_request(migrated, night) == Job(job, "backfill", "1045-1391")


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Queue order")
async def test_polls_by_tier_then_jobs_by_kind(migrated: AsyncConnection) -> None:
    """Queue order: polls from P1 to P4, then articles, attachments and re-discovery."""
    at = WEDNESDAY
    discovery = await enqueue(migrated, "discovery", "1000", at)
    attachment = await enqueue(migrated, "attachment", "1", at)
    article = await enqueue(migrated, "article", "1000-153625", at)
    await import_seed(
        migrated,
        [
            Board(1000, 4, "h", "u", "n", "announcement", "P4"),
            Board(1000, 1, "h", "u", "n", "announcement", "P1"),
        ],
    )
    order: list[Poll | Job] = []
    while (request := await next_request(migrated, at)) is not None:
        order.append(request)
        if isinstance(request, Poll):
            await mark_polled(migrated, request.site_id, request.rcg, at)
        else:
            await migrated.execute("DELETE FROM job WHERE id = %s", (request.id,))

    assert order == [
        Poll(1000, 1),
        Poll(1000, 4),
        Job(article, "article", "1000-153625"),
        Job(attachment, "attachment", "1"),
        Job(discovery, "discovery", "1000"),
    ]
