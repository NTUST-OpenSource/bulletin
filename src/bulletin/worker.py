"""The loop that sends the most urgent request, one at a time, and what each request does."""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING

import aiohttp

from bulletin import archive, polllog
from bulletin.archive import fetch_article
from bulletin.backfill import queue_walks, walk
from bulletin.detection import detect, prune_frontier, record_frontier
from bulletin.discovery import discover, queue_discoveries
from bulletin.files import FileStore, keep_files, prune_files
from bulletin.http import Fetch, Response
from bulletin.pacer import Pacer
from bulletin.pages import PageError, list_url, parse_list
from bulletin.pointers import resolve_pointers
from bulletin.poller import poll_board
from bulletin.polllog import Entry, log_request
from bulletin.registry import get_board
from bulletin.schedule import MAX_BACKOFF, TAIPEI, Job, Poll, enqueue, mark_failed, next_request

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from psycopg import AsyncConnection

    from bulletin.http import KeepBody
    from bulletin.model import Listed

log = logging.getLogger(__name__)

# Seconds the whole queue waits after an HTTP 406 from the school's WAF.
WAF_PAUSE = 15 * 60
JOB_RETRY = timedelta(hours=1)
# The nightly cleanup runs on the first step of a day from this hour, Taipei time.
CLEANUP_HOUR = 3


@dataclass(frozen=True)
class Sent:
    """A request as the poll log records it."""

    at: datetime
    status: int | None
    size: int | None
    ms: int


def _ms_since(start: float) -> int:
    return round((time.monotonic() - start) * 1000)


class Paced:
    """A `Fetch` that waits for the pacer before each request and remembers every one it sent."""

    def __init__(self, fetch: Fetch, pacer: Pacer, now: Callable[[], datetime]) -> None:
        """Send through `fetch`, paced by `pacer`; `now` stamps each request."""
        self._fetch = fetch
        self._pacer = pacer
        self._now = now
        self.sent: list[Sent] = []

    async def __call__(
        self,
        url: str,
        /,
        *,
        headers: Mapping[str, str] | None = None,
        keep_body: KeepBody | None = None,
    ) -> Response:
        """Send one GET in the pacer's slot; an HTTP 406 pauses the whole queue."""
        async with self._pacer.slot():
            at, start = self._now(), time.monotonic()
            try:
                response = await self._fetch(url, headers=headers, keep_body=keep_body)
            except BaseException:
                self.sent.append(Sent(at, None, None, _ms_since(start)))
                raise
            self.sent.append(Sent(at, response.status, len(response.body), _ms_since(start)))
            if response.status == HTTPStatus.NOT_ACCEPTABLE:
                self._pacer.pause(WAF_PAUSE)
        return response


async def run_job(conn: AsyncConnection, fetch: Fetch, job: Job) -> bool:
    """Fetch the article an article, re-check or backfill job names, then remove the job.

    Return whether a page was stored.
    """
    match job.kind:
        case "article" | "recheck" | "backfill":
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
        await self.upkeep(conn)
        at = self.now()
        request = await next_request(conn, at)
        if request is None:
            return False
        paced = Paced(self.fetch, self.pacer, self.now)
        if isinstance(request, Poll):
            board = (request.site_id, request.rcg)
            changed, new = await self.poll(conn, paced, board, at)
            entries = [
                Entry("poll", s.at, s.status, s.size, s.ms, board, changed, tuple(new))
                if n == 0
                else Entry("poll", s.at, s.status, s.size, s.ms, board)
                for n, s in enumerate(paced.sent)
            ]
        else:
            await self.job(conn, paced, request, at)
            entries = [Entry(request.kind, s.at, s.status, s.size, s.ms) for s in paced.sent]
        for entry in entries:
            await log_request(conn, entry)
        return True

    async def poll(
        self, conn: AsyncConnection, fetch: Fetch, board: tuple[int, int], at: datetime
    ) -> tuple[bool | None, list[int]]:
        """Poll a board; return whether page 1 changed (None on failure) and the new ids."""
        found = await get_board(conn, *board)
        if found is None:
            return None, []

        async def read_page(page: int) -> list[Listed]:
            response = await fetch(list_url(found.host, *board, page))
            if response.status != HTTPStatus.OK:
                raise PageError(response.status)
            items = parse_list(response.text(), response.url, found.site_id)
            return await resolve_pointers(conn, fetch, items, at)

        new: list[int] = []

        async def detect_new(
            conn: AsyncConnection, board: tuple[int, int], items: Sequence[Listed], at: datetime
        ) -> None:
            new.extend(await detect(conn, board, items, at))

        try:
            changed = await poll_board(conn, board, read_page, at, detect_new)
        except (PageError, aiohttp.ClientError, TimeoutError) as error:
            log.warning("poll of %s-%s failed: %r", *board, error)
            await mark_failed(conn, *board, at)
            return None, []
        except Exception:
            # A page the parser or detection cannot handle must not be polled again at once.
            log.exception("poll of %s-%s failed", *board)
            await mark_failed(conn, *board, at)
            return None, []
        return changed, new

    async def job(self, conn: AsyncConnection, fetch: Fetch, job: Job, at: datetime) -> None:
        """Run a job; a failing one is tried again later, an hour at first, at most a day."""
        try:
            if job.kind == "attachment":
                await keep_files(conn, fetch, self.store, int(job.ref), at)
                await conn.execute("DELETE FROM job WHERE id = %s", (job.id,))
            elif job.kind == "discovery":
                await discover(conn, fetch, int(job.ref), at)
                await conn.execute("DELETE FROM job WHERE id = %s", (job.id,))
            elif job.kind == "backfill" and "-" in job.ref:
                # A board's walk, `<site>-<board>`; the others fetch an article.
                site, _, rcg = job.ref.partition("-")
                await walk(conn, fetch, (int(site), int(rcg)), at)
                await conn.execute("DELETE FROM job WHERE id = %s", (job.id,))
            elif await run_job(conn, fetch, job):
                await enqueue(conn, "attachment", job.ref, at)
        except Exception as error:  # noqa: BLE001 - a failing job must not stop the queue
            log.warning("%s job %s failed: %r", job.kind, job.ref, error)
            await conn.execute(
                "UPDATE job SET attempts = attempts + 1, last_error = %s,"
                " run_after = %s + LEAST(%s * power(2, attempts), %s) WHERE id = %s",
                (repr(error), at, JOB_RETRY, MAX_BACKOFF, job.id),
            )

    async def upkeep(self, conn: AsyncConnection) -> None:
        """Record the frontier on the first step of each hour; clean up once a night."""
        now = self.now()
        hour = now.replace(minute=0, second=0, microsecond=0)
        if hour != self.hour:
            await record_frontier(conn, hour)
            await prune_frontier(conn, now)
            await queue_walks(conn, now)
            await queue_discoveries(conn, now)
            self.hour = hour
        local = now.astimezone(TAIPEI)
        if local.hour >= CLEANUP_HOUR and local.date() != self.cleaned:
            await polllog.prune(conn, now)
            await archive.prune(conn, now)
            await prune_files(conn, self.store, now)
            self.cleaned = local.date()
