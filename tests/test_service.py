"""The service: its settings, and both listeners and the worker running together."""

import asyncio
import json
import socket
from typing import TYPE_CHECKING
from urllib.parse import quote

import aiohttp
import pytest

from bulletin.service import Settings, serve

if TYPE_CHECKING:
    from pathlib import Path

    from storage import Schema

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


async def test_the_service_serves_and_stops(schema: Schema, tmp_path: Path) -> None:
    """Both listeners answer while the worker runs; setting `stop` ends all three."""
    seed = tmp_path / "boards.json"
    board = {"site_id": 1053, "rcg": 1435, "host": "h", "unit": "u", "name": "n"}
    seed.write_text(json.dumps({"boards": [{**board, "category": "excluded", "tier": "off"}]}))
    options = quote(f"-c search_path={schema.name},public")
    settings = Settings(
        f"{schema.url}?options={options}",
        {TOKEN: "owner"},
        public_host="127.0.0.1",
        public_port=free_port(),
        admin_port=free_port(),
        files=tmp_path / "files",
        seed=seed,
    )
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
