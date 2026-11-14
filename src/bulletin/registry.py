"""The sites and boards bulletin knows about, with each board's category and tier."""

import json
import re
from dataclasses import dataclass
from importlib import resources
from typing import TYPE_CHECKING, Literal, cast

from bulletin.schedule import interval

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import datetime
    from pathlib import Path

    from psycopg import AsyncConnection

type Tier = Literal["P1", "P2", "P3", "P4", "off"]
type Category = Literal["announcement", "news", "regulation", "course", "excluded"]
TIERS: tuple[Tier, ...] = ("P1", "P2", "P3", "P4", "off")

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


async def set_tier(
    conn: AsyncConnection, site_id: int, rcg: int, tier: Tier, *, by: str = "cli"
) -> None:
    """Change a board's tier, due again one new interval after its last poll.

    The change is recorded with `by`, who made it. An unknown tier raises ValueError and an
    unknown board LookupError; neither changes anything.
    """
    if tier not in TIERS:
        msg = f"unknown tier {tier}"
        raise ValueError(msg)
    async with conn.transaction():
        cur = await conn.execute(
            "SELECT tier, last_polled_at FROM board WHERE site_id = %s AND rcg = %s FOR UPDATE",
            (site_id, rcg),
        )
        row = await cur.fetchone()
        if row is None:
            msg = f"no board {site_id}-{rcg}"
            raise LookupError(msg)
        old, last = row
        step = None if last is None else interval(tier, last)
        await conn.execute(
            "UPDATE board SET tier = %s, next_poll_at = %s WHERE site_id = %s AND rcg = %s",
            (tier, None if last is None or step is None else last + step, site_id, rcg),
        )
        if old != tier:
            await conn.execute(
                "INSERT INTO tier_change (site_id, rcg, old_tier, new_tier, changed_by)"
                " VALUES (%s, %s, %s, %s, %s)",
                (site_id, rcg, old, tier, by),
            )


def guess_category(name: str) -> Category:
    """Guess a newly discovered board's category from its name."""
    for category, pattern in GUESSES:
        if pattern.search(name):
            return category
    return "announcement"


@dataclass(frozen=True)
class Found:
    """A board that re-discovery saw on a known site."""

    site_id: int
    rcg: int
    name: str


async def add_discovered(conn: AsyncConnection, found: Iterable[Found]) -> list[tuple[int, int]]:
    """Add the boards the registry does not hold as off and pending review; return their keys.

    Boards the registry holds are left as they are, renamed or not.
    """
    added: list[tuple[int, int]] = []
    async with conn.transaction(), conn.cursor() as cur:
        for f in found:
            await cur.execute(
                "INSERT INTO board (site_id, rcg, name, category, tier, pending_review)"
                " VALUES (%s, %s, %s, %s, 'off', true)"
                " ON CONFLICT DO NOTHING RETURNING site_id, rcg",
                (f.site_id, f.rcg, f.name, guess_category(f.name)),
            )
            added += await cur.fetchall()
    return added


@dataclass(frozen=True)
class TierChange:
    """A board's tier change: from what, to what, by whom and when."""

    old_tier: Tier
    new_tier: Tier
    changed_by: str
    changed_at: datetime


async def tier_history(conn: AsyncConnection, site_id: int, rcg: int) -> list[TierChange]:
    """Return a board's tier changes, newest first."""
    cur = await conn.execute(
        "SELECT old_tier, new_tier, changed_by, changed_at FROM tier_change"
        " WHERE site_id = %s AND rcg = %s ORDER BY changed_at DESC, id DESC",
        (site_id, rcg),
    )
    return [TierChange(*row) for row in await cur.fetchall()]
