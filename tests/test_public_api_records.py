"""Requirements of the public-api capability: one announcement, events, sites and tags."""

from datetime import date
from typing import TYPE_CHECKING
from urllib.parse import quote

import pytest

from bulletin.events import read_after
from bulletin.files import FileStore
from bulletin.model import Attachment
from bulletin.registry import Board
from bulletin.units import units
from world import World, rendition

if TYPE_CHECKING:
    from pathlib import Path

    from psycopg import AsyncConnection

DAY = date(2026, 11, 13)
PENDING = (AssertionError, NotImplementedError)
PDF = Attachment(
    "113/1 schedule.pdf", "https://student.ntust.edu.tw/var/file/53/1053/a.pdf", "module"
)
LARGE = Attachment("photos.zip", "https://student.ntust.edu.tw/var/file/53/1053/b.zip", "module")


@pytest.fixture
async def world(migrated: AsyncConnection, tmp_path: Path) -> World:
    created = World(migrated, tmp_path)
    await created.boards()
    return created


async def keep(world: World, attachment: Attachment, content: bytes) -> str:
    """Store `content` as the attachment's file, as the worker does, and return its digest."""
    digest = FileStore(world.files).put(content)
    await world.conn.execute(
        "UPDATE attachment SET size = %s, sha256 = %s WHERE url = %s",
        (len(content), digest, attachment.url),
    )
    return digest


async def one(world: World, announcement: int) -> dict[str, object]:
    async with world.client() as http:
        response = await http.get(f"/api/v1/announcements/{announcement}")
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.xfail(strict=True, raises=PENDING, reason="One announcement")
async def test_attachments(world: World) -> None:
    """One announcement: a stored file has its path, a file that was not stored has null."""
    announcement = await world.add(
        DAY, body="text", rendition=rendition(markdown="**m**"), attachments=(PDF, LARGE)
    )
    digest = await keep(world, PDF, b"%PDF-1.7")
    await world.conn.execute("UPDATE attachment SET size = 7000000 WHERE url = %s", (LARGE.url,))

    got = await one(world, announcement)
    assert got["body_html"] == "<p>text</p>"
    assert got["rendition"] == {
        "title": "rewritten",
        "summary": "summary",
        "deadline": None,
        "markdown": "**m**",
    }
    assert got["attachments"] == [
        {
            "name": PDF.name,
            "url": PDF.url,
            "size": 8,
            "file": f"/api/v1/files/{digest}/{quote(PDF.name, safe='')}",
        },
        {"name": LARGE.name, "url": LARGE.url, "size": 7000000, "file": None},
    ]
    assert len(got["revisions"]) == 1  # type: ignore[arg-type]
    assert (got["cross_posts"], got["cross_post_of"]) == ([], None)


@pytest.mark.xfail(strict=True, raises=PENDING, reason="One announcement")
async def test_a_pruned_file(world: World) -> None:
    """One announcement: a file the one-year window deleted has a null path."""
    announcement = await world.add(DAY, attachments=(PDF,))
    digest = await keep(world, PDF, b"%PDF-1.7")
    FileStore(world.files).path(digest).unlink()

    got = await one(world, announcement)
    assert got["attachments"][0]["file"] is None  # type: ignore[index]


@pytest.mark.xfail(strict=True, raises=PENDING, reason="One announcement")
async def test_a_cross_posts_own_page(world: World) -> None:
    """One announcement: a cross-post names the announcement it copies, which lists it."""
    office = await world.add(DAY)
    copy = await world.cross_post(office, DAY)

    assert (await one(world, copy))["cross_post_of"] == office
    copies = (await one(world, office))["cross_posts"]
    assert [c["id"] for c in copies] == [copy]  # type: ignore[union-attr]


