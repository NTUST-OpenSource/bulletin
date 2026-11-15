"""Requirements of the public-api capability: caching, CORS, stored files, rate limit, OpenAPI."""

from datetime import date
from typing import TYPE_CHECKING
from urllib.parse import quote

import pytest

from bulletin.files import FileStore
from bulletin.model import Attachment
from world import World

if TYPE_CHECKING:
    from pathlib import Path

    from psycopg import AsyncConnection

DAY = date(2026, 11, 13)
STREAM = "/api/v1/announcements"
CACHED = "public, max-age=60, stale-while-revalidate=600"
PENDING = (AssertionError, KeyError, NotImplementedError)
PROXY = "172.20.0.2"  # nginx-proxy-manager on proxy-net
SCHOOL = "https://student.ntust.edu.tw/var/file/53/1053/attach"


@pytest.fixture
async def world(migrated: AsyncConnection, tmp_path: Path) -> World:
    created = World(migrated, tmp_path)
    await created.boards()
    return created


@pytest.mark.xfail(strict=True, raises=PENDING, reason="HTTP caching")
async def test_nothing_changed(world: World) -> None:
    """HTTP caching: repeating a stream request with its ETag gets a 304 without a body."""
    await world.add(DAY)
    async with world.client() as http:
        first = await http.get(STREAM)
        again = await http.get(STREAM, headers={"If-None-Match": first.headers["ETag"]})

    assert first.headers["Cache-Control"] == CACHED
    assert (again.status_code, again.content) == (304, b"")


@pytest.mark.xfail(strict=True, raises=PENDING, reason="HTTP caching")
async def test_a_new_event(world: World) -> None:
    """HTTP caching: after a new event the answer is 200 with a new ETag."""
    await world.add(DAY)
    async with world.client() as http:
        first = await http.get(STREAM)
        await world.add(DAY)
        again = await http.get(STREAM, headers={"If-None-Match": first.headers["ETag"]})

    assert again.status_code == 200
    assert again.headers["ETag"] != first.headers["ETag"]


@pytest.mark.xfail(strict=True, raises=PENDING, reason="HTTP caching")
@pytest.mark.parametrize("path", ["/api/v1/sites", "/api/v1/tags", "/api/v1/announcements/{id}"])
async def test_unchanged_content(world: World, path: str) -> None:
    """HTTP caching: sites, tags and an announcement answer 304 while their content stays."""
    announcement = await world.add(DAY)
    async with world.client() as http:
        first = await http.get(path.format(id=announcement))
        again = await http.get(
            path.format(id=announcement), headers={"If-None-Match": first.headers["ETag"]}
        )

    assert first.headers["Cache-Control"] == CACHED
    assert again.status_code == 304


@pytest.mark.xfail(strict=True, raises=PENDING, reason="HTTP caching")
@pytest.mark.parametrize("path", [f"{STREAM}?limit=0", f"{STREAM}/999999", "/api/v1/files/x/y"])
async def test_errors_are_not_cached(world: World, path: str) -> None:
    """HTTP caching: error answers are never cacheable."""
    async with world.client() as http:
        response = await http.get(path)

    assert response.status_code >= 400
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.xfail(strict=True, raises=PENDING, reason="CORS")
async def test_another_sites_page(world: World) -> None:
    """CORS: a GET from another origin is allowed from any origin."""
    async with world.client() as http:
        response = await http.get(STREAM, headers={"Origin": "https://example.org"})

    assert response.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.xfail(strict=True, raises=PENDING, reason="CORS")
async def test_a_preflight(world: World) -> None:
    """CORS: a preflight for a GET with If-None-Match is allowed."""
    headers = {
        "Origin": "https://example.org",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "if-none-match",
    }
    async with world.client() as http:
        response = await http.options(STREAM, headers=headers)

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert "if-none-match" in response.headers["Access-Control-Allow-Headers"].lower()


