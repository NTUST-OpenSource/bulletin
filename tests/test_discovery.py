"""Requirement: Re-discovery (board registry), from site maps."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from bulletin.discovery import board_hints, discover, home_url, queue_discoveries, site_map_url
from bulletin.markup import parse
from bulletin.pages import list_url
from bulletin.registry import Board, Found, get_board, import_seed, load_seed
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
<a href="/p/406-1053-152183,r1436.php">an article on a board without a list page</a>
<a href="https://www.ntust.edu.tw/p/403-1000-168-1.php">another site's board</a>
<a href="https://www.ntust.edu.tw/p/403-9999-1-1.php">an unknown site's board</a>
<a href="/p/412-1053-8693.php">a page</a>
</div>"""


@pytest.mark.xfail(strict=True, reason="Re-discovery")
def test_list_links_name_their_boards() -> None:
    """Re-discovery: list links give boards, each once, named by the first link's text."""
    url = site_map_url(HOST, 1053)

    assert url == "https://student.ntust.edu.tw/p/17-1053.php"
    assert board_hints(SITE_MAP.decode(), url, 1053) == [
        Found(1053, 1435, "renamed"),
        Found(1053, 2000, "new board"),
        Found(1053, 1436, ""),
        Found(1000, 168, "another site's board"),
        Found(9999, 1, "an unknown site's board"),
    ]


@pytest.mark.xfail(strict=True, reason="Re-discovery")
async def test_a_new_board_appears(migrated: AsyncConnection) -> None:
    """Re-discovery: a new board joins off and pending review; known boards stay as they are."""
    await import_seed(migrated, [KNOWN])
    web = FakeWeb({site_map_url(HOST, 1053): Answer(200, body=SITE_MAP)})
    web.answers[home_url(HOST)] = Answer(200, body=b"<html></html>")
    web.answers[list_url(HOST, 1053, 1436)] = Answer(302, {"Location": "/"})

    assert await discover(migrated, web, 1053, AT) == [(1053, 2000)]

    # 1436 has no list page, so it is not a board to add.
    assert [r.url for r in web.requests] == [
        home_url(HOST),
        site_map_url(HOST, 1053),
        list_url(HOST, 1053, 1436),
    ]

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


DISCOVERY = Path(__file__).parent / "fixtures" / "discovery"
HOME = (DISCOVERY / "student-1053-home.html").read_bytes()
RECORDED_MAP = (DISCOVERY / "student-1053-site-map.html").read_bytes()
MENU = [1435, 1436, 1437, 1439, 1440, 1441, 1442, 1443, 1444, 1446, 1506, 1665]


@pytest.mark.xfail(strict=True, reason="Re-discovery")
def test_menus_and_article_links_name_boards() -> None:
    """Re-discovery: the recorded home page names boards in menu scripts and article links; the
    recorded site map names one board in a menu script."""
    home = board_hints(HOME.decode(), home_url(HOST), 1053)
    site_map = board_hints(RECORDED_MAP.decode(), site_map_url(HOST, 1053), 1053)

    assert sorted({(f.site_id, f.rcg) for f in home}) == [(1053, n) for n in MENU]
    assert {f.name for f in home} == {""}
    assert site_map == [Found(1053, 1506, "")]


@pytest.mark.xfail(strict=True, reason="Re-discovery")
async def test_a_board_from_a_recorded_menu(migrated: AsyncConnection) -> None:
    """Re-discovery: a board only a menu names is named by its own list page; known boards cost
    no request."""
    seed = Path(__file__).parents[1] / "seeds" / "boards.json"
    await import_seed(migrated, [b for b in load_seed(seed) if (b.site_id, b.rcg) != (1053, 1665)])
    page = (Path(__file__).parent / "fixtures" / "lists" / "academic-course.html").read_bytes()
    web = FakeWeb({home_url(HOST): Answer(200, body=HOME)})
    web.answers[site_map_url(HOST, 1053)] = Answer(200, body=RECORDED_MAP)
    web.answers[list_url(HOST, 1053, 1665)] = Answer(200, body=page)

    assert await discover(migrated, web, 1053, AT) == [(1053, 1665)]

    assert [r.url for r in web.requests] == [
        home_url(HOST),
        site_map_url(HOST, 1053),
        list_url(HOST, 1053, 1665),
    ]
    added = await get_board(migrated, 1053, 1665)
    title = parse(page.decode()).select_first("title")
    assert added is not None
    assert title is not None
    assert (added.name, added.tier, added.pending_review) == (title.text().strip(), "off", True)
