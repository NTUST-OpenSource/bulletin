"""The ten-year backfill: each board's older list pages, one page per job, at night."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.http import Fetch


async def walk(conn: AsyncConnection, fetch: Fetch, board: tuple[int, int], at: datetime) -> None:
    """Read the board's next unread list page, store its items and queue what follows."""
    raise NotImplementedError


async def queue_walks(conn: AsyncConnection, at: datetime) -> int:
    """Queue a walk for every board that is on, not backfilled and not queued; return how many."""
    raise NotImplementedError
