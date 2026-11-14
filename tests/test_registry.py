"""Requirements of the board-registry capability."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import psycopg
import pytest

from bulletin.registry import (
    Board,
    get_board,
    guess_category,
    import_seed,
    load_seed,
    set_tier,
)
from bulletin.schedule import due_boards
from bulletin.startup import start

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


async def test_one_board_number_on_two_sites(migrated: AsyncConnection) -> None:
    """Board identity: the same board number on two sites are two boards."""
    await import_seed(migrated, [board(1100, 1927), board(1101, 1927)])

    await set_tier(migrated, 1100, 1927, "P2")

    assert await tier_of(migrated, 1100, 1927) == "P2"
    assert await tier_of(migrated, 1101, 1927) == "P4"


def write_seed(path: Path, boards: list[Board]) -> Path:
    seed = path / "boards.json"
    seed.write_text(json.dumps({"boards": [asdict(b) for b in boards]}), encoding="utf-8")
    return seed


SEED = [board(1000, 167, "P3", "news"), board(1000, 168), board(1001, 1, "P1")]


async def test_first_start(db: AsyncConnection, tmp_path: Path) -> None:
    """Seed import: an empty database gets the seed's boards, tiers and categories."""
    await start(db, write_seed(tmp_path, SEED))

    assert [await get_board(db, b.site_id, b.rcg) for b in SEED] == SEED


async def test_the_owners_changes_survive_a_restart(db: AsyncConnection, tmp_path: Path) -> None:
    """Seed import: a board the seed has as P4 stays P1 once the owner set it so."""
    seed = write_seed(tmp_path, SEED)
    await start(db, seed)
    await set_tier(db, 1000, 168, "P1")

    await start(db, seed)

    assert await tier_of(db, 1000, 168) == "P1"


async def test_a_board_added_to_the_seed_later(db: AsyncConnection, tmp_path: Path) -> None:
    """Seed import: a fourth seed board is added on restart; the other three are unchanged."""
    await start(db, write_seed(tmp_path, SEED))
    await set_tier(db, 1000, 167, "off")
    fourth = board(1002, 5, "P2", "regulation")

    await start(db, write_seed(tmp_path, [*SEED, fourth]))

    assert await get_board(db, 1002, 5) == fourth
    assert await tier_of(db, 1000, 167) == "off"


def test_the_repository_seed_loads() -> None:
    """Seed import: seeds/boards.json reads as boards with valid tiers and categories."""
    boards = load_seed(Path(__file__).parents[1] / "seeds" / "boards.json")

    assert len(boards) == 445
    assert len({(b.site_id, b.rcg) for b in boards}) == len(boards)
    assert {b.tier for b in boards} == {"P1", "P2", "P3", "P4", "off"}


async def test_boards_are_never_deleted(migrated: AsyncConnection) -> None:
    """Boards are kept: an off, excluded board cannot be deleted, so it can be turned on later."""
    await import_seed(migrated, [board(1000, 9, "off", "excluded")])

    with pytest.raises(psycopg.errors.RaiseException):
        await migrated.execute("DELETE FROM board")

    assert await tier_of(migrated, 1000, 9) == "off"


async def test_an_excluded_board_turned_on(migrated: AsyncConnection) -> None:
    """Board categories: the tier alone decides polling; an excluded P4 board is polled."""
    await import_seed(
        migrated,
        [
            board(1000, 1, "off", "excluded"),
            board(1000, 2, "off", "announcement"),
            board(1000, 3, "P4", "announcement"),
        ],
    )
    await set_tier(migrated, 1000, 1, "P4")

    due = await due_boards(migrated, datetime.now(UTC))

    assert sorted(due) == [(1000, 1), (1000, 3)]


def test_guessing_from_names() -> None:
    """Category guess: banners, downloads, media coverage and announcements by their names."""
    fixture = Path(__file__).parent / "fixtures" / "category-guesses.json"
    guesses = json.loads(fixture.read_text(encoding="utf-8"))["guesses"]

    assert {name: guess_category(name) for name in guesses} == guesses
