"""The announcement stream: filters, cursor pages and stream items (openspec/specs/public-api)."""

import base64
import binascii
from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

from psycopg import sql

from bulletin.archive import article_url
from bulletin.taxonomy import taxonomy

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from psycopg import AsyncConnection

MAX_WORDS = 10
MAX_QUERY = 100
DIMENSIONS = ("topic", "audience", "nature", "source")


class InvalidRequestError(ValueError):
    """A parameter the stream cannot use; its message is the API's error detail."""


@dataclass(frozen=True)
class Cursor:
    """Where a page ended: the stream day and id of its last item."""

    day: date
    id: int

    def encode(self) -> str:
        """The cursor as clients pass it, opaque URL-safe base64."""
        raw = f"{self.day.isoformat()}.{self.id}".encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    @classmethod
    def decode(cls, value: str) -> Cursor:
        """Read a cursor that `encode` wrote; anything else is invalid."""
        try:
            raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)).decode()
            day, _, announcement = raw.partition(".")
            return cls(date.fromisoformat(day), int(announcement))
        except (binascii.Error, UnicodeDecodeError, ValueError) as error:
            msg = "invalid cursor"
            raise InvalidRequestError(msg) from error


@dataclass(frozen=True)
class Filters:
    """What a stream request narrows to; empty means everything."""

    sites: tuple[int, ...] = ()
    boards: tuple[tuple[int, int], ...] = ()
    tags: tuple[tuple[str, str], ...] = ()
    since: date | None = None
    until: date | None = None
    words: tuple[str, ...] = ()
    titles_only: bool = False


def board_key(value: str) -> tuple[int, int]:
    """Read `<site>-<board>`."""
    site, _, rcg = value.partition("-")
    if not (site.isdigit() and rcg.isdigit()):
        msg = f"invalid board {value}"
        raise InvalidRequestError(msg)
    return int(site), int(rcg)


def tag_key(value: str) -> tuple[str, str]:
    """Read `<dimension>:<id>` against the taxonomy."""
    dimension, _, tag = value.partition(":")
    if tag not in {t.id for t in taxonomy().get(dimension, ())}:
        msg = f"unknown tag {value}"
        raise InvalidRequestError(msg)
    return dimension, tag


def query_words(query: str) -> tuple[str, ...]:
    """The words of a search, each matched as plain text."""
    words = tuple(query.split())
    if len(words) > MAX_WORDS or len(query) > MAX_QUERY:
        msg = "query too long"
        raise InvalidRequestError(msg)
    return words


def _where(
    filters: Filters, after: Cursor | None
) -> tuple[list[sql.Composable], dict[str, object]]:
    conditions: list[sql.Composable] = [sql.SQL("a.cross_post_of IS NULL")]
    params: dict[str, object] = {}
    if after is not None:
        conditions.append(sql.SQL("(a.dated, a.id) < (%(day)s, %(after)s)"))
        params |= {"day": after.day, "after": after.id}
    if filters.sites or filters.boards:
        # Placed on a selected board, itself or through a cross-post of it.
        conditions.append(
            sql.SQL(
                "a.id IN (SELECT COALESCE(c.cross_post_of, c.id) FROM placement p"
                " JOIN announcement c ON c.id = p.announcement_id"
                " WHERE p.site_id = ANY(%(sites)s) OR (p.site_id, p.rcg) IN"
                " (SELECT * FROM unnest(%(board_sites)s::integer[], %(board_rcgs)s::integer[])))"
            )
        )
        params |= {
            "sites": list(filters.sites),
            "board_sites": [site for site, _ in filters.boards],
            "board_rcgs": [rcg for _, rcg in filters.boards],
        }
    for n, (dimension, tag) in enumerate(filters.tags):
        conditions.append(
            sql.SQL(
                "EXISTS (SELECT FROM tag t WHERE t.announcement_id = a.id"
                " AND t.dimension = {} AND t.tag = {})"
            ).format(sql.Placeholder(f"dimension{n}"), sql.Placeholder(f"tag{n}"))
        )
        params |= {f"dimension{n}": dimension, f"tag{n}": tag}
    if filters.since is not None:
        conditions.append(sql.SQL("a.dated >= %(since)s"))
        params["since"] = filters.since
    if filters.until is not None:
        conditions.append(sql.SQL("a.dated <= %(until)s"))
        params["until"] = filters.until
    if filters.words:
        conditions.append(sql.SQL("a.id IN (SELECT id FROM matched)"))
    return conditions, params


def _matched(filters: Filters) -> tuple[sql.Composable, dict[str, object]]:
    """The search's matches, materialized so the planner scans the index once."""
    if not filters.words:
        return sql.SQL(""), {}
    each = [
        (
            sql.SQL("title &@ {w}")
            if filters.titles_only
            else sql.SQL("(title &@ {w} OR body_text &@ {w})")
        ).format(w=sql.Placeholder(f"word{n}"))
        for n in range(len(filters.words))
    ]
    cte = sql.SQL("WITH matched AS MATERIALIZED (SELECT id FROM announcement WHERE {}) ").format(
        sql.SQL(" AND ").join(each)
    )
    return cte, {f"word{n}": word for n, word in enumerate(filters.words)}


