"""The loop that sends the most urgent request, one at a time, and what each request does."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from psycopg import AsyncConnection

    from bulletin.http import Fetch
    from bulletin.schedule import Job


async def run_job(conn: AsyncConnection, fetch: Fetch, job: Job) -> None:
    """Do what a queued job asks, then remove it from the queue."""
    raise NotImplementedError
