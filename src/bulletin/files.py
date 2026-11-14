"""Attachment sizes, and copies of small school files kept for a year."""

import re
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from bulletin.http import Fetch

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
