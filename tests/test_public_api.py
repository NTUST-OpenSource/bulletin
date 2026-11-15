"""Requirements of the public-api capability: the stream, its items, filters and search."""

from datetime import date, timedelta
from typing import TYPE_CHECKING

import pytest

from bulletin.archive import revise
from bulletin.model import Content
from bulletin.renditions import store
from world import World, rendition

if TYPE_CHECKING:
    from pathlib import Path

    from psycopg import AsyncConnection

DAY = date(2026, 11, 13)
STREAM = "/api/v1/announcements"


@pytest.fixture
async def world(migrated: AsyncConnection, tmp_path: Path) -> World:
    created = World(migrated, tmp_path)
    await created.boards()
    return created


async def stream(world: World, **params: object) -> list[int]:
    """The ids of every page of a stream request, following `next`."""
    ids: list[int] = []
    query: dict[str, object] = dict(params)
    async with world.client() as http:
        while True:
            response = await http.get(STREAM, params=query)  # type: ignore[arg-type]
            assert response.status_code == 200, response.text
            page = response.json()
            ids += [item["id"] for item in page["items"]]
            if page["next"] is None:
                return ids
            query["cursor"] = page["next"]


async def test_a_write(world: World) -> None:
    """Read-only JSON under /api/v1: a POST gets a JSON 405 and changes nothing."""
    async with world.client() as http:
        response = await http.post(STREAM, json={})

    assert response.status_code == 405
    assert "detail" in response.json()


async def test_the_admin_path(world: World) -> None:
    """Read-only JSON under /api/v1: the admin API does not answer on the public listener."""
    async with world.client() as http:
        response = await http.get("/admin/boards")

    assert response.status_code == 404


async def test_two_pages(world: World) -> None:
    """Announcement stream: 45 announcements come once each, in order, over two pages."""
    added = [await world.add(DAY - timedelta(days=n % 9)) for n in range(45)]
    wanted = sorted(added, key=lambda a: (added.index(a) % 9, -a))
    async with world.client() as http:
        first = (await http.get(STREAM)).json()
        second = (await http.get(STREAM, params={"cursor": first["next"]})).json()

    assert len(first["items"]) == 30
    assert second["next"] is None
    assert [i["id"] for i in first["items"] + second["items"]] == wanted


async def test_a_new_announcement_between_pages(world: World) -> None:
    """Announcement stream: an announcement stored between pages neither repeats nor skips one."""
    added = [await world.add(DAY) for _ in range(4)]
    async with world.client() as http:
        first = (await http.get(STREAM, params={"limit": 2})).json()
        await world.add(DAY)
        second = (await http.get(STREAM, params={"limit": 2, "cursor": first["next"]})).json()

    assert [i["id"] for i in first["items"] + second["items"]] == added[::-1]


async def test_a_cross_post(world: World) -> None:
    """Announcement stream: a cross-post is folded into the announcement it copies."""
    office = await world.add(DAY)
    await world.cross_post(office, DAY)

    assert await stream(world) == [office]


@pytest.mark.parametrize("params", [{"cursor": "xyz"}, {"limit": 500}, {"limit": 0}])
async def test_bad_paging_values(world: World, params: dict[str, object]) -> None:
    """Announcement stream: a malformed cursor or a limit outside 1 to 100 is a 400."""
    async with world.client() as http:
        response = await http.get(STREAM, params=params)  # type: ignore[arg-type]

    assert response.status_code == 400


async def item(world: World, announcement: int) -> dict[str, object]:
    async with world.client() as http:
        page = (await http.get(STREAM)).json()
    return next(i for i in page["items"] if i["id"] == announcement)


async def test_a_rendered_announcement(world: World) -> None:
    """Stream items: a rendered announcement carries its rendition and tags by dimension."""
    tags = {("topic", "scholarships"), ("nature", "information"), ("source", "on-campus")}
    rendered = await world.add(
        DAY,
        boards=("1053-1435", "1053-1436"),
        title="school title",
        publisher="office",
        rendition=rendition("new title", deadline=date(2026, 12, 1), tags=tags),
    )

    got = await item(world, rendered)
    assert isinstance(got.pop("first_seen_at"), str)
    assert got == {
        "id": rendered,
        "site": 1053,
        "unit": "student affairs",
        "url": f"https://student.ntust.edu.tw/p/406-1053-{world.next_article}.php",
        "link_item": False,
        "title": "school title",
        "publisher": "office",
        "day": "2026-11-13",
        "listed_on": "2026-11-13",
        "withdrawn_at": None,
        "boards": ["1053-1435", "1053-1436"],
        "tags": {
            "topic": ["scholarships"],
            "audience": [],
            "nature": ["information"],
            "source": ["on-campus"],
        },
        "rendition": {"title": "new title", "summary": "summary", "deadline": "2026-12-01"},
    }


