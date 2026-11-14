"""Requirements of the detection capability."""

from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING

from bulletin.archive import Listed
from bulletin.detection import detect
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
