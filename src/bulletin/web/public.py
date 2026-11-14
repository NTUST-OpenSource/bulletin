"""The public app: health now, the read-only API in add-public-api."""

from fastapi import FastAPI


def public_app() -> FastAPI:
    """Build the public app."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/health")
    async def health() -> dict[str, str]:  # pyright: ignore[reportUnusedFunction]
        return {"status": "ok"}

    return app
