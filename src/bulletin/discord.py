"""Discord Markdown: the fixes a rendition gets and the check it must pass (decision E4)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncio
    from pathlib import Path


class CheckerError(RuntimeError):
    """The Node check did not answer; like an API error, it is no fault of the answer."""


def fix(markdown: str) -> str:
    """Wrap bare URLs as `<url>`; replace masked links whose text holds a URL by the URL."""
    raise NotImplementedError


class Checker:
    """A long-lived `node check.mjs` that names what Discord's parser makes of a text."""

    def __init__(self, script: Path, node: str = "node") -> None:
        """Run `script` with `node` once the first check needs it."""
        self.script = script
        self.node = node
        self.process: asyncio.subprocess.Process | None = None

    async def check(self, markdown: str) -> str:
        """Return `markdown` with the fixes, or raise `AnswerError` naming its problems."""
        raise NotImplementedError

    async def close(self) -> None:
        """Stop the subprocess."""
