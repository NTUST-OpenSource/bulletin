"""Requirement: The page (web-frontend): the built frontend on the public listener."""

from typing import TYPE_CHECKING

import httpx
import pytest

from bulletin.files import FileStore
from bulletin.web.public import public_app

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager
    from pathlib import Path

    from psycopg import AsyncConnection

PAGE = "<!doctype html><title>bulletin.</title><script src=/assets/index-1a2b3c.js></script>"
SCRIPT = "export {};"
REVALIDATE = "no-cache, no-transform"
IMMUTABLE = "public, max-age=31536000, immutable"
NO_FRAMES = "frame-ancestors 'none'"


def no_database() -> AbstractAsyncContextManager[AsyncConnection]:
    raise AssertionError


def built(tmp_path: Path) -> Path:
    """A build as Vite writes it: the page and its hashed files under assets/."""
    web = tmp_path / "web"
    (web / "assets").mkdir(parents=True)
    (web / "index.html").write_text(PAGE)
    (web / "assets" / "index-1a2b3c.js").write_text(SCRIPT)
    return web


def client(web: Path, tmp_path: Path) -> httpx.AsyncClient:
    app = public_app(no_database, FileStore(tmp_path / "files"), "test", web)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://bulletin")


@pytest.mark.parametrize("path", ["/", "/a/2412"])
async def test_the_page(tmp_path: Path, path: str) -> None:
    """The page: / and an article link serve the page, revalidated and never framed."""
    async with client(built(tmp_path), tmp_path) as http:
        response = await http.get(path)

    assert response.status_code == 200
    assert response.text == PAGE
    assert response.headers["Content-Type"].startswith("text/html")
    assert response.headers["Cache-Control"] == REVALIDATE
    assert response.headers["Content-Security-Policy"] == NO_FRAMES


async def test_built_files(tmp_path: Path) -> None:
    """The page: hashed built files are immutable and carry no page policy."""
    async with client(built(tmp_path), tmp_path) as http:
        response = await http.get("/assets/index-1a2b3c.js")

    assert response.status_code == 200
    assert response.text == SCRIPT
    assert response.headers["Cache-Control"] == IMMUTABLE
    assert "Content-Security-Policy" not in response.headers


async def test_a_new_release(tmp_path: Path) -> None:
    """The page: after a new build is deployed, a reload references the new built files."""
    web = built(tmp_path)
    async with client(web, tmp_path) as http:
        await http.get("/")
        (web / "index.html").write_text(PAGE.replace("1a2b3c", "4d5e6f"))
        response = await http.get("/")

    assert "/assets/index-4d5e6f.js" in response.text


@pytest.mark.parametrize(
    "path",
    ["/nope", "/a/x", "/a/1/2", "/assets/missing.js", "/assets/..%2Findex.html", "/index.html"],
)
async def test_other_paths(tmp_path: Path, path: str) -> None:
    """The page: other paths are 404, so nothing outside assets/ is served."""
    async with client(built(tmp_path), tmp_path) as http:
        response = await http.get(path)

    assert response.status_code == 404


async def test_api_answers_keep_their_headers(tmp_path: Path) -> None:
    """The page: the page's policy is not sent with other answers."""
    async with client(built(tmp_path), tmp_path) as http:
        response = await http.get("/health")

    assert response.status_code == 200
    assert "Content-Security-Policy" not in response.headers


@pytest.mark.parametrize("path", ["/notices", "/a/x", "/index.html"])
async def test_an_unknown_path(tmp_path: Path, path: str) -> None:
    """Unknown paths: an unknown path answers 404 with the page, revalidated and never framed."""
    async with client(built(tmp_path), tmp_path) as http:
        response = await http.get(path)

    assert response.status_code == 404
    assert response.text == PAGE
    assert response.headers["Cache-Control"] == REVALIDATE
    assert response.headers["Content-Security-Policy"] == NO_FRAMES


@pytest.mark.parametrize("path", ["/api/v1/notices", "/assets/missing.js"])
async def test_an_unknown_api_path(tmp_path: Path, path: str) -> None:
    """Unknown paths: the API and the built files keep their own 404 answers."""
    async with client(built(tmp_path), tmp_path) as http:
        response = await http.get(path)

    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"


ICONS = {
    "favicon.svg": "image/svg+xml",
    "favicon.ico": "image/vnd.microsoft.icon",
    "apple-touch-icon.png": "image/png",
}
DAY = "public, max-age=86400"


@pytest.mark.parametrize(("name", "kind"), ICONS.items())
async def test_the_icons(tmp_path: Path, name: str, kind: str) -> None:
    """The site's icon: each icon is served from the site's root and cached for a day."""
    web = built(tmp_path)
    (web / name).write_bytes(b"icon")
    async with client(web, tmp_path) as http:
        response = await http.get(f"/{name}")

    assert response.status_code == 200
    assert response.content == b"icon"
    assert response.headers["Content-Type"] == kind
    assert response.headers["Cache-Control"] == DAY


@pytest.mark.parametrize("path", ["/", "/notices"])
async def test_the_page_is_not_rewritten(tmp_path: Path, path: str) -> None:
    """The page: proxies may not rewrite the page, so Cloudflare injects no script into it."""
    async with client(built(tmp_path), tmp_path) as http:
        response = await http.get(path)

    assert "no-transform" in response.headers["Cache-Control"].split(", ")
