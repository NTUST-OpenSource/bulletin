"""Re-discovery: each known site's site map, walked once a month for boards the registry lacks."""

import re
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urljoin, urlsplit

from bulletin.markup import parse
from bulletin.pages import PageError
from bulletin.registry import Found, add_discovered
from bulletin.tls import is_school

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.http import Fetch

# A board's list page: /p/403-1053-1435-1.php, the page number optional.
BOARD_PATH = re.compile(r"/p/403-(\d+)-(\d+)(?:-\d+)?\.php")


def site_map_url(host: str, site_id: int) -> str:
    """A site's site map page."""
    return f"https://{host}/p/17-{site_id}.php"


def home_url(host: str) -> str:
    """A site's home page."""
    return f"https://{host}/index.php"


def board_hints(page: str, url: str, site_id: int) -> list[Found]:  # noqa: ARG001
    """Read the boards a page of site `site_id` names, in page order, each once.

    A list link names its board; article links and menu entries give only the number, so the
    name is empty.
    """
    found: dict[tuple[int, int], Found] = {}
    for anchor in parse(page).select("a"):
        link = urlsplit(urljoin(url, anchor.attr("href").strip()))
        board = BOARD_PATH.fullmatch(link.path)
        if board and is_school(link.hostname or ""):
            key = (int(board[1]), int(board[2]))
            found.setdefault(key, Found(*key, anchor.text().strip()))
    return list(found.values())


async def discover(
    conn: AsyncConnection, fetch: Fetch, site_id: int, at: datetime
) -> list[tuple[int, int]]:
    """Walk a site's site map and add the boards of known sites the registry lacks; return them."""
    cur = await conn.execute("SELECT host FROM site WHERE site_id = %s", (site_id,))
    row = await cur.fetchone()
    if row is None:
        msg = f"no site {site_id}"
        raise LookupError(msg)
    url = site_map_url(row[0], site_id)
    response = await fetch(url)
    if response.status != HTTPStatus.OK:
        raise PageError(response.status)
    cur = await conn.execute("SELECT site_id FROM site")
    known = {r[0] for r in await cur.fetchall()}
    async with conn.transaction():
        found = [f for f in board_hints(response.text(), url, site_id) if f.site_id in known]
        added = await add_discovered(conn, found)
        await conn.execute("UPDATE site SET discovered_at = %s WHERE site_id = %s", (at, site_id))
    return added


async def queue_discoveries(conn: AsyncConnection, at: datetime) -> int:
    """Queue a walk of every site not walked in 30 days and not queued; return how many."""
    cur = await conn.execute(
        "INSERT INTO job (kind, ref, run_after) SELECT 'discovery', s.site_id::text, %s FROM site s"
        " WHERE s.discovered_at <= %s - interval '30 days' AND NOT EXISTS"
        " (SELECT 1 FROM job j WHERE j.kind = 'discovery' AND j.ref = s.site_id::text)",
        (at, at),
    )
    return cur.rowcount
