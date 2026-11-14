"""The one queue every request to a school host goes through."""

import asyncio
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
        self._clock = clock
        self._sleep = sleep
        self._random = random
        self._gap = gap
        self._jitter = jitter
        self._lock = asyncio.Lock()
        self._ready_at = clock()

    @asynccontextmanager
    async def slot(self) -> AsyncGenerator[None]:
        """Wait for the queue, then hold it while the caller sends one request."""
        async with self._lock:
            wait = self._ready_at - self._clock()
            if wait > 0:
                await self._sleep(wait)
            try:
                yield
            finally:
                self._ready_at = self._clock() + self._gap + self._random() * self._jitter
