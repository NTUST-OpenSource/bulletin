"""HTTP: the bot's User-Agent, redirects left to the caller, bodies read only when wanted."""

from typing import TYPE_CHECKING

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from bulletin.http import USER_AGENT, Client

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Mapping


async def echo(request: web.Request) -> web.Response:
    return web.Response(
        text=request.headers.get("User-Agent", ""),
        headers={"X-Range": request.headers.get("Range", "")},
    )


async def moved(_: web.Request) -> web.Response:
    return web.Response(status=302, headers={"Location": "/index.php"})


async def large(_: web.Request) -> web.Response:
    return web.Response(body=b"x" * 2**20, content_type="application/pdf")


def always(_status: int, _headers: Mapping[str, str]) -> bool:
    return True


@pytest.fixture
async def server() -> AsyncGenerator[TestServer]:
    app = web.Application()
    app.router.add_get("/echo", echo)
    app.router.add_get("/p/406-1000-1.php", moved)
    app.router.add_get("/file.pdf", large)
    running = TestServer(app, host="127.0.0.1")
    async with running:
        yield running


@pytest.fixture
async def client() -> AsyncGenerator[Client]:
    async with aiohttp.ClientSession() as session:
        yield Client(session)


async def test_requests_name_the_bot(server: TestServer, client: Client) -> None:
    """List page fetch: every request carries the bot's User-Agent, and the caller's headers."""
    response = await client(str(server.make_url("/echo")), headers={"Range": "bytes=0-0"})

    assert USER_AGENT.startswith("bulletin/")
    assert USER_AGENT.endswith(" (+https://bulletin.ntust.org)")
    assert (response.status, response.text()) == (200, USER_AGENT)
    assert response.headers["x-range"] == "bytes=0-0"


async def test_redirects_are_not_followed(server: TestServer, client: Client) -> None:
    """Withdrawal check: the 302 to the home page reaches the caller."""
    url = str(server.make_url("/p/406-1000-1.php"))

    response = await client(url)

    assert (response.url, response.status) == (url, 302)
    assert response.headers["Location"] == "/index.php"


async def test_a_body_not_wanted_is_not_read(server: TestServer, client: Client) -> None:
    """Attachment sizes: when `keep_body` says no, the response comes back without its body."""
    seen: list[tuple[int, str]] = []

    def keep_body(status: int, headers: Mapping[str, str]) -> bool:
        seen.append((status, headers["Content-Length"]))
        return False

    response = await client(str(server.make_url("/file.pdf")), keep_body=keep_body)

    assert seen == [(200, str(2**20))]
    assert (response.status, response.body) == (200, b"")
    kept = await client(str(server.make_url("/file.pdf")), keep_body=always)
    assert len(kept.body) == 2**20
