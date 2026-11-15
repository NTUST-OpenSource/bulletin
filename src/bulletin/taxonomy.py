"""The fixed taxonomy of decision E3: each tag's dimension, stable id and approved label."""

import json
from dataclasses import dataclass
from functools import cache
from importlib import resources
from typing import cast

# Dimensions that hold several tags; the others hold exactly one.
SEVERAL = frozenset({"topic", "audience"})


@dataclass(frozen=True)
class Tag:
    """One tag of the taxonomy."""

    dimension: str
    id: str
    label: str


class TagError(ValueError):
    """An answer's tags do not fit the taxonomy."""


@cache
def taxonomy() -> dict[str, tuple[Tag, ...]]:
    """Return each dimension's tags, in the order of taxonomy.json."""
    rows: dict[str, list[dict[str, str]]] = json.loads(
        (resources.files("bulletin") / "taxonomy.json").read_text(encoding="utf-8")
    )
    return {
        dimension: tuple(Tag(dimension, tag["id"], tag["label"]) for tag in tags)
        for dimension, tags in rows.items()
    }


def parse_tags(value: object) -> frozenset[tuple[str, str]]:
    """Return the (dimension, id) pairs of an answer's tags object.

    Raises:
        TagError: a dimension is missing or has the wrong shape, or a tag is unknown.
    """
    if not isinstance(value, dict):
        msg = "tags are not an object"
        raise TagError(msg)
    answer = cast("dict[str, object]", value)
    pairs: set[tuple[str, str]] = set()
    for dimension, tags in taxonomy().items():
        given = answer.get(dimension)
        if dimension not in SEVERAL:
            given = [given]
        elif not isinstance(given, list):
            msg = f"{dimension} is not a list"
            raise TagError(msg)
        known = {tag.id for tag in tags}
        for tag in cast("list[object]", given):
            if not isinstance(tag, str) or tag not in known:
                msg = f"{dimension} has no tag {tag!r}"
                raise TagError(msg)
            pairs.add((dimension, tag))
    return frozenset(pairs)
