"""Requirement "Model input" of the rendering capability."""

import json
from pathlib import Path

from bulletin.model_input import model_input
from bulletin.pages import parse_article

FIXTURES = Path(__file__).parent / "fixtures"
ARTICLE = FIXTURES / "articles" / "1068-152869"
URL = "https://she.ntust.edu.tw/p/406-1068-152869.php"
IMAGES = "https://she.ntust.edu.tw/var/file/68/1068/img/"


def test_a_recorded_article() -> None:
    """Model input: body text, every attachment's name, placeholders for links, and no URL."""
    content = parse_article(ARTICLE.with_suffix(".html").read_text(encoding="utf-8"), URL)
    module = [a.url for a in content.attachments if a.origin == "module"]

    given = model_input(content.title, content.body_html, content.attachments, URL)

    expected = (FIXTURES / "model" / "input-1068-152869.md").read_text(encoding="utf-8")
    assert given.text == expected.rstrip("\n")
    assert given.targets == {
        "L1": "https://forms.gle/M3P93zsX3KY41s829",
        "L2": f"{IMAGES}376682279.docx",
        "I1": f"{IMAGES}506086235.png",
        "I2": f"{IMAGES}9083a1d6-c8b7-4424-8334-755399834607.png",
        "L3": module[0],
        "L4": module[1],
    }
    for text in json.loads(ARTICLE.with_suffix(".json").read_text(encoding="utf-8"))[
        "body_text_has"
    ]:
        assert text in given.text
    assert "http" not in given.text
    assert "mailto" not in given.text


def test_the_kept_elements() -> None:
    """Model input: paragraphs, lists, tables, links and bold; headings become bold lines."""
    body = (
        '<div class="mpgdetail"><h3>Dates</h3>'
        '<p>Apply <strong>now</strong> at <a href="/apply">the form</a>.</p>'
        "<ul><li>one<ul><li>nested</li></ul></li><li>two</li></ul><ol><li>first</li></ol>"
        "<table><tr><th>Item</th><th>Fee | NTD</th></tr><tr><td>A</td><td>100</td></tr></table>"
        "<script>x()</script>"
        '<p><span style="color:red">plain</span> <a href="javascript:void(0)">no link</a>'
        ' <a href="/apply">again</a></p></div>'
    )

    given = model_input("T", body, (), "https://www.ntust.edu.tw/p/406-1000-1.php")

    assert given.text == (
        "Title: T\n\nBody:\n**Dates**\n\nApply **now** at [the form](L1).\n\n"
        "- one\n  - nested\n- two\n\n1. first\n\n"
        "| Item | Fee \\| NTD |\n| --- | --- |\n| A | 100 |\n\n"
        "plain no link [again](L1)"
    )
    assert given.targets == {"L1": "https://www.ntust.edu.tw/apply"}
