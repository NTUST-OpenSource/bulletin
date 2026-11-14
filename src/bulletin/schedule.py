"""When each board is polled: its tier's interval, and the queue of what is due."""

from datetime import timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.registry import Tier


TAIPEI = ZoneInfo("Asia/Taipei")
OFFICE_HOURS = range(8, 18)
# Minutes between polls: (office hours, otherwise). Office hours are weekdays 08:00-18:00 in
# Taipei, holidays included.
INTERVALS: dict[Tier, tuple[int, int]] = {
    "P1": (5, 20),
    "P2": (15, 60),
    "P3": (60, 240),
    "P4": (24 * 60, 24 * 60),
}


def in_office_hours(at: datetime) -> bool:
    """Whether `at` falls on a weekday between 08:00 and 18:00 in Taipei."""
    local = at.astimezone(TAIPEI)
    return local.weekday() < 5 and local.hour in OFFICE_HOURS  # noqa: PLR2004 - Saturday is 5


def interval(tier: Tier, last_poll: datetime) -> timedelta | None:
    """Return how long after `last_poll` a board of `tier` is due again; None for off."""
    if tier == "off":
        return None
    office, otherwise = INTERVALS[tier]
    return timedelta(minutes=office if in_office_hours(last_poll) else otherwise)


async def mark_polled(conn: AsyncConnection, site_id: int, rcg: int, at: datetime) -> None:
    """Record a successful poll of a board at `at` and schedule its next one."""
    cur = await conn.execute(
        "SELECT tier FROM board WHERE site_id = %s AND rcg = %s FOR UPDATE", (site_id, rcg)
    )
    row = await cur.fetchone()
    if row is None:
        msg = f"no board {site_id}-{rcg}"
        raise LookupError(msg)
    step = interval(row[0], at)
    await conn.execute(
        "UPDATE board SET last_polled_at = %s, next_poll_at = %s, failures = 0"
        " WHERE site_id = %s AND rcg = %s",
        (at, None if step is None else at + step, site_id, rcg),
    )


async def due_boards(conn: AsyncConnection, now: datetime) -> list[tuple[int, int]]:
    """Return the boards due for a poll at `now`, most overdue first.

    The tier alone decides: every board that is not off is polled, whatever its category. A board
    never polled is due at once.
    """
    cur = await conn.execute(
        "SELECT site_id, rcg FROM board"
        " WHERE tier <> 'off' AND (next_poll_at IS NULL OR next_poll_at <= %s)"
        " ORDER BY next_poll_at NULLS FIRST, site_id, rcg",
        (now,),
    )
    return await cur.fetchall()
