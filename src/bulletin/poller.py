"""What a poll does with the items it read from a board's page 1."""

import hashlib
import json
from typing import TYPE_CHECKING

from bulletin.schedule import mark_polled

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.archive import Listed

# A burst reads at most this many pages.
LAST_BURST_PAGE = 5

type Detect = Callable[[AsyncConnection, tuple[int, int], Sequence[Listed]], Awaitable[None]]


def fingerprint(items: Sequence[Listed]) -> str:
    """Hash the items' identities, titles and list dates, in page order."""
    key = [
        [i.site_id, i.article_id or i.link_url, i.title, i.listed_on and i.listed_on.isoformat()]
        for i in items
    ]
    return hashlib.sha256(json.dumps(key, ensure_ascii=False).encode()).hexdigest()


async def handle_page(
    conn: AsyncConnection,
    board: tuple[int, int],
    items: Sequence[Listed],
    at: datetime,
    detect: Detect,
) -> bool:
    """Run detection on a page that changed since the last poll; return whether it changed."""
    site_id, rcg = board
    current = fingerprint(items)
    async with conn.transaction():
        cur = await conn.execute(
            "SELECT fingerprint FROM board WHERE site_id = %s AND rcg = %s FOR UPDATE", board
        )
        row = await cur.fetchone()
        if row is None:
            msg = f"no board {site_id}-{rcg}"
            raise LookupError(msg)
        changed = row[0] != current
        if changed:
            await conn.execute(
                "UPDATE board SET fingerprint = %s WHERE site_id = %s AND rcg = %s",
                (current, site_id, rcg),
            )
            await detect(conn, board, items)
        await mark_polled(conn, site_id, rcg, at)
    return changed


type ReadPage = Callable[[int], Awaitable[list[Listed]]]


async def poll_board(
    conn: AsyncConnection,
    board: tuple[int, int],
    read_page: ReadPage,
    at: datetime,
    detect: Detect,
) -> bool:
    """Poll a board's page 1, and later pages on a burst; return whether page 1 changed.

    When every item on page 1 is unknown and the board was polled before, pages 2 to 5 are read
    until one holds a known item, and detection gets the items of every page read.
    """
    first = await read_page(1)
    extra: list[Listed] = []
    cur = await conn.execute(
        "SELECT last_polled_at IS NOT NULL FROM board WHERE site_id = %s AND rcg = %s", board
    )
    row = await cur.fetchone()
    if row is not None and row[0]:
        page, items = 1, first
        while page < LAST_BURST_PAGE and items and not await any_known(conn, items):
            page += 1
            items = await read_page(page)
            extra += items

    async def detect_all(
        conn: AsyncConnection, board: tuple[int, int], page_one: Sequence[Listed]
    ) -> None:
        await detect(conn, board, [*page_one, *extra])

    return await handle_page(conn, board, first, at, detect_all)


async def any_known(conn: AsyncConnection, items: Sequence[Listed]) -> bool:
    """Whether any of `items` is already stored, by article id or, for links, by URL."""
    cur = await conn.execute(
        "SELECT EXISTS (SELECT 1 FROM announcement a"
        " JOIN unnest(%s::int[], %s::bigint[], %s::text[]) AS i(site_id, article_id, link_url)"
        " ON a.site_id = i.site_id"
        " AND (a.article_id = i.article_id OR a.link_url = i.link_url))",
        (
            [i.site_id for i in items],
            [i.article_id for i in items],
            [i.link_url for i in items],
        ),
    )
    row = await cur.fetchone()
    return bool(row and row[0])
