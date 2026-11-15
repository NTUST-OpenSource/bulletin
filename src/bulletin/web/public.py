"""The public app: health, the read-only API under /api/v1 and the web page."""

import re
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from bulletin.files import FileStore
from bulletin.web.api import api_app
from bulletin.web.db import Connect

if TYPE_CHECKING:
    from pathlib import Path

# The page revalidates on every load and is never framed; Vite's hashed files never change.
PAGE_HEADERS = {"Cache-Control": "no-cache", "Content-Security-Policy": "frame-ancestors 'none'"}
IMMUTABLE = {"Cache-Control": "public, max-age=31536000, immutable"}
ASSET = re.compile(r"[\w.-]+", re.ASCII)  # Vite writes assets/ flat


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
    """Serve the page at / and /a/{id}, and its built files under /assets; nothing else."""

    async def page() -> FileResponse:
        return FileResponse(web / "index.html", headers=PAGE_HEADERS)

    async def asset(name: str) -> FileResponse:
        path = web / "assets" / name
        if not ASSET.fullmatch(name) or not path.is_file():
            raise HTTPException(404)
        return FileResponse(path, headers=IMMUTABLE)

    app.get("/")(page)
    app.get("/a/{announcement:int}")(page)
    app.get("/assets/{name}")(asset)
