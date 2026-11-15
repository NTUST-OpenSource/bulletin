"""Cross-post pointers: `450` links take the identity of the article they redirect to."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from bulletin.pages import parse_list
from bulletin.pointers import resolve_pointers
from web import Answer, FakeWeb

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from bulletin.model import Listed

AT = datetime(2026, 11, 18, 2, 0, tzinfo=UTC)
LISTS = Path(__file__).parent / "fixtures" / "lists"
RECORDED = json.loads((LISTS / "pointer-450-1045-152885.json").read_text())
LISTED = "https://bulletin.ntust.edu.tw/p/450-1045-152885,c0.php?Lang=zh-tw"


def bulletin_items() -> list[Listed]:
    page = (LISTS / "bulletin-1045-1391.html").read_text("utf-8")
    return parse_list(page, "https://bulletin.ntust.edu.tw/p/403-1045-1391-1.php", 1045)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Cross-post pointers")
async def test_a_cross_post_pointer(migrated: AsyncConnection) -> None:
    """A cross-post pointer: the item is read as the article it redirects to, and later polls do
    not request the pointer again."""
    items = bulletin_items()
    web = FakeWeb({LISTED: Answer(RECORDED["status"], {"Location": RECORDED["location"]})})

    resolved = await resolve_pointers(migrated, web, items, AT)
    again = await resolve_pointers(migrated, web, items, AT)

    assert [r.url for r in web.requests] == [LISTED]
    assert resolved == again
    pointer = next(i for i in items if i.link_url == LISTED)
    article = resolved[items.index(pointer)]
    assert (article.site_id, article.host, article.article_id, article.link_url) == (
        1068,
        "she.ntust.edu.tw",
        152869,
        None,
    )
    assert (article.title, article.listed_on, article.publisher) == (
        pointer.title,
        pointer.listed_on,
        pointer.publisher,
    )
    assert [i for i in resolved if i is not article] == [i for i in items if i is not pointer]


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Cross-post pointers")
async def test_a_pointer_that_does_not_redirect(migrated: AsyncConnection) -> None:
    """A pointer that does not redirect: the item stays a link item; the pointer is asked once."""
    items = bulletin_items()
    web = FakeWeb({LISTED: Answer(200, body=b"<html></html>")})

    assert await resolve_pointers(migrated, web, items, AT) == items
    assert await resolve_pointers(migrated, web, items, AT) == items
    assert len(web.requests) == 1
