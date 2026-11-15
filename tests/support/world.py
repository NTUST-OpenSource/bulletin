"""A small archive for API tests: boards, announcements on them, renditions and tags."""

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
from psycopg import AsyncConnection

from bulletin.archive import publish, revise, withdraw
from bulletin.files import FileStore
from bulletin.model import Attachment, Content, Listed
from bulletin.registry import Board, import_seed
from bulletin.renditions import Rendition, store
from bulletin.web.public import public_app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable
    from datetime import date


BOARDS = (
    Board(1045, 1391, "bulletin.ntust.edu.tw", "school-wide", "board", "announcement", "P1"),
    Board(1053, 1435, "student.ntust.edu.tw", "student affairs", "news", "announcement", "P1"),
    Board(1053, 1436, "student.ntust.edu.tw", "student affairs", "awards", "news", "P2"),
    Board(1017, 631, "ece.ntust.edu.tw", "electronics", "jobs", "announcement", "P3"),
    Board(1017, 632, "ece.ntust.edu.tw", "electronics", "banner", "excluded", "off"),
)
HOSTS = {b.site_id: b.host for b in BOARDS}


@dataclass
class World:
    """An archive in a migrated schema, and a client of the public app over it."""

    conn: AsyncConnection
    files: Path
    next_article: int = 150000
    ids: dict[int, int] = field(default_factory=dict[int, int])  # article id -> announcement id

    async def boards(self, boards: Iterable[Board] = BOARDS) -> None:
        await import_seed(self.conn, list(boards))

    async def add(  # noqa: PLR0913 - an announcement's parts, all optional
        self,
        listed_on: date | None,
        *,
        boards: Iterable[str] = ("1053-1435",),
        title: str = "",
        body: str = "body",
        publisher: str | None = None,
        rendition: Rendition | None = None,
        tags: Iterable[tuple[str, str]] = (),
        attachments: Iterable[Attachment] = (),
        link: str | None = None,
        withdrawn: bool = False,
    ) -> int:
        """Store an announcement placed on `boards` (the first names its site) and return its id."""
        keys = [tuple(int(part) for part in key.split("-")) for key in boards]
        site = keys[0][0]
        self.next_article += 1
        article = None if link else self.next_article
        title = title or f"title {self.next_article}"
        listed = Listed(site, HOSTS[site], article, link, title, listed_on, publisher)
        announcement = await publish(self.conn, listed, notify=False, late=False)
        if article:
            self.ids[article] = announcement
        await revise(
            self.conn,
            announcement,
            Content(title, publisher, f"<p>{body}</p>", body, tuple(attachments)),
        )
        for board_site, rcg in keys:
            await self.conn.execute(
                "INSERT INTO placement (site_id, rcg, announcement_id, listed_on)"
                " VALUES (%s, %s, %s, %s)",
                (board_site, rcg, announcement, listed_on),
            )
        if rendition is not None:
            await store(self.conn, announcement, await self.revision(announcement), rendition)
        for dimension, tag in tags:
            await self.conn.execute(
                "INSERT INTO tag VALUES (%s, %s, %s, 'manual') ON CONFLICT DO NOTHING",
                (announcement, dimension, tag),
            )
        if withdrawn:
            await withdraw(self.conn, announcement)
        return announcement

    async def cross_post(self, of: int, listed_on: date, board: str = "1045-1391") -> int:
        """Store the school-wide board's copy of announcement `of`, linked as its cross-post."""
        copy = await self.add(listed_on, boards=(board,))
        await self.conn.execute(
            "UPDATE announcement SET cross_post_of = %s WHERE id = %s", (of, copy)
        )
        return copy

    async def revision(self, announcement: int) -> int:
        cur = await self.conn.execute(
            "SELECT current_revision FROM announcement WHERE id = %s", (announcement,)
        )
        row = await cur.fetchone()
        assert row is not None
        return row[0]

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[httpx.AsyncClient]:
        @asynccontextmanager
        async def connect() -> AsyncGenerator[AsyncConnection]:
            yield self.conn

        app = public_app(connect, FileStore(self.files), "test")
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://bulletin") as client:
            yield client


def rendition(  # noqa: PLR0913 - the parts of a rendition a test may set
    title: str = "rewritten",
    *,
    summary: str | None = "summary",
    deadline: date | None = None,
    tags: Iterable[tuple[str, str]] = (),
    fallback: bool = False,
    markdown: str = "m",
) -> Rendition:
    """A rendition as rendering would store it."""
    return Rendition(
        1, "gemini-4-hydrogen", title, markdown, summary, deadline, frozenset(tags), fallback
    )
