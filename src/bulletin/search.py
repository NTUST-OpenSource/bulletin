"""Full-text search over titles and bodies, through the PGroonga indexes."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from psycopg import AsyncConnection


async def search(conn: AsyncConnection, query: str, *, titles_only: bool = False) -> list[int]:
    """Return the announcements matching `query`, newest first.

    The query uses PGroonga's syntax: words are ANDed, `OR` and `-word` work.
    """
    where = "title &@~ %s" if titles_only else "(title &@~ %s OR body_text &@~ %s)"
    cur = await conn.execute(
        f"SELECT id FROM announcement WHERE {where} ORDER BY first_seen_at DESC, id DESC",  # noqa: S608
        (query,) if titles_only else (query, query),
    )
    return [row[0] for row in await cur.fetchall()]
