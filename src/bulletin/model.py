"""The shapes the collector passes around: list items and article contents."""

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from datetime import date


@dataclass(frozen=True)
class Listed:
    """An announcement as a list page shows it; its identity comes from the item's link."""

    site_id: int
    host: str
    article_id: int | None
    link_url: str | None
    title: str
    listed_on: date | None = None
    publisher: str | None = None


@dataclass(frozen=True)
class Attachment:
    """A file an article names, from its attachment module or a link in its body."""

    name: str
    url: str
    origin: Literal["module", "body"]


@dataclass(frozen=True)
class Content:
    """What an article page holds."""

    title: str
    publisher: str | None
    body_html: str
    body_text: str
    attachments: tuple[Attachment, ...] = ()

    def digest(self) -> str:
        """Hash what a revision is compared by: the title, the body and the attachment links."""
        key = [self.title, self.body_text, [a.url for a in self.attachments]]
        return hashlib.sha256(json.dumps(key, ensure_ascii=False).encode()).hexdigest()
