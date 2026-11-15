"""Requirements of the rendering and tags capabilities that storage meets."""

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from bulletin.archive import publish, revise
from bulletin.model import Attachment, Content, Listed
from bulletin.renditions import Pending, Rendition, next_pending, store

if TYPE_CHECKING:
    from psycopg import AsyncConnection

LISTED = Listed(site_id=1000, host="www.ntust.edu.tw", article_id=153625, link_url=None, title="t")
RENDITION = Rendition(prompt_version=1, model="gemini-4-hydrogen", title="t", markdown="m")
NEW_TAGS = frozenset(
    {("topic", "scholarships"), ("nature", "information"), ("source", "on-campus")}
)


async def stored(conn: AsyncConnection, body: str = "first") -> tuple[int, int]:
    """A stored announcement and its current revision."""
    announcement = await publish(conn, LISTED, notify=True, late=False)
    await revise(conn, announcement, Content("t", "p", f"<p>{body}</p>", body))
    cur = await conn.execute(
        "SELECT current_revision FROM announcement WHERE id = %s", (announcement,)
    )
    row = await cur.fetchone()
    assert row is not None
    return announcement, row[0]


async def tags_of(conn: AsyncConnection, announcement: int) -> set[tuple[str, str, str]]:
    cur = await conn.execute(
        "SELECT dimension, tag, set_by FROM tag WHERE announcement_id = %s", (announcement,)
    )
    return set(await cur.fetchall())


async def tag(conn: AsyncConnection, announcement: int, dimension: str, tag: str, by: str) -> None:
    await conn.execute(
        "INSERT INTO tag (announcement_id, dimension, tag, set_by) VALUES (%s, %s, %s, %s)",
        (announcement, dimension, tag, by),
    )


async def test_a_new_rendition_replaces_model_tags(migrated: AsyncConnection) -> None:
    """Tags with their source: new model tags replace the old ones; a manual tag stays."""
    announcement, revision = await stored(migrated)
    await tag(migrated, announcement, "topic", "fees", "manual")
    await tag(migrated, announcement, "topic", "housing", "model")

    rendition = replace(RENDITION, tags=NEW_TAGS | {("topic", "fees")})
    await store(migrated, announcement, revision, rendition)

    assert await tags_of(migrated, announcement) == {
        ("topic", "fees", "manual"),
        ("topic", "scholarships", "model"),
        ("nature", "information", "model"),
        ("source", "on-campus", "model"),
    }


async def test_a_fallback_leaves_the_tags(migrated: AsyncConnection) -> None:
    """Tags with their source: a fallback rendition leaves the tags unchanged."""
    announcement, revision = await stored(migrated)
    await tag(migrated, announcement, "topic", "housing", "model")

    await store(migrated, announcement, revision, Rendition(1, "m", "t", "[t](u)", fallback=True))

    assert await tags_of(migrated, announcement) == {("topic", "housing", "model")}


NOW = datetime.now(UTC)
TODAY = NOW.date()
FILE = Attachment("a.pdf", "https://www.ntust.edu.tw/var/file/0/1000/attach/a.pdf", "module")


async def article(
    conn: AsyncConnection, article_id: int, listed_on: date | None, *, late: bool = False
) -> int:
    """A stored article with one revision."""
    listed = Listed(1000, "www.ntust.edu.tw", article_id, None, f"t{article_id}", listed_on)
    announcement = await publish(conn, listed, notify=not late, late=late)
    await revise(conn, announcement, Content(f"t{article_id}", "p", "<p>b</p>", "b", (FILE,)))
    return announcement


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="What gets rendered")
async def test_a_new_announcement_during_the_backlog(migrated: AsyncConnection) -> None:
    """What gets rendered: a first publication goes before late discoveries from last spring."""
    await article(migrated, 1, TODAY - timedelta(days=200), late=True)
    spring = await article(migrated, 2, TODAY - timedelta(days=100), late=True)
    new = await article(migrated, 3, TODAY)

    first = await next_pending(migrated, NOW)
    assert first is not None
    assert first.announcement_id == new
    await store(migrated, new, first.revision_id, RENDITION)
    second = await next_pending(migrated, NOW)

    assert second is not None
    assert second.announcement_id == spring
    assert first == Pending(
        announcement_id=new,
        revision_id=first.revision_id,
        url="https://www.ntust.edu.tw/p/406-1000-3.php",
        title="t3",
        body_html="<p>b</p>",
        attachments=(FILE,),
        listed_on=TODAY,
        year=TODAY.year,
    )


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="What gets rendered")
async def test_an_announcement_from_two_years_ago(migrated: AsyncConnection) -> None:
    """What gets rendered: backfill's announcement listed two years ago stays raw."""
    await article(migrated, 1, TODAY - timedelta(days=730), late=True)

    assert await next_pending(migrated, NOW) is None


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="What gets rendered")
async def test_a_link_item(migrated: AsyncConnection) -> None:
    """What gets rendered: an announcement that links straight to a file stays raw."""
    link = Listed(1000, "www.ntust.edu.tw", None, FILE.url, "t", TODAY)
    await publish(migrated, link, notify=True, late=False)

    assert await next_pending(migrated, NOW) is None


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="What gets rendered")
async def test_resting_and_undated_announcements(migrated: AsyncConnection) -> None:
    """What gets rendered: a resting announcement waits; one without a list date counts its
    first sight."""
    resting = await article(migrated, 1, TODAY)
    undated = await article(migrated, 2, None)

    picked = await next_pending(migrated, NOW, [resting])

    assert picked is not None
    assert (picked.announcement_id, picked.listed_on, picked.year) == (undated, None, NOW.year)
