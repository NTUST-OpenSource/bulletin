"""Requirements of the attachments capability."""

import json
from pathlib import Path

import pytest

from bulletin.files import read_size
from bulletin.pages import is_file, parse_article
from web import Answer, FakeWeb

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


VAR_FILE = "https://student.ntust.edu.tw/var/file/53/1053/img/1435/notice.pdf"
MODULE_FILE = "https://student.ntust.edu.tw/app/index.php?Action=downloadfile&file=a&fname=b"
FIVE_MB = 5 * 2**20


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Size without HEAD")
async def test_range_answer() -> None:
    """Size without HEAD: a 206 with Content-Range gives the size of a /var/file/ link."""
    web = FakeWeb({VAR_FILE: Answer(206, {"Content-Range": "bytes 0-0/278993"}, b"%")})

    size, _ = await read_size(web, VAR_FILE, lambda size: size < FIVE_MB)

    assert size == 278993
    assert web.requests[0].headers == {"Range": "bytes=0-0"}


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Size without HEAD")
async def test_a_module_file_over_five_mb() -> None:
    """Size without HEAD: Content-Length gives the size; the body of a large file is not read."""
    web = FakeWeb({MODULE_FILE: Answer(200, {"Content-Length": "7900000"}, b"x" * 16)})

    size, content = await read_size(web, MODULE_FILE, lambda size: size < FIVE_MB)

    assert (size, content) == (7900000, None)
    assert [r.body_read for r in web.requests] == [False]


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Size without HEAD")
async def test_a_small_module_file_is_read_once() -> None:
    """Size without HEAD: a downloadfile link small enough to keep is read in the same request."""
    web = FakeWeb({MODULE_FILE: Answer(200, {"Content-Length": "4"}, b"%PDF")})

    assert await read_size(web, MODULE_FILE, lambda size: size < FIVE_MB) == (4, b"%PDF")
    assert len(web.requests) == 1
