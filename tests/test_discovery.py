"""Requirement: Re-discovery (board registry), from site maps."""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from bulletin.discovery import discover, parse_site_map, queue_discoveries, site_map_url
from bulletin.registry import Board, Found, get_board, import_seed
from web import Answer, FakeWeb

if TYPE_CHECKING:
    from psycopg import AsyncConnection

AT = datetime(2026, 12, 20, 2, 0, tzinfo=UTC)
HOST = "student.ntust.edu.tw"
KNOWN = Board(1053, 1435, HOST, "u", "known name", "announcement", "P2")
# A site map in the school's markup: menu links to boards, articles and other sites.
SITE_MAP = b"""<div class="sitemap">
<a href="/p/403-1053-1435-1.php?Lang=zh-tw">renamed</a>
<a href="https://student.ntust.edu.tw/p/403-1053-2000-1.php">new board</a>
<a href="/p/403-1053-2000-1.php">new board again</a>
<a href="/p/406-1053-152183,r1436.php">an article</a>
<a href="https://www.ntust.edu.tw/p/403-1000-168-1.php">another site's board</a>
<a href="https://www.ntust.edu.tw/p/403-9999-1-1.php">an unknown site's board</a>
<a href="/p/412-1053-8693.php">a page</a>
</div>"""


def test_parse_a_site_map() -> None:
    """Re-discovery: the boards a site map links to, each once, with the first link's text."""
    url = site_map_url(HOST, 1053)

    assert url == "https://student.ntust.edu.tw/p/17-1053.php"
    assert parse_site_map(SITE_MAP.decode(), url) == [
        Found(1053, 1435, "renamed"),
        Found(1053, 2000, "new board"),
        Found(1000, 168, "another site's board"),
        Found(9999, 1, "an unknown site's board"),
    ]


async def test_a_new_board_appears(migrated: AsyncConnection) -> None:
    """Re-discovery: a new board joins off and pending review; known boards stay as they are."""
    await import_seed(migrated, [KNOWN])
    web = FakeWeb({site_map_url(HOST, 1053): Answer(200, body=SITE_MAP)})

    assert await discover(migrated, web, 1053, AT) == [(1053, 2000)]

    assert await get_board(migrated, 1053, 1435) == KNOWN
    added = await get_board(migrated, 1053, 2000)
    assert added == Board(
        1053, 2000, HOST, "u", "new board", "announcement", "off", pending_review=True
    )
    cur = await migrated.execute("SELECT discovered_at FROM site")
    assert await cur.fetchone() == (AT,)


async def test_once_a_month(migrated: AsyncConnection) -> None:
    """Re-discovery: a site is queued once 30 days have passed since its last walk, and once."""
    await import_seed(migrated, [KNOWN])
    await migrated.execute("UPDATE site SET discovered_at = %s", (AT - timedelta(days=29),))
    assert await queue_discoveries(migrated, AT) == 0

    await migrated.execute("UPDATE site SET discovered_at = %s", (AT - timedelta(days=31),))
    assert await queue_discoveries(migrated, AT) == 1
    assert await queue_discoveries(migrated, AT) == 0
    cur = await migrated.execute("SELECT kind, ref FROM job")
    assert await cur.fetchall() == [("discovery", "1053")]
