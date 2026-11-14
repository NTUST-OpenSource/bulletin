"""When each board is polled: its tier's interval, and the queue of what is due."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from psycopg import AsyncConnection

    from bulletin.registry import Tier


def interval(tier: Tier, last_poll: datetime) -> timedelta | None:
    """Return how long after `last_poll` a board of `tier` is due again; None for off."""
    raise NotImplementedError


async def mark_polled(conn: AsyncConnection, site_id: int, rcg: int, at: datetime) -> None:
    """Record a successful poll of a board at `at` and schedule its next one."""
    raise NotImplementedError


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
