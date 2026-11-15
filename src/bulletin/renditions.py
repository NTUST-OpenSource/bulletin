"""Renditions of revisions and the tags they bring, stored with their rendered events."""

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from bulletin.events import Kind, record

if TYPE_CHECKING:
    from psycopg import AsyncConnection


@dataclass(frozen=True)
class Rendition:
    """What a rendering made of one revision; a fallback holds the title and link only."""

    prompt_version: int
    model: str
    title: str
    markdown: str
    summary: str | None = None
    deadline: date | None = None
    tags: frozenset[tuple[str, str]] = frozenset()
    fallback: bool = False


async def store(
    conn: AsyncConnection, announcement_id: int, revision_id: int, rendition: Rendition
) -> int:
    """Store `rendition` of the revision as the announcement's current one and return its id.

    Unless it is a fallback, its tags replace the announcement's model tags; manual tags stay. The
    rendered event is recorded in the same transaction.
    """
    async with conn.transaction():
        cur = await conn.execute(
            "INSERT INTO rendition (revision_id, prompt_version, model, fallback, title, markdown,"
            " summary, deadline) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (
                revision_id,
                rendition.prompt_version,
                rendition.model,
                rendition.fallback,
                rendition.title,
                rendition.markdown,
                rendition.summary,
                rendition.deadline,
            ),
        )
        row = await cur.fetchone()
        assert row is not None  # noqa: S101 - INSERT ... RETURNING returns its row
        await conn.execute(
            "UPDATE announcement SET current_rendition = %s WHERE id = %s",
            (row[0], announcement_id),
        )
        if not rendition.fallback:
            await conn.execute(
                "DELETE FROM tag WHERE announcement_id = %s AND set_by = 'model'",
                (announcement_id,),
            )
            async with conn.cursor() as many:
                # A manual tag the model also gives stays manual.
                await many.executemany(
                    "INSERT INTO tag (announcement_id, dimension, tag, set_by)"
                    " VALUES (%s, %s, %s, 'model') ON CONFLICT DO NOTHING",
                    [
                        (announcement_id, dimension, tag)
                        for dimension, tag in sorted(rendition.tags)
                    ],
                )
        await record(conn, announcement_id, Kind.RENDERED)
    return row[0]
