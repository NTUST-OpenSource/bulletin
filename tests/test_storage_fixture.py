"""Scaffolding: storage tests run on a throwaway schema of a real PostgreSQL."""

from typing import TYPE_CHECKING

import pytest

from storage import database_url

if TYPE_CHECKING:
    from psycopg import AsyncConnection

URL = "postgresql://user:password@localhost/bulletin"


def test_url_comes_from_the_environment() -> None:
    assert database_url({"BULLETIN_TEST_DATABASE_URL": URL}) == URL


def test_missing_url_skips() -> None:
    with pytest.raises(pytest.skip.Exception):
        database_url({})


def test_missing_url_fails_when_required() -> None:
    with pytest.raises(pytest.fail.Exception):
        database_url({"BULLETIN_REQUIRE_DB": "1"})


async def test_fixture_uses_an_empty_schema(db: AsyncConnection) -> None:
    cur = await db.execute(
        "SELECT current_schema(), count(*) FROM pg_tables WHERE schemaname = current_schema()"
    )
    row = await cur.fetchone()

    assert row is not None
    assert row[0].startswith("test_")
    assert row[1] == 0
