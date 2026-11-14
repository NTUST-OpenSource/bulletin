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
