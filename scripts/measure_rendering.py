"""Measure rendering on the labelled corpus sample (design.md, Measurement)."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

Outcome = Literal["correct", "none", "missed", "false", "wrong"]


@dataclass(frozen=True)
class Scores:
    """Micro-averaged agreement of predicted tags with the labelled ones."""

    precision: float
    recall: float
    f1: float


def tag_scores(pairs: Iterable[tuple[frozenset[str], frozenset[str]]]) -> Scores:
    """Scores over (predicted, labelled) tag sets, counted over every tag of every article."""
    raise NotImplementedError


def deadline_outcome(got: date | None, wanted: date | None) -> Outcome:
    """How the rendered deadline compares with the labelled one."""
    raise NotImplementedError
