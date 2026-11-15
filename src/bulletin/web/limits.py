"""The search rate limit per client (F4), kept in memory by the one process."""

import ipaddress
import math
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request

SEARCHES = 30
WINDOW = 60.0
MAX_CLIENTS = 10_000


def client_key(request: Request) -> str | None:
    """Who a request counts against, or None for an internal client, which is exempt.

    uvicorn has already taken the client from the proxy chain. A request that reached the listener
    without `X-Forwarded-For` from a private address comes from `proxy-net` directly. IPv6 clients
    count by their /64, which one host may fill with addresses.
    """
    host = request.client.host if request.client else ""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return host
    if "x-forwarded-for" not in request.headers and address.is_private:
        return None
    if address.version == 6:  # noqa: PLR2004 - the IP version
        return str(ipaddress.ip_network(f"{address}/64", strict=False))
    return str(address)


@dataclass
class SearchLimit:
    """A sliding window of searches per client; the least recently seen clients go first."""

    clock: Callable[[], float] = time.monotonic
    hits: dict[str, deque[float]] = field(default_factory=dict[str, deque[float]])

    def refuse(self, key: str) -> int | None:
        """Count a search by `key`; return the seconds to wait when it is one too many."""
        now = self.clock()
        times = self.hits.pop(key, deque[float]())
        while times and now - times[0] >= WINDOW:
            times.popleft()
        self.hits[key] = times
        if len(times) >= SEARCHES:
            return max(1, math.ceil(WINDOW - (now - times[0])))
        times.append(now)
        while len(self.hits) > MAX_CLIENTS:
            del self.hits[next(iter(self.hits))]
        return None
