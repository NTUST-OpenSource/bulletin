"""Requirements of the detection capability."""

import json
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from bulletin.archive import Listed
from bulletin.detection import detect, normalize, prune_frontier, record_frontier
from bulletin.events import Event, read_after
from bulletin.registry import Board, import_seed

if TYPE_CHECKING:
    from psycopg import AsyncConnection

AT = datetime(2026, 11, 18, 2, 0, tzinfo=UTC)
BULLETIN = (1045, 1391)
SECRETARIAT = (1063, 2211)
PDF = "https://bulletin.ntust.edu.tw/var/file/45/1045/img/1391/notice.pdf"


def article(article_id: int, listed_on: date | None = None, site_id: int = 1045) -> Listed:
    return Listed(
        site_id, f"site{site_id}.ntust.edu.tw", article_id, None, f"t{article_id}", listed_on
    )


async def seed(conn: AsyncConnection) -> None:
    await import_seed(
        conn,
        [
            Board(1045, 1391, "bulletin.ntust.edu.tw", "u", "n", "announcement", "P1"),
            Board(1045, 1392, "bulletin.ntust.edu.tw", "u", "n", "announcement", "P1"),
            Board(1063, 2211, "www.secretariat.ntust.edu.tw", "u", "n", "announcement", "P2"),
        ],
    )


async def placements(conn: AsyncConnection) -> set[tuple[int, int, int, int | None, str | None]]:
    cur = await conn.execute(
        "SELECT p.site_id, p.rcg, a.site_id, a.article_id, a.link_url"
        " FROM placement p JOIN announcement a ON a.id = p.announcement_id"
    )
    return {tuple(row) for row in await cur.fetchall()}


async def test_an_item_moves_up_from_page_two(migrated: AsyncConnection) -> None:
    """New announcement: a known item taking a freed place on page 1 is not new."""
    await seed(migrated)
    await detect(migrated, BULLETIN, [article(n) for n in (5, 4, 3, 2)], AT)

    new = await detect(migrated, BULLETIN, [article(n) for n in (5, 4, 2, 1)], AT)
    again = await detect(migrated, BULLETIN, [article(n) for n in (5, 4, 2, 1)], AT)

    assert new == [await announcement_id(migrated, 1045, 1)]
    assert again == []


async def test_a_pinned_old_announcement(migrated: AsyncConnection) -> None:
    """New announcement: a known two-year-old item pinned above newer ones is not new."""
    await seed(migrated)
    old = article(100, date(2024, 11, 1))
    await detect(migrated, BULLETIN, [old], AT - timedelta(days=700))

    new = await detect(migrated, BULLETIN, [old, article(200), article(199)], AT)

    assert len(new) == 2
    assert await announcement_id(migrated, 1045, 100) not in new


async def test_a_known_announcement_on_a_second_board(migrated: AsyncConnection) -> None:
    """New announcement: a stored item on another board gains a placement and is not new."""
    await seed(migrated)
    await detect(migrated, BULLETIN, [article(7)], AT)

    assert await detect(migrated, (1045, 1392), [article(7)], AT) == []
    assert await detect(migrated, SECRETARIAT, [article(7)], AT) == []
    assert await placements(migrated) == {
        (1045, 1391, 1045, 7, None),
        (1045, 1392, 1045, 7, None),
        (1063, 2211, 1045, 7, None),
    }


async def test_another_sites_article(migrated: AsyncConnection) -> None:
    """New announcement: site 1000's article listed by board 1063-2211 belongs to site 1000."""
    await seed(migrated)

    await detect(migrated, SECRETARIAT, [article(153625, site_id=1000)], AT)

    assert await placements(migrated) == {(1063, 2211, 1000, 153625, None)}


async def test_a_link_entry(migrated: AsyncConnection) -> None:
    """New announcement: an item linking to a PDF is a link entry of the board's site."""
    await seed(migrated)
    entry = Listed(1045, "bulletin.ntust.edu.tw", None, PDF, "notice")

    first = await detect(migrated, BULLETIN, [entry], AT)
    second = await detect(migrated, BULLETIN, [entry], AT)

    assert len(first) == 1
    assert second == []
    assert await placements(migrated) == {(1045, 1391, 1045, None, PDF)}


async def announcement_id(conn: AsyncConnection, site_id: int, article_id: int) -> int:
    cur = await conn.execute(
        "SELECT id FROM announcement WHERE site_id = %s AND article_id = %s", (site_id, article_id)
    )
    row = await cur.fetchone()
    assert row is not None
    return row[0]


async def test_a_redated_article(migrated: AsyncConnection) -> None:
    """Recycled articles: a newer list date updates the placement and records no event."""
    await seed(migrated)
    await detect(migrated, BULLETIN, [article(500, date(2021, 5, 3))], AT)
    events = await read_after(migrated, 0)

    new = await detect(migrated, BULLETIN, [article(500, date(2026, 11, 12))], AT)

    assert new == []
    assert await read_after(migrated, 0) == events
    cur = await migrated.execute("SELECT listed_on FROM placement")
    assert await cur.fetchall() == [(date(2026, 11, 12),)]


async def test_hourly_record(migrated: AsyncConnection) -> None:
    """Frontier record: the highest stored article id is recorded with the time."""
    await seed(migrated)
    await detect(migrated, BULLETIN, [article(153700), article(153650, site_id=1000)], AT)
    ten = AT.replace(hour=10)

    assert await record_frontier(migrated, ten) == 153700
    cur = await migrated.execute("SELECT at, max_article_id FROM frontier")
    assert await cur.fetchall() == [(ten, 153700)]


