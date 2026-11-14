"""What the school's RPage list and article pages hold."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bulletin.archive import Content


def parse_article(page: str, url: str, publisher: str | None = None) -> Content:
    """Read an article page at `url`: title, body as HTML and text, and attachments."""
    raise NotImplementedError
