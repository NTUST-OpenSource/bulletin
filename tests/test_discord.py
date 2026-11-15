"""Requirement "Discord Markdown" of the rendering capability, against the real Node check."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from bulletin.answers import AnswerError
from bulletin.discord import Checker, CheckerError, fix

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

SCRIPT = Path(__file__).parents[1] / "tools" / "discord-markdown" / "check.mjs"
URL = "https://forms.gle/abc"


@pytest.fixture
async def checker() -> AsyncIterator[Checker]:
    running = Checker(SCRIPT)
    yield running
    await running.close()


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Discord Markdown")
def test_a_bare_url() -> None:
    """Discord Markdown: a bare URL is wrapped as <url>; links and autolinks stay."""
    assert fix(f"Apply at {URL}. Or [here]({URL}) or <{URL}>.") == (
        f"Apply at <{URL}>. Or [here]({URL}) or <{URL}>."
    )
    assert fix(f"(see {URL})") == f"(see <{URL}>)"


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Discord Markdown")
def test_a_masked_link_whose_text_is_a_url() -> None:
    """Discord Markdown: a masked link whose text holds a URL becomes the URL."""
    assert fix(f"[{URL}]({URL})") == f"<{URL}>"
    assert fix(f"[Form: {URL}]({URL}) now") == f"Form: <{URL}> now"
    assert fix(f"![poster]({URL}/p.png)") == f"![poster]({URL}/p.png)"


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Discord Markdown")
async def test_a_rendition_that_passes(checker: Checker) -> None:
    """Discord Markdown: fixed Markdown that the parser takes is returned."""
    markdown = f"### Apply\n\n- by **12/10** at {URL}\n  - [form]({URL})\n\n![poster]({URL}/p.png)"

    assert await checker.check(markdown) == markdown.replace(f"at {URL}", f"at <{URL}>")


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Discord Markdown")
@pytest.mark.parametrize(
    ("markdown", "problem"),
    [
        pytest.param("| a | b |\n| --- | --- |\n| 1 | 2 |", "table", id="a table"),
        pytest.param("a | b\n---|---\n1 | 2", "table", id="a table without outer pipes"),
        pytest.param("Hi @everyone", "mention", id="a mention"),
        pytest.param("[form](ftp://example.com/f)", "unparsed link", id="a link Discord drops"),
        pytest.param("<mailto:office@example.com>", "link scheme", id="a mail link"),
        pytest.param("x" * 4097, "4,096", id="too long"),
    ],
)
async def test_a_rendition_that_fails(checker: Checker, markdown: str, problem: str) -> None:
    """Discord Markdown: a table, a mention, a broken link or too much text fails."""
    with pytest.raises(AnswerError, match=problem):
        await checker.check(markdown)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Discord Markdown")
async def test_a_crashed_check(checker: Checker) -> None:
    """Discord Markdown: a check that dies is an error of its own, and the next check restarts."""
    assert await checker.check("ok") == "ok"
    process = checker.process
    assert process is not None
    process.kill()
    await process.wait()

    with pytest.raises(CheckerError):
        await checker.check("ok")
    assert await checker.check("ok") == "ok"


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Discord Markdown")
async def test_no_node(tmp_path: Path) -> None:
    """Discord Markdown: without Node the check cannot answer."""
    missing = Checker(SCRIPT, node=str(tmp_path / "node"))

    with pytest.raises(CheckerError):
        await missing.check("ok")
