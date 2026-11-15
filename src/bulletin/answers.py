"""Checks of the model's answer, in order; any that fails fails the attempt."""

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import cast
from urllib.parse import quote

from bulletin.taxonomy import TagError, parse_tags

# A placeholder of the model input (`L1`, `I1`), not part of a longer ASCII word or number.
PLACEHOLDER = re.compile(r"(?<![A-Za-z0-9])([LI])([1-9][0-9]*)(?![0-9])")
# What a URL keeps as it is inside a Markdown link: the reserved characters but parentheses.
URL_SAFE = "!#$%&'*+,/:;=?@[]~"
YEAR, MONTH = chr(0x5E74), chr(0x6708)
# Dates as the school writes them, after NFKC: a Gregorian or ROC year, a month and a day, with
# dashes, slashes, dots or the year and month characters; or a month and a day alone.
FULL_DATE = re.compile(
    rf"(?<![0-9])([0-9]{{2,4}}) *(?:[-/.]|{YEAR}) *([0-9]{{1,2}}) *(?:[-/.]|{MONTH}) *"
    r"([0-9]{1,2})(?![0-9])"
)
MONTH_DAY = re.compile(rf"(?<![0-9/.-])([0-9]{{1,2}}) *(?:/|{MONTH}) *([0-9]{{1,2}})(?![0-9])")
ROC_OFFSET = 1911
MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
# English dates: "November 25, 2026", "Nov. 25", "25 November 2026".
NAME = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
NAMED_DATE = re.compile(
    rf"\b{NAME} ([0-9]{{1,2}})(?:st|nd|rd|th)?\b(?:,? ([0-9]{{4}}))?"
    rf"|\b([0-9]{{1,2}}) {NAME}(?: ([0-9]{{4}}))?",
    re.IGNORECASE,
)


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


def keep_deadline(deadline: date | None, text: str, year: int) -> date | None:
    """`deadline` if `text` holds its date in a form the school writes, else None.

    Dates without a year are read in `year`, the year of the list date, and the next one.
    """
    if deadline is None:
        return None
    return deadline if deadline in _dates(unicodedata.normalize("NFKC", text), year) else None


def _dates(text: str, year: int) -> set[date]:
    found: set[date] = set()
    for match in FULL_DATE.finditer(text):
        given, month, day = map(int, match.groups())
        _add(found, given if given > ROC_OFFSET else given + ROC_OFFSET, month, day)
    for match in MONTH_DAY.finditer(text):
        month, day = map(int, match.groups())
        _add(found, year, month, day)
        _add(found, year + 1, month, day)
    for match in NAMED_DATE.finditer(text):
        name, day, given = match.group(1, 2, 3) if match[1] else match.group(5, 4, 6)
        month = MONTHS.index(name.lower()) + 1
        for in_year in (int(given),) if given else (year, year + 1):
            _add(found, in_year, month, int(day))
    return found


def _add(found: set[date], year: int, month: int, day: int) -> None:
    try:
        found.add(date(year, month, day))
    except ValueError:
        return
