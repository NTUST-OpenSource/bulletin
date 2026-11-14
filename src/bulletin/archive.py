"""Announcements as the school published them, with their revisions and withdrawals."""

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from bulletin.events import Kind, record

if TYPE_CHECKING:
    from datetime import date

    from psycopg import AsyncConnection


@dataclass(frozen=True)
class Listed:
    """An announcement as a list page shows it; its identity comes from the item's link."""

    site_id: int
    host: str
    article_id: int | None
    link_url: str | None
    title: str
    listed_on: date | None = None


@dataclass(frozen=True)
class Attachment:
    """A file an article names, from its attachment module or a link in its body."""

    name: str
    url: str
    origin: Literal["module", "body"]


@dataclass(frozen=True)
class Content:
    """What an article page holds."""

    title: str
    publisher: str | None
    body_html: str
    body_text: str
    attachments: tuple[Attachment, ...] = ()

    def digest(self) -> str:
        """Hash what a revision is compared by: the title, the body and the attachment links."""
        key = [self.title, self.body_text, [a.url for a in self.attachments]]
        return hashlib.sha256(json.dumps(key, ensure_ascii=False).encode()).hexdigest()


async def publish(conn: AsyncConnection, listed: Listed, *, notify: bool, late: bool) -> int:
    """Store a new announcement, record its published event and return its id."""
    async with conn.transaction():
        cur = await conn.execute(
            "INSERT INTO announcement (site_id, host, article_id, link_url, title, listed_on, late)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (
                listed.site_id,
                listed.host,
                listed.article_id,
                listed.link_url,
                listed.title,
                listed.listed_on,
                late,
            ),
        )
        row = await cur.fetchone()
        assert row is not None  # noqa: S101 - INSERT ... RETURNING returns its row
        await record(conn, row[0], Kind.PUBLISHED, notify=notify, late=late)
    return row[0]


async def revise(conn: AsyncConnection, announcement_id: int, content: Content) -> bool:
    """Store `content` as a revision unless it matches the latest; return whether it was stored.

    A revision after the first records a revised event.
    """
    digest = content.digest()
    async with conn.transaction():
        cur = await conn.execute(
            "SELECT r.content_hash FROM announcement a"
            " LEFT JOIN revision r ON r.id = a.current_revision"
            " WHERE a.id = %s FOR UPDATE OF a",
            (announcement_id,),
        )
        row = await cur.fetchone()
        if row is None:
            msg = f"no announcement {announcement_id}"
            raise LookupError(msg)
        latest: str | None = row[0]
        if latest == digest:
            return False
        cur = await conn.execute(
            "INSERT INTO revision (announcement_id, title, body_html, body_text, content_hash)"
            " VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (announcement_id, content.title, content.body_html, content.body_text, digest),
        )
        revision = await cur.fetchone()
        assert revision is not None  # noqa: S101 - INSERT ... RETURNING returns its row
        async with conn.cursor() as many:
            await many.executemany(
                "INSERT INTO attachment (revision_id, name, url, origin) VALUES (%s, %s, %s, %s)",
                [(revision[0], a.name, a.url, a.origin) for a in content.attachments],
            )
        await conn.execute(
            "UPDATE announcement SET current_revision = %s, publisher = %s, body_text = %s"
            " WHERE id = %s",
            (revision[0], content.publisher, content.body_text, announcement_id),
        )
        if latest is not None:
            await record(conn, announcement_id, Kind.REVISED)
    return True


async def withdraw(conn: AsyncConnection, announcement_id: int) -> None:
    """Mark an announcement withdrawn by the school, keeping its content."""
    async with conn.transaction():
        cur = await conn.execute(
            "UPDATE announcement SET withdrawn_at = now()"
            " WHERE id = %s AND withdrawn_at IS NULL RETURNING id",
            (announcement_id,),
        )
        if await cur.fetchone():
            await record(conn, announcement_id, Kind.WITHDRAWN)


async def restore(conn: AsyncConnection, announcement_id: int) -> None:
    """Lift the withdrawn mark of an announcement that answers again."""
    async with conn.transaction():
        cur = await conn.execute(
            "UPDATE announcement SET withdrawn_at = NULL"
            " WHERE id = %s AND withdrawn_at IS NOT NULL RETURNING id",
            (announcement_id,),
        )
        if await cur.fetchone():
            await record(conn, announcement_id, Kind.RESTORED)
