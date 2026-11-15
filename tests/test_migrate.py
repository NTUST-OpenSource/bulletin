"""Scaffolding: numbered SQL migrations, each applied once in its own transaction."""

from typing import TYPE_CHECKING

import psycopg
import pytest

from bulletin.migrate import migrate

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
