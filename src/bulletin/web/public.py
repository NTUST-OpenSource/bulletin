"""The public app: health and the read-only API under /api/v1."""

from fastapi import FastAPI

from bulletin.files import FileStore
from bulletin.web.api import api_app
from bulletin.web.db import Connect


def public_app(connect: Connect, store: FileStore, release: str) -> FastAPI:
    """Build the public app."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/health")
    async def health() -> dict[str, str]:  # pyright: ignore[reportUnusedFunction]
        return {"status": "ok"}

    app.mount("/api/v1", api_app(connect, store, release))
    return app
