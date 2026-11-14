"""The service: migrations and the seed at start, then both listeners and the worker in one loop."""

import asyncio
import contextlib
import logging
import random
import time
from collections.abc import Generator, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import aiohttp
import uvicorn
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from bulletin.files import FileStore
from bulletin.http import Client
from bulletin.pacer import Pacer
from bulletin.startup import start
from bulletin.web.admin import admin_app
from bulletin.web.public import public_app
from bulletin.worker import Worker

log = logging.getLogger(__name__)

DATABASE_URL = "BULLETIN_DATABASE_URL"
ADMIN_TOKENS = "BULLETIN_ADMIN_TOKENS"
# Admin tokens are random strings of at least this many characters: `openssl rand -hex 32`.
MIN_TOKEN = 32
# Seconds between looks at a queue with nothing due.
IDLE = 10.0


@dataclass(frozen=True)
class Settings:
    """What the service reads from its environment."""

    database_url: str
    # Bearer token -> the name its tier changes record.
    admin_tokens: Mapping[str, str] = field(default_factory=dict[str, str])
    public_host: str = "0.0.0.0"  # noqa: S104 - inside the container; proxy-net reaches it
    public_port: int = 8000
    admin_host: str = "127.0.0.1"
    admin_port: int = 8001
    files: Path = Path("/data/files")
    seed: Path = Path("seeds/boards.json")

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> Settings:
        """Read the settings; raise ValueError naming the variable that is missing or wrong.

        `BULLETIN_ADMIN_TOKENS` holds comma-separated `name:token` pairs.
        """
        url = env.get(DATABASE_URL, "")
        if not url:
            msg = f"{DATABASE_URL} is not set"
            raise ValueError(msg)
        tokens: dict[str, str] = {}
        for pair in filter(None, (p.strip() for p in env.get(ADMIN_TOKENS, "").split(","))):
            name, _, token = pair.partition(":")
            if not name or len(token) < MIN_TOKEN:
                msg = f"{ADMIN_TOKENS} holds name:token pairs, tokens of {MIN_TOKEN}+ characters"
                raise ValueError(msg)
            tokens[token] = name
        defaults = cls(url)
        return cls(
            url,
            tokens,
            admin_host=env.get("BULLETIN_ADMIN_HOST", defaults.admin_host),
            files=Path(env.get("BULLETIN_FILES", str(defaults.files))),
            seed=Path(env.get("BULLETIN_SEED", str(defaults.seed))),
        )


class Listener(uvicorn.Server):
    """A uvicorn server that leaves signals to the service, which runs two of them."""

    @contextlib.contextmanager
    def capture_signals(self) -> Generator[None]:
        """Capture nothing."""
        yield


async def work(pool: AsyncConnectionPool[AsyncConnection], worker: Worker) -> None:
    """Step the worker forever; an empty queue or a failed step waits a little."""
    while True:
        try:
            async with pool.connection() as conn:
                busy = await worker.step(conn)
        except Exception:
            log.exception("worker step failed")
            busy = False
        if not busy:
            await asyncio.sleep(IDLE)


async def serve(settings: Settings, stop: asyncio.Event) -> None:
    """Prepare the database, then serve and work until `stop` is set."""
    pool = AsyncConnectionPool(
        settings.database_url,
        connection_class=AsyncConnection,
        kwargs={"autocommit": True},
        min_size=1,
        max_size=4,
        open=False,
    )
    async with pool:
        async with pool.connection() as conn:
            await start(conn, settings.seed)
        async with aiohttp.ClientSession() as session:
            worker = Worker(
                Client(session),
                Pacer(clock=time.monotonic, sleep=asyncio.sleep, random=random.random),
                FileStore(settings.files),
                lambda: datetime.now(UTC),
            )
            public = Listener(
                uvicorn.Config(public_app(), settings.public_host, settings.public_port)
            )
            admin = Listener(
                uvicorn.Config(
                    admin_app(settings.admin_tokens, pool.connection),
                    settings.admin_host,
                    settings.admin_port,
                )
            )
            async with asyncio.TaskGroup() as tasks:
                tasks.create_task(public.serve())
                tasks.create_task(admin.serve())
                working = tasks.create_task(work(pool, worker))
                await stop.wait()
                public.should_exit = admin.should_exit = True
                working.cancel()
