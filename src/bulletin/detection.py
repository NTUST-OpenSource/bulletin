"""Which items on a polled list are new announcements, and which of those are news."""

from datetime import timedelta
from typing import TYPE_CHECKING

from bulletin.archive import publish

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.archive import Listed

FRONTIER_KEPT = timedelta(days=7)


async def detect(
    conn: AsyncConnection, board: tuple[int, int], items: Sequence[Listed], at: datetime
) -> list[int]:
    """Store the new announcements among `items` and place every item on `board`.

    Return the ids of the new announcements, in page order. An item's identity is its link's site
    and article id, or the board's site and the URL for link entries; position, list date and
    title do not matter.
    """
    new: list[int] = []
    async with conn.transaction():
        for position, item in enumerate(items, 1):
            announcement = await find(conn, item)
            if announcement is None:
                announcement = await publish(conn, item, notify=False, late=False)
                new.append(announcement)
            await place(conn, board, announcement, item, position, at)
    return new


async def find(conn: AsyncConnection, item: Listed) -> int | None:
    """Return the id of the stored announcement with `item`'s identity, or None."""
    if item.article_id is not None:
        cur = await conn.execute(
            "SELECT id FROM announcement WHERE site_id = %s AND article_id = %s",
            (item.site_id, item.article_id),
        )
    else:
        cur = await conn.execute(
            "SELECT id FROM announcement WHERE site_id = %s AND link_url = %s",
            (item.site_id, item.link_url),
        )
    row = await cur.fetchone()
    return None if row is None else row[0]


async def place(  # noqa: PLR0913, PLR0917 - a placement's key and what the list showed
    conn: AsyncConnection,
    board: tuple[int, int],
    announcement: int,
    item: Listed,
    position: int,
    at: datetime,
) -> None:
    """Record that `board` lists `announcement` at `position`, keeping the newest list date."""
    await conn.execute(
        "INSERT INTO placement (site_id, rcg, announcement_id, listed_on, first_seen_at,"
        " last_seen_at, last_position) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        " ON CONFLICT (site_id, rcg, announcement_id) DO UPDATE"
        " SET last_seen_at = EXCLUDED.last_seen_at, last_position = EXCLUDED.last_position,"
        " listed_on = GREATEST(placement.listed_on, EXCLUDED.listed_on)",
        (*board, announcement, item.listed_on, at, at, position),
    )


async def record_frontier(conn: AsyncConnection, at: datetime) -> int | None:
    """Record the highest article id stored on any site, at `at`; return it.

    Nothing is recorded while no article is stored.
    """
    cur = await conn.execute(
        "INSERT INTO frontier (at, max_article_id)"
        " SELECT %s, max(article_id) FROM announcement HAVING max(article_id) IS NOT NULL"
        " ON CONFLICT (at) DO UPDATE SET max_article_id = EXCLUDED.max_article_id"
        " RETURNING max_article_id",
        (at,),
    )
    row = await cur.fetchone()
    return None if row is None else row[0]


async def prune_frontier(conn: AsyncConnection, now: datetime) -> int:
    """Delete frontier records older than 7 days; return how many."""
    cur = await conn.execute("DELETE FROM frontier WHERE at < %s", (now - FRONTIER_KEPT,))
    return cur.rowcount
