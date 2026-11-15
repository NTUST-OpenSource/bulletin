"""API keys in turn, each within its own requests per minute; a rate-limited key rests."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

WINDOW = 60.0  # seconds in which a key takes at most its limit of requests


class KeyRing:
    """A client-side rate limit: each key's requests in a sliding window, keys in turn."""

    def __init__(self, keys: Sequence[str], limit: int, window: float = WINDOW) -> None:
        """Start at the first key with no request counted."""
        self.keys = tuple(keys)
        self.limit = limit
        self.window = window

    def take(self, now: float) -> int | None:
        """The position of the next key with room, its request counted; None if none has."""
        raise NotImplementedError

    def wait(self, now: float) -> float:
        """Seconds until a key has room again, when none has."""
        raise NotImplementedError

    def rest(self, index: int, now: float) -> None:
        """Rest the key at `index` until its window ends: the API said it is rate-limited."""
        raise NotImplementedError

    def hide(self, text: str) -> str:
        """`text` with every key hidden and every URL cut to its origin."""
        raise NotImplementedError
