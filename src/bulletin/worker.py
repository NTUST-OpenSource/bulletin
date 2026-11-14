"""The loop that sends the most urgent request, one at a time, and what each request does."""

from typing import TYPE_CHECKING

from bulletin.archive import fetch_article

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from bulletin.http import Fetch
    from bulletin.schedule import Job


async def run_job(conn: AsyncConnection, fetch: Fetch, job: Job) -> None:
    """Do what a queued job asks, then remove it from the queue."""
    match job.kind:
        case "article" | "recheck":
            await fetch_article(conn, fetch, int(job.ref))
        case _:
            raise NotImplementedError(job.kind)
    await conn.execute("DELETE FROM job WHERE id = %s", (job.id,))
