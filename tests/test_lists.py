"""List page fetch: what a board's list page holds, read from recorded pages."""

import json
from datetime import date
from pathlib import Path

import pytest

from bulletin.model import Listed
from bulletin.pages import parse_list

LISTS = Path(__file__).parent / "fixtures" / "lists"


def read(name: str) -> str:
    return (LISTS / name).read_text("utf-8")


def test_a_table_board() -> None:
    """A table board: every item's article site and id, title and list date, in page order."""
    url = "https://www.academic.ntust.edu.tw/p/403-1048-1416-1.php"

    items = parse_list(read("academic-course.html"), url, 1048)

    assert [(i.site_id, i.host, i.article_id, i.link_url) for i in items] == [
        (1048, "www.academic.ntust.edu.tw", n, None) for n in (149096, 148431, 146657, 145601)
    ]
    assert [i.listed_on for i in items] == [
        date(2026, 6, 18),
        date(2026, 6, 2),
        date(2026, 4, 15),
        date(2026, 3, 16),
    ]
    assert all(i.title and i.title == i.title.strip() for i in items)
    assert items[0].title.startswith("114-2")


def test_a_list_board_without_dates() -> None:
    """A board in the list layout, which shows no dates, reads its items without one."""
    url = "https://lc.ntust.edu.tw/p/403-1070-1626-1.php"

    items = parse_list(read("language-center-recruitment.html"), url, 1070)

    assert [i.article_id for i in items] == [148534, 145598, 142619, 144111]
    assert {(i.site_id, i.host, i.listed_on) for i in items} == {(1070, "lc.ntust.edu.tw", None)}


def test_a_link_that_is_not_an_article() -> None:
    """A link to a file: the item keeps its URL and title, and has no article id.

    Links outside the list, such as the site's menu, are not items.
    """
    url = "https://student.ntust.edu.tw/p/403-1053-1436-1.php"

    items = parse_list(read("student-dormitory.html"), url, 1053)

    assert len(items) == 6
    link = items[-1]
    assert link == Listed(
        1053,
        "student.ntust.edu.tw",
        None,
        "https://docs.google.com/spreadsheets/d/EXAMPLE/edit?usp=sharing",
        link.title,
        link.listed_on,
    )
    assert link.title.endswith("2026 summer")
    assert all(i.listed_on is not None for i in items)


def test_the_publisher_column() -> None:
    """List page fetch: a board that lists a publisher gives each item its publisher."""
    expected = json.loads(read("bulletin-1045-1391.json"))
    url = "https://bulletin.ntust.edu.tw/p/403-1045-1391-1.php"

    items = parse_list(read("bulletin-1045-1391.html"), url, 1045)

    assert len(items) == expected["items"]
    first = expected["first"]
    assert (items[0].site_id, items[0].article_id, items[0].listed_on) == (
        first["site_id"],
        first["article_id"],
        date.fromisoformat(first["listed_on"]),
    )
    assert [i.publisher for i in items] == expected["publishers"]
    assert [i.link_url for i in items if i.article_id is None] == [
        "https://bulletin.ntust.edu.tw/p/450-1045-152885,c0.php?Lang=zh-tw"
    ]


def test_a_board_listing_another_sites_articles() -> None:
    """List page fetch: identity comes from the link, `404` news pages included."""
    url = "https://www.secretariat.ntust.edu.tw/p/403-1063-2211-1.php"

    items = parse_list(read("secretariat-1063-2211.html"), url, 1063)

    assert len(items) == 10
    assert all(i.article_id is not None for i in items)
    keys = {(i.host, i.site_id, i.article_id) for i in items}
    assert {("www.ntust.edu.tw", 1000, 153625), ("www.ntust.edu.tw", 1000, 153631)} <= keys


@pytest.mark.xfail(strict=True, raises=ValueError, reason="List page fetch")
def test_a_link_that_cannot_be_parsed() -> None:
    """List page fetch: an item whose link cannot be parsed is skipped; the others stay."""
    row = '<div class="listBS"><div class="mtitle"><a href="{}">{}</a></div></div>'
    page = (
        '<div id="pageptlist">'
        + row.format("http://[bad", "bad")
        + row.format("/p/406-1053-153698.php", "good")
        + "</div>"
    )

    items = parse_list(page, "https://student.ntust.edu.tw/p/403-1053-1-1.php", 1053)

    assert [item.title for item in items] == ["good"]
