"""The ordered record of what happened to announcements, read by clients from a cursor."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from psycopg.rows import class_row

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
    cur = await conn.execute(
        "INSERT INTO event (announcement_id, kind, notify, late) VALUES (%s, %s, %s, %s)"
        " RETURNING id",
        (announcement_id, kind, notify, late),
    )
    row = await cur.fetchone()
    assert row is not None  # noqa: S101 - INSERT ... RETURNING returns its row
    return row[0]


async def read_after(conn: AsyncConnection, cursor: int, limit: int = 100) -> list[Event]:
    """Return up to `limit` events with ids above `cursor`, in id order."""
    async with conn.cursor(row_factory=class_row(Event)) as cur:
        await cur.execute(
            "SELECT id, announcement_id, kind, notify, late, at FROM event"
            " WHERE id > %s ORDER BY id LIMIT %s",
            (cursor, limit),
        )
        return await cur.fetchall()
