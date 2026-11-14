import os
from typing import TYPE_CHECKING

import pytest

from bulletin.migrate import migrate
from storage import Schema, database_url, throwaway_schema

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from psycopg import AsyncConnection


@pytest.fixture
async def schema() -> AsyncIterator[Schema]:
    async with throwaway_schema(database_url(os.environ)) as created:
        yield created


@pytest.fixture
async def db(schema: Schema) -> AsyncIterator[AsyncConnection]:
    async with await schema.connect() as conn:
        yield conn


@pytest.fixture
async def migrated(db: AsyncConnection) -> AsyncConnection:
    """A connection to a schema with every migration applied."""
    await migrate(db)
    return db
