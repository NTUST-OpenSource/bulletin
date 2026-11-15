"""The public read-only API, mounted at /api/v1 (openspec/specs/public-api)."""

import re
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from bulletin import stream
from bulletin.files import FileStore
from bulletin.registry import Site, public_sites
from bulletin.stream import Announcement, Cursor, EventItem, Filters, Item
from bulletin.taxonomy import SEVERAL, taxonomy
from bulletin.web.caching import answer, handle_errors, latest
from bulletin.web.db import Conn, Connect
from bulletin.web.limits import SearchLimit, client_key

DEFAULT_LIMIT = 30
MAX_LIMIT = 100
DEFAULT_EVENTS = 100
MAX_EVENTS = 500
DIGEST = re.compile(r"[0-9a-f]{64}")
IMMUTABLE = "public, max-age=31536000, immutable"
OFFICE = "application/vnd.openxmlformats-officedocument"
OPEN = "application/vnd.oasis.opendocument"
# Stored files' types by extension; others are octet-stream attachments.
TYPES = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "doc": "application/msword",
    "docx": f"{OFFICE}.wordprocessingml.document",
    "xls": "application/vnd.ms-excel",
    "xlsx": f"{OFFICE}.spreadsheetml.sheet",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": f"{OFFICE}.presentationml.presentation",
    "odt": f"{OPEN}.text",
    "ods": f"{OPEN}.spreadsheet",
    "odp": f"{OPEN}.presentation",
    "zip": "application/zip",
    "7z": "application/x-7z-compressed",
    "rar": "application/vnd.rar",
}


@dataclass(frozen=True)
class Page:
    """One page of the stream and the cursor of the next, null on the last."""

    items: tuple[Item, ...]
    next: str | None


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


Latest = Annotated[str, Depends(latest)]


def api_app(connect: Connect, store: FileStore, release: str) -> FastAPI:  # noqa: C901 - the routes
    """Build the API; `release` starts every ETag, so a new release never answers 304."""
    app = FastAPI(title="bulletin", docs_url=None, redoc_url=None, openapi_url="/openapi.json")
    app.state.connect = connect
    app.state.store = store
    app.state.release = release
    app.state.limit = SearchLimit()
    handle_errors(app)
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["If-None-Match"]
    )

    @app.get("/announcements", response_model=Page)
    async def announcements(  # noqa: PLR0913, PLR0917 - the stream's parameters  # pyright: ignore[reportUnusedFunction]
        conn: Conn,
        request: Request,
        etag: Latest,
        site: Annotated[list[int] | None, Query()] = None,
        board: Annotated[list[str] | None, Query()] = None,
        tag: Annotated[list[str] | None, Query()] = None,
        since: Annotated[date | None, Query(alias="from")] = None,
        until: Annotated[date | None, Query(alias="to")] = None,
        q: str = "",
        scope: Annotated[Literal["title"] | None, Query(alias="in")] = None,
        cursor: str | None = None,
        limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    ) -> Response:
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
        if filters.words and (key := client_key(request)) is not None:
            wait = request.app.state.limit.refuse(key)
            if wait is not None:
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    "too many searches",
                    {"Retry-After": str(wait)},
                )
        ids, following = await stream.page(conn, filters, after, limit)
        found = Page(tuple(await stream.items(conn, ids)), following and following.encode())
        return answer(request, found, etag)

    @app.get("/announcements/{announcement}", response_model=Announcement)
    async def one(conn: Conn, request: Request, announcement: int) -> Response:  # pyright: ignore[reportUnusedFunction]
        """One announcement with its raw text, rendition, attachments and revisions."""
        found = await stream.announcement(conn, request.app.state.store, announcement)
        if found is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"no announcement {announcement}")
        return answer(request, found)

    @app.get("/events", response_model=Events)
    async def events(  # pyright: ignore[reportUnusedFunction]
        conn: Conn,
        request: Request,
        etag: Latest,
        after: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=MAX_EVENTS)] = DEFAULT_EVENTS,
    ) -> Response:
        """Events with ids above `after`, in id order, each with its announcement."""
        found = await stream.events_after(conn, after, limit)
        return answer(request, Events(tuple(found), found[-1].id if found else after), etag)

    @app.get("/sites", response_model=list[Site])
    async def sites(conn: Conn, request: Request) -> Response:  # pyright: ignore[reportUnusedFunction]
        """The sites with their unit's kind and college, and their boards."""
        return answer(request, await public_sites(conn))

    @app.get("/tags", response_model=list[Dimension])
    async def tags(request: Request) -> Response:  # pyright: ignore[reportUnusedFunction]
        """The taxonomy: four dimensions, whether each allows several tags, and their tags."""
        return answer(
            request,
            [
                Dimension(
                    dimension, dimension in SEVERAL, tuple(TagLabel(t.id, t.label) for t in found)
                )
                for dimension, found in taxonomy().items()
            ],
        )

    @app.get("/files/{sha256}/{name:path}", response_class=FileResponse)
    async def file(conn: Conn, request: Request, sha256: str, name: str) -> FileResponse:  # pyright: ignore[reportUnusedFunction]
        """A stored attachment file under a name it was recorded with."""
        path = request.app.state.store.path(sha256) if DIGEST.fullmatch(sha256) else None
        cur = await conn.execute(
            "SELECT FROM attachment WHERE sha256 = %s AND name = %s LIMIT 1", (sha256, name)
        )
        if path is None or await cur.fetchone() is None or not path.is_file():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no file")
        kind = TYPES.get(name.rpartition(".")[2].lower())
        return FileResponse(
            path,
            media_type=kind or "application/octet-stream",
            filename=name,
            content_disposition_type="inline" if kind else "attachment",
            headers={"X-Content-Type-Options": "nosniff", "Cache-Control": IMMUTABLE},
        )

    return app
