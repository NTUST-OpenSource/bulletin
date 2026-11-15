"""Requirement "Attempts and fallback" of the rendering capability, with fake model answers."""

import json
from datetime import date
from pathlib import Path

import pytest

from bulletin.answers import AnswerError
from bulletin.discord import CheckerError, fix
from bulletin.keys import KeyRing
from bulletin.model_api import ApiError
from bulletin.pages import parse_article
from bulletin.prompt import PROMPT_VERSION
from bulletin.rendering import API_REST, Pending, Renderer
from bulletin.renditions import Rendition

FIXTURES = Path(__file__).parent / "fixtures"
URL = "https://she.ntust.edu.tw/p/406-1068-152869.php"
CONTENT = parse_article(
    (FIXTURES / "articles" / "1068-152869.html").read_text(encoding="utf-8"), URL
)
ITEM = Pending(
    announcement_id=7,
    revision_id=11,
    url=URL,
    title=CONTENT.title,
    body_html=CONTENT.body_html,
    attachments=CONTENT.attachments,
    listed_on=date(2026, 11, 3),
    year=2026,
)
KEYS = ("key-one-0123456789", "key-two-0123456789")
TAGS = {"topic": ["safety-and-health"], "audience": ["staff"], "nature": "information"}


def answer(markdown: str, deadline: str | None = None) -> str:
    tags = TAGS | {"source": "on-campus"}
    fields = {"title": "t", "markdown": markdown, "summary": "s", "deadline": deadline}
    return json.dumps(fields | {"tags": tags})


GOOD = answer("Register [here](L1).\n\n![poster](I1) ![poster](I2)", "2026-10-21")


class Model:
    """Answers in order, each a text or an error to raise; records the keys used."""

    def __init__(self, *answers: str | Exception) -> None:
        self.answers = list(answers)
        self.keys: list[str] = []

    async def __call__(self, key: str, prompt: str, /) -> str:
        assert "L1" in prompt
        self.keys.append(key)
        given = self.answers.pop(0)
        if isinstance(given, Exception):
            raise given
        return given


class Checker:
    """The fixes, and a failure for Markdown that holds BAD."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    async def check(self, markdown: str, /) -> str:
        if self.error is not None:
            raise self.error
        if "BAD" in markdown:
            msg = "Discord Markdown: table"
            raise AnswerError(msg)
        return fix(markdown)


async def no_sleep(_: float) -> None:
    return None


def renderer(model: Model, checker: Checker | None = None) -> Renderer:
    return Renderer(
        model, KeyRing(KEYS, limit=10), checker or Checker(), "m", lambda: 100.0, no_sleep
    )


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Attempts and fallback")
async def test_a_good_answer() -> None:
    """Attempts and fallback: a second answer that passes gives the rendition."""
    model = Model(answer("BAD"), GOOD)

    rendition = await renderer(model).render(ITEM)

    assert rendition is not None
    assert not rendition.fallback
    assert rendition.markdown.startswith("Register [here](https://forms.gle/M3P93zsX3KY41s829).")
    assert rendition.deadline == date(2026, 10, 21)
    assert ("topic", "safety-and-health") in rendition.tags
    assert (rendition.prompt_version, rendition.model) == (PROMPT_VERSION, "m")
    assert model.keys == list(KEYS)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Attempts and fallback")
async def test_three_bad_answers() -> None:
    """Attempts and fallback: after three failed answers, the title and its link."""
    model = Model("prose", answer("BAD"), answer("[here](L9)"))

    rendition = await renderer(model).render(ITEM)

    assert rendition == Rendition(
        prompt_version=PROMPT_VERSION,
        model="m",
        title=CONTENT.title,
        markdown=f"[{CONTENT.title}]({URL})",
        fallback=True,
    )
    assert len(model.keys) == 3


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Attempts and fallback")
async def test_a_rate_limit() -> None:
    """Attempts and fallback: a 429 counts no attempt, stores nothing and rests the article."""
    model = Model(ApiError(429, f"quota of {KEYS[0]}"))
    rendering = renderer(model)

    assert await rendering.render(ITEM) is None
    assert rendering.resting == {ITEM.announcement_id: 100.0 + API_REST}
    assert rendering.resting_ids() == [ITEM.announcement_id]
    assert rendering.ring.take(100.0) == 1  # the first key rests


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Attempts and fallback")
@pytest.mark.parametrize(
    "error",
    [ApiError(503, "unavailable"), ApiError(None, "timeout")],
    ids=["a server error", "a timeout"],
)
async def test_other_api_errors(error: ApiError) -> None:
    """Attempts and fallback: server errors and timeouts count no attempt either."""
    rendering = renderer(Model(error))

    assert await rendering.render(ITEM) is None
    assert rendering.resting_ids() == [ITEM.announcement_id]
    assert rendering.ring.take(100.0) == 1  # only a rate limit rests the key


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Attempts and fallback")
async def test_a_check_that_cannot_answer() -> None:
    """Attempts and fallback: a Discord check that dies counts no attempt."""
    rendering = renderer(Model(GOOD), Checker(CheckerError("died")))

    assert await rendering.render(ITEM) is None
    assert rendering.resting_ids() == [ITEM.announcement_id]
