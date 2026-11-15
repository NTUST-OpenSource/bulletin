"""Checks of the model's answer, in order; any that fails fails the attempt."""

import re
from dataclasses import dataclass
from datetime import date
from urllib.parse import quote

# A placeholder of the model input (`L1`, `I1`), not part of a longer ASCII word or number.
PLACEHOLDER = re.compile(r"(?<![A-Za-z0-9])([LI])([1-9][0-9]*)(?![0-9])")
# What a URL keeps as it is inside a Markdown link: the reserved characters but parentheses.
URL_SAFE = "!#$%&'*+,/:;=?@[]~"


class AnswerError(ValueError):
    """The answer fails a check."""


@dataclass(frozen=True)
class Answer:
    """The fields of an answer that matches the schema; its Markdown still holds placeholders."""

    title: str
    markdown: str
    summary: str
    deadline: date | None
    tags: frozenset[tuple[str, str]]


def parse_answer(text: str) -> Answer:
    """Read the model's answer as JSON that matches the answer schema."""
    raise NotImplementedError


def restore(text: str, targets: dict[str, str]) -> str:
    """Replace each placeholder in `text` by the URL it stands for.

    Raises:
        AnswerError: `text` holds a placeholder that `targets` lacks, or leaves out an image.
    """
    used = {match[0] for match in PLACEHOLDER.finditer(text)}
    if unknown := sorted(used - targets.keys()):
        msg = f"unknown placeholders {', '.join(unknown)}"
        raise AnswerError(msg)
    if dropped := sorted(name for name in targets if name[0] == "I" and name not in used):
        msg = f"dropped images {', '.join(dropped)}"
        raise AnswerError(msg)
    return PLACEHOLDER.sub(lambda match: quote(targets[match[0]], safe=URL_SAFE), text)
