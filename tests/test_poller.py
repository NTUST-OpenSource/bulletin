"""Requirements of the polling capability that decide what a poll does with a page."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from bulletin.archive import Listed, publish
from bulletin.poller import handle_page, poll_board
from bulletin.registry import Board, import_seed
from bulletin.schedule import mark_polled

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


def item(article_id: int) -> Listed:
    return Listed(1000, "www.ntust.edu.tw", article_id, None, f"article {article_id}")


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Paging on bursts")
async def test_six_new_announcements_on_a_five_item_page(migrated: AsyncConnection) -> None:
    """Paging on bursts: pages 1 and 2 are read, page 3 is not, and all six are detected."""
    await import_seed(migrated, [Board(1000, 168, "h", "u", "n", "announcement", "P1")])
    for known in (90, 89, 88):
        await publish(migrated, item(known), notify=False, late=True)
    await mark_polled(migrated, 1000, 168, AT - timedelta(minutes=5))
    pages = {
        1: [item(n) for n in (106, 105, 104, 103, 102)],
        2: [item(101), item(90), item(89)],
        3: [item(88)],
    }
    requested: list[int] = []

    async def read_page(page: int) -> list[Listed]:
        requested.append(page)
        return pages[page]

    detect = Detections()
    await poll_board(migrated, (1000, 168), read_page, AT, detect)

    assert requested == [1, 2]
    [(_, detected)] = detect.pages
    assert {i.article_id for i in detected} >= {106, 105, 104, 103, 102, 101}


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Paging on bursts")
async def test_bursts_stop_at_page_five(migrated: AsyncConnection) -> None:
    """Paging on bursts: a board whose first pages are all new is read up to page 5."""
    await import_seed(migrated, [Board(1000, 168, "h", "u", "n", "announcement", "P1")])
    await mark_polled(migrated, 1000, 168, AT - timedelta(minutes=5))
    requested: list[int] = []

    async def read_page(page: int) -> list[Listed]:
        requested.append(page)
        return [item(1000 - page)]

    await poll_board(migrated, (1000, 168), read_page, AT, Detections())

    assert requested == [1, 2, 3, 4, 5]


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Paging on bursts")
async def test_a_first_poll_reads_page_one_only(migrated: AsyncConnection) -> None:
    """Paging on bursts: a board never polled before records page 1 and pages no further."""
    await import_seed(migrated, [Board(1000, 168, "h", "u", "n", "announcement", "P1")])
    requested: list[int] = []

    async def read_page(page: int) -> list[Listed]:
        requested.append(page)
        return [item(1000 - page)]

    await poll_board(migrated, (1000, 168), read_page, AT, Detections())

    assert requested == [1]
