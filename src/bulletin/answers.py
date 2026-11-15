"""Checks of the model's answer, in order; any that fails fails the attempt."""

import json
import re
from dataclasses import dataclass
from datetime import date
from typing import cast
from urllib.parse import quote

from bulletin.taxonomy import TagError, parse_tags

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
    """Read the model's answer as JSON that matches the answer schema.

    Raises:
        AnswerError: the answer is not JSON, a field is missing or of the wrong type, the deadline
            is not a date, or the tags do not fit the taxonomy.
    """
    try:
        value: object = json.loads(text)
    except json.JSONDecodeError as error:
        msg = "the answer is not JSON"
        raise AnswerError(msg) from error
    if not isinstance(value, dict):
        msg = "the answer is not an object"
        raise AnswerError(msg)
    fields = cast("dict[str, object]", value)
    try:
        tags = parse_tags(fields.get("tags"))
    except TagError as error:
        raise AnswerError(str(error)) from error
    return Answer(
        title=_text(fields, "title"),
        markdown=_text(fields, "markdown"),
        summary=_text(fields, "summary"),
        deadline=_date(fields),
        tags=tags,
    )


def _text(fields: dict[str, object], name: str) -> str:
    value = fields.get(name)
    if not isinstance(value, str) or not value.strip():
        msg = f"{name} is not a text"
        raise AnswerError(msg)
    return value.strip()


def _date(fields: dict[str, object]) -> date | None:
    if "deadline" not in fields:
        msg = "deadline is missing"
        raise AnswerError(msg)
    value = fields["deadline"]
    if value is None:
        return None
    try:
        return date.fromisoformat(cast("str", value))
    except (TypeError, ValueError) as error:
        msg = f"deadline {value!r} is not a date"
        raise AnswerError(msg) from error


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
