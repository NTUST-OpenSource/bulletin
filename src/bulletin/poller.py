"""What a poll does with the items it read from a board's page 1."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.archive import Listed

type Detect = Callable[[AsyncConnection, tuple[int, int], Sequence[Listed]], Awaitable[None]]


def fingerprint(items: Sequence[Listed]) -> str:
    """Hash the items' identities, titles and list dates, in page order."""
    raise NotImplementedError


async def handle_page(
    conn: AsyncConnection,
    board: tuple[int, int],
    items: Sequence[Listed],
    at: datetime,
    detect: Detect,
) -> bool:
    """Run detection on a page that changed since the last poll; return whether it changed."""
    raise NotImplementedError
