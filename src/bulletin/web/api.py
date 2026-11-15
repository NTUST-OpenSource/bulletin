"""The public read-only API, mounted at /api/v1 (openspec/specs/public-api)."""

from dataclasses import dataclass
from datetime import date
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from bulletin import stream
from bulletin.files import FileStore
from bulletin.registry import Site, public_sites
from bulletin.stream import Announcement, Cursor, EventItem, Filters, InvalidRequestError, Item
from bulletin.taxonomy import SEVERAL, taxonomy
from bulletin.web.db import Conn, Connect

DEFAULT_LIMIT = 30
MAX_LIMIT = 100
DEFAULT_EVENTS = 100
MAX_EVENTS = 500


@dataclass(frozen=True)
class Events:
    """A page of the events feed and the last id it holds, `after` when it holds none."""

    events: tuple[EventItem, ...]
    last: int


@dataclass(frozen=True)
class TagLabel:
    """A tag's id and approved label."""

    id: str
    label: str


@dataclass(frozen=True)
class Dimension:
    """A tag dimension, whether it allows several tags, and its tags in order."""

    id: str
    several: bool
    tags: tuple[TagLabel, ...]


@dataclass(frozen=True)
class Page:
    """One page of the stream and the cursor of the next, null on the last."""

    items: tuple[Item, ...]
    next: str | None


def bad_request(_: Request, error: Exception) -> JSONResponse:
    """A 400 whose detail names what was wrong."""
    if isinstance(error, RequestValidationError):
        problem = error.errors()[0]
        detail = f"invalid {problem['loc'][-1]}"
    else:
        detail = str(error)
    return JSONResponse({"detail": detail}, status.HTTP_400_BAD_REQUEST)


def api_app(connect: Connect, store: FileStore, release: str) -> FastAPI:
    """Build the API; `release` starts every ETag, so a new release never answers 304."""
    app = FastAPI(title="bulletin", docs_url=None, redoc_url=None, openapi_url="/openapi.json")
    app.state.connect = connect
    app.state.store = store
    app.state.release = release
    app.add_exception_handler(RequestValidationError, bad_request)
    app.add_exception_handler(InvalidRequestError, bad_request)

    @app.get("/announcements")
    async def announcements(  # noqa: PLR0913, PLR0917 - the stream's parameters  # pyright: ignore[reportUnusedFunction]
        conn: Conn,
        site: Annotated[list[int] | None, Query()] = None,
        board: Annotated[list[str] | None, Query()] = None,
        tag: Annotated[list[str] | None, Query()] = None,
        since: Annotated[date | None, Query(alias="from")] = None,
        until: Annotated[date | None, Query(alias="to")] = None,
        q: str = "",
        scope: Annotated[Literal["title"] | None, Query(alias="in")] = None,
        cursor: str | None = None,
        limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    ) -> Page:
        """The announcements that are not cross-posts, newest stream day first."""
        filters = Filters(
            sites=tuple(site or ()),
            boards=tuple(stream.board_key(b) for b in board or ()),
            tags=tuple(stream.tag_key(t) for t in tag or ()),
            since=since,
            until=until,
            words=stream.query_words(q),
            titles_only=scope == "title",
        )
        after = Cursor.decode(cursor) if cursor else None
        ids, following = await stream.page(conn, filters, after, limit)
        return Page(tuple(await stream.items(conn, ids)), following and following.encode())

    @app.get("/announcements/{announcement}")
    async def one(conn: Conn, request: Request, announcement: int) -> Announcement:  # pyright: ignore[reportUnusedFunction]
        """One announcement with its raw text, rendition, attachments and revisions."""
        found = await stream.announcement(conn, request.app.state.store, announcement)
        if found is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"no announcement {announcement}")
        return found

    @app.get("/events")
    async def events(  # pyright: ignore[reportUnusedFunction]
        conn: Conn,
        after: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=MAX_EVENTS)] = DEFAULT_EVENTS,
    ) -> Events:
        """Events with ids above `after`, in id order, each with its announcement."""
        found = await stream.events_after(conn, after, limit)
        return Events(tuple(found), found[-1].id if found else after)

    @app.get("/sites")
    async def sites(conn: Conn) -> list[Site]:  # pyright: ignore[reportUnusedFunction]
        """The sites with their unit's kind and college, and their boards."""
        return await public_sites(conn)

    @app.get("/tags")
    async def tags() -> list[Dimension]:  # pyright: ignore[reportUnusedFunction]
        """The taxonomy: four dimensions, whether each allows several tags, and their tags."""
        return [
            Dimension(
                dimension, dimension in SEVERAL, tuple(TagLabel(t.id, t.label) for t in found)
            )
            for dimension, found in taxonomy().items()
        ]

    return app
