"""Requirement: Poll log (polling)."""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from bulletin.polllog import Entry, log_request, prune

if TYPE_CHECKING:
    from psycopg import AsyncConnection

NOW = datetime(2026, 11, 18, 3, 0, tzinfo=UTC)


async def test_log_retention(migrated: AsyncConnection) -> None:
    """Poll log: the nightly cleanup deletes the 31-day-old entry and keeps the 29-day-old one."""
    kept = Entry(
        "poll",
        NOW - timedelta(days=29),
        200,
        8123,
        140,
        board=(1045, 1391),
        changed=True,
        new_ids=(153703,),
    )
    await log_request(migrated, kept)
    await log_request(migrated, Entry("article", NOW - timedelta(days=31), 406, None, 90))

    assert await prune(migrated, NOW) == 1
    cur = await migrated.execute(
        "SELECT purpose, at, status, bytes, ms, site_id, rcg, changed, new_ids FROM poll"
    )
    assert await cur.fetchall() == [
        ("poll", kept.at, 200, 8123, 140, 1045, 1391, True, [153703]),
    ]
