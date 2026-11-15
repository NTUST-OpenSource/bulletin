"""Cross-post pointers: `450` links that redirect to an article on another site."""

from dataclasses import replace
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from bulletin.archive import REDIRECTS
from bulletin.pages import article_key, is_pointer

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.http import Fetch
    from bulletin.model import Listed


async def resolve_pointers(
    conn: AsyncConnection, fetch: Fetch, items: Sequence[Listed], at: datetime
) -> list[Listed]:
    """Replace each item that links to a pointer with the article it redirects to.

    A pointer is requested once; its target is kept for later polls. A pointer that does not
    redirect to an article leaves its item a link item.
    """
    resolved: list[Listed] = []
    for item in items:
        target = None
        if item.link_url is not None and is_pointer(item.link_url):
            target = await _target(conn, fetch, item.link_url, at)
        key = None if target is None else article_key(target)
        if key is None:
            resolved.append(item)
        else:
            host, site_id, article_id = key
            resolved.append(
                replace(item, site_id=site_id, host=host, article_id=article_id, link_url=None)
            )
    return resolved


async def _target(conn: AsyncConnection, fetch: Fetch, url: str, at: datetime) -> str | None:
    cur = await conn.execute("SELECT target FROM pointer WHERE url = %s", (url,))
    if (row := await cur.fetchone()) is not None:
        return row[0]
    response = await fetch(url)
    location = response.headers.get("Location", "")
    target = urljoin(url, location) if response.status in REDIRECTS and location else None
    # A server error says nothing about the pointer; it is asked again at the next poll.
    if response.status < HTTPStatus.INTERNAL_SERVER_ERROR:
        await conn.execute(
            "INSERT INTO pointer (url, target, resolved_at) VALUES (%s, %s, %s)"
            " ON CONFLICT DO NOTHING",
            (url, target, at),
        )
    return target
