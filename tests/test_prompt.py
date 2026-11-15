"""Requirement "Structured answer": the prompt, its schema and their version."""

import hashlib
from datetime import date
from importlib import resources
from typing import cast

from bulletin.model_input import ModelInput
from bulletin.prompt import PROMPT_VERSION, answer_schema, prompt
from bulletin.taxonomy import taxonomy

# The SHA-256 of the files behind each prompt version. Editing one of them fails this test until
# PROMPT_VERSION is raised and its digest added: a new version renders the last year again.
DIGESTS = {
    1: "7f66a7fa1bc0537e5c1b6bf0331a137fc06b9d243a798197900f75c3b5bd1a2a",
}
FILES = ("prompt.md", "answer.schema.json", "taxonomy.json")


def at(value: object, *keys: str) -> object:
    """The value under `keys` in nested JSON objects."""
    for key in keys:
        assert isinstance(value, dict)
        value = cast("dict[str, object]", value)[key]
    return value


def test_the_prompt_version_pins_its_files() -> None:
    """Structured answer: the prompt's files match the digest of PROMPT_VERSION."""
    digest = hashlib.sha256()
    for name in FILES:
        digest.update((resources.files("bulletin") / name).read_bytes())

    assert digest.hexdigest() == DIGESTS[PROMPT_VERSION]


def test_the_schema_lists_the_taxonomy() -> None:
    """Structured answer: the schema's tag enums are the taxonomy's ids."""
    schema = answer_schema()

    for dimension, known in taxonomy().items():
        field = at(schema, "properties", "tags", "properties", dimension)
        enum = at(field, "items", "enum") if at(field, "type") == "array" else at(field, "enum")
        assert enum == [tag.id for tag in known]


def test_the_prompt_holds_the_input() -> None:
    """Structured answer: the prompt holds the input, the list date and every tag label."""
    given = ModelInput("Title: T\n\nBody:\nB", {})

    text = prompt(given, date(2026, 11, 3))

    assert text.endswith("Title: T\n\nBody:\nB\n")
    assert "2026-11-03" in text
    assert all(tag.label in text for tags in taxonomy().values() for tag in tags)
    assert "{{" not in text
