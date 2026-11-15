"""HTTP caching of API answers: ETags, 304s, and errors that no cache keeps (F3)."""

import hashlib
import json
from typing import TYPE_CHECKING

from fastapi import Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from bulletin.stream import InvalidRequestError
from bulletin.web.db import Conn

if TYPE_CHECKING:
    from fastapi import FastAPI

CACHED = "public, max-age=60, stale-while-revalidate=600"
UNCACHED = "no-store"


class NotModifiedError(Exception):
    """The client's copy is current; raised before the route reads anything."""

    def __init__(self, etag: str) -> None:
        """Carry the ETag the 304 repeats."""
        super().__init__(etag)
        self.etag = etag


def matches(request: Request, etag: str) -> bool:
    """Whether `If-None-Match` holds `etag`."""
    held = request.headers.get("if-none-match", "")
    return held.strip() == "*" or etag in (tag.strip() for tag in held.split(","))


async def latest(request: Request, conn: Conn) -> str:
    """The ETag of the stream and the events: the release and the latest event and revision.

    Answer 304 at once when the client holds it.
    """
    cur = await conn.execute("SELECT (SELECT max(id) FROM event), (SELECT max(id) FROM revision)")
    row = await cur.fetchone()
    event, revision = row or (None, None)
    etag = f'W/"{request.app.state.release}.{event or 0}.{revision or 0}"'
    if matches(request, etag):
        raise NotModifiedError(etag)
    return etag


def answer(request: Request, value: object, etag: str | None = None) -> Response:
    """`value` as cacheable JSON, its ETag `etag` or else a digest of the body; 304 on a match."""
    body = json.dumps(jsonable_encoder(value), ensure_ascii=False, separators=(",", ":")).encode()
    if etag is None:
        etag = f'W/"{request.app.state.release}.{hashlib.sha256(body).hexdigest()[:20]}"'
    headers = {"ETag": etag, "Cache-Control": CACHED}
    if matches(request, etag):
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)
    return Response(body, media_type="application/json", headers=headers)


def not_modified(_: Request, error: Exception) -> Response:
    """The 304 for a current copy found before the route ran."""
    assert isinstance(error, NotModifiedError)  # noqa: S101 - registered for this type only
    headers = {"ETag": error.etag, "Cache-Control": CACHED}
    return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)


def failure(_: Request, error: Exception) -> JSONResponse:
    """An error as JSON that no cache keeps; bad parameters are 400s naming what was wrong."""
    if isinstance(error, HTTPException):
        code, detail, headers = error.status_code, error.detail, dict(error.headers or {})
    elif isinstance(error, RequestValidationError):
        code, detail, headers = 400, f"invalid {error.errors()[0]['loc'][-1]}", {}
    else:
        code, detail, headers = 400, str(error), {}
    return JSONResponse({"detail": detail}, code, headers | {"Cache-Control": UNCACHED})


def handle_errors(app: FastAPI) -> None:
    """Install the 304 and error handlers on `app`."""
    app.add_exception_handler(NotModifiedError, not_modified)
    for kind in (HTTPException, RequestValidationError, InvalidRequestError):
        app.add_exception_handler(kind, failure)
