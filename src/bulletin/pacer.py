"""The one queue every request to a school host goes through."""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable


class Pacer:
    """Sends one request at a time, each a gap plus random jitter after the previous one ended."""

    def __init__(
        self,
        *,
        clock: Callable[[], float],
        sleep: Callable[[float], Awaitable[None]],
        random: Callable[[], float],
        gap: float = 2.0,
        jitter: float = 1.0,
    ) -> None:
        """Pace with `clock` in seconds; `random` returns a float in [0, 1)."""
        raise NotImplementedError

    @asynccontextmanager
    async def slot(self) -> AsyncGenerator[None]:
        """Wait for the queue, then hold it while the caller sends one request."""
        raise NotImplementedError
        yield
