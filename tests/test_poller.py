"""Requirements of the polling capability that decide what a poll does with a page."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from bulletin.archive import Listed
from bulletin.poller import handle_page
from bulletin.registry import Board, import_seed

if TYPE_CHECKING:
    from collections.abc import Sequence

    from psycopg import AsyncConnection

AT = datetime(2026, 11, 18, 2, 0, tzinfo=UTC)
PAGE = [
    Listed(1000, "www.ntust.edu.tw", 153625, None, "first", AT.date()),
    Listed(1045, "bulletin.ntust.edu.tw", None, "https://example.com/a.pdf", "a file"),
]


class Detections:
    def __init__(self) -> None:
        self.pages: list[tuple[tuple[int, int], list[Listed]]] = []

    async def __call__(
        self, _conn: AsyncConnection, board: tuple[int, int], items: Sequence[Listed]
    ) -> None:
        self.pages.append((board, list(items)))


async def test_same_page_twice(migrated: AsyncConnection) -> None:
    """Unchanged pages: the second identical poll is unchanged and detection does not run."""
    await import_seed(migrated, [Board(1045, 1391, "h", "u", "n", "announcement", "P1")])
    detect = Detections()

    first = await handle_page(migrated, (1045, 1391), PAGE, AT, detect)
    second = await handle_page(migrated, (1045, 1391), PAGE, AT + timedelta(minutes=5), detect)
    edited = [PAGE[0], replace(PAGE[1], title="a file, renamed")]
    third = await handle_page(migrated, (1045, 1391), edited, AT + timedelta(minutes=10), detect)

    assert (first, second, third) == (True, False, True)
    assert detect.pages == [((1045, 1391), PAGE), ((1045, 1391), edited)]
