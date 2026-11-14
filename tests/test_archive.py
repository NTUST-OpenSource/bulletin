"""Requirements of the archive capability."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from bulletin.archive import fetch_article, publish
from bulletin.detection import detect
from bulletin.events import Kind, read_after
from bulletin.http import Response
from bulletin.model import Listed
from bulletin.registry import Board, import_seed
from bulletin.schedule import Job
from bulletin.worker import run_job

if TYPE_CHECKING:
    from psycopg import AsyncConnection

FIXTURES = Path(__file__).parent / "fixtures" / "articles"
PAGE = (FIXTURES / "1068-152869.html").read_bytes()
EXPECTED = json.loads((FIXTURES / "1068-152869.json").read_text(encoding="utf-8"))
AT = datetime(2026, 11, 18, 2, 0, tzinfo=UTC)
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


async def test_another_sites_article(migrated: AsyncConnection) -> None:
    """Article fetch: site 1000's article listed elsewhere is fetched from site 1000's host."""
    listed = Listed(1000, "www.ntust.edu.tw", 153625, None, "t")
    announcement = await publish(migrated, listed, notify=False, late=True)
    web = FakeWeb()

    await fetch_article(migrated, web, announcement)

    assert web.requested == ["https://www.ntust.edu.tw/p/406-1000-153625.php"]


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


async def test_new_articles_are_queued_for_fetching(migrated: AsyncConnection) -> None:
    """Article fetch: detection queues an article fetch for each new article, none for links."""
    await import_seed(migrated, [Board(1045, 1391, "h", "u", "n", "announcement", "P1")])
    pdf = Listed(1045, "bulletin.ntust.edu.tw", None, "https://example.com/a.pdf", "a file")

    [new, _] = await detect(migrated, (1045, 1391), [SHE, pdf], AT)

    cur = await migrated.execute("SELECT kind, ref, run_after FROM job")
    assert await cur.fetchall() == [("article", str(new), AT)]


@pytest.mark.xfail(strict=True, reason="Revisions")
async def test_rechecks_are_scheduled(migrated: AsyncConnection) -> None:
    """Revisions: a new article is re-checked 1, 3, 7 and 30 days after it was first seen."""
    await import_seed(migrated, [Board(1045, 1391, "h", "u", "n", "announcement", "P1")])

    [new] = await detect(migrated, (1045, 1391), [SHE], AT)

    cur = await migrated.execute("SELECT kind, ref, run_after FROM job ORDER BY run_after")
    assert await cur.fetchall() == [
        ("article", str(new), AT),
        *[("recheck", str(new), AT + timedelta(days=d)) for d in (1, 3, 7, 30)],
    ]


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Revisions")
async def test_an_edited_deadline(migrated: AsyncConnection) -> None:
    """Revisions: a changed body at the 3-day re-check is a second revision and a revised event."""
    announcement = await publish(migrated, SHE, notify=False, late=True)
    await fetch_article(migrated, FakeWeb(), announcement)
    edited = PAGE.replace(b"ntustoesh@gmail.com", b"ntust.oesh@gmail.com")

    await run_job(migrated, FakeWeb(edited), Job(1, "recheck", str(announcement)))

    assert len(await revisions(migrated, announcement)) == 2
    assert (await read_after(migrated, 0))[-1].kind is Kind.REVISED


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Revisions")
async def test_no_change(migrated: AsyncConnection) -> None:
    """Revisions: the same content at the 7-day re-check adds no revision or event."""
    announcement = await publish(migrated, SHE, notify=False, late=True)
    await fetch_article(migrated, FakeWeb(), announcement)
    events = await read_after(migrated, 0)

    await run_job(migrated, FakeWeb(), Job(1, "recheck", str(announcement)))

    assert len(await revisions(migrated, announcement)) == 1
    assert await read_after(migrated, 0) == events
