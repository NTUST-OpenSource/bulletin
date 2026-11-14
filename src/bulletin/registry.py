"""The sites and boards bulletin knows about, with each board's category and tier."""

import json
import re
from dataclasses import dataclass
from importlib import resources
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from psycopg import AsyncConnection

type Tier = Literal["P1", "P2", "P3", "P4", "off"]
type Category = Literal["announcement", "news", "regulation", "course", "excluded"]

# The name patterns of categories.json, in the order they are tried.
GUESSES: list[tuple[Category, re.Pattern[str]]] = [
    (cast("Category", category), re.compile(pattern))
    for category, pattern in json.loads(
        (resources.files("bulletin") / "categories.json").read_text(encoding="utf-8")
    ).items()
    if not category.startswith("_")
]


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
    """Add the boards the registry does not hold yet; return their keys.

    Boards already held keep their tier, category and review state, whatever the seed says.
    """
    boards = list(boards)
    async with conn.transaction(), conn.cursor() as cur:
        await cur.executemany(
            "INSERT INTO site (site_id, host, unit) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            sorted({(b.site_id, b.host, b.unit) for b in boards}),
        )
        added: list[tuple[int, int]] = []
        for b in boards:
            await cur.execute(
                "INSERT INTO board (site_id, rcg, name, category, tier, pending_review)"
                " VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING RETURNING site_id, rcg",
                (b.site_id, b.rcg, b.name, b.category, b.tier, b.pending_review),
            )
            added += await cur.fetchall()
    return added


async def get_board(conn: AsyncConnection, site_id: int, rcg: int) -> Board | None:
    """Return a board of the registry, or None."""
    cur = await conn.execute(
        "SELECT b.site_id, b.rcg, s.host, s.unit, b.name, b.category, b.tier, b.pending_review"
        " FROM board b JOIN site s USING (site_id) WHERE b.site_id = %s AND b.rcg = %s",
        (site_id, rcg),
    )
    row = await cur.fetchone()
    return None if row is None else Board(*row)


async def set_tier(conn: AsyncConnection, site_id: int, rcg: int, tier: Tier) -> None:
    """Change a board's tier; an unknown board raises LookupError."""
    cur = await conn.execute(
        "UPDATE board SET tier = %s WHERE site_id = %s AND rcg = %s RETURNING rcg",
        (tier, site_id, rcg),
    )
    if await cur.fetchone() is None:
        msg = f"no board {site_id}-{rcg}"
        raise LookupError(msg)


def guess_category(name: str) -> Category:
    """Guess a newly discovered board's category from its name."""
    for category, pattern in GUESSES:
        if pattern.search(name):
            return category
    return "announcement"
