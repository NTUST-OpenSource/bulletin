"""Rendering: an announcement's current revision rewritten by the model, checked, or a fallback."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING, Protocol

from bulletin.keys import KeyRing
from bulletin.model import Attachment

if TYPE_CHECKING:
    from bulletin.renditions import Rendition

MAX_ATTEMPTS = 3
API_REST = 600.0  # seconds an announcement rests after an API error


@dataclass(frozen=True)
class Pending:
    """An announcement whose current revision waits for a rendition."""

    announcement_id: int
    revision_id: int
    url: str  # the article page
    title: str
    body_html: str
    attachments: tuple[Attachment, ...]
    listed_on: date | None
    year: int  # the year dates without one belong to: the list date's, else the first sight's


class Generate(Protocol):
    """One request to the model: the answer's text for a prompt, asked with a key."""

    def __call__(self, key: str, prompt: str, /) -> Awaitable[str]:
        """Ask the model."""
        ...


class Check(Protocol):
    """The Discord Markdown check."""

    def check(self, markdown: str, /) -> Awaitable[str]:
        """The fixed Markdown, or `AnswerError`; `CheckerError` when the check cannot answer."""
        ...


@dataclass
class Renderer:
    """Renders one announcement at a time with the keys in turn."""

    generate: Generate
    ring: KeyRing
    checker: Check
    model: str
    clock: Callable[[], float]  # monotonic seconds
    sleep: Callable[[float], Awaitable[object]]
    resting: dict[int, float] = field(default_factory=dict[int, float])

    def resting_ids(self) -> list[int]:
        """The announcements that rest after an API error."""
        raise NotImplementedError

    async def render(self, item: Pending) -> Rendition | None:
        """The rendition of `item`, a fallback after three failed answers, or None."""
        raise NotImplementedError
