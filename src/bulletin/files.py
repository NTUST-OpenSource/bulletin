"""Attachment sizes, and copies of small school files kept for a year."""

import asyncio
import hashlib
import re
from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from bulletin.tls import is_school

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from datetime import datetime
    from pathlib import Path

    from psycopg import AsyncConnection

    from bulletin.http import Fetch

# School files under this size are kept while their announcement is within the window.
MAX_KEPT = 5 * 2**20
FILE_WINDOW = timedelta(days=365)
CONTENT_RANGE = re.compile(r"bytes \d+-\d+/(\d+)")


def _never(_status: int, _headers: Mapping[str, str]) -> bool:
    return False


def _length(headers: Mapping[str, str]) -> int | None:
    value = headers.get("Content-Length", "")
    return int(value) if value.isdigit() else None


async def read_size(
    fetch: Fetch, url: str, keep: Callable[[int], bool]
) -> tuple[int | None, bytes | None]:
    """Read a school file's size without HEAD, and its content when `keep(size)` allows it.

    `/var/file/` links answer a GET for bytes 0 to 0 with the total in `Content-Range`.
    `downloadfile` links ignore `Range`, so their GET's `Content-Length` gives the size, and the
    body is read in the same request only when it is kept. Return the size, or None when the
    server does not say, and the content when it was read.
    """
    if "/var/file/" in urlsplit(url).path:
        response = await fetch(url, headers={"Range": "bytes=0-0"}, keep_body=_never)
        match = CONTENT_RANGE.fullmatch(response.headers.get("Content-Range", ""))
        if response.status == HTTPStatus.PARTIAL_CONTENT and match:
            return int(match.group(1)), None
        return _length(response.headers) if response.status == HTTPStatus.OK else None, None

    def keep_body(status: int, headers: Mapping[str, str]) -> bool:
        size = _length(headers)
        return status == HTTPStatus.OK and size is not None and keep(size)

    response = await fetch(url, keep_body=keep_body)
    if response.status != HTTPStatus.OK:
        return None, None
    size = _length(response.headers)
    return size, response.body if keep_body(response.status, response.headers) else None


class FileStore:
    """Files kept by SHA-256 digest under `root/<first two hex digits>/<digest>`."""

    def __init__(self, root: Path) -> None:
        """Keep files under `root`."""
        self.root = root

    def path(self, digest: str) -> Path:
        """Where the file with `digest` is kept."""
        return self.root / digest[:2] / digest

    def put(self, content: bytes) -> str:
        """Keep `content` once, written whole before it appears; return its digest."""
        digest = hashlib.sha256(content).hexdigest()
        path = self.path(digest)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            partial = path.with_suffix(".part")
            partial.write_bytes(content)
            partial.replace(path)
        return digest


async def keep_files(
    conn: AsyncConnection, fetch: Fetch, store: FileStore, announcement_id: int, now: datetime
) -> None:
    """Read the sizes of an announcement's attachments and keep copies of small school files.

    Only announcements first seen or listed within the last 365 days, and only attachments on
    the school's hosts, are requested; files under 5 MB are kept once per digest.
    """
    cur = await conn.execute(
        "SELECT f.id, f.url FROM attachment f"
        " JOIN announcement a ON f.revision_id = a.current_revision"
        " WHERE a.id = %s AND f.size IS NULL"
        " AND (a.first_seen_at > %s OR a.listed_on > %s::date) ORDER BY f.id",
        (announcement_id, now - FILE_WINDOW, now - FILE_WINDOW),
    )
    for attachment, url in await cur.fetchall():
        if not is_school(urlsplit(str(url)).hostname or ""):
            continue
        size, content = await read_size(fetch, url, lambda size: size < MAX_KEPT)
        if content is None and size is not None and size < MAX_KEPT:
            response = await fetch(url)
            content = response.body if response.status == HTTPStatus.OK else None
        digest = None if content is None else await asyncio.to_thread(store.put, content)
        await conn.execute(
            "UPDATE attachment SET size = %s, sha256 = %s WHERE id = %s",
            (size, digest, attachment),
        )


async def prune_files(conn: AsyncConnection, store: FileStore, now: datetime) -> int:
    """Delete kept files no announcement of the last 365 days links to; return how many."""
    raise NotImplementedError