async def stored(world: World, name: str, content: bytes = b"%PDF-1.7") -> str:
    """An announcement whose one attachment, `name`, is in the store; return the file's path."""
    attachment = Attachment(name, f"{SCHOOL}/{len(world.ids)}", "module")
    await world.add(DAY, attachments=(attachment,))
    digest = FileStore(world.files).put(content)
    await world.conn.execute(
        "UPDATE attachment SET size = %s, sha256 = %s WHERE url = %s",
        (len(content), digest, attachment.url),
    )
    return f"/api/v1/files/{digest}/{quote(name, safe='')}"


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Stored files")
async def test_a_pdf(world: World) -> None:
    """Stored files: a PDF comes inline as application/pdf, named, cached as immutable."""
    path = await stored(world, "schedule.pdf")
    async with world.client() as http:
        response = await http.get(path)

    assert response.status_code == 200
    assert response.content == b"%PDF-1.7"
    assert response.headers["Content-Type"] == "application/pdf"
    assert response.headers["Content-Disposition"].startswith("inline;")
    assert "schedule.pdf" in response.headers["Content-Disposition"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "public, max-age=31536000, immutable"


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Stored files")
async def test_an_unexpected_type(world: World) -> None:
    """Stored files: a name outside the allow-list comes as an octet-stream attachment."""
    path = await stored(world, "page.html", b"<script>alert(1)</script>")
    async with world.client() as http:
        response = await http.get(path)

    assert response.headers["Content-Type"] == "application/octet-stream"
    assert response.headers["Content-Disposition"].startswith("attachment;")


async def test_a_pruned_file(world: World) -> None:
    """Stored files: a file the one-year window deleted is a 404."""
    path = await stored(world, "schedule.pdf")
    digest = path.split("/")[4]
    FileStore(world.files).path(digest).unlink()
    async with world.client() as http:
        response = await http.get(path)

    assert response.status_code == 404


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Stored files")
async def test_a_name_with_a_slash(world: World) -> None:
    """Stored files: a recorded name with `/`, percent-encoded in the path, is found."""
    path = await stored(world, "113/1 schedule.pdf")
    async with world.client() as http:
        response = await http.get(path)

    assert response.status_code == 200


async def test_another_name_or_digest(world: World) -> None:
    """Stored files: a name the digest was not recorded under, or a malformed digest, is 404."""
    path = await stored(world, "schedule.pdf")
    async with world.client() as http:
        renamed = await http.get(path.replace("schedule.pdf", "other.pdf"))
        malformed = await http.get("/api/v1/files/../schedule.pdf")

    assert (renamed.status_code, malformed.status_code) == (404, 404)


async def searches(world: World, count: int, peer: str, **headers: str) -> list[int]:
    """The statuses of `count` searches sent from `peer`."""
    async with world.client(peer) as http:
        return [
            (await http.get(STREAM, params={"q": f"w{n}"}, headers=headers)).status_code
            for n in range(count)
        ]


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Search rate limit")
async def test_too_many_searches(world: World) -> None:
    """Search rate limit: the 31st search within a minute through the proxy is a 429."""
    statuses = await searches(world, 30, PROXY, **{"X-Forwarded-For": "203.0.113.9"})
    async with world.client(PROXY) as http:
        refused = await http.get(
            STREAM, params={"q": "x"}, headers={"X-Forwarded-For": "203.0.113.9"}
        )

    assert set(statuses) == {200}
    assert refused.status_code == 429
    assert int(refused.headers["Retry-After"]) >= 1


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Search rate limit")
async def test_a_forged_private_address(world: World) -> None:
    """Search rate limit: an address written on the left of the proxy chain is not taken."""
    forged = {"X-Forwarded-For": "10.0.0.5, 203.0.113.9"}
    statuses = await searches(world, 31, PROXY, **forged)

    assert statuses[-1] == 429


@pytest.mark.xfail(strict=True, raises=PENDING, reason="Search rate limit")
async def test_an_ipv6_network(world: World) -> None:
    """Search rate limit: addresses of one IPv6 /64 share a limit."""
    await searches(world, 30, PROXY, **{"X-Forwarded-For": "2001:db8:1:2::1"})
    statuses = await searches(world, 1, PROXY, **{"X-Forwarded-For": "2001:db8:1:2::ffff"})

    assert statuses == [429]


async def test_an_internal_client(world: World) -> None:
    """Search rate limit: a client on proxy-net without a forwarded address is exempt."""
    assert set(await searches(world, 100, "172.20.0.7")) == {200}


async def test_browsing(world: World) -> None:
    """Search rate limit: requests without `q` are never limited."""
    async with world.client(PROXY) as http:
        statuses = {
            (await http.get(STREAM, headers={"X-Forwarded-For": "203.0.113.9"})).status_code
            for _ in range(100)
        }
        await searches(world, 30, PROXY, **{"X-Forwarded-For": "203.0.113.9"})
        browsing = await http.get(STREAM, headers={"X-Forwarded-For": "203.0.113.9"})

    assert statuses == {200}
    assert browsing.status_code == 200


@pytest.mark.xfail(strict=True, raises=PENDING, reason="API description")
async def test_the_description(world: World) -> None:
    """API description: openapi.json lists every endpoint with its parameters."""
    async with world.client() as http:
        described = (await http.get("/api/v1/openapi.json")).json()

    assert set(described["paths"]) == {
        "/announcements",
        "/announcements/{announcement}",
        "/events",
        "/sites",
        "/tags",
        "/files/{sha256}/{name}",
    }
    parameters = {p["name"] for p in described["paths"]["/announcements"]["get"]["parameters"]}
    assert parameters == {"site", "board", "tag", "from", "to", "q", "in", "cursor", "limit"}
