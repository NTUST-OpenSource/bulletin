"""Requirements of the archive capability."""

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from bulletin.archive import Listed, fetch_article, publish
from bulletin.http import Response

if TYPE_CHECKING:
    from psycopg import AsyncConnection

FIXTURES = Path(__file__).parent / "fixtures" / "articles"
PAGE = (FIXTURES / "1068-152869.html").read_bytes()
EXPECTED = json.loads((FIXTURES / "1068-152869.json").read_text(encoding="utf-8"))
SHE = Listed(1068, "she.ntust.edu.tw", 152869, None, "listed title", publisher="publisher")


class FakeWeb:
    """Answers every request with one recorded page and remembers what was asked."""

    def __init__(self, page: bytes = PAGE, status: int = 200, location: str = "") -> None:
        self.page, self.status, self.location = page, status, location
        self.requested: list[str] = []

    async def __call__(self, url: str) -> Response:
        self.requested.append(url)
        headers = {"Location": self.location} if self.location else {}
        return Response(url, self.status, headers, self.page if self.status == 200 else b"")


async def revisions(conn: AsyncConnection, announcement: int) -> list[tuple[str, str, str]]:
    cur = await conn.execute(
        "SELECT title, body_html, body_text FROM revision WHERE announcement_id = %s ORDER BY id",
        (announcement,),
    )
    return await cur.fetchall()


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Article fetch")
async def test_a_recorded_article(migrated: AsyncConnection) -> None:
    """Article fetch: the first revision holds the page's title, body and attachment links."""
    announcement = await publish(migrated, SHE, notify=False, late=True)
    web = FakeWeb()

    assert await fetch_article(migrated, web, announcement)

    assert web.requested == [EXPECTED["url"]]
    [(title, body_html, body_text)] = await revisions(migrated, announcement)
    assert title == EXPECTED["title"]
    assert body_html.startswith('<div class="mpgdetail">')
    assert all(part in body_text for part in EXPECTED["body_text_has"])
    cur = await migrated.execute("SELECT name, url, origin FROM attachment ORDER BY id")
    assert [list(row) for row in await cur.fetchall()] == EXPECTED["attachments"]
    cur = await migrated.execute("SELECT publisher FROM announcement")
    assert await cur.fetchall() == [("publisher",)]


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Article fetch")
async def test_another_sites_article(migrated: AsyncConnection) -> None:
    """Article fetch: site 1000's article listed elsewhere is fetched from site 1000's host."""
    listed = Listed(1000, "www.ntust.edu.tw", 153625, None, "t")
    announcement = await publish(migrated, listed, notify=False, late=True)
    web = FakeWeb()

    await fetch_article(migrated, web, announcement)

    assert web.requested == ["https://www.ntust.edu.tw/p/406-1000-153625.php"]


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Article fetch")
async def test_a_file_link_on_the_bulletin_board(migrated: AsyncConnection) -> None:
    """Article fetch: an item linking straight to a PDF is stored without a page request."""
    pdf = "https://bulletin.ntust.edu.tw/var/file/45/1045/img/1391/notice.pdf"
    listed = Listed(1045, "bulletin.ntust.edu.tw", None, pdf, "notice")
    announcement = await publish(migrated, listed, notify=False, late=True)
    web = FakeWeb()

    assert not await fetch_article(migrated, web, announcement)

    assert web.requested == []
    cur = await migrated.execute("SELECT link_url, title FROM announcement")
    assert await cur.fetchall() == [(pdf, "notice")]
