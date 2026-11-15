"""Rendering: an announcement's current revision rewritten by the model, checked, or a fallback."""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from http import HTTPStatus
from typing import Protocol

from bulletin.answers import AnswerError, keep_deadline, parse_answer, restore
from bulletin.discord import CheckerError
from bulletin.emoji import strip_emoji
from bulletin.keys import KeyRing
from bulletin.model_api import ApiError
from bulletin.model_input import ModelInput, model_input
from bulletin.prompt import PROMPT_VERSION, prompt
from bulletin.renditions import Pending, Rendition
from bulletin.schedule import TAIPEI

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
API_REST = 600.0  # seconds an announcement rests after an API error
# Answers that say the key, not the request, is the problem: the key rests for its window.
KEY_PROBLEMS = frozenset(
    {HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}
)


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

    def close(self) -> Awaitable[None]:
        """Stop the check."""
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
    today: Callable[[], date] = lambda: datetime.now(TAIPEI).date()
    resting: dict[int, float] = field(default_factory=dict[int, float])

    def rest(self, announcement_id: int) -> None:
        """Leave the announcement for `API_REST` seconds."""
        self.resting[announcement_id] = self.clock() + API_REST

    def resting_ids(self) -> list[int]:
        """The announcements that rest after an API error."""
        now = self.clock()
        self.resting = {id_: until for id_, until in self.resting.items() if until > now}
        return sorted(self.resting)

    async def render(self, item: Pending) -> Rendition | None:
        """The rendition of `item`, a fallback after three failed answers, or None.

        None means an API error, or a Discord check that could not answer: no attempt counts,
        and the announcement rests for `API_REST` seconds. A rate-limited key rests too.
        """
        given = model_input(item.title, item.body_html, item.attachments, item.url)
        text = prompt(given, item.dated, self.today())
        for attempt in range(1, MAX_ATTEMPTS + 1):
            index = await self._key()
            try:
                answer = await self.generate(self.ring.keys[index], text)
                return await self._checked(answer, given, item)
            except AnswerError as error:
                log.info(
                    "attempt %d of %d for %s failed: %s",
                    attempt,
                    MAX_ATTEMPTS,
                    item.url,
                    self.ring.hide(str(error)),
                )
            except (ApiError, CheckerError) as error:
                if isinstance(error, ApiError) and error.status in KEY_PROBLEMS:
                    self.ring.rest(index, self.clock())
                log.warning(
                    "rendering %s waits: %s with key %d",
                    item.url,
                    self.ring.hide(str(error)),
                    index + 1,
                )
                self.rest(item.announcement_id)
                return None
        log.warning("rendering %s fell back after %d attempts", item.url, MAX_ATTEMPTS)
        title = strip_emoji(item.title).strip()
        escaped = title.replace("[", "\\[").replace("]", "\\]")
        return Rendition(
            PROMPT_VERSION, self.model, title, f"[{escaped}]({item.url})", fallback=True
        )

    async def _key(self) -> int:
        """The next key with room, waiting while none has."""
        while True:
            now = self.clock()
            if (index := self.ring.take(now)) is not None:
                return index
            await self.sleep(self.ring.wait(now))

    async def _checked(self, text: str, given: ModelInput, item: Pending) -> Rendition:
        """The answer's rendition after every check, in the order of design.md."""
        answer = parse_answer(text)
        markdown = await self.checker.check(strip_emoji(restore(answer.markdown, given.targets)))
        return Rendition(
            prompt_version=PROMPT_VERSION,
            model=self.model,
            title=strip_emoji(answer.title).strip(),
            markdown=markdown,
            summary=strip_emoji(answer.summary).strip(),
            deadline=keep_deadline(answer.deadline, given.text, item.dated.year),
            tags=answer.tags,
        )
