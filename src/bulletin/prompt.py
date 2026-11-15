"""The prompt and the answer schema, versioned: a new version renders the last year again."""

import json
import re
from functools import cache
from importlib import resources
from typing import TYPE_CHECKING

from bulletin.taxonomy import taxonomy

if TYPE_CHECKING:
    from datetime import date

    from bulletin.model_input import ModelInput

# Raise it with every change of prompt.md, answer.schema.json or taxonomy.json.
PROMPT_VERSION = 1
TOKEN = re.compile(r"\{\{(taxonomy|dated|today|input)\}\}")


def _read(name: str) -> str:
    return (resources.files("bulletin") / name).read_text(encoding="utf-8")


def _taxonomy() -> str:
    """Each dimension's ids with their labels, as list items under the `tags` rule."""
    return "\n  ".join(
        f"- `{dimension}`: " + ", ".join(f"`{tag.id}` {tag.label}" for tag in tags)
        for dimension, tags in taxonomy().items()
    )


def prompt(given: ModelInput, dated: date, today: date) -> str:
    """The prompt for one article: the rules, the taxonomy, its day and today, and its input."""
    values = {
        "taxonomy": _taxonomy(),
        "dated": dated.isoformat(),
        "today": today.isoformat(),
        "input": given.text,
    }
    return TOKEN.sub(lambda token: values[token[1]], _read("prompt.md"))


@cache
def answer_schema() -> dict[str, object]:
    """The JSON schema the answer must match."""
    return json.loads(_read("answer.schema.json"))
