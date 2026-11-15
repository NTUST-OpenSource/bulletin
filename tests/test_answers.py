"""Requirements of the rendering capability that check the model's answer."""

import pytest

from bulletin.answers import AnswerError, restore

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
