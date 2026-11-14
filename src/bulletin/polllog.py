"""The log of every request sent to a school host."""

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection


RETENTION = timedelta(days=30)


@dataclass(frozen=True)
class Entry:
    """One request: why it was sent, for which board, and how it went."""

    purpose: str
    at: datetime
    status: int | None
    size: int | None
    ms: int | None
    board: tuple[int, int] | None = None
    changed: bool | None = None
    new_ids: tuple[int, ...] = ()


async def log_request(conn: AsyncConnection, entry: Entry) -> None:
    """Add a request to the log."""
    site_id, rcg = entry.board or (None, None)
    await conn.execute(
        "INSERT INTO poll (purpose, site_id, rcg, at, status, bytes, ms, changed, new_ids)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            entry.purpose,
            site_id,
            rcg,
            entry.at,
            entry.status,
            entry.size,
            entry.ms,
            entry.changed,
            list(entry.new_ids),
        ),
    )


async def prune(conn: AsyncConnection, now: datetime) -> int:
    """Delete entries older than 30 days; return how many."""
    cur = await conn.execute("DELETE FROM poll WHERE at < %s", (now - RETENTION,))
    return cur.rowcount
