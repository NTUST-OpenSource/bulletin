"""The loop that sends the most urgent request, one at a time, and what each request does."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

from bulletin.archive import fetch_article
from bulletin.files import FileStore
from bulletin.http import Fetch
from bulletin.pacer import Pacer

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from bulletin.schedule import Job


async def run_job(conn: AsyncConnection, fetch: Fetch, job: Job) -> bool:
    """Do what an article or re-check job asks, then remove it; return whether a page was stored."""
    match job.kind:
        case "article" | "recheck":
            stored = await fetch_article(conn, fetch, int(job.ref))
        case _:
            raise NotImplementedError(job.kind)
    await conn.execute("DELETE FROM job WHERE id = %s", (job.id,))
    return stored


@dataclass
class Worker:
    """Sends the queue's requests through the pacer and does the hourly and nightly upkeep."""

    fetch: Fetch
    pacer: Pacer
    store: FileStore
    now: Callable[[], datetime]
    hour: datetime | None = None
    cleaned: date | None = None

    async def step(self, conn: AsyncConnection) -> bool:
        """Do the upkeep that is due, then send the most urgent request; return whether one was."""
        raise NotImplementedError
