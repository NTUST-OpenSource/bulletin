"""Throwaway schemas on the test database for storage tests."""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from psycopg import AsyncConnection, sql

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Mapping

URL_VARIABLE = "BULLETIN_TEST_DATABASE_URL"
REQUIRE_VARIABLE = "BULLETIN_REQUIRE_DB"


def database_url(environ: Mapping[str, str]) -> str:
    """Return the test database URL; skip without one, or fail when CI requires it."""
    url = environ.get(URL_VARIABLE)
    if url:
        return url
    if environ.get(REQUIRE_VARIABLE) == "1":
        pytest.fail(f"{REQUIRE_VARIABLE}=1 but {URL_VARIABLE} is not set", pytrace=False)
    pytest.skip(f"{URL_VARIABLE} is not set")


@dataclass(frozen=True)
class Schema:
    """A schema of the test database that connections search first."""

    url: str
    name: str

    async def connect(self) -> AsyncConnection:
        """Open an autocommit connection whose search path starts at this schema."""
        return await AsyncConnection.connect(
            self.url, autocommit=True, options=f"-c search_path={self.name},public"
        )


@asynccontextmanager
async def throwaway_schema(url: str) -> AsyncGenerator[Schema]:
    """Create a new, empty schema and drop it with everything in it afterwards."""
    name = f"test_{uuid4().hex}"
    async with await AsyncConnection.connect(url, autocommit=True) as admin:
        await admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(name)))
        try:
            yield Schema(url, name)
        finally:
            await admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(name)))
