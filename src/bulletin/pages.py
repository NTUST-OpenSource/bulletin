"""What the school's RPage list and article pages hold."""

import json
import posixpath
import re
from datetime import date
from importlib import resources
from urllib.parse import urljoin, urlsplit

from bulletin.markup import Element, parse
from bulletin.model import Attachment, Content, Listed
from bulletin.tls import is_school

# An article's path, with the optional board suffix: /p/406-1048-149096,r1416.php. A 404 page
# shows the same article.
ARTICLE_PATH = re.compile(r"/p/40[46]-(\d+)-(\d+)(?:,r\d+)?\.php")
# A cross-post pointer: /p/450-1045-152885,c0.php redirects to the article on its own site.
POINTER_PATH = re.compile(r"/p/450-\d+-\d+(?:,c\d+)?\.php")
# The labels of the column that names an item's publisher, as the school writes them.
PUBLISHER = frozenset(
    json.loads((resources.files("bulletin") / "columns.json").read_text(encoding="utf-8"))[
        "publisher"
    ]
)
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
    outside its title, and the publisher is the cell under a publisher column.
    """
    document = parse(page)
    rows = document.select("div#pageptlist tbody tr") or document.select(
        "div#pageptlist div.listBS"
    )
    items = (_item(row, url, site_id) for row in rows)
    return [item for item in items if item is not None]


def _item(row: Element, url: str, site_id: int) -> Listed | None:
    anchor = row.select_first("div.mtitle a")
    if anchor is None or not anchor.attr("href").strip():
        return None
    title = anchor.text().strip()
    listed = LIST_DATE.search(row.text().replace(title, ""))
    listed_on = date(*map(int, listed.groups())) if listed else None
    publisher = next(
        (td.text().strip() or None for td in row.select("td") if td.attr("data-th") in PUBLISHER),
        None,
    )
    link = urljoin(url, anchor.attr("href").strip())
    if (article := article_key(link)) is not None:
        return Listed(article[1], article[0], article[2], None, title, listed_on, publisher)
    host = urlsplit(url).hostname or ""
    return Listed(site_id, host, None, link, title, listed_on, publisher)


def article_key(url: str) -> tuple[str, int, int] | None:
    """The host, site and article id of an article link on a school host, or None."""
    parts = urlsplit(url)
    article = ARTICLE_PATH.fullmatch(parts.path)
    if article and parts.scheme == "https" and is_school(parts.hostname or ""):
        return parts.hostname or "", int(article[1]), int(article[2])
    return None


def is_pointer(url: str) -> bool:
    """Whether `url` is a cross-post pointer, a `450` page that redirects to an article."""
    parts = urlsplit(url)
    return POINTER_PATH.fullmatch(parts.path) is not None and is_school(parts.hostname or "")


def page_count(page: str) -> int | None:
    """The number of pages a list page's pager states, if it has one."""
    counts = (span.text().strip() for span in parse(page).select("span.pg-txt span"))
    return next((int(text) for text in counts if text.isdigit()), None)
