"""What the collector needs from HTTP: one GET at a time, redirects not followed."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

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
