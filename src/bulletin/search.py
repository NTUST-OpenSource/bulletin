"""Full-text search over titles and bodies, through the PGroonga indexes."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from psycopg import AsyncConnection


async def search(conn: AsyncConnection, query: str, *, titles_only: bool = False) -> list[int]:
    """Return the announcements matching `query`, newest first."""
    raise NotImplementedError
