"""The service: migrations and the seed at start, then both listeners and the worker in one loop."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncio

DATABASE_URL = "BULLETIN_DATABASE_URL"
ADMIN_TOKENS = "BULLETIN_ADMIN_TOKENS"
# Admin tokens are random strings of at least this many characters: `openssl rand -hex 32`.
MIN_TOKEN = 32


@dataclass(frozen=True)
class Settings:
    """What the service reads from its environment."""

    database_url: str
    # Bearer token -> the name its tier changes record.
    admin_tokens: Mapping[str, str] = field(default_factory=dict[str, str])
    public_host: str = "0.0.0.0"  # noqa: S104 - inside the container; proxy-net reaches it
    public_port: int = 8000
    admin_host: str = "127.0.0.1"
    admin_port: int = 8001
    files: Path = Path("/data/files")
    seed: Path = Path("seeds/boards.json")

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> Settings:
        """Read the settings; raise ValueError naming the variable that is missing or wrong."""
        raise NotImplementedError


async def serve(settings: Settings, stop: asyncio.Event) -> None:
    """Prepare the database, then serve and work until `stop` is set."""
    raise NotImplementedError
