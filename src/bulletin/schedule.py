"""When each board is polled: its tier's interval, and the queue of what is due."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection


async def due_boards(conn: AsyncConnection, now: datetime) -> list[tuple[int, int]]:
    """Return the boards due for a poll at `now`, most overdue first."""
    raise NotImplementedError
