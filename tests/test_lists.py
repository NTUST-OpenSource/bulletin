"""List page fetch: what a board's list page holds, read from recorded pages."""

from datetime import date
from pathlib import Path

import pytest

from bulletin.model import Listed
from bulletin.pages import parse_list

LISTS = Path(__file__).parent / "fixtures" / "lists"


def read(name: str) -> str:
    return (LISTS / name).read_text("utf-8")


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="List page fetch")
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


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="List page fetch")
def test_a_list_board_without_dates() -> None:
    """A board in the list layout, which shows no dates, reads its items without one."""
    url = "https://lc.ntust.edu.tw/p/403-1070-1626-1.php"

    items = parse_list(read("language-center-recruitment.html"), url, 1070)

    assert [i.article_id for i in items] == [148534, 145598, 142619, 144111]
    assert {(i.site_id, i.host, i.listed_on) for i in items} == {(1070, "lc.ntust.edu.tw", None)}


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="List page fetch")
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
