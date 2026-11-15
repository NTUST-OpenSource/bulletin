"""Measurement (design.md): tag agreement and deadline outcomes of the rendering report."""

from datetime import date

import pytest

from measure_rendering import Outcome, Result, Scores, deadline_outcome, summarize, tag_scores

DAY = date(2026, 12, 10)
OTHER = date(2026, 12, 11)


def test_tag_scores_count_every_tag() -> None:
    """One right and one wrong tag, and one missed: precision, recall and F1 of one half."""
    pairs = [(frozenset({"a", "b"}), frozenset({"a"})), (frozenset[str](), frozenset({"c"}))]
    assert tag_scores(pairs) == Scores(0.5, 0.5, 0.5)


def test_tag_scores_without_tags() -> None:
    """Nothing predicted and nothing labelled scores zero rather than dividing by zero."""
    assert tag_scores([(frozenset[str](), frozenset[str]())]) == Scores(0.0, 0.0, 0.0)


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


def test_summary_without_passed_articles() -> None:
    """A run where every article fell back reports zero agreement instead of failing."""
    fallback = Result(
        id=1, url="https://example.edu/p/406-1000-1.php", outcome="fallback", failures=("a",) * 3,
        api_errors=0, waits=(), requests=3, input_tokens=30, output_tokens=60, seconds=1.5,
        images=0, left_out_images=(),
        tags={key: list[str]() for key in ("topic", "audience", "nature", "source")},
        labels={"topic": ["t"], "audience": ["a"], "nature": ["n"], "source": ["s"]},
        model_deadline=None, deadline=None, labelled_deadline=DAY, title="T", summary=None,
        markdown="[T](https://example.edu/p/406-1000-1.php)",
    )  # fmt: skip
    summary = summarize([fallback])
    assert (summary["passed"], summary["fallbacks"]) == (0, 1)
    assert summary["per_article"] == {
        "requests": 3.0,
        "input_tokens": 30.0,
        "output_tokens": 60.0,
        "seconds": 1.5,
    }
    assert summary["tags"] == {
        "topic": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
        "audience": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
        "nature": {"accuracy": 0.0},
        "source": {"accuracy": 0.0},
    }
