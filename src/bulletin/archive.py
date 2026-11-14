"""Announcements as the school published them, with their revisions and withdrawals."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

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


async def publish(conn: AsyncConnection, listed: Listed, *, notify: bool, late: bool) -> int:
    """Store a new announcement, record its published event and return its id."""
    raise NotImplementedError


async def revise(conn: AsyncConnection, announcement_id: int, content: Content) -> bool:
    """Store `content` as a revision unless it matches the latest; return whether it was stored."""
    raise NotImplementedError


async def withdraw(conn: AsyncConnection, announcement_id: int) -> None:
    """Mark an announcement withdrawn by the school, keeping its content."""
    raise NotImplementedError


async def restore(conn: AsyncConnection, announcement_id: int) -> None:
    """Lift the withdrawn mark of an announcement that answers again."""
    raise NotImplementedError
