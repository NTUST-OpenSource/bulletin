"""What the service does when it starts, before it polls anything."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from psycopg import AsyncConnection


async def start(conn: AsyncConnection, seed: Path) -> None:
    """Apply pending migrations, then add the seed's boards that the registry does not hold."""
    raise NotImplementedError
