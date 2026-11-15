"""Cross-post pointers: `450` links that redirect to an article on another site."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.http import Fetch
    from bulletin.model import Listed


async def resolve_pointers(
    conn: AsyncConnection, fetch: Fetch, items: Sequence[Listed], at: datetime
) -> list[Listed]:
    """Replace each item that links to a pointer with the article it redirects to.

    A pointer is requested once; its target is kept for later polls.
    """
    raise NotImplementedError
