"""The log of every request sent to a school host."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection


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
    raise NotImplementedError


async def prune(conn: AsyncConnection, now: datetime) -> int:
    """Delete entries older than 30 days; return how many."""
    raise NotImplementedError
