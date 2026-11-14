"""Requirements of the event-log capability."""

from typing import TYPE_CHECKING

import psycopg
import pytest

from bulletin.archive import Content, Listed, publish, restore, revise, withdraw
from bulletin.events import Kind, read_after

if TYPE_CHECKING:
    from psycopg import AsyncConnection

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