async def page(
    conn: AsyncConnection, filters: Filters, after: Cursor | None, limit: int
) -> tuple[list[int], Cursor | None]:
    """The ids of one page of the stream, newest stream day first, and the next page's cursor."""
    cte, params = _matched(filters)
    conditions, more = _where(filters, after)
    query = sql.SQL(
        "{}SELECT a.id, a.dated FROM announcement a WHERE {}"
        " ORDER BY a.dated DESC, a.id DESC LIMIT {}"
    ).format(cte, sql.SQL(" AND ").join(conditions), sql.Literal(limit + 1))
    cur = await conn.execute(query, params | more)
    rows = await cur.fetchall()
    if len(rows) <= limit:
        return [row[0] for row in rows], None
    last = rows[limit - 1]
    return [row[0] for row in rows[:limit]], Cursor(last[1], last[0])


@dataclass(frozen=True)
class RenditionSummary:
    """What a stream item shows of its rendition."""

    title: str
    summary: str | None
    deadline: date | None


@dataclass(frozen=True)
class Tags:
    """An announcement's stored tags, each dimension a list in the taxonomy's order."""

    topic: tuple[str, ...] = ()
    audience: tuple[str, ...] = ()
    nature: tuple[str, ...] = ()
    source: tuple[str, ...] = ()


@dataclass(frozen=True)
class Item:
    """One announcement as the stream lists it."""

    id: int
    site: int
    unit: str | None
    url: str
    link_item: bool
    title: str
    publisher: str | None
    day: date
    listed_on: date | None
    first_seen_at: datetime
    withdrawn_at: datetime | None
    boards: tuple[str, ...]
    tags: Tags
    rendition: RenditionSummary | None


async def _boards(conn: AsyncConnection, ids: Sequence[int]) -> dict[int, tuple[str, ...]]:
    """The boards each announcement and its cross-posts are placed on, its own site's first."""
    cur = await conn.execute(
        "SELECT o.id, p.site_id, p.rcg FROM placement p"
        " JOIN announcement c ON c.id = p.announcement_id"
        " JOIN announcement o ON o.id = COALESCE(c.cross_post_of, c.id)"
        " WHERE o.id = ANY(%s)"
        " ORDER BY o.id, p.site_id <> o.site_id, p.site_id, p.rcg",
        (list(ids),),
    )
    boards: dict[int, list[str]] = {}
    for announcement, site, rcg in await cur.fetchall():
        keys = boards.setdefault(announcement, [])
        if (key := f"{site}-{rcg}") not in keys:
            keys.append(key)
    return {announcement: tuple(keys) for announcement, keys in boards.items()}


async def _tags(conn: AsyncConnection, ids: Sequence[int]) -> dict[int, Tags]:
    order = {(t.dimension, t.id): n for tags in taxonomy().values() for n, t in enumerate(tags)}
    cur = await conn.execute(
        "SELECT announcement_id, dimension, tag FROM tag WHERE announcement_id = ANY(%s)",
        (list(ids),),
    )
    found: dict[int, dict[str, list[str]]] = {}
    for announcement, dimension, tag in await cur.fetchall():
        found.setdefault(announcement, {}).setdefault(dimension, []).append(tag)
    return {
        announcement: Tags(
            **{
                dimension: tuple(sorted(tags, key=lambda t, d=dimension: order.get((d, t), 0)))
                for dimension, tags in by_dimension.items()
                if dimension in DIMENSIONS
            }
        )
        for announcement, by_dimension in found.items()
    }


async def items(conn: AsyncConnection, ids: Iterable[int]) -> list[Item]:
    """The stream items of `ids`, in that order; unknown ids are left out."""
    wanted = list(ids)
    cur = await conn.execute(
        "SELECT a.id, a.site_id, s.unit, a.host, a.article_id, a.link_url, a.title, a.publisher,"
        " a.dated, a.listed_on, a.first_seen_at, a.withdrawn_at, n.title, n.summary, n.deadline"
        " FROM announcement a LEFT JOIN site s ON s.site_id = a.site_id"
        " LEFT JOIN rendition n ON n.id = a.current_rendition AND NOT n.fallback"
        " WHERE a.id = ANY(%s)",
        (wanted,),
    )
    rows = {row[0]: row for row in await cur.fetchall()}
    boards = await _boards(conn, wanted)
    tags = await _tags(conn, wanted)
    found: list[Item] = []
    for announcement in wanted:
        if (row := rows.get(announcement)) is None:
            continue
        _, site, unit, host, article, link, title, publisher, day, listed, seen, gone = row[:12]
        found.append(
            Item(
                id=announcement,
                site=site,
                unit=unit,
                url=article_url(host, site, article) if article else link,
                link_item=article is None,
                title=title,
                publisher=publisher,
                day=day,
                listed_on=listed,
                first_seen_at=seen,
                withdrawn_at=gone,
                boards=boards.get(announcement, ()),
                tags=tags.get(announcement, Tags()),
                rendition=None if row[12] is None else RenditionSummary(*row[12:15]),
            )
        )
    return found
