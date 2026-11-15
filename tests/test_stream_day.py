"""Requirement: Stream day (archive)."""

from datetime import date, datetime
from typing import TYPE_CHECKING

import pytest
from psycopg.errors import UndefinedColumn

from bulletin.archive import publish, redate
from bulletin.model import Listed

if TYPE_CHECKING:
    from psycopg import AsyncConnection

pytestmark = pytest.mark.xfail(
    strict=True, raises=(UndefinedColumn, NotImplementedError), reason="Stream day"
)

HOST = "www.ntust.edu.tw"
LAST_WEEK = date(2026, 11, 8)
LAST_SPRING = date(2026, 4, 20)


async def stored(conn: AsyncConnection, article: int | None, listed_on: date | None) -> int:
    link = None if article else f"https://{HOST}/var/file/0/1000/attach/{article}.pdf"
    return await publish(
        conn, Listed(1000, HOST, article, link, f"t{article}", listed_on), notify=False, late=False
    )


async def stream_day(conn: AsyncConnection, announcement: int) -> date:
    cur = await conn.execute("SELECT dated FROM announcement WHERE id = %s", (announcement,))
    row = await cur.fetchone()
    assert row is not None
    return row[0]


async def test_a_listed_announcement(migrated: AsyncConnection) -> None:
    """Stream day: an announcement listed on 3 November is dated 3 November."""
    listed = await stored(migrated, 150000, date(2026, 11, 3))

    assert await stream_day(migrated, listed) == date(2026, 11, 3)


async def test_an_article_without_a_list_date(migrated: AsyncConnection) -> None:
    """Stream day: an undated article takes the list date of its nearest dated neighbour."""
    await stored(migrated, 150000, LAST_SPRING)
    await stored(migrated, 150100, LAST_WEEK)
    undated = await stored(migrated, 150090, None)

    assert await stream_day(migrated, undated) == LAST_WEEK


async def test_a_link_item(migrated: AsyncConnection) -> None:
    """Stream day: a link item without a list date or article id is dated by first sight."""
    await stored(migrated, 150100, LAST_WEEK)
    link = await stored(migrated, None, None)
    await migrated.execute(
        "UPDATE announcement SET first_seen_at = %s WHERE id = %s",
        (datetime.fromisoformat("2026-11-14T17:30:00+00:00"), link),
    )
    await redate(migrated)

    # 17:30 UTC is 01:30 the next day in Taipei.
    assert await stream_day(migrated, link) == date(2026, 11, 15)


async def test_a_nearer_neighbour_later(migrated: AsyncConnection) -> None:
    """Stream day: the nightly upkeep moves an estimate to a nearer dated article stored later."""
    await stored(migrated, 150000, LAST_SPRING)
    undated = await stored(migrated, 150090, None)
    await stored(migrated, 150091, LAST_WEEK)

    assert await redate(migrated) == 1
    assert await stream_day(migrated, undated) == LAST_WEEK
