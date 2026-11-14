"""What the collector needs from HTTP: one GET at a time, redirects not followed."""

from collections.abc import Mapping
from dataclasses import dataclass
from importlib.metadata import version
from typing import TYPE_CHECKING, Protocol
from urllib.parse import urlsplit

import aiohttp

from bulletin.tls import context_for

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


@dataclass(frozen=True)
class Response:
    """A response as the collector reads it."""

    url: str
    status: int
    headers: Mapping[str, str]
    body: bytes = b""

    def text(self) -> str:
        """The body decoded as UTF-8, which every school page uses."""
        return self.body.decode("utf-8", errors="replace")


type KeepBody = Callable[[int, Mapping[str, str]], bool]


class Fetch(Protocol):
    """One GET, never HEAD, that does not follow redirects.

    `keep_body` sees the status and headers and decides whether the body is read; when it says
    no, the connection is closed before the body. By default the body is read.
    """

    def __call__(
        self,
        url: str,
        /,
        *,
        headers: Mapping[str, str] | None = None,
        keep_body: KeepBody | None = None,
    ) -> Awaitable[Response]:
        """Send the request."""
        ...


USER_AGENT = f"bulletin/{version('bulletin')} (+https://bulletin.ntust.org)"
TIMEOUT = aiohttp.ClientTimeout(total=60)


class Client:
    """`Fetch` over aiohttp: the bot's User-Agent, the school's TLS context, no redirects."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Send every request through `session`."""
        self._session = session

    async def __call__(
        self,
        url: str,
        /,
        *,
        headers: Mapping[str, str] | None = None,
        keep_body: KeepBody | None = None,
    ) -> Response:
        """Send one GET; close the connection unread when `keep_body` says no."""
        host = urlsplit(url).hostname or ""
        sent = {"User-Agent": USER_AGENT, **(headers or {})}
        async with self._session.get(
            url, headers=sent, allow_redirects=False, ssl=context_for(host), timeout=TIMEOUT
        ) as response:
            if keep_body is not None and not keep_body(response.status, response.headers):
                response.close()
                return Response(url, response.status, response.headers)
            return Response(url, response.status, response.headers, await response.read())
