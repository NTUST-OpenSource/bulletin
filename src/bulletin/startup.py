"""What the service does when it starts, before it polls anything."""

from typing import TYPE_CHECKING

from bulletin.migrate import migrate
from bulletin.registry import import_seed, load_seed

if TYPE_CHECKING:
    from pathlib import Path

    from psycopg import AsyncConnection


async def start(conn: AsyncConnection, seed: Path) -> None:
    """Apply pending migrations, then add the seed's boards that the registry does not hold."""
    await migrate(conn)
    await import_seed(conn, load_seed(seed))
