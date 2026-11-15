"""Discord Markdown: the fixes a rendition gets and the check it must pass (decision E4)."""

import asyncio
import json
import re
from typing import TYPE_CHECKING, cast

from bulletin.answers import AnswerError

if TYPE_CHECKING:
    from pathlib import Path

# Discord's limit for an embed description, counted as JavaScript counts, in UTF-16 code units.
LIMIT = 4096
ANSWER_TIMEOUT = 10  # seconds the check may take for one text
STOP_TIMEOUT = 5
# A masked link or image, an autolink, or a bare URL; restored URLs are ASCII, so CJK text and
# full-width punctuation end a bare one.
LINK = re.compile(
    r"(?P<masked>!?\[(?P<text>[^\]\n]*)\]\((?P<target>[^)\s]*)\))"
    r"|(?P<auto><https?://[^>\s]*>)"
    r"|(?P<bare>https?://[A-Za-z0-9\-._~:/?#@!$&'*+,;=%\[\]]+)"
)
URL_IN_TEXT = re.compile(r"https?://\S+")
CJK = re.compile(f"[{chr(0x4E00)}-{chr(0x9FFF)}]")
PICTURE = chr(0x5716) + chr(0x7247)  # what an image without a description is called in Chinese
TRAILING = ".,;:!?'*"
SEPARATOR = re.compile(r"\|? *:?-{3,}:? *(\| *:?-{3,}:? *)*\|?")


class CheckerError(RuntimeError):
    """The Node check did not answer; like an API error, it is no fault of the answer."""


def fix(markdown: str) -> str:
    """Wrap bare URLs as `<url>`, and fix the links Discord would show wrongly.

    A masked link whose text holds a URL, or nothing, becomes the URL; an image without a
    description gets one, since Discord leaves an empty link text unparsed.
    """
    picture = PICTURE if CJK.search(markdown) else "Image"
    return LINK.sub(lambda match: _fixed(match, picture), markdown)


def _fixed(match: re.Match[str], picture: str) -> str:
    if match["bare"]:
        url = match["bare"].rstrip(TRAILING)
        return f"<{url}>{match['bare'][len(url) :]}"
    if match["masked"] and match["target"] and not match["text"].strip():
        image = match["masked"].startswith("!")
        return f"![{picture}]({match['target']})" if image else f"<{match['target']}>"
    if match["masked"] and not match["masked"].startswith("!") and "://" in match["text"]:
        rest = URL_IN_TEXT.sub("", match["text"]).strip()
        return f"{rest} <{match['target']}>" if rest else f"<{match['target']}>"
    return match[0]


def _problems(markdown: str) -> list[str]:
    """What Discord cannot show, found without the parser: tables and too much text."""
    problems: list[str] = []
    if any("|" in line and SEPARATOR.fullmatch(line.strip()) for line in markdown.split("\n")):
        problems.append("table")
    if len(markdown.encode("utf-16-le")) // 2 > LIMIT:
        problems.append(f"longer than {LIMIT:,} characters")
    return problems


class Checker:
    """A long-lived `node check.mjs` that names what Discord's parser makes of a text."""

    def __init__(self, script: Path, node: str = "node") -> None:
        """Run `script` with `node` once the first check needs it."""
        self.script = script
        self.node = node
        self.process: asyncio.subprocess.Process | None = None

    async def check(self, markdown: str) -> str:
        """Return `markdown` with the fixes, or raise `AnswerError` naming its problems.

        Raises:
            AnswerError: the fixed Markdown holds a table, a mention or a link Discord drops, or
                is too long.
            CheckerError: the check could not start, or died or hung during the check.
        """
        fixed = fix(markdown)
        if problems := _problems(fixed) + await self._ask(fixed):
            msg = f"Discord Markdown: {', '.join(problems)}"
            raise AnswerError(msg)
        return fixed

    async def _ask(self, text: str) -> list[str]:
        process = self.process
        if process is None or process.returncode is not None:
            try:
                process = await asyncio.create_subprocess_exec(
                    self.node,
                    str(self.script),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                )
            except OSError as error:
                msg = f"the Discord check did not start: {error}"
                raise CheckerError(msg) from error
            self.process = process
        stdin, stdout = process.stdin, process.stdout
        assert stdin is not None  # noqa: S101 - a pipe
        assert stdout is not None  # noqa: S101 - a pipe
        try:
            stdin.write(json.dumps({"text": text}).encode() + b"\n")
            await stdin.drain()
            line = await asyncio.wait_for(stdout.readline(), ANSWER_TIMEOUT)
            answer: object = json.loads(line) if line else None
        except (OSError, TimeoutError, ValueError) as error:
            await self.close()
            msg = f"the Discord check failed: {error!r}"
            raise CheckerError(msg) from error
        if not isinstance(answer, dict) or "problems" not in answer:
            await self.close()
            msg = f"the Discord check gave no answer: {line!r}"
            raise CheckerError(msg)
        return cast("list[str]", cast("dict[str, object]", answer)["problems"])

    async def close(self) -> None:
        """Stop the subprocess."""
        process, self.process = self.process, None
        if process is None or process.returncode is not None:
            return
        if process.stdin is not None:
            process.stdin.close()
        try:
            await asyncio.wait_for(process.wait(), STOP_TIMEOUT)
        except TimeoutError:
            process.kill()
            await process.wait()
