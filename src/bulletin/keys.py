"""API keys in turn, each within its own requests per minute; a rate-limited key rests."""

import re
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

WINDOW = 60.0  # seconds in which a key takes at most its limit of requests
HIDDEN = "..."
URL_IN_TEXT = re.compile(r"\bhttps?://\S+", re.IGNORECASE)
AUTHORITY_END = re.compile(r"[/?#]")


class KeyRing:
    """A client-side rate limit: each key's requests in a sliding window, keys in turn.

    Ported from the xincord bot's `ntust_announcements` plugin. A key listed twice has one budget.
    """

    def __init__(self, keys: Sequence[str], limit: int, window: float = WINDOW) -> None:
        """Start at the first key with no request counted."""
        self.keys = tuple(keys)
        self.limit = limit
        self.window = window
        self.next = 0  # where the next search starts: after the last key used
        self.requests: dict[str, deque[float]] = {key: deque() for key in self.keys}
        self.resting: dict[str, float] = {}  # key -> when its rest ends

    def _requests(self, key: str, now: float) -> deque[float]:
        requests = self.requests[key]
        while requests and now - requests[0] >= self.window:
            requests.popleft()
        return requests

    def _free_at(self, key: str, now: float) -> float:
        """When the key can take a request: now, the end of its rest, or when one leaves."""
        requests = self._requests(key, now)
        full = requests[0] + self.window if len(requests) >= self.limit else now
        return max(full, self.resting.get(key, now))

    def take(self, now: float) -> int | None:
        """The position of the next key with room, its request counted; None if none has."""
        for offset in range(len(self.keys)):
            index = (self.next + offset) % len(self.keys)
            key = self.keys[index]
            if self._free_at(key, now) <= now:
                self._requests(key, now).append(now)
                self.next = (index + 1) % len(self.keys)
                return index
        return None

    def wait(self, now: float) -> float:
        """Seconds until a key has room again, when none has."""
        return min(self._free_at(key, now) for key in self.keys) - now

    def rest(self, index: int, now: float) -> None:
        """Rest the key at `index` until its window ends: the API said it is rate-limited."""
        key = self.keys[index]
        requests = self._requests(key, now)
        self.resting[key] = (requests[0] if requests else now) + self.window

    def hide(self, text: str) -> str:
        """`text` with every URL cut to its origin and every key hidden."""
        text = URL_IN_TEXT.sub(_origin, text)
        for key in sorted(set(self.keys), key=len, reverse=True):
            text = text.replace(key, HIDDEN)
        return text


def _origin(match: re.Match[str]) -> str:
    """The scheme, host and port of a URL: its path and query may carry a key or a token."""
    scheme, _, rest = match[0].partition("://")
    return f"{scheme.lower()}://{AUTHORITY_END.split(rest, maxsplit=1)[0].rpartition('@')[2]}"