@pytest.mark.xfail(strict=True, raises=PENDING, reason="One announcement")
async def test_an_unknown_announcement(world: World) -> None:
    """One announcement: an unknown id is a 404."""
    async with world.client() as http:
        response = await http.get("/api/v1/announcements/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "no announcement 999999"}


async def events(world: World, after: int | None = None) -> dict[str, object]:
    async with world.client() as http:
        params = {} if after is None else {"after": after}
        response = await http.get("/api/v1/events", params=params)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Events feed")
async def test_resuming(world: World) -> None:
    """Events feed: asking after an id gives the later events, each with its announcement."""
    first = await world.add(DAY)
    second = await world.add(DAY, rendition=rendition())
    recorded = await read_after(world.conn, 0)
    after = recorded[0].id

    got = await events(world, after)
    assert [(e["kind"], e["announcement"]["id"]) for e in got["events"]] == [  # type: ignore[union-attr]
        ("published", second),
        ("rendered", second),
    ]
    assert got["last"] == recorded[-1].id
    assert first not in [e["announcement"]["id"] for e in got["events"]]  # type: ignore[union-attr]


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Events feed")
async def test_nothing_new(world: World) -> None:
    """Events feed: with nothing after `after`, the list is empty and the last id is `after`."""
    await world.add(DAY)
    last = (await read_after(world.conn, 0))[-1].id

    assert await events(world, last) == {"events": [], "last": last}


async def sites(world: World) -> list[dict[str, object]]:
    async with world.client() as http:
        response = await http.get("/api/v1/sites")
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Sites and boards")
async def test_an_academic_unit(world: World) -> None:
    """Sites and boards: a department is academic with its college, after the college's site."""
    await world.boards(
        [Board(1001, 1, "www.ceecs.ntust.edu.tw", "college", "news", "announcement", "P3")]
    )
    college = next(u.college for u in units() if u.site == 1017)

    listed = await sites(world)
    assert [s["id"] for s in listed] == [1045, 1053, 1001, 1017]
    ece = listed[3]
    assert (ece["kind"], ece["college"], ece["unit"], ece["host"]) == (
        "academic",
        college,
        "electronics",
        "ece.ntust.edu.tw",
    )
    assert (listed[0]["kind"], listed[0]["college"]) == ("all", None)


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Sites and boards")
async def test_an_excluded_board(world: World) -> None:
    """Sites and boards: excluded boards are not listed, nor sites with nothing else."""
    await world.boards([Board(1089, 1, "audit.ntust.edu.tw", "audit", "banner", "excluded", "off")])

    listed = await sites(world)
    ece = next(s for s in listed if s["id"] == 1017)
    assert ece["boards"] == [{"key": "1017-631", "name": "jobs", "category": "announcement"}]
    assert 1089 not in [s["id"] for s in listed]


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Sites and boards")
async def test_a_board_turned_off(world: World) -> None:
    """Sites and boards: a board turned off stays listed beside one that still polls."""
    await world.conn.execute("UPDATE board SET tier = 'off' WHERE site_id = 1053 AND rcg = 1436")

    student = next(s for s in await sites(world) if s["id"] == 1053)
    assert [b["key"] for b in student["boards"]] == ["1053-1435", "1053-1436"]  # type: ignore[union-attr]


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Sites and boards")
async def test_a_site_outside_the_unit_data(world: World) -> None:
    """Sites and boards: a site missing from the unit data is listed last, as admin."""
    await world.boards([Board(1999, 1, "new.ntust.edu.tw", "new", "news", "announcement", "P4")])

    listed = await sites(world)
    assert (listed[-1]["id"], listed[-1]["kind"]) == (1999, "admin")


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Tag taxonomy")
async def test_the_topics(world: World) -> None:
    """Tag taxonomy: four dimensions in order; topics allow several and include the library."""
    async with world.client() as http:
        dimensions = (await http.get("/api/v1/tags")).json()

    assert [(d["id"], d["several"]) for d in dimensions] == [
        ("topic", True),
        ("audience", True),
        ("nature", False),
        ("source", False),
    ]
    topics = dimensions[0]["tags"]
    assert len(topics) == 21
    assert {"id": "library", "label": chr(0x5716) + chr(0x66F8) + chr(0x9928)} in topics
