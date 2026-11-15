"""The service: its settings, and both listeners and the worker running together."""

import asyncio
import json
import socket
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import quote

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from bulletin.archive import publish, revise
from bulletin.migrate import migrate
from bulletin.model import Content, Listed
from bulletin.model_api import ModelConfig
from bulletin.service import Settings, serve

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable

    from storage import Schema

CHECK = Path(__file__).parents[1] / "tools" / "discord-markdown" / "check.mjs"

TOKEN = "0123456789abcdef" * 4


def test_settings_from_the_environment(tmp_path: Path) -> None:
    """Admin API access: tokens come as `name:token` pairs; short tokens are refused."""
    env = {
        "BULLETIN_DATABASE_URL": "postgresql://db/bulletin",
        "BULLETIN_ADMIN_TOKENS": f"owner:{TOKEN}, ci:{TOKEN[::-1]}",
        "BULLETIN_ADMIN_HOST": "bulletin-internal-admin",
        "BULLETIN_FILES": str(tmp_path),
    }

    settings = Settings.from_env(env)

    assert settings.admin_tokens == {TOKEN: "owner", TOKEN[::-1]: "ci"}
    assert (settings.admin_host, settings.files) == ("bulletin-internal-admin", tmp_path)
    assert Settings.from_env({"BULLETIN_DATABASE_URL": "u"}).admin_tokens == {}
    with pytest.raises(ValueError, match="BULLETIN_DATABASE_URL"):
        Settings.from_env({})
    with pytest.raises(ValueError, match="BULLETIN_ADMIN_TOKENS"):
        Settings.from_env({"BULLETIN_DATABASE_URL": "u", "BULLETIN_ADMIN_TOKENS": "owner:short"})
    with pytest.raises(ValueError, match="BULLETIN_ADMIN_TOKENS"):
        Settings.from_env({"BULLETIN_DATABASE_URL": "u", "BULLETIN_ADMIN_TOKENS": TOKEN})


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


async def get(
    session: aiohttp.ClientSession, running: asyncio.Task[None], url: str, **headers: str
) -> int:
    """GET `url` once the service listens; a service that ended raises its error here."""
    for _ in range(100):
        if running.done():
            running.result()
        try:
            async with session.get(url, headers=headers) as response:
                return response.status
        except aiohttp.ClientConnectionError:
            await asyncio.sleep(0.1)
    raise TimeoutError(url)


def settings_for(schema: Schema, tmp_path: Path, model: ModelConfig | None = None) -> Settings:
    """Settings for a service on `schema` with free ports and one excluded board."""
    seed = tmp_path / "boards.json"
    board = {"site_id": 1053, "rcg": 1435, "host": "h", "unit": "u", "name": "n"}
    seed.write_text(json.dumps({"boards": [{**board, "category": "excluded", "tier": "off"}]}))
    options = quote(f"-c search_path={schema.name},public")
    return Settings(
        f"{schema.url}?options={options}",
        {TOKEN: "owner"},
        public_host="127.0.0.1",
        public_port=free_port(),
        admin_port=free_port(),
        files=tmp_path / "files",
        seed=seed,
        model=model or ModelConfig(),
        discord_check=CHECK,
    )


async def test_the_service_serves_and_stops(schema: Schema, tmp_path: Path) -> None:
    """Both listeners answer while the worker runs; setting `stop` ends all three."""
    settings = settings_for(schema, tmp_path)
    stop = asyncio.Event()
    running = asyncio.create_task(serve(settings, stop))

    async with aiohttp.ClientSession() as session:
        public = f"http://127.0.0.1:{settings.public_port}"
        admin = f"http://127.0.0.1:{settings.admin_port}/admin/boards"
        assert await get(session, running, f"{public}/health") == 200
        assert await get(session, running, f"{public}/admin/boards") == 404
        assert await get(session, running, admin) == 401
        assert await get(session, running, admin, Authorization=f"Bearer {TOKEN}") == 200
    stop.set()
    await asyncio.wait_for(running, 10)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="Model configuration")
