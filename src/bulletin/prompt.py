"""The prompt and the answer schema, versioned: a new version renders the last year again."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from bulletin.model_input import ModelInput

# Raise it with every change of prompt.md, answer.schema.json or taxonomy.json.
PROMPT_VERSION = 1


def prompt(given: ModelInput, listed_on: date | None) -> str:
    """The prompt for one article."""
    raise NotImplementedError


def answer_schema() -> dict[str, object]:
    """The JSON schema the answer must match."""
    raise NotImplementedError
