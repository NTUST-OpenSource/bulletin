"""Requirements of the attachments capability."""

import json
from pathlib import Path

from bulletin.pages import is_file, parse_article

FIXTURES = Path(__file__).parent / "fixtures" / "articles"
EXPECTED = json.loads((FIXTURES / "1068-152869.json").read_text(encoding="utf-8"))


def test_module_and_body_files() -> None:
    """Attachment records: two module files and a body file, not the web page or mailto link."""
    page = (FIXTURES / "1068-152869.html").read_text(encoding="utf-8")

    content = parse_article(page, EXPECTED["url"])

    assert [[a.name, a.url, a.origin] for a in content.attachments] == EXPECTED["attachments"]


def test_what_counts_as_a_file() -> None:
    """Attachment records: a file extension or a /var/file/ path makes a body link a file."""
    assert is_file("https://she.ntust.edu.tw/var/file/68/1068/img/376682279.docx")
    assert is_file("https://www.ntust.edu.tw/var/file/0/1000/attach/1/pta_1_2.pdf?x=1")
    assert is_file("https://example.com/forms/Notice.PDF")
    assert not is_file("https://forms.gle/M3P93zsX3KY41s829")
    assert not is_file("mailto:office@example.com")
    assert not is_file("https://www.ntust.edu.tw/p/406-1000-153625.php")
