"""Numbered SQL migrations, applied in order, each once and in its own transaction."""

from importlib import resources
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

    from psycopg import AsyncConnection

MIGRATIONS = resources.files("bulletin") / "migrations"


async def migrate(conn: AsyncConnection, source: Traversable = MIGRATIONS) -> list[str]:
    """Apply the migrations not yet recorded in `schema_migration`; return their names."""
    await conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migration"
        " (name text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"
    )
    cur = await conn.execute("SELECT name FROM schema_migration")
    done = {row[0] for row in await cur.fetchall()}
    applied: list[str] = []
    for path in sorted(source.iterdir(), key=lambda p: p.name):
        if not path.name.endswith(".sql") or path.name in done:
            continue
        async with conn.transaction():
            await conn.execute(path.read_bytes())
            await conn.execute("INSERT INTO schema_migration (name) VALUES (%s)", (path.name,))
        applied.append(path.name)
    return applied
