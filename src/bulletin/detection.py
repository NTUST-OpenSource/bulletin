"""Which items on a polled list are new announcements, and which of those are news."""

import json
import re
import unicodedata
from datetime import timedelta
from importlib import resources
from typing import TYPE_CHECKING

from bulletin.archive import publish
from bulletin.schedule import TAIPEI

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.archive import Listed

FRONTIER_KEPT = timedelta(days=7)
# A cross-post copies another site's announcement first seen this recently, under a title this long.
CROSS_POST_WINDOW = timedelta(days=14)
CROSS_POST_MIN_LENGTH = 8
_TITLES = json.loads((resources.files("bulletin") / "titles.json").read_text(encoding="utf-8"))
PREFIX = re.compile(_TITLES["prefix"])
FILLER = re.compile(_TITLES["words"])
# On a board not yet backfilled, news is above the frontier of this long ago, or freshly dated.
FRONTIER_AGE = timedelta(hours=72)
FRESH_LIST_DATE = timedelta(days=2)


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
        # A backfilled board has listed everything older, so whatever is new is news.
        backfilled = await is_backfilled(conn, board)
        line = None if backfilled else await frontier(conn, at)
        for position, item in enumerate(items, 1):
            announcement = await find(conn, item)
            if announcement is None:
                original = await cross_post_of(conn, item, at)
                news = (backfilled or is_news(item, line, at)) and original is None
                announcement = await publish(conn, item, notify=news, late=not news)
                if original is not None:
                    await conn.execute(
                        "UPDATE announcement SET cross_post_of = %s WHERE id = %s",
                        (original, announcement),
                    )
                new.append(announcement)
            await place(conn, board, announcement, item, position, at)
    return new


def is_news(item: Listed, line: int | None, at: datetime) -> bool:
    """The frontier rule: above the frontier, or listed at most 2 days before the poll.

    With no frontier recorded yet, nothing is news.
    """
    if line is None:
        return False
    if item.article_id is not None and item.article_id > line:
        return True
    return (
        item.listed_on is not None
        and at.astimezone(TAIPEI).date() - item.listed_on <= FRESH_LIST_DATE
    )


async def frontier(conn: AsyncConnection, at: datetime) -> int | None:
    """Return the frontier of 72 hours before `at`, or the oldest while the service is younger."""
    cur = await conn.execute(
        "SELECT COALESCE("
        "(SELECT max_article_id FROM frontier WHERE at <= %s ORDER BY at DESC LIMIT 1),"
        " (SELECT max_article_id FROM frontier ORDER BY at LIMIT 1))",
        (at - FRONTIER_AGE,),
    )
    row = await cur.fetchone()
    return None if row is None else row[0]


async def is_backfilled(conn: AsyncConnection, board: tuple[int, int]) -> bool:
    """Whether the board's ten-year backfill is complete."""
    cur = await conn.execute(
        "SELECT backfilled_at IS NOT NULL FROM board WHERE site_id = %s AND rcg = %s", board
    )
    row = await cur.fetchone()
    return bool(row and row[0])


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


def normalize(title: str) -> str:
    """Reduce a title to what cross-posts share: no bracketed prefix, filler word or punctuation."""
    text = FILLER.sub("", PREFIX.sub("", title))
    return "".join(
        c for c in text if not unicodedata.category(c).startswith(("P", "Z", "C"))
    ).casefold()


async def cross_post_of(conn: AsyncConnection, item: Listed, at: datetime) -> int | None:
    """Return another site's announcement of the last 14 days with `item`'s normalized title."""
    key = normalize(item.title)
    if len(key) < CROSS_POST_MIN_LENGTH:
        return None
    cur = await conn.execute(
        "SELECT id, title FROM announcement WHERE site_id <> %s AND first_seen_at > %s"
        " ORDER BY first_seen_at, id",
        (item.site_id, at - CROSS_POST_WINDOW),
    )
    return next((id_ for id_, title in await cur.fetchall() if normalize(title) == key), None)
