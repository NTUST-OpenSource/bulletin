"""The worker: one request at a time from the queue, logged, with the hourly and nightly upkeep."""

import asyncio
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp

from bulletin.archive import publish
from bulletin.files import FileStore
from bulletin.model import Listed
from bulletin.pacer import Pacer
from bulletin.polllog import Entry, log_request
from bulletin.registry import Board, import_seed
from bulletin.schedule import enqueue
from bulletin.worker import Worker
from web import Answer, FakeWeb

if TYPE_CHECKING:
    import pytest
    from psycopg import AsyncConnection

    from bulletin.http import Fetch, Response

NOW = datetime(2026, 11, 18, 2, 0, tzinfo=UTC)  # Wednesday 10:00 in Taipei
FIXTURES = Path(__file__).parent / "fixtures"
LIST = "https://www.academic.ntust.edu.tw/p/403-1048-1416-1.php"
ARTICLE = "https://she.ntust.edu.tw/p/406-1068-152869.php"
ACADEMIC = Board(1048, 1416, "www.academic.ntust.edu.tw", "u", "n", "announcement", "P1")


class Clock:
    """Seconds that only move when the worker sleeps."""

    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def __call__(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds
        await asyncio.sleep(0)


def worker(web: Fetch, tmp_path: Path, clock: Clock | None = None) -> Worker:
    clock = clock or Clock()
    pacer = Pacer(clock=clock, sleep=clock.sleep, random=lambda: 0.0)
    return Worker(web, pacer, FileStore(tmp_path), lambda: NOW)


async def polls(conn: AsyncConnection) -> list[tuple[object, ...]]:
    cur = await conn.execute(
        "SELECT purpose, site_id, rcg, status, changed, cardinality(new_ids) FROM poll ORDER BY id"
    )
    return await cur.fetchall()


async def test_a_poll_is_logged(migrated: AsyncConnection, tmp_path: Path) -> None:
    """Poll log: a board's poll is logged with its board, status, change and new ids."""
    await import_seed(migrated, [ACADEMIC])
    page = (FIXTURES / "lists" / "academic-course.html").read_bytes()
    web = FakeWeb({LIST: Answer(200, body=page)})

    assert await worker(web, tmp_path).step(migrated)

    assert await polls(migrated) == [("poll", 1048, 1416, 200, True, 4)]
    cur = await migrated.execute("SELECT next_poll_at FROM board")
    assert await cur.fetchone() == (NOW + timedelta(minutes=5),)
    cur = await migrated.execute("SELECT count(*) FROM job WHERE kind = 'article'")
    assert await cur.fetchone() == (4,)


async def test_a_waf_block_pauses_the_queue(migrated: AsyncConnection, tmp_path: Path) -> None:
    """Failure backoff: after HTTP 406 the board backs off and no request starts for 15 minutes."""
    await import_seed(migrated, [ACADEMIC])
    clock = Clock()
    collector = worker(FakeWeb({LIST: Answer(406)}), tmp_path, clock)

    assert await collector.step(migrated)
    async with collector.pacer.slot():
        pass

    assert await polls(migrated) == [("poll", 1048, 1416, 406, None, 0)]
    cur = await migrated.execute("SELECT failures FROM board")
    assert await cur.fetchone() == (1,)
    assert clock.slept[-1] >= 15 * 60


async def test_a_failing_job_waits(migrated: AsyncConnection, tmp_path: Path) -> None:
    """A job that fails is tried again an hour later, and the queue moves on."""
    await enqueue(migrated, "discovery", "1053", NOW)

    assert await worker(FakeWeb({}), tmp_path).step(migrated)

    cur = await migrated.execute("SELECT attempts, run_after, last_error FROM job")
    attempts, run_after, error = await cur.fetchone() or (None, None, "")
    assert (attempts, run_after) == (1, NOW + timedelta(hours=1))
    assert "NotImplementedError" in error


async def test_an_article_queues_its_attachments(migrated: AsyncConnection, tmp_path: Path) -> None:
    """An article fetch is logged, and its attachments are queued for their sizes."""
    listed = Listed(1068, "she.ntust.edu.tw", 152869, None, "t")
    announcement = await publish(migrated, listed, notify=False, late=True)
    await enqueue(migrated, "article", str(announcement), NOW)
    page = (FIXTURES / "articles" / "1068-152869.html").read_bytes()

    assert await worker(FakeWeb({ARTICLE: Answer(200, body=page)}), tmp_path).step(migrated)

    assert await polls(migrated) == [("article", None, None, 200, None, 0)]
    cur = await migrated.execute("SELECT kind, ref FROM job")
    assert await cur.fetchall() == [("attachment", str(announcement))]


async def test_hourly_frontier_and_nightly_cleanup(
    migrated: AsyncConnection, tmp_path: Path
) -> None:
    """Frontier record and Poll log: the first step of an hour records the frontier, and the
    first step of a day after 03:00 in Taipei deletes old log entries."""
    await publish(migrated, Listed(1045, "h", 153700, None, "t"), notify=False, late=True)
    await log_request(migrated, Entry("poll", NOW - timedelta(days=31), 200, 1, 1))
    collector = worker(FakeWeb({}), tmp_path)

    assert not await collector.step(migrated)
    assert not await collector.step(migrated)

    cur = await migrated.execute("SELECT at, max_article_id FROM frontier")
    assert await cur.fetchall() == [(NOW, 153700)]
    assert await polls(migrated) == []
    assert collector.cleaned == date(2026, 11, 18)


async def test_an_attachment_job_keeps_the_files(migrated: AsyncConnection, tmp_path: Path) -> None:
    """Attachment sizes: the queued attachment job keeps the article's small files."""
    listed = Listed(1068, "she.ntust.edu.tw", 152869, None, "t")
    announcement = await publish(migrated, listed, notify=False, late=True)
    await enqueue(migrated, "article", str(announcement), NOW)
    expected = json.loads((FIXTURES / "articles" / "1068-152869.json").read_text("utf-8"))
    answers = {ARTICLE: Answer(200, body=(FIXTURES / "articles" / "1068-152869.html").read_bytes())}
    for n, (_, url, _) in enumerate(expected["attachments"]):
        answers[url] = Answer(200, {"Content-Length": "3"}, b"%03d" % n)
    collector = worker(FakeWeb(answers), tmp_path)

    assert await collector.step(migrated)
    assert await collector.step(migrated)

    cur = await migrated.execute("SELECT count(*) FROM attachment WHERE sha256 IS NOT NULL")
    assert await cur.fetchone() == (3,)
    cur = await migrated.execute("SELECT count(*) FROM job")
    assert await cur.fetchone() == (0,)
    assert [p[0] for p in await polls(migrated)].count("attachment") >= 3


async def test_a_transport_error_backs_the_board_off(
    migrated: AsyncConnection, tmp_path: Path
) -> None:
    """Failure backoff: a request that fails without an answer is logged and backs the board off."""
    await import_seed(migrated, [ACADEMIC])

    async def broken(url: str, /, **_: object) -> Response:
        raise aiohttp.ClientConnectionError(url)

    assert await worker(broken, tmp_path).step(migrated)

    assert await polls(migrated) == [("poll", 1048, 1416, None, None, 0)]
    cur = await migrated.execute("SELECT failures FROM board")
    assert await cur.fetchone() == (1,)


async def test_an_unreadable_page_backs_the_board_off(
    migrated: AsyncConnection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Failure backoff: a page that breaks the parser counts as a failed poll, not a retry loop."""
    await import_seed(migrated, [ACADEMIC])

    def unreadable(*_: object) -> list[Listed]:
        raise ValueError

    monkeypatch.setattr("bulletin.worker.parse_list", unreadable)
    collector = worker(FakeWeb({LIST: Answer(200, body=b"<html>")}), tmp_path)

    assert await collector.step(migrated)
    assert not await collector.step(migrated)

    assert await polls(migrated) == [("poll", 1048, 1416, 200, None, 0)]
