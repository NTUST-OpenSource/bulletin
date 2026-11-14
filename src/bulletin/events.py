"""The ordered record of what happened to announcements, read by clients from a cursor."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection


class Kind(StrEnum):
    """What happened to an announcement."""

    PUBLISHED = "published"
    REVISED = "revised"
    WITHDRAWN = "withdrawn"
    RESTORED = "restored"


@dataclass(frozen=True)
class Event:
    """One recorded event."""

    id: int
    announcement_id: int
    kind: Kind
    notify: bool
    late: bool
    at: datetime


async def record(
    conn: AsyncConnection,
    announcement_id: int,
    kind: Kind,
    *,
    notify: bool = False,
    late: bool = False,
) -> int:
    """Record an event in the caller's transaction and return its id."""
    raise NotImplementedError


async def read_after(conn: AsyncConnection, cursor: int, limit: int = 100) -> list[Event]:
    """Return up to `limit` events with ids above `cursor`, in id order."""
    raise NotImplementedError
