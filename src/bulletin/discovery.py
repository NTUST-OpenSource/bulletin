"""Re-discovery: each known site's site map, walked once a month for boards the registry lacks."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from psycopg import AsyncConnection

    from bulletin.http import Fetch
    from bulletin.registry import Found


def site_map_url(host: str, site_id: int) -> str:
    """A site's site map page."""
    return f"https://{host}/p/17-{site_id}.php"


def parse_site_map(page: str, url: str) -> list[Found]:
    """Read the boards a site map links to, in page order, each once, with its link text."""
    raise NotImplementedError


async def discover(
    conn: AsyncConnection, fetch: Fetch, site_id: int, at: datetime
) -> list[tuple[int, int]]:
    """Walk a site's site map and add the boards of known sites the registry lacks; return them."""
    raise NotImplementedError


async def queue_discoveries(conn: AsyncConnection, at: datetime) -> int:
    """Queue a walk of every site not walked in 30 days and not queued; return how many."""
    raise NotImplementedError
