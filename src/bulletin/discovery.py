"""Re-discovery: each known site's site map, walked once a month for boards the registry lacks."""

import re
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from bulletin.markup import parse
from bulletin.pages import PageError, join, list_url
from bulletin.registry import Found, add_discovered
from bulletin.tls import is_school

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.http import Fetch

# A board's list page: /p/403-1053-1435-1.php, the page number optional.
BOARD_PATH = re.compile(r"/p/403-(\d+)-(\d+)(?:-\d+)?\.php")
# An article link that names its board: /p/406-1053-152183,r1436.php.
ARTICLE_BOARD = re.compile(r"/p/40[46]-(\d+)-\d+,r(\d+)\.php")
# A menu entry that loads a board of the page's own site.
MENU = re.compile(r"Type=mobile_rcg_mstr&(?:amp;)?Nbr=(\d+)|name:\s*'Rcg',\s*value:\s*'?(\d+)")


def home_url(host: str) -> str:
    """A site's home page."""
    return f"https://{host}/index.php"


def site_map_url(host: str, site_id: int) -> str:
    """A site's site map page."""
    return f"https://{host}/p/17-{site_id}.php"


def board_hints(page: str, url: str, site_id: int) -> list[Found]:
    """Read the boards a page of site `site_id` names, in page order, each once.

    A list link names its board; article links and menu entries give only the number, so the
    name stays empty unless a list link names the board too.
    """
    hints: list[Found] = []
    for anchor in parse(page).select("a"):
        joined = join(url, anchor.attr("href"))
        link = urlsplit(joined or "")
        if not is_school(link.hostname or ""):
            continue
        if board := BOARD_PATH.fullmatch(link.path):
            hints.append(Found(int(board[1]), int(board[2]), anchor.text().strip()))
        elif article := ARTICLE_BOARD.fullmatch(link.path):
            hints.append(Found(int(article[1]), int(article[2]), ""))
    hints += [Found(site_id, int(menu[1] or menu[2]), "") for menu in MENU.finditer(page)]
    return merge(hints)


def merge(hints: list[Found]) -> list[Found]:
    """Each board once, in order of first mention, with the first name any hint gives it."""
    merged: dict[tuple[int, int], Found] = {}
    for hint in hints:
        key = (hint.site_id, hint.rcg)
        if key not in merged or (hint.name and not merged[key].name):
            merged[key] = hint
    return list(merged.values())


async def discover(
    conn: AsyncConnection, fetch: Fetch, site_id: int, at: datetime
) -> list[tuple[int, int]]:
    """Read a site's home page and site map and add the boards the registry lacks; return them.

    A board known only by its number is named by its list page, and left out when that page does
    not answer.
    """
    cur = await conn.execute("SELECT site_id, host FROM site")
    hosts: dict[int, str] = dict(await cur.fetchall())
    if site_id not in hosts:
        msg = f"no site {site_id}"
        raise LookupError(msg)
    cur = await conn.execute("SELECT site_id, rcg FROM board")
    held = set(await cur.fetchall())
    hints: list[Found] = []
    for url in (home_url(hosts[site_id]), site_map_url(hosts[site_id], site_id)):
        response = await fetch(url)
        if response.status != HTTPStatus.OK:
            raise PageError(response.status)
        hints += board_hints(response.text(), url, site_id)
    new: list[Found] = []
    for hint in merge(hints):
        key = (hint.site_id, hint.rcg)
        if hint.site_id not in hosts or key in held:
            continue
        name = hint.name or await list_title(fetch, hosts[hint.site_id], *key)
        if name is not None:
            new.append(Found(*key, name))
    async with conn.transaction():
        added = await add_discovered(conn, new)
        await conn.execute("UPDATE site SET discovered_at = %s WHERE site_id = %s", (at, site_id))
    return added


async def list_title(fetch: Fetch, host: str, site_id: int, rcg: int) -> str | None:
    """The title of a board's list page, or None when the page does not answer."""
    response = await fetch(list_url(host, site_id, rcg))
    if response.status != HTTPStatus.OK:
        return None
    title = parse(response.text()).select_first("title")
    return "" if title is None else title.text().strip()


async def queue_discoveries(conn: AsyncConnection, at: datetime) -> int:
    """Queue a walk of every site not walked in 30 days and not queued; return how many."""
    cur = await conn.execute(
        "INSERT INTO job (kind, ref, run_after) SELECT 'discovery', s.site_id::text, %s FROM site s"
        " WHERE s.discovered_at <= %s - interval '30 days' AND NOT EXISTS"
        " (SELECT 1 FROM job j WHERE j.kind = 'discovery' AND j.ref = s.site_id::text)",
        (at, at),
    )
    return cur.rowcount
