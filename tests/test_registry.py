"""Requirements of the board-registry capability."""

from typing import TYPE_CHECKING

import pytest

from bulletin.registry import Board, get_board, import_seed, set_tier

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from bulletin.registry import Category, Tier


def board(site_id: int, rcg: int, tier: Tier = "P4", category: Category = "announcement") -> Board:
    return Board(
        site_id,
        rcg,
        f"site{site_id}.ntust.edu.tw",
        f"unit {site_id}",
        f"board {rcg}",
        category,
        tier,
    )


async def tier_of(conn: AsyncConnection, site_id: int, rcg: int) -> Tier:
    found = await get_board(conn, site_id, rcg)
    assert found is not None
    return found.tier


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Board identity")
async def test_one_board_number_on_two_sites(migrated: AsyncConnection) -> None:
    """Board identity: the same board number on two sites are two boards."""
    await import_seed(migrated, [board(1100, 1927), board(1101, 1927)])

    await set_tier(migrated, 1100, 1927, "P2")

    assert await tier_of(migrated, 1100, 1927) == "P2"
    assert await tier_of(migrated, 1101, 1927) == "P4"
