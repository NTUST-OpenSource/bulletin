"""The ordered record of what happened to announcements, read by clients from a cursor."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from psycopg.pq import TransactionStatus

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection


# The advisory lock key that orders event writers.
EVENT_LOCK = 0x6275_6C6C_6574_696E


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
    """Record an event in the caller's transaction and return its id.

    The transaction lock makes ids commit in the order they are taken, so a reader resuming after
    the last id it saw never misses one.
    """
    if notify and kind is not Kind.PUBLISHED:
        msg = f"a {kind} event is never notify-worthy"
        raise ValueError(msg)
    if notify and late:
        msg = "a late event is never notify-worthy"
        raise ValueError(msg)
    if conn.info.transaction_status is TransactionStatus.IDLE:
        msg = "events are recorded inside a transaction"
        raise RuntimeError(msg)
    await conn.execute("SELECT pg_advisory_xact_lock(%s)", (EVENT_LOCK,))
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
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, announcement_id, kind, notify, late, at FROM event"
            " WHERE id > %s ORDER BY id LIMIT %s",
            (cursor, limit),
        )
        return [
            Event(id_, announcement_id, Kind(kind), notify, late, at)
            for id_, announcement_id, kind, notify, late, at in await cur.fetchall()
        ]
