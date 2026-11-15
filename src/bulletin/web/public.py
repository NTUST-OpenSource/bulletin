"""The public app: health, the read-only API under /api/v1 and the web page."""

import re
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from bulletin.files import FileStore
from bulletin.web.api import api_app
from bulletin.web.db import Connect

if TYPE_CHECKING:
    from pathlib import Path

    from starlette.responses import Response

# The page revalidates on every load and is never framed; Vite's hashed files never change.
PAGE_HEADERS = {"Cache-Control": "no-cache", "Content-Security-Policy": "frame-ancestors 'none'"}
IMMUTABLE = {"Cache-Control": "public, max-age=31536000, immutable"}
ASSET = re.compile(r"[\w.-]+", re.ASCII)  # Vite writes assets/ flat
# The site's icons, at the root where browsers ask for them; not hashed, so cached for a day.
ICONS = {
    "favicon.svg": "image/svg+xml",
    "favicon.ico": "image/vnd.microsoft.icon",
    "apple-touch-icon.png": "image/png",
}
DAY = {"Cache-Control": "public, max-age=86400"}


def public_app(
    connect: Connect, store: FileStore, release: str, web: Path | None = None
) -> FastAPI:
    """Build the public app; `web` is the built frontend, served at / when given."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/health")
    async def health() -> dict[str, str]:  # pyright: ignore[reportUnusedFunction]
        return {"status": "ok"}

    app.mount("/api/v1", api_app(connect, store, release))
    if web is not None:
        _serve_page(app, web)
    return app


def _serve_page(app: FastAPI, web: Path) -> None:
    """Serve the page at / and /a/{id}, its built files under /assets and its icons; nothing else.

    Other paths answer 404 with the page, which shows its not-found view; the API mounted under
    /api/v1 keeps its own answers.
    """

    async def page() -> FileResponse:
        return FileResponse(web / "index.html", headers=PAGE_HEADERS)

    async def asset(name: str) -> FileResponse:
        path = web / "assets" / name
        if not ASSET.fullmatch(name) or not path.is_file():
            raise HTTPException(404)
        return FileResponse(path, headers=IMMUTABLE)

    async def icon(name: str) -> FileResponse:
        path = web / name
        if name not in ICONS or not path.is_file():
            raise HTTPException(404)
        return FileResponse(path, headers=DAY, media_type=ICONS[name])

    async def missing(request: Request, error: Exception) -> Response:
        assert isinstance(error, StarletteHTTPException)  # noqa: S101 - registered for this type only
        built_file = request.url.path.startswith("/assets/")
        if error.status_code != status.HTTP_404_NOT_FOUND or built_file:
            return await http_exception_handler(request, error)
        return FileResponse(web / "index.html", status.HTTP_404_NOT_FOUND, PAGE_HEADERS)

    app.get("/")(page)
    app.get("/a/{announcement:int}")(page)
    app.get("/assets/{name}")(asset)
    app.get("/{name}")(icon)
    app.add_exception_handler(StarletteHTTPException, missing)