async def test_a_raw_announcement(world: World) -> None:
    """Stream items: without a rendition or tags, the school's title and empty tag lists."""
    raw = await world.add(DAY, title="school title")

    got = await item(world, raw)
    assert (got["title"], got["rendition"]) == ("school title", None)
    assert got["tags"] == {"topic": [], "audience": [], "nature": [], "source": []}


async def test_a_fallback(world: World) -> None:
    """Stream items: a fallback after a new revision is null and leaves the stored tags."""
    fallen = await world.add(
        DAY, rendition=rendition(tags={("topic", "fees"), ("nature", "information")})
    )
    await revise(world.conn, fallen, Content("t", None, "<p>new</p>", "new"))
    await store(world.conn, fallen, await world.revision(fallen), rendition(fallback=True))

    got = await item(world, fallen)
    assert got["rendition"] is None
    assert got["tags"] == {
        "topic": ["fees"],
        "audience": [],
        "nature": ["information"],
        "source": [],
    }


async def test_a_link_item(world: World) -> None:
    """Stream items: a link item says so, with the link as its URL."""
    link = "https://student.ntust.edu.tw/var/file/53/1053/attach/12/pta_1_0.pdf"
    linked = await world.add(DAY, link=link)

    got = await item(world, linked)
    assert (got["link_item"], got["url"]) == (True, link)


async def test_followed_sites_and_a_board(world: World) -> None:
    """Stream filters: `site` and `board` together select a set of boards."""
    student = await world.add(DAY, boards=("1053-1436",))
    board = await world.add(DAY, boards=("1045-1391",))
    await world.add(DAY, boards=("1017-631",))

    assert set(await stream(world, site=1053, board="1045-1391")) == {student, board}


async def test_placed_through_a_cross_post(world: World) -> None:
    """Stream filters: an announcement matches a board its cross-post is placed on."""
    office = await world.add(DAY, boards=("1017-631",))
    await world.cross_post(office, DAY, "1045-1391")

    assert await stream(world, board="1045-1391") == [office]


async def test_two_tags(world: World) -> None:
    """Stream filters: every `tag` given has to match."""
    both = await world.add(DAY, tags=[("topic", "scholarships"), ("audience", "graduate-students")])
    await world.add(DAY, tags=[("topic", "scholarships")])

    got = await stream(world, tag=["topic:scholarships", "audience:graduate-students"])
    assert got == [both]


async def test_a_range_of_days(world: World) -> None:
    """Stream filters: `from` and `to` bound the stream day, inclusive."""
    inside = [await world.add(date(2026, 11, d)) for d in (1, 7)]
    await world.add(date(2026, 10, 31))
    await world.add(date(2026, 11, 8))

    assert await stream(world, **{"from": "2026-11-01", "to": "2026-11-07"}) == inside[::-1]


@pytest.mark.parametrize("value", ["topic:weather", "weather", "colour:fees"])
async def test_an_unknown_tag(world: World, value: str) -> None:
    """Stream filters: an unknown tag is a 400 naming it."""
    async with world.client() as http:
        response = await http.get(STREAM, params={"tag": value})

    assert response.status_code == 400
    assert value in response.json()["detail"]


async def test_a_word_in_the_body(world: World) -> None:
    """Search: a two-character term found only in a six-year-old body is found."""
    term = chr(0x734E) + chr(0x5B78)
    old = await world.add(DAY - timedelta(days=6 * 365), body=f"x{term}y")
    await world.add(DAY)

    assert await stream(world, q=term) == [old]
    assert await stream(world, q=term, **{"in": "title"}) == []


@pytest.mark.parametrize("query", ["113-1", "(OR"])
async def test_characters_with_meaning_elsewhere(world: World, query: str) -> None:
    """Search: words are plain text, so syntax characters find themselves."""
    found = await world.add(DAY, title=f"plan {query} now")
    await world.add(DAY, title="plan 113 now")

    assert await stream(world, q=query) == [found]


async def test_a_long_query(world: World) -> None:
    """Search: eleven words are a 400."""
    async with world.client() as http:
        response = await http.get(STREAM, params={"q": " ".join("abcdefghijk")})

    assert response.status_code == 400
