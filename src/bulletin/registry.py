"""The sites and boards bulletin knows about, with each board's category and tier."""

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from psycopg import AsyncConnection

type Tier = Literal["P1", "P2", "P3", "P4", "off"]
type Category = Literal["announcement", "news", "regulation", "course", "excluded"]


@dataclass(frozen=True)
class Board:
    """A board of a site: a list of announcements at `/p/403-{site_id}-{rcg}-1.php`."""

    site_id: int
    rcg: int
    host: str
    unit: str
    name: str
    category: Category
    tier: Tier
    pending_review: bool = False


def load_seed(path: Path) -> list[Board]:
    """Read the boards of a seed file such as `seeds/boards.json`."""
    rows = json.loads(path.read_text(encoding="utf-8"))["boards"]
    return [Board(**row) for row in rows]


async def import_seed(conn: AsyncConnection, boards: Iterable[Board]) -> list[tuple[int, int]]:
    """Add the boards the registry does not hold yet; return their keys."""
    raise NotImplementedError


async def get_board(conn: AsyncConnection, site_id: int, rcg: int) -> Board | None:
    """Return a board of the registry, or None."""
    raise NotImplementedError


async def set_tier(conn: AsyncConnection, site_id: int, rcg: int, tier: Tier) -> None:
    """Change a board's tier."""
    raise NotImplementedError
