"""Scaffolding: numbered SQL migrations, each applied once in its own transaction."""

from datetime import date
from typing import TYPE_CHECKING

import psycopg
import pytest

from bulletin.archive import publish, revise
from bulletin.migrate import MIGRATIONS, migrate
from bulletin.model import Content, Listed
from bulletin.renditions import Rendition, store

if TYPE_CHECKING:
    from pathlib import Path

    from psycopg import AsyncConnection

TABLES = {
    "site",
    "board",
    "tier_change",
    "announcement",
    "placement",
    "revision",
    "attachment",
    "event",
    "job",
    "poll",
    "frontier",
    "pointer",
    "rendition",
    "tag",
    "schema_migration",
}


async def tables(db: AsyncConnection) -> set[str]:
    cur = await db.execute("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")
    return {row[0] for row in await cur.fetchall()}


async def test_migrations_apply_to_an_empty_schema(db: AsyncConnection) -> None:
    assert await migrate(db) == [
        "0001_initial.sql",
        "0002_site_discovered_at.sql",
        "0003_pointer.sql",
        "0004_rendering.sql",
        "0005_dated_articles.sql",
        "0006_stream_day.sql",
    ]
    assert await tables(db) == TABLES


async def test_a_second_run_changes_nothing(db: AsyncConnection) -> None:
    await migrate(db)

    assert await migrate(db) == []


async def test_a_failing_migration_leaves_nothing_behind(
    db: AsyncConnection, tmp_path: Path
) -> None:
    (tmp_path / "0001_good.sql").write_text("CREATE TABLE good (id int);", encoding="utf-8")
    (tmp_path / "0002_bad.sql").write_text(
        "CREATE TABLE half (id int); SELECT missing;", encoding="utf-8"
    )

    with pytest.raises(psycopg.errors.UndefinedColumn):
        await migrate(db, tmp_path)

    assert await tables(db) == {"good", "schema_migration"}
    cur = await db.execute("SELECT name FROM schema_migration")
    assert await cur.fetchall() == [("0001_good.sql",)]


async def test_title_search_finds_two_character_terms(db: AsyncConnection) -> None:
    """PGroonga indexes the title, so a two-character CJK term matches inside it."""
    await migrate(db)
    title = "".join(map(chr, (0x734E, 0x5B78, 0x91D1, 0x7533, 0x8ACB)))
    await db.execute("INSERT INTO site VALUES (1000, 'www.ntust.edu.tw', 'unit')")
    await db.execute(
        "INSERT INTO announcement (site_id, host, article_id, title)"
        " VALUES (1000, 'www.ntust.edu.tw', 1, %s)",
        (title,),
    )

    cur = await db.execute("SELECT article_id FROM announcement WHERE title &@~ %s", (title[1:3],))

    assert await cur.fetchall() == [(1,)]


async def stored(
    db: AsyncConnection, article_id: int, listed_on: date | None, *, fallback: bool = False
) -> int:
    """An article with a rendition and a model tag, as rendering stored it before 0005; a
    fallback has no tag."""
    listed = Listed(1000, "www.ntust.edu.tw", article_id, None, "t", listed_on)
    announcement = await publish(db, listed, notify=False, late=True)
    await revise(db, announcement, Content("t", "p", "<p>b</p>", "b"))
    cur = await db.execute(
        "SELECT current_revision FROM announcement WHERE id = %s", (announcement,)
    )
    revision = await cur.fetchone()
    assert revision is not None
    tags = frozenset[tuple[str, str]]() if fallback else frozenset({("topic", "courses")})
    rendition = Rendition(1, "m", "t", "m", tags=tags, fallback=fallback)
    await store(db, announcement, revision[0], rendition)
    return announcement


async def test_renditions_of_undated_articles_go(db: AsyncConnection, tmp_path: Path) -> None:
    """Migration 0005: articles without a list date lose their renditions and model tags, which
    were read against the day of the backfill; dated articles keep theirs, manual tags stay."""
    for source in MIGRATIONS.iterdir():
        if source.name < "0005":
            (tmp_path / source.name).write_text(source.read_text(encoding="utf-8"), "utf-8")
    await migrate(db, tmp_path)
    dated = await stored(db, 1, date(2026, 11, 1))
    undated = await stored(db, 2, None)
    await db.execute("INSERT INTO tag VALUES (%s, 'topic', 'fees', 'manual')", (undated,))

    assert (await migrate(db))[0] == "0005_dated_articles.sql"

    cur = await db.execute("SELECT id, current_rendition IS NOT NULL FROM announcement")
    assert set(await cur.fetchall()) == {(dated, True), (undated, False)}
    cur = await db.execute(
        "SELECT r.announcement_id FROM rendition n JOIN revision r ON r.id = n.revision_id"
    )
    assert set(await cur.fetchall()) == {(dated,)}
    cur = await db.execute("SELECT announcement_id, set_by FROM tag")
    assert set(await cur.fetchall()) == {(dated, "model"), (undated, "manual")}


@pytest.mark.xfail(strict=True, raises=IndexError, reason="Placeholders put back")
async def test_fallbacks_go(db: AsyncConnection, tmp_path: Path) -> None:
    """Migration 0007: fallback renditions go, so their articles render again with placeholders
    put back only in link targets; other renditions stay."""
    for source in MIGRATIONS.iterdir():
        if source.name < "0007":
            (tmp_path / source.name).write_text(source.read_text(encoding="utf-8"), "utf-8")
    await migrate(db, tmp_path)
    rendered = await stored(db, 1, date(2026, 11, 1))
    fell_back = await stored(db, 2, date(2026, 11, 1), fallback=True)

    assert (await migrate(db))[0] == "0007_retry_fallbacks.sql"

    cur = await db.execute("SELECT id, current_rendition IS NOT NULL FROM announcement")
    assert set(await cur.fetchall()) == {(rendered, True), (fell_back, False)}
    cur = await db.execute(
        "SELECT r.announcement_id FROM rendition n JOIN revision r ON r.id = n.revision_id"
    )
    assert set(await cur.fetchall()) == {(rendered,)}
