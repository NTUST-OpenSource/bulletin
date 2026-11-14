import os
from typing import TYPE_CHECKING

import pytest

from storage import database_url, throwaway_schema

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from psycopg import AsyncConnection


@pytest.fixture
async def db() -> AsyncIterator[AsyncConnection]:
    async with throwaway_schema(database_url(os.environ)) as conn:
        yield conn
