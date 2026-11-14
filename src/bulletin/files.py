"""Attachment sizes, and copies of small school files kept for a year."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from bulletin.http import Fetch


async def read_size(
    fetch: Fetch, url: str, keep: Callable[[int], bool]
) -> tuple[int | None, bytes | None]:
    """Read a school file's size without HEAD, and its content when `keep(size)` allows it.

    Return the size, or None when the server does not say, and the content when it was read.
    """
    raise NotImplementedError
