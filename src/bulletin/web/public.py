"""The public app: health, the read-only API under /api/v1 and the web page."""

from typing import TYPE_CHECKING

from fastapi import FastAPI

from bulletin.files import FileStore
from bulletin.web.api import api_app
from bulletin.web.db import Connect

if TYPE_CHECKING:
    from pathlib import Path


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
        raise NotImplementedError
    return app
