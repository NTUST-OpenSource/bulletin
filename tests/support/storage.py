"""Throwaway schemas on the test database for storage tests."""

from contextlib import asynccontextmanager
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


@asynccontextmanager
async def throwaway_schema(url: str) -> AsyncGenerator[AsyncConnection]:
    """Yield an autocommit connection whose search path starts at a new, empty schema."""
    schema = sql.Identifier(f"test_{uuid4().hex}")
    async with await AsyncConnection.connect(url, autocommit=True) as conn:
        await conn.execute(sql.SQL("CREATE SCHEMA {}").format(schema))
        try:
            await conn.execute(sql.SQL("SET search_path TO {}, public").format(schema))
            yield conn
        finally:
            await conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(schema))
