"""The ten-year backfill: each board's older list pages, one page per job, at night."""

from datetime import date
from http import HTTPStatus
from typing import TYPE_CHECKING

from bulletin.archive import is_redirect_home, publish
from bulletin.detection import find
from bulletin.pages import PageError, list_url, page_count, parse_list
from bulletin.schedule import TAIPEI, enqueue

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.http import Fetch
    from bulletin.model import Listed

# Page 1 is the poll's.
FIRST_PAGE = 2
YEARS = 10


def horizon(at: datetime) -> date:
    """The earliest list date within ten years of `at`, by the calendar in Taipei."""
    day = at.astimezone(TAIPEI).date()
    try:
        return day.replace(year=day.year - YEARS)
    except ValueError:  # 29 February
        return date(day.year - YEARS, 2, 28)


async def walk(conn: AsyncConnection, fetch: Fetch, board: tuple[int, int], at: datetime) -> None:
    """Read the board's next unread list page, store its items and queue what follows.

    The walk ends at the pager's last page, at a page with no item from the last ten years, or at
    a page past the last one, which redirects home. A board that is off or already backfilled is
    left alone.
    """
    cur = await conn.execute(
        "SELECT s.host, b.tier, b.backfill_page, b.backfilled_at FROM board b"
        " JOIN site s USING (site_id) WHERE b.site_id = %s AND b.rcg = %s",
        board,
    )
    row = await cur.fetchone()
    if row is None:
        msg = f"no board {board[0]}-{board[1]}"
        raise LookupError(msg)
    host, tier, next_page, backfilled_at = row
    if tier == "off" or backfilled_at is not None:
        return
    number = next_page or FIRST_PAGE
    response = await fetch(list_url(host, *board, number))
    if is_redirect_home(response.status, response.headers.get("Location", ""), response.url):
        # A page past the last one redirects home.
        items, last = [], True
    elif response.status != HTTPStatus.OK:
        raise PageError(response.status)
    else:
        oldest = horizon(at)
        text = response.text()
        items = [
            item
            for item in parse_list(text, response.url, board[0])
            if item.listed_on is None or item.listed_on >= oldest
        ]
        count = page_count(text)
        last = not items or (count is not None and number >= count)
    async with conn.transaction():
        for item in items:
            await store(conn, board, item, at)
        if last:
            await conn.execute(
                "UPDATE board SET backfill_page = %s, backfilled_at = %s"
                " WHERE site_id = %s AND rcg = %s",
                (number, at, *board),
            )
        else:
            await conn.execute(
                "UPDATE board SET backfill_page = %s WHERE site_id = %s AND rcg = %s",
                (number + 1, *board),
            )
            await enqueue(conn, "backfill", f"{board[0]}-{board[1]}", at)


async def store(conn: AsyncConnection, board: tuple[int, int], item: Listed, at: datetime) -> None:
    """Store an item a walk found as a late discovery and queue its article for the night."""
    announcement, _ = await find(conn, item)
    if announcement is None:
        announcement = await publish(conn, item, notify=False, late=True)
        if item.article_id is not None:
            await enqueue(conn, "backfill", str(announcement), at)
    # No position: what page 1 listed at the last poll stays as the poll saw it.
    await conn.execute(
        "INSERT INTO placement (site_id, rcg, announcement_id, listed_on, first_seen_at,"
        " last_seen_at) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (*board, announcement, item.listed_on, at, at),
    )


async def queue_walks(conn: AsyncConnection, at: datetime) -> int:
    """Queue a walk for every board that is on, not backfilled and not queued; return how many."""
    cur = await conn.execute(
        "INSERT INTO job (kind, ref, run_after)"
        " SELECT 'backfill', b.site_id || '-' || b.rcg, %s FROM board b"
        " WHERE b.tier <> 'off' AND b.backfilled_at IS NULL AND NOT EXISTS"
        " (SELECT 1 FROM job j WHERE j.kind = 'backfill' AND j.ref = b.site_id || '-' || b.rcg)",
        (at,),
    )
    return cur.rowcount
