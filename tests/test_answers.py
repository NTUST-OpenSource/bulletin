"""Requirements of the rendering capability that check the model's answer."""

import json
from datetime import date

import pytest

from bulletin.answers import Answer, AnswerError, parse_answer, restore

TARGETS = {
    "L1": "https://forms.gle/abc",
    "I1": "https://www.ntust.edu.tw/var/file/0/1000/img/poster.png",
    "L2": "https://www.ntust.edu.tw/var/file/0/1000/attach/form (1).pdf",
}


def test_links_restored() -> None:
    """Placeholders put back: the Markdown holds the URLs of L1 and I1 and no placeholder."""
    restored = restore("Apply [here](L1).\n\n![poster](I1)", TARGETS)

    assert restored == f"Apply [here]({TARGETS['L1']}).\n\n![poster]({TARGETS['I1']})"


def test_urls_fit_markdown() -> None:
    """Placeholders put back: spaces and parentheses in a URL are escaped for the link."""
    restored = restore("![poster](I1) [form](L2)", TARGETS)

    assert restored.endswith(
        "[form](https://www.ntust.edu.tw/var/file/0/1000/attach/form%20%281%29.pdf)"
    )


def test_an_invented_placeholder() -> None:
    """Placeholders put back: an answer holding L9 when the input had L1 fails."""
    with pytest.raises(AnswerError, match="L9"):
        restore("[here](L9) ![poster](I1)", TARGETS)


def test_a_dropped_image() -> None:
    """Placeholders put back: an answer without the input's I1 fails."""
    with pytest.raises(AnswerError, match="I1"):
        restore("Apply [here](L1).", TARGETS)


def answer(**fields: object) -> str:
    valid: dict[str, object] = {
        "title": "t",
        "markdown": "m",
        "summary": "s",
        "deadline": "2026-12-10",
        "tags": {
            "topic": ["scholarships"],
            "audience": [],
            "nature": "action-required",
            "source": "on-campus",
        },
    }
    return json.dumps(valid | fields)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Structured answer")
def test_an_answer() -> None:
    """Structured answer: title, Markdown, summary, deadline and tags."""
    parsed = parse_answer(answer())

    assert parsed == Answer(
        title="t",
        markdown="m",
        summary="s",
        deadline=date(2026, 12, 10),
        tags=frozenset(
            {
                ("topic", "scholarships"),
                ("nature", "action-required"),
                ("source", "on-campus"),
            }
        ),
    )
    assert parse_answer(answer(deadline=None)).deadline is None


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Structured answer")
@pytest.mark.parametrize(
    "text",
    [
        pytest.param("Here is the rewritten announcement.", id="prose"),
        pytest.param("[]", id="not an object"),
        pytest.param(json.dumps({"title": "t"}), id="fields missing"),
        pytest.param(answer(markdown=" "), id="empty markdown"),
        pytest.param(answer(title=7), id="title not a text"),
        pytest.param(answer(deadline="next week"), id="deadline not a date"),
        pytest.param(answer(tags={"topic": ["weather"]}), id="tags outside the taxonomy"),
    ],
)
def test_answers_that_fail(text: str) -> None:
    """Structured answer: prose, or JSON that does not match the schema, fails the attempt."""
    with pytest.raises(AnswerError):
        parse_answer(text)
