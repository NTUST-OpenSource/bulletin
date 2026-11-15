"""Requirements of the rendering and tags capabilities that storage meets."""

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from bulletin.archive import publish, revise
from bulletin.model import Content, Listed
from bulletin.renditions import Rendition, store

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


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Tags with their source")
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


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Tags with their source")
async def test_a_fallback_leaves_the_tags(migrated: AsyncConnection) -> None:
    """Tags with their source: a fallback rendition leaves the tags unchanged."""
    announcement, revision = await stored(migrated)
    await tag(migrated, announcement, "topic", "housing", "model")

    await store(migrated, announcement, revision, Rendition(1, "m", "t", "[t](u)", fallback=True))

    assert await tags_of(migrated, announcement) == {("topic", "housing", "model")}
