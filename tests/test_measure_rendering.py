"""Measurement (design.md): tag agreement and deadline outcomes of the rendering report."""

from datetime import date

import pytest

from measure_rendering import Outcome, Scores, deadline_outcome, tag_scores

DAY = date(2026, 12, 10)
OTHER = date(2026, 12, 11)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Measurement")
def test_tag_scores_count_every_tag() -> None:
    """One right and one wrong tag, and one missed: precision, recall and F1 of one half."""
    pairs = [(frozenset({"a", "b"}), frozenset({"a"})), (frozenset[str](), frozenset({"c"}))]
    assert tag_scores(pairs) == Scores(0.5, 0.5, 0.5)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Measurement")
def test_tag_scores_without_tags() -> None:
    """Nothing predicted and nothing labelled scores zero rather than dividing by zero."""
    assert tag_scores([(frozenset[str](), frozenset[str]())]) == Scores(0.0, 0.0, 0.0)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Measurement")
@pytest.mark.parametrize(
    ("got", "wanted", "outcome"),
    [
        (DAY, DAY, "correct"),
        (None, None, "none"),
        (None, DAY, "missed"),
        (DAY, None, "false"),
        (OTHER, DAY, "wrong"),
    ],
)
def test_deadline_outcomes(got: date | None, wanted: date | None, outcome: Outcome) -> None:
    """A rendered deadline is right, rightly absent, missed, invented or a wrong day."""
    assert deadline_outcome(got, wanted) == outcome
