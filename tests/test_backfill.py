"""Requirements of the backfill capability."""

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from bulletin.backfill import queue_walks, walk
from bulletin.detection import detect
from bulletin.events import read_after
from bulletin.pages import list_url
from bulletin.registry import Board, import_seed
from bulletin.schedule import Job
from bulletin.worker import run_job
from web import Answer, FakeWeb

if TYPE_CHECKING:
    from psycopg import AsyncConnection

AT = datetime(2026, 11, 17, 18, 0, tzinfo=UTC)  # 02:00 in Taipei, inside the backfill window
LISTS = Path(__file__).parent / "fixtures" / "lists"
ARTICLES = Path(__file__).parent / "fixtures" / "articles"
BOARD = (1048, 1416)
HOST = "www.academic.ntust.edu.tw"
ACADEMIC = Board(*BOARD, HOST, "u", "n", "announcement", "P4")
# The recorded page lists four articles from 2026; the same page from 2015 is past ten years.
RECENT = (LISTS / "academic-course.html").read_bytes()
OLD = RECENT.replace(b"2026-", b"2015-")
LANGUAGE = (LISTS / "language-center-recruitment.html").read_bytes()
EMPTY = b'<div id="pageptlist"></div>'


def page(n: int) -> str:
    return list_url(HOST, *BOARD, n)


async def walks(conn: AsyncConnection) -> list[str]:
    cur = await conn.execute("SELECT ref FROM job WHERE kind = 'backfill' ORDER BY id")
    return [row[0] for row in await cur.fetchall()]


async def walk_to_the_end(conn: AsyncConnection, web: FakeWeb) -> None:
    while f"{BOARD[0]}-{BOARD[1]}" in await walks(conn):
        await conn.execute("DELETE FROM job WHERE ref = %s", (f"{BOARD[0]}-{BOARD[1]}",))
        await walk(conn, web, BOARD, AT)


async def backfill_state(conn: AsyncConnection) -> tuple[object, ...] | None:
    cur = await conn.execute("SELECT backfill_page, backfilled_at FROM board")
    return await cur.fetchone()


async def test_a_board_with_three_pages(migrated: AsyncConnection) -> None:
    """Ten-year walk: pages 2 and 3 are stored and the walk ends after the last page."""
    await import_seed(migrated, [ACADEMIC])
    web = FakeWeb({page(2): Answer(200, body=RECENT), page(3): Answer(200, body=LANGUAGE)})
    web.answers[page(4)] = Answer(200, body=EMPTY)

    assert await queue_walks(migrated, AT) == 1
    assert await queue_walks(migrated, AT) == 0
    await walk_to_the_end(migrated, web)

    assert [r.url for r in web.requests] == [page(2), page(3), page(4)]
    cur = await migrated.execute("SELECT count(*) FROM announcement")
    assert await cur.fetchone() == (8,)
    assert await backfill_state(migrated) == (4, AT)
    assert await queue_walks(migrated, AT) == 0


async def test_ten_years_reached(migrated: AsyncConnection) -> None:
    """Ten-year walk: a page of items older than ten years ends the walk and stores none."""
    await import_seed(migrated, [ACADEMIC])
    await migrated.execute("UPDATE board SET backfill_page = 40")
    await migrated.execute("INSERT INTO job (kind, ref) VALUES ('backfill', '1048-1416')")
    web = FakeWeb({page(40): Answer(200, body=OLD)})

    await walk_to_the_end(migrated, web)

    assert [r.url for r in web.requests] == [page(40)]
    cur = await migrated.execute("SELECT count(*) FROM announcement")
    assert await cur.fetchone() == (0,)
    assert await backfill_state(migrated) == (40, AT)


async def test_article_bodies(migrated: AsyncConnection) -> None:
    """Backfill articles: each stored article is fetched through a backfill job."""
    await import_seed(migrated, [ACADEMIC])
    web = FakeWeb({page(2): Answer(200, body=RECENT)})

    await walk(migrated, web, BOARD, AT)

    cur = await migrated.execute("SELECT id FROM announcement ORDER BY id")
    stored = [str(row[0]) for row in await cur.fetchall()]
    assert await walks(migrated) == [*stored, "1048-1416"]
    cur = await migrated.execute("SELECT id, kind, ref FROM job ORDER BY id LIMIT 1")
    job = Job(*(await cur.fetchone() or ()))
    article = "https://www.academic.ntust.edu.tw/p/406-1048-149096.php"
    web.answers[article] = Answer(200, body=(ARTICLES / "1068-152869.html").read_bytes())
    assert await run_job(migrated, web, job)
    cur = await migrated.execute("SELECT count(*) FROM revision")
    assert await cur.fetchone() == (1,)


async def test_restart_in_the_middle(migrated: AsyncConnection) -> None:
    """Resumable progress: a walk continues at the next unread page; a finished one stays done."""
    await import_seed(migrated, [ACADEMIC])
    await migrated.execute("UPDATE board SET backfill_page = 13")
    web = FakeWeb({page(13): Answer(200, body=RECENT)})

    await walk(migrated, web, BOARD, AT)
    assert await backfill_state(migrated) == (14, None)
    await migrated.execute("UPDATE board SET backfilled_at = %s", (AT,))
    await walk(migrated, web, BOARD, AT)

    assert [r.url for r in web.requests] == [page(13)]
    assert await queue_walks(migrated, AT) == 0


async def test_backfill_finds_an_unseen_announcement(migrated: AsyncConnection) -> None:
    """No announcements from backfill: the published events are late and not notify-worthy.

    A later poll that finds nothing new does not take the backfilled items for page 1's.
    """
    await import_seed(migrated, [ACADEMIC])
    await walk(migrated, FakeWeb({page(2): Answer(200, body=RECENT)}), BOARD, AT)

    events = await read_after(migrated, 0)
    assert len(events) == 4
    assert all(e.late and not e.notify for e in events)
    await detect(migrated, BOARD, [], AT)
    cur = await migrated.execute("SELECT count(*) FROM job WHERE kind = 'recheck'")
    assert await cur.fetchone() == (0,)
