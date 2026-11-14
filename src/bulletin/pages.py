"""What the school's RPage list and article pages hold."""

import posixpath
import re
from datetime import date
from urllib.parse import urljoin, urlsplit

from bulletin.markup import parse
from bulletin.model import Attachment, Content, Listed
from bulletin.tls import is_school

# An article's path, with the optional board suffix: /p/406-1048-149096,r1416.php
ARTICLE_PATH = re.compile(r"/p/406-(\d+)-(\d+)(?:,r\d+)?\.php")
LIST_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

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


class PageError(Exception):
    """A list page answered with something other than 200."""


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


def list_url(host: str, site_id: int, rcg: int, page: int = 1) -> str:
    """The static list page `page` of a board."""
    return f"https://{host}/p/403-{site_id}-{rcg}-{page}.php"


def parse_list(page: str, url: str, site_id: int) -> list[Listed]:
    """Read a list page at `url` of a board on site `site_id`: its items in page order.

    An item linking to an article on a school host takes its site and id from the link; any
    other link is an item of the board's own site, identified by its URL. Table boards hold their
    items in rows, the others in `listBS` blocks; the list date is the first date in the item
    outside its title.
    """
    document = parse(page)
    rows = document.select("div#pageptlist tbody tr") or document.select(
        "div#pageptlist div.listBS"
    )
    host = urlsplit(url).hostname or ""
    items: list[Listed] = []
    for row in rows:
        anchor = row.select_first("div.mtitle a")
        if anchor is None or not anchor.attr("href").strip():
            continue
        title = anchor.text().strip()
        listed = LIST_DATE.search(row.text().replace(title, ""))
        listed_on = date(*map(int, listed.groups())) if listed else None
        link = urljoin(url, anchor.attr("href").strip())
        parts = urlsplit(link)
        article = ARTICLE_PATH.fullmatch(parts.path)
        if article and parts.scheme == "https" and is_school(parts.hostname or ""):
            item = Listed(
                int(article[1]), parts.hostname or "", int(article[2]), None, title, listed_on
            )
        else:
            item = Listed(site_id, host, None, link, title, listed_on)
        items.append(item)
    return items
