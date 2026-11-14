"""Which items on a polled list are new announcements, and which of those are news."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.archive import Listed


async def detect(
    conn: AsyncConnection, board: tuple[int, int], items: Sequence[Listed], at: datetime
) -> list[int]:
    """Store the new announcements among `items` and place every item on `board`.

    Return the ids of the new announcements, in page order.
    """
    raise NotImplementedError
