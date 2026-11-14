"""What the collector needs from HTTP: one GET at a time, redirects not followed."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping


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


type Fetch = Callable[[str], Awaitable[Response]]
