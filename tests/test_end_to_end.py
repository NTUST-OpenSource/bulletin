"""The collector end to end: seed, polls, article fetches and a re-check, through the worker."""

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from bulletin.events import Kind, read_after
from bulletin.files import FileStore
from bulletin.pacer import Pacer
from bulletin.startup import start
from bulletin.worker import Worker
from web import Answer, FakeWeb

if TYPE_CHECKING:
    from psycopg import AsyncConnection

HOST = "www.academic.ntust.edu.tw"
LIST = f"https://{HOST}/p/403-1048-1416-1.php"
PAGE = (Path(__file__).parent / "fixtures" / "lists" / "academic-course.html").read_bytes()
# The same board an hour later: 149200 is new at the top, dated today.
LATER = PAGE.replace(b"149096", b"149200").replace(b"2026-06-18", b"2026-11-18")
ARTICLE = b'<h2 class="hdline">t</h2><div class="mpgdetail"><p>body</p></div>'
IDS = (149096, 148431, 146657, 145601, 149200)


class Clock:
    def __init__(self, at: datetime) -> None:
        self.at = at
        self.seconds = 0.0

    def __call__(self) -> datetime:
        return self.at

    def monotonic(self) -> float:
        return self.seconds

    async def sleep(self, seconds: float) -> None:
        self.seconds += seconds
        await asyncio.sleep(0)


async def drain(worker: Worker, conn: AsyncConnection) -> None:
    for _ in range(100):
        if not await worker.step(conn):
            return
    pytest.fail("the queue did not empty")


async def test_end_to_end(migrated: AsyncConnection, tmp_path: Path) -> None:
    """Seed import, a first poll that announces nothing, a new article that is announced, and a
    re-check that finds it withdrawn."""
    seed = tmp_path / "boards.json"
    board = {"site_id": 1048, "rcg": 1416, "host": HOST, "unit": "u", "name": "n"}
    seed.write_text(json.dumps({"boards": [{**board, "category": "announcement", "tier": "P1"}]}))
    web = FakeWeb({LIST: Answer(200, body=PAGE)})
    for article in IDS:
        web.answers[f"https://{HOST}/p/406-1048-{article}.php"] = Answer(200, body=ARTICLE)
    clock = Clock(datetime(2026, 11, 18, 2, 0, tzinfo=UTC))  # Wednesday 10:00 in Taipei
    pacer = Pacer(clock=clock.monotonic, sleep=clock.sleep, random=lambda: 0.0)
    worker = Worker(web, pacer, FileStore(tmp_path / "files"), clock)

    await start(migrated, seed)
    await drain(worker, migrated)
    clock.at += timedelta(hours=1)
    web.answers[LIST] = Answer(200, body=LATER)
    await drain(worker, migrated)
    clock.at += timedelta(days=1, minutes=1)
    web.answers[f"https://{HOST}/p/406-1048-149200.php"] = Answer(
        302, {"Location": f"https://{HOST}/index.php"}
    )
    await drain(worker, migrated)

    cur = await migrated.execute("SELECT id, article_id FROM announcement")
    article_of = dict(await cur.fetchall())
    events = [
        (article_of[e.announcement_id], e.kind, e.notify) for e in await read_after(migrated, 0)
    ]
    first_poll = [(article, Kind.PUBLISHED, False) for article in IDS[:4]]
    assert events == [
        *first_poll,
        (149200, Kind.PUBLISHED, True),
        (149200, Kind.WITHDRAWN, False),
    ]
    cur = await migrated.execute("SELECT count(*) FROM revision")
    assert await cur.fetchone() == (5,)
