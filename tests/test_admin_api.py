"""Requirement: Admin API access (tier-admin), and the admin API's routes."""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import httpx
import pytest

from bulletin.files import FileStore
from bulletin.registry import Board, get_board, import_seed
from bulletin.web.admin import admin_app
from bulletin.web.public import public_app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from contextlib import AbstractAsyncContextManager
    from pathlib import Path

    from fastapi import FastAPI
    from psycopg import AsyncConnection

TOKENS = {"example-token-owner": "owner"}
TIER = "/admin/boards/1053-1435/tier"


def client(app: FastAPI) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://admin")


def admin(conn: AsyncConnection) -> FastAPI:
    @asynccontextmanager
    async def connect() -> AsyncGenerator[AsyncConnection]:
        yield conn

    return admin_app(TOKENS, connect)


async def tier_of(conn: AsyncConnection) -> str:
    board = await get_board(conn, 1053, 1435)
    assert board is not None
    return board.tier


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"}, {"Authorization": "x"}])
async def test_missing_token(migrated: AsyncConnection, headers: dict[str, str]) -> None:
    """Admin API access: a request without a valid token gets 401 and changes nothing."""
    await import_seed(migrated, [Board(1053, 1435, "h", "u", "n", "announcement", "P2")])

    async with client(admin(migrated)) as http:
        response = await http.put(TIER, json={"tier": "P1"}, headers=headers)

    assert response.status_code == 401
    assert await tier_of(migrated) == "P2"


async def test_the_public_port(tmp_path: Path) -> None:
    """Admin API access: an admin path on the public port gets 404."""

    def no_database() -> AbstractAsyncContextManager[AsyncConnection]:
        raise AssertionError

    async with client(public_app(no_database, FileStore(tmp_path), "test")) as http:
        response = await http.put(TIER, json={"tier": "P1"})

    assert response.status_code == 404


async def test_routes_with_a_token(migrated: AsyncConnection) -> None:
    """Change a tier and Tier audit through the admin API, under the token holder's name."""
    await import_seed(migrated, [Board(1053, 1435, "h", "u", "n", "announcement", "P2")])
    auth = {"Authorization": "Bearer example-token-owner"}

    async with client(admin(migrated)) as http:
        changed = await http.put(TIER, json={"tier": "P1"}, headers=auth)
        unknown = await http.put("/admin/boards/1053-9/tier", json={"tier": "P1"}, headers=auth)
        bad_tier = await http.put(TIER, json={"tier": "P9"}, headers=auth)
        history = await http.get("/admin/boards/1053-1435/tier-changes", headers=auth)
        listed = await http.get("/admin/boards", params={"tier": "P1"}, headers=auth)

    assert (changed.status_code, unknown.status_code, bad_tier.status_code) == (204, 404, 422)
    assert [(c["old_tier"], c["new_tier"], c["changed_by"]) for c in history.json()] == [
        ("P2", "P1", "owner")
    ]
    assert [(b["site_id"], b["rcg"], b["tier"]) for b in listed.json()] == [(1053, 1435, "P1")]