def test_model_settings_from_the_environment() -> None:
    """Model configuration: the service reads the model's settings and the Discord check."""
    settings = Settings.from_env(
        {
            "BULLETIN_DATABASE_URL": "u",
            "BULLETIN_MODEL_KEYS": "a,b",
            "BULLETIN_DISCORD_CHECK": "/app/tools/discord-markdown/check.mjs",
        }
    )

    assert settings.model.keys == ("a", "b")
    assert str(settings.discord_check) == "/app/tools/discord-markdown/check.mjs"
    assert Settings.from_env({"BULLETIN_DATABASE_URL": "u"}).model == ModelConfig()


class Model:
    """A fake Gemini API that answers every request with one rendition of "b"."""

    def __init__(self) -> None:
        self.requests = 0

    async def answer(self, _: web.Request) -> web.Response:
        self.requests += 1
        tags: dict[str, object] = {"topic": [], "audience": [], "nature": "information"}
        tags["source"] = "on-campus"
        fields = {"title": "t", "markdown": "b", "summary": "s", "deadline": None, "tags": tags}
        text = json.dumps(fields)
        return web.json_response({"candidates": [{"content": {"parts": [{"text": text}]}}]})


@pytest.fixture
async def model() -> AsyncGenerator[tuple[Model, TestServer]]:
    fake = Model()
    app = web.Application()
    app.router.add_post("/v1beta/models/gemini-4-hydrogen:generateContent", fake.answer)
    running = TestServer(app, host="127.0.0.1")
    async with running:
        yield fake, running


async def pending_article(schema: Schema) -> None:
    """A stored article that waits for its rendition."""
    async with await schema.connect() as conn:
        await migrate(conn)
        listed = Listed(1000, "www.ntust.edu.tw", 1, None, "t", datetime.now(UTC).date())
        announcement = await publish(conn, listed, notify=True, late=False)
        await revise(conn, announcement, Content("t", "p", "<p>b</p>", "b"))


async def renditions(schema: Schema) -> list[tuple[str, bool]]:
    async with await schema.connect() as conn:
        cur = await conn.execute("SELECT markdown, fallback FROM rendition")
        return await cur.fetchall()


async def run_until(settings: Settings, done: Callable[[], Awaitable[bool]]) -> None:
    """Run the service until `done`, for at most ten seconds."""
    stop = asyncio.Event()
    running = asyncio.create_task(serve(settings, stop))
    async with aiohttp.ClientSession() as session:
        assert await get(session, running, f"http://127.0.0.1:{settings.public_port}/health") == 200
    for _ in range(100):
        if await done():
            break
        await asyncio.sleep(0.1)
    stop.set()
    await asyncio.wait_for(running, 10)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="Model configuration")
async def test_the_service_renders(
    schema: Schema, tmp_path: Path, model: tuple[Model, TestServer]
) -> None:
    """Model configuration: with keys, the service renders beside the worker."""
    fake, server = model
    await pending_article(schema)
    config = ModelConfig(keys=("k",), endpoint=str(server.make_url("/v1beta")))

    async def rendered() -> bool:
        return bool(await renditions(schema))

    await run_until(settings_for(schema, tmp_path, config), rendered)

    assert await renditions(schema) == [("b", False)]
    assert fake.requests == 1


async def test_no_keys(schema: Schema, tmp_path: Path, model: tuple[Model, TestServer]) -> None:
    """Model configuration: without keys the service runs and sends no rendering request."""
    fake, server = model
    await pending_article(schema)
    config = ModelConfig(endpoint=str(server.make_url("/v1beta")))
    started = asyncio.get_running_loop().time()

    async def a_second() -> bool:
        return asyncio.get_running_loop().time() - started > 1

    await run_until(settings_for(schema, tmp_path, config), a_second)

    assert await renditions(schema) == []
    assert fake.requests == 0
