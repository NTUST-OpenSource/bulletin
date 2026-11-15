"""Requirements of the rendering capability that check the model's answer."""

import json
from datetime import date

import pytest

from bulletin.answers import Answer, AnswerError, keep_deadline, parse_answer, restore

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


YEAR, MONTH, DAY = chr(0x5E74), chr(0x6708), chr(0x65E5)
DECEMBER_10 = date(2026, 12, 10)


@pytest.mark.parametrize(
    "written",
    [
        pytest.param(f"115{YEAR}12{MONTH}10{DAY}", id="ROC with year, month and day"),
        pytest.param(f"2026{YEAR}12{MONTH}10{DAY}", id="Gregorian with year, month and day"),
        pytest.param("2026-12-10", id="ISO"),
        pytest.param("2026/12/10", id="Gregorian with slashes"),
        pytest.param("115/12/10", id="ROC with slashes"),
        pytest.param("115.12.10", id="ROC with dots"),
        pytest.param(f"12{MONTH}10{DAY}", id="month and day"),
        pytest.param("12/10(Thu)", id="month and day with slashes"),
        pytest.param("".join(chr(0xFF10 + int(d)) for d in "115") + "/12/10", id="full-width"),
        pytest.param("December 10, 2026", id="English"),
        pytest.param("Thursday, Dec. 10th", id="English without the year"),
        pytest.param("10 December 2026", id="English day first"),
    ],
)
def test_a_deadline_in_the_text(written: str) -> None:
    """Deadlines from the text: a date the text holds in one of the school's forms is kept."""
    text = f"Apply before {written} noon."

    assert keep_deadline(DECEMBER_10, text, 2026) == DECEMBER_10


def test_a_date_of_the_next_year() -> None:
    """Deadlines from the text: a month and day may belong to the year after the list date."""
    assert keep_deadline(date(2027, 1, 5), "Due 1/5.", 2026) == date(2027, 1, 5)
    assert keep_deadline(date(2028, 1, 5), "Due 1/5.", 2026) is None


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("Apply before 2026/12/11.", id="another day"),
        pytest.param("Call 2026-1210 or room 12/101.", id="numbers that are not dates"),
        pytest.param("No date at all.", id="no date"),
        pytest.param("December 10, 2025", id="English, another year"),
    ],
)
def test_an_invented_date(text: str) -> None:
    """Deadlines from the text: a deadline whose date the text does not hold is dropped."""
    assert keep_deadline(DECEMBER_10, text, 2026) is None


def test_no_deadline() -> None:
    """Deadlines from the text: an answer without a deadline keeps none."""
    assert keep_deadline(None, "2026/12/10", 2026) is None
