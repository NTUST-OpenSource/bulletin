"""The fixed taxonomy of decision E3: each tag's dimension, stable id and approved label."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tag:
    """One tag of the taxonomy."""

    dimension: str
    id: str
    label: str


class TagError(ValueError):
    """An answer's tags do not fit the taxonomy."""


def taxonomy() -> dict[str, tuple[Tag, ...]]:
    """Return each dimension's tags, in the order of taxonomy.json."""
    raise NotImplementedError


def parse_tags(value: object) -> frozenset[tuple[str, str]]:
    """Return the (dimension, id) pairs of an answer's tags object."""
    raise NotImplementedError