async def test_records_are_kept_for_seven_days(migrated: AsyncConnection) -> None:
    """Frontier record: records younger than 7 days stay."""
    await seed(migrated)
    await detect(migrated, BULLETIN, [article(10)], AT)
    for days in (8, 6):
        await record_frontier(migrated, AT - timedelta(days=days))

    assert await prune_frontier(migrated, AT) == 1
    cur = await migrated.execute("SELECT at FROM frontier")
    assert await cur.fetchall() == [(AT - timedelta(days=6),)]


async def published(conn: AsyncConnection, announcement: int) -> Event:
    [event] = [e for e in await read_after(conn, 0) if e.announcement_id == announcement]
    return event


async def test_a_late_published_draft(migrated: AsyncConnection) -> None:
    """Notify rule on backfilled boards: an unknown id 2,000 below the frontier is news."""
    await seed(migrated)
    await detect(migrated, (1045, 1392), [article(150000)], AT - timedelta(hours=80))
    await record_frontier(migrated, AT - timedelta(hours=73))
    await migrated.execute("UPDATE board SET backfilled_at = %s", (AT - timedelta(days=30),))

    [draft] = await detect(migrated, BULLETIN, [article(148000, date(2026, 9, 1))], AT)

    event = await published(migrated, draft)
    assert (event.notify, event.late) == (True, False)


async def with_frontier(conn: AsyncConnection, article_id: int, hours_ago: int) -> None:
    await detect(conn, (1045, 1392), [article(article_id)], AT - timedelta(hours=hours_ago + 1))
    await record_frontier(conn, AT - timedelta(hours=hours_ago))


async def test_a_board_turned_on(migrated: AsyncConnection) -> None:
    """Frontier rule: twenty unknown announcements from last year are late discoveries."""
    await seed(migrated)
    await with_frontier(migrated, 153000, 72)
    last_year = [article(140000 + n, date(2025, 11, 1)) for n in range(20)]

    new = await detect(migrated, SECRETARIAT, last_year, AT)

    assert len(new) == 20
    assert {(e.notify, e.late) for e in [await published(migrated, a) for a in new]} == {
        (False, True)
    }


async def test_a_genuinely_new_one(migrated: AsyncConnection) -> None:
    """Frontier rule: an id above the frontier of 72 hours ago is news."""
    await seed(migrated)
    await with_frontier(migrated, 153000, 80)
    await with_frontier(migrated, 153050, 72)
    await with_frontier(migrated, 153090, 10)

    news, late = await detect(migrated, SECRETARIAT, [article(153060), article(153040)], AT)

    assert ((await published(migrated, news)).notify, (await published(migrated, late)).notify) == (
        True,
        False,
    )


async def test_a_recent_list_date_is_news(migrated: AsyncConnection) -> None:
    """Frontier rule: a list date at most 2 days before the poll makes an old id news."""
    await seed(migrated)
    await with_frontier(migrated, 153000, 72)
    entry = Listed(1045, "bulletin.ntust.edu.tw", None, PDF, "notice", date(2026, 11, 16))

    recent, old = await detect(migrated, BULLETIN, [entry, article(100, date(2026, 11, 15))], AT)

    assert (await published(migrated, recent)).notify
    assert not (await published(migrated, old)).notify


async def test_first_start(migrated: AsyncConnection) -> None:
    """Frontier rule: with no frontier recorded, every announcement is stored and none is news."""
    await seed(migrated)

    new = await detect(migrated, BULLETIN, [article(200, AT.date()), article(199)], AT)

    assert len(new) == 2
    assert not any(e.notify for e in await read_after(migrated, 0))


TITLES = json.loads((Path(__file__).parent / "fixtures" / "cross-posts.json").read_text("utf-8"))


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Cross-posts")
def test_normalized_titles() -> None:
    """Cross-posts: prefixes, filler words, punctuation and spaces are dropped."""
    assert normalize(TITLES["original"]) == TITLES["normalized"]
    assert normalize(TITLES["copy"]) == TITLES["normalized"]


@pytest.mark.xfail(strict=True, reason="Cross-posts")
async def test_the_bulletin_boards_copy(migrated: AsyncConnection) -> None:
    """Cross-posts: the bulletin board's copy of yesterday's office post is linked, not news."""
    await seed(migrated)
    office = replace(article(153500, site_id=1063), title=TITLES["original"])
    [original] = await detect(migrated, SECRETARIAT, [office], AT - timedelta(days=1))
    await migrated.execute("UPDATE announcement SET first_seen_at = %s", (AT - timedelta(days=1),))
    await migrated.execute("UPDATE board SET backfilled_at = %s", (AT - timedelta(days=30),))

    [copy] = await detect(migrated, BULLETIN, [replace(article(153600), title=TITLES["copy"])], AT)

    cur = await migrated.execute("SELECT cross_post_of FROM announcement WHERE id = %s", (copy,))
    assert await cur.fetchone() == (original,)
    assert (await published(migrated, copy)).notify is False


async def test_short_generic_titles(migrated: AsyncConnection) -> None:
    """Cross-posts: two sites' posts with the same four-character title are not linked."""
    await seed(migrated)
    await migrated.execute("UPDATE board SET backfilled_at = %s", (AT - timedelta(days=30),))
    short = TITLES["short"]
    await detect(migrated, SECRETARIAT, [replace(article(1, site_id=1063), title=short)], AT)

    [second] = await detect(migrated, BULLETIN, [replace(article(2), title=short)], AT)

    cur = await migrated.execute("SELECT cross_post_of FROM announcement WHERE id = %s", (second,))
    assert await cur.fetchone() == (None,)
    assert (await published(migrated, second)).notify is True
