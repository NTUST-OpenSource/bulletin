"""What the school's RPage list and article pages hold."""

import posixpath
from urllib.parse import urljoin, urlsplit

from bulletin.markup import parse
from bulletin.model import Attachment, Content, Listed

# A body link is a file when its path has one of these extensions or is under /var/file/.
FILE_EXTENSIONS = frozenset(
    {
        ".7z",
        ".csv",
        ".doc",
        ".docx",
        ".gif",
        ".jpeg",
        ".jpg",
        ".odp",
        ".ods",
        ".odt",
        ".pdf",
        ".png",
        ".ppt",
        ".pptx",
        ".rar",
        ".txt",
        ".xls",
        ".xlsx",
        ".zip",
    }
)


def is_file(url: str) -> bool:
    """Whether a body link points at a file rather than a page."""
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        return False
    return (
        "/var/file/" in parts.path or posixpath.splitext(parts.path)[1].lower() in FILE_EXTENSIONS
    )


def parse_article(page: str, url: str, publisher: str | None = None) -> Content:
    """Read an article page at `url`: title, body as HTML and text, and attachments.

    Attachments are the links of the attachment module, then the body's links to files.
    """
    document = parse(page)
    heading = document.select_first("h2.hdline")
    body = document.select_first("div.mpgdetail")
    attachments = [
        Attachment(a.text(), urljoin(url, a.attr("href")), "module")
        for a in document.select("ul.mptattach a")
        if a.attr("href")
    ]
    if body is not None:
        links = ((a, urljoin(url, a.attr("href"))) for a in body.select("a") if a.attr("href"))
        attachments += [Attachment(a.text(), link, "body") for a, link in links if is_file(link)]
    return Content(
        title=heading.text() if heading is not None else "",
        publisher=publisher,
        body_html=body.outer_html() if body is not None else "",
        body_text=body.text() if body is not None else "",
        attachments=tuple(attachments),
    )


def parse_list(page: str, url: str, site_id: int) -> list[Listed]:
    """Read a list page at `url` of a board on site `site_id`: its items in page order.

    An item linking to an article on a school host takes its site and id from the link; any
    other link is an item of the board's own site, identified by its URL.
    """
    raise NotImplementedError
