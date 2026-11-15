"""Requirements of the tags capability."""

import re
from pathlib import Path

import pytest

from bulletin.taxonomy import TagError, parse_tags, taxonomy

DECISIONS = Path(__file__).parents[1] / "docs" / "decisions.md"
ID = re.compile(r"[a-z]+(-[a-z]+)*")


def approved_labels() -> list[list[str]]:
    """The `Labels:` lines of decision E3, in the order of its dimensions."""
    text = DECISIONS.read_text(encoding="utf-8").split("**E3 Tags**", 1)[1].split("**E4", 1)[0]
    return [
        [label.strip() for label in " ".join(line.split()).split(",")]
        for line in re.findall(r"Labels: ([^.]+)\.", text)
    ]


def answer(**tags: object) -> dict[str, object]:
    valid: dict[str, object] = {
        "topic": [],
        "audience": [],
        "nature": "information",
        "source": "on-campus",
    }
    return valid | tags


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Fixed taxonomy")
def test_the_taxonomy() -> None:
    """Fixed taxonomy: 20 topics, 8 audiences, 4 natures and 2 sources with ids and labels."""
    loaded = taxonomy()

    assert {dimension: len(tags) for dimension, tags in loaded.items()} == {
        "topic": 20,
        "audience": 8,
        "nature": 4,
        "source": 2,
    }
    assert [[tag.label for tag in tags] for tags in loaded.values()] == approved_labels()
    for dimension, tags in loaded.items():
        assert all(tag.dimension == dimension and ID.fullmatch(tag.id) for tag in tags)
        assert len({tag.id for tag in tags}) == len(tags)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Fixed taxonomy")
def test_tags_of_an_answer() -> None:
    """Fixed taxonomy: several topics and audiences, one nature and one source."""
    tags = parse_tags(answer(topic=["scholarships", "fees"], audience=["undergraduates"]))

    assert tags == {
        ("topic", "scholarships"),
        ("topic", "fees"),
        ("audience", "undergraduates"),
        ("nature", "information"),
        ("source", "on-campus"),
    }


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Fixed taxonomy")
@pytest.mark.parametrize(
    "tags",
    [
        pytest.param(answer(nature=["action-required", "information"]), id="two natures"),
        pytest.param(answer(source=None), id="no source"),
        pytest.param(answer(topic=["weather"]), id="a tag outside the taxonomy"),
        pytest.param(answer(audience="staff"), id="audiences not a list"),
        pytest.param({"topic": [], "nature": "information", "source": "on-campus"}, id="missing"),
    ],
)
def test_tags_that_fail(tags: dict[str, object]) -> None:
    """Fixed taxonomy: two natures, no source or an unknown tag fail the attempt."""
    with pytest.raises(TagError):
        parse_tags(tags)
