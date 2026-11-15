"""Renditions of revisions and the tags they bring, stored with their rendered events."""

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

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
    """Store `rendition` of the revision as the announcement's current one and return its id."""
    raise NotImplementedError
