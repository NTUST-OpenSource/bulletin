"""Requirements of the event-log capability."""

import asyncio
from dataclasses import replace
from datetime import date
from typing import TYPE_CHECKING

import psycopg
import pytest

from bulletin.archive import Content, Listed, publish, restore, revise, withdraw
from bulletin.events import Kind, read_after, record

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from storage import Schema

LISTED = Listed(site_id=1000, host="www.ntust.edu.tw", article_id=153625, link_url=None, title="t")


def content(body: str) -> Content:
    return Content(title="t", publisher="p", body_html=f"<p>{body}</p>", body_text=body)


async def test_a_full_life(migrated: AsyncConnection) -> None:
    """Events: stored, edited, withdrawn and restored, in that order."""
    announcement = await publish(migrated, LISTED, notify=True, late=False)
    await revise(migrated, announcement, content("first"))
    await revise(migrated, announcement, content("edited"))
    await withdraw(migrated, announcement)
    await restore(migrated, announcement)

    events = await read_after(migrated, 0)

    assert [e.kind for e in events] == [
        Kind.PUBLISHED,
        Kind.REVISED,
        Kind.WITHDRAWN,
        Kind.RESTORED,
    ]
    assert {e.announcement_id for e in events} == {announcement}


async def test_events_are_never_changed(migrated: AsyncConnection) -> None:
    """Events: an event cannot be updated or deleted."""
    await publish(migrated, LISTED, notify=True, late=False)

    with pytest.raises(psycopg.errors.RaiseException):
        await migrated.execute("UPDATE event SET notify = false")
    with pytest.raises(psycopg.errors.RaiseException):
        await migrated.execute("DELETE FROM event")


async def test_concurrent_writers(schema: Schema, migrated: AsyncConnection) -> None:
    """Gap-free order: a reader resuming from its last id gets both writers' events once each."""
    announcement = await publish(migrated, LISTED, notify=True, late=False)
    start = (await read_after(migrated, 0))[-1].id
    first_recorded = asyncio.Event()
    release_first = asyncio.Event()

    async def first_writer(conn: AsyncConnection) -> None:
        async with conn.transaction():
            await record(conn, announcement, Kind.REVISED)
            first_recorded.set()
            await release_first.wait()

    async def second_writer(conn: AsyncConnection) -> None:
        async with conn.transaction():
            await record(conn, announcement, Kind.REVISED)

    async with await schema.connect() as first, await schema.connect() as second:
        first_task = asyncio.create_task(first_writer(first))
        await first_recorded.wait()
        second_task = asyncio.create_task(second_writer(second))
        # Room for the second writer to commit, if nothing holds it back.
        await asyncio.sleep(0.3)
        seen = await read_after(migrated, start)
        release_first.set()
        await asyncio.gather(first_task, second_task)
        seen += await read_after(migrated, seen[-1].id if seen else start)

    ids = [e.id for e in seen]
    assert len(ids) == 2
    assert len(set(ids)) == 2


async def test_events_need_a_transaction(migrated: AsyncConnection) -> None:
    """Gap-free order: outside a transaction the lock would be released before the insert."""
    with pytest.raises(RuntimeError):
        await record(migrated, 1, Kind.REVISED)


async def test_a_revision_is_not_notify_worthy(migrated: AsyncConnection) -> None:
    """Notify flag: only published events may be notify-worthy."""
    announcement = await publish(migrated, LISTED, notify=True, late=False)
    await revise(migrated, announcement, content("first"))
    await revise(migrated, announcement, content("edited"))

    revised = (await read_after(migrated, 0))[-1]

    assert revised.kind is Kind.REVISED
    assert not revised.notify
    for kind in (Kind.REVISED, Kind.WITHDRAWN, Kind.RESTORED):
        with pytest.raises(ValueError, match="notify"):
            async with migrated.transaction():
                await record(migrated, announcement, kind, notify=True)


async def test_backfill_is_marked_late(migrated: AsyncConnection) -> None:
    """Late discoveries are marked: a backfilled announcement is late and not notify-worthy."""
    backfilled = Listed(1000, "www.ntust.edu.tw", 90001, None, "t", date(2019, 3, 1))

    await publish(migrated, backfilled, notify=False, late=True)
    published = (await read_after(migrated, 0))[-1]

    assert published.kind is Kind.PUBLISHED
    assert published.late
    assert not published.notify
    with pytest.raises(ValueError, match="late"):
        await publish(migrated, replace(backfilled, article_id=90002), notify=True, late=True)
