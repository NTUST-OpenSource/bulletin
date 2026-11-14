"""Announcements as the school published them, with their revisions and withdrawals."""

from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urljoin, urlsplit

from bulletin.events import Kind, record
from bulletin.pages import parse_article

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.http import Fetch
    from bulletin.model import Content, Listed


async def publish(conn: AsyncConnection, listed: Listed, *, notify: bool, late: bool) -> int:
    """Store a new announcement, record its published event and return its id."""
    async with conn.transaction():
        cur = await conn.execute(
            "INSERT INTO announcement"
            " (site_id, host, article_id, link_url, title, publisher, listed_on, late)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (
                listed.site_id,
                listed.host,
                listed.article_id,
                listed.link_url,
                listed.title,
                listed.publisher,
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
            "UPDATE announcement SET current_revision = %s,"
            " publisher = COALESCE(%s, publisher), body_text = %s WHERE id = %s",
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


REDIRECTS = frozenset({301, 302, 303, 307, 308})


def is_redirect_home(status: int, location: str, url: str) -> bool:
    """Whether a response to `url` redirects to its site's home page, as a withdrawal does."""
    if status not in REDIRECTS or not location:
        return False
    target, page = urlsplit(urljoin(url, location)), urlsplit(url)
    return target.netloc == page.netloc and target.path in {"", "/", "/index.php"}


def article_url(host: str, site_id: int, article_id: int) -> str:
    """The article page of an announcement, on the host and site of its own link."""
    return f"https://{host}/p/406-{site_id}-{article_id}.php"


async def fetch_article(conn: AsyncConnection, fetch: Fetch, announcement_id: int) -> bool:
    """Fetch an announcement's article page and store it as a revision; return whether it did.

    A redirect to the site's home page withdraws the announcement, and an answer with content
    restores a withdrawn one. A link entry has no article page and is left as it is.
    """
    cur = await conn.execute(
        "SELECT host, site_id, article_id, publisher, withdrawn_at IS NOT NULL"
        " FROM announcement WHERE id = %s",
        (announcement_id,),
    )
    row = await cur.fetchone()
    if row is None:
        msg = f"no announcement {announcement_id}"
        raise LookupError(msg)
    host, site_id, article_id, publisher, withdrawn = row
    if article_id is None:
        return False
    url = article_url(host, site_id, article_id)
    response = await fetch(url)
    if is_redirect_home(response.status, response.headers.get("Location", ""), url):
        await withdraw(conn, announcement_id)
        return False
    if response.status != HTTPStatus.OK:
        return False
    await revise(conn, announcement_id, parse_article(response.text(), url, publisher))
    if withdrawn:
        await restore(conn, announcement_id)
    return True


async def prune(conn: AsyncConnection, now: datetime) -> int:
    """Delete announcements first seen or listed more than ten years ago, with all they hold.

    Withdrawn ones go too; return how many announcements were deleted.
    """
    async with conn.transaction():
        cur = await conn.execute(
            "SELECT id FROM announcement WHERE first_seen_at < %s - interval '10 years'"
            " OR listed_on < (%s - interval '10 years')::date",
            (now, now),
        )
        old = [row[0] for row in await cur.fetchall()]
        if not old:
            return 0
        # The event trigger lets this transaction delete events.
        await conn.execute("SET LOCAL bulletin.retention = 'on'")
        for statement in (
            "UPDATE announcement SET current_revision = NULL WHERE id = ANY(%s)",
            "UPDATE announcement SET cross_post_of = NULL WHERE cross_post_of = ANY(%s)",
            (
                "DELETE FROM attachment WHERE revision_id IN"
                " (SELECT id FROM revision WHERE announcement_id = ANY(%s))"
            ),
            "DELETE FROM revision WHERE announcement_id = ANY(%s)",
            "DELETE FROM placement WHERE announcement_id = ANY(%s)",
            "DELETE FROM event WHERE announcement_id = ANY(%s)",
            # Board walks are `<site>-<board>`; every other ref is an announcement id.
            (
                "DELETE FROM job WHERE kind IN ('article', 'recheck', 'backfill')"
                " AND ref = ANY(%s::bigint[]::text[])"
            ),
            "DELETE FROM announcement WHERE id = ANY(%s)",
        ):
            await conn.execute(statement, (old,))
    return len(old)
