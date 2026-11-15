"""Renditions of revisions and the tags they bring, stored with their rendered events."""

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from bulletin.archive import article_url
from bulletin.events import Kind, record
from bulletin.model import Attachment
from bulletin.prompt import PROMPT_VERSION

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from psycopg import AsyncConnection


@dataclass(frozen=True)
class Pending:
    """An announcement whose current revision waits for a rendition."""

    announcement_id: int
    revision_id: int
    url: str  # the article page
    title: str
    body_html: str
    attachments: tuple[Attachment, ...]
    dated: date  # the list date, else the day it was first seen in Taipei; dates are read by it


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
    rendered event is recorded in the same transaction. A rendition of a revision that is no longer
    current, edited while the model answered, is kept but changes neither the current rendition
    nor the tags: the new revision is rendered next.
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
        cur = await conn.execute(
            "UPDATE announcement SET current_rendition = %s"
            " WHERE id = %s AND current_revision = %s",
            (row[0], announcement_id, revision_id),
        )
        if cur.rowcount and not rendition.fallback:
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


async def next_pending(
    conn: AsyncConnection, now: datetime, resting: Sequence[int] = ()
) -> Pending | None:
    """The announcement to render next, if any waits.

    An article whose current revision has no rendition for `PROMPT_VERSION`, whose day falls
    within the last year, and not resting. Its day is the list date; without one, the list date of
    the dated article with the nearest id, since ids grow with time across the sites; else the
    day it was first seen in Taipei. First publications go before late discoveries; within each,
    the most recent day first.
    """
    cur = await conn.execute(
        "SELECT id, revision, host, site_id, article_id, title, body_html, dated FROM ("
        " SELECT a.id, r.id AS revision, a.host, a.site_id, a.article_id, r.title, r.body_html,"
        "  a.late, a.first_seen_at, COALESCE(a.listed_on, near.listed_on,"
        "  (a.first_seen_at AT TIME ZONE 'Asia/Taipei')::date) AS dated"
        " FROM announcement a JOIN revision r ON r.id = a.current_revision"
        " LEFT JOIN LATERAL (SELECT n.listed_on FROM ("
        "  (SELECT b.listed_on, b.article_id - a.article_id AS gap FROM announcement b"
        "   WHERE a.listed_on IS NULL AND b.listed_on IS NOT NULL AND b.article_id >= a.article_id"
        "   ORDER BY b.article_id LIMIT 1)"
        "  UNION ALL"
        "  (SELECT b.listed_on, a.article_id - b.article_id FROM announcement b"
        "   WHERE a.listed_on IS NULL AND b.listed_on IS NOT NULL AND b.article_id < a.article_id"
        "   ORDER BY b.article_id DESC LIMIT 1)"
        "  ) n ORDER BY n.gap LIMIT 1) near ON true"
        " WHERE a.article_id IS NOT NULL AND NOT (a.id = ANY(%s))"
        " AND NOT EXISTS (SELECT FROM rendition n"
        "  WHERE n.revision_id = r.id AND n.prompt_version = %s)"
        ") p WHERE dated >= (%s - interval '1 year')::date"
        " ORDER BY late, dated DESC, first_seen_at DESC, id DESC LIMIT 1",
        (list(resting), PROMPT_VERSION, now),
    )
    row = await cur.fetchone()
    if row is None:
        return None
    announcement, revision, host, site, article, title, body, dated = row
    cur = await conn.execute(
        "SELECT name, url, origin FROM attachment WHERE revision_id = %s ORDER BY id", (revision,)
    )
    return Pending(
        announcement_id=announcement,
        revision_id=revision,
        url=article_url(host, site, article),
        title=title,
        body_html=body,
        attachments=tuple(Attachment(*file) for file in await cur.fetchall()),
        dated=dated,
    )
