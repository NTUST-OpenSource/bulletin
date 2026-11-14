"""Requirements of the attachments capability."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from bulletin.archive import publish, revise
from bulletin.files import FileStore, keep_files, read_size
from bulletin.model import Attachment, Content, Listed
from bulletin.pages import is_file, parse_article
from web import Answer, FakeWeb

if TYPE_CHECKING:
    from psycopg import AsyncConnection

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


async def test_range_answer() -> None:
    """Size without HEAD: a 206 with Content-Range gives the size of a /var/file/ link."""
    web = FakeWeb({VAR_FILE: Answer(206, {"Content-Range": "bytes 0-0/278993"}, b"%")})

    size, _ = await read_size(web, VAR_FILE, lambda size: size < FIVE_MB)

    assert size == 278993
    assert web.requests[0].headers == {"Range": "bytes=0-0"}


async def test_a_module_file_over_five_mb() -> None:
    """Size without HEAD: Content-Length gives the size; the body of a large file is not read."""
    web = FakeWeb({MODULE_FILE: Answer(200, {"Content-Length": "7900000"}, b"x" * 16)})

    size, content = await read_size(web, MODULE_FILE, lambda size: size < FIVE_MB)

    assert (size, content) == (7900000, None)
    assert [r.body_read for r in web.requests] == [False]


async def test_a_small_module_file_is_read_once() -> None:
    """Size without HEAD: a downloadfile link small enough to keep is read in the same request."""
    web = FakeWeb({MODULE_FILE: Answer(200, {"Content-Length": "4"}, b"%PDF")})

    assert await read_size(web, MODULE_FILE, lambda size: size < FIVE_MB) == (4, b"%PDF")
    assert len(web.requests) == 1


AT = datetime(2026, 11, 18, 2, 0, tzinfo=UTC)


async def announcement_with(conn: AsyncConnection, article_id: int, *urls: str) -> int:
    listed = Listed(1053, "student.ntust.edu.tw", article_id, None, f"t{article_id}")
    announcement = await publish(conn, listed, notify=False, late=True)
    files = tuple(Attachment(f"f{n}", url, "body") for n, url in enumerate(urls))
    await revise(conn, announcement, Content(f"t{article_id}", None, "<p/>", "b", files))
    return announcement


async def recorded(conn: AsyncConnection) -> dict[str, tuple[int | None, str | None]]:
    cur = await conn.execute("SELECT url, size, sha256 FROM attachment")
    return {url: (size, digest) for url, size, digest in await cur.fetchall()}


async def test_a_small_school_file(migrated: AsyncConnection, tmp_path: Path) -> None:
    """Stored copies: a 600 KB school PDF is stored, with its size and digest recorded."""
    pdf = b"%PDF" + b"0" * (600 * 1024 - 4)
    web = FakeWeb({VAR_FILE: Answer(200, {"Content-Length": str(len(pdf))}, pdf)})
    announcement = await announcement_with(migrated, 1, VAR_FILE)
    store = FileStore(tmp_path)

    await keep_files(migrated, web, store, announcement, AT)

    digest = hashlib.sha256(pdf).hexdigest()
    assert await recorded(migrated) == {VAR_FILE: (len(pdf), digest)}
    assert store.path(digest).read_bytes() == pdf


async def test_a_large_file(migrated: AsyncConnection, tmp_path: Path) -> None:
    """Stored copies: a 7 MB attachment keeps its name, URL and size only."""
    web = FakeWeb({MODULE_FILE: Answer(200, {"Content-Length": str(7 * 2**20)}, b"x")})
    announcement = await announcement_with(migrated, 1, MODULE_FILE)

    await keep_files(migrated, web, FileStore(tmp_path), announcement, AT)

    assert await recorded(migrated) == {MODULE_FILE: (7 * 2**20, None)}
    assert list(tmp_path.iterdir()) == []


async def test_a_file_outside_the_school(migrated: AsyncConnection, tmp_path: Path) -> None:
    """Stored copies: an attachment outside ntust.edu.tw is neither requested nor stored."""
    outside = "https://drive.example.com/notice.pdf"
    web = FakeWeb({})
    announcement = await announcement_with(migrated, 1, outside)

    await keep_files(migrated, web, FileStore(tmp_path), announcement, AT)

    assert web.requests == []
    assert await recorded(migrated) == {outside: (None, None)}


async def test_the_same_file_twice(migrated: AsyncConnection, tmp_path: Path) -> None:
    """Stored copies: two links to the same content keep one copy."""
    other = VAR_FILE.replace("notice", "copy")
    pdf = b"%PDF same"
    web = FakeWeb({url: Answer(200, {"Content-Length": "9"}, pdf) for url in (VAR_FILE, other)})
    store = FileStore(tmp_path)
    first = await announcement_with(migrated, 1, VAR_FILE)
    second = await announcement_with(migrated, 2, other)

    for announcement in (first, second):
        await keep_files(migrated, web, store, announcement, AT)

    digest = hashlib.sha256(pdf).hexdigest()
    assert set((await recorded(migrated)).values()) == {(9, digest)}
    assert [p.name for p in tmp_path.rglob("*") if p.is_file()] == [digest]
