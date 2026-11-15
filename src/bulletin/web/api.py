"""The public read-only API, mounted at /api/v1 (openspec/specs/public-api)."""

from fastapi import FastAPI

from bulletin.files import FileStore
from bulletin.web.db import Connect


def api_app(connect: Connect, store: FileStore, release: str) -> FastAPI:
    """Build the API; `release` starts every ETag, so a new release never answers 304."""
    app = FastAPI(title="bulletin", docs_url=None, redoc_url=None, openapi_url="/openapi.json")
    app.state.connect = connect
    app.state.store = store
    app.state.release = release
    return app
