"""The admin API: tier changes and board review, behind bearer tokens, on the admin listener."""

import hmac
from collections.abc import AsyncGenerator, Callable, Mapping
from contextlib import AbstractAsyncContextManager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, status
from psycopg import AsyncConnection
from pydantic import BaseModel

from bulletin.registry import (
    Board,
    Category,
    Pending,
    Tier,
    TierChange,
    accept,
    list_boards,
    pending_boards,
    set_tier,
    tier_history,
)

type Connect = Callable[[], AbstractAsyncContextManager[AsyncConnection]]

router = APIRouter(prefix="/admin")


def operator(request: Request, authorization: Annotated[str, Header()] = "") -> str:
    """Return the name of the bearer token's holder; refuse anyone else with 401."""
    scheme, _, token = authorization.partition(" ")
    tokens: Mapping[str, str] = request.app.state.tokens
    if scheme.lower() == "bearer" and token:
        for known, name in tokens.items():
            if hmac.compare_digest(known.encode(), token.encode()):
                return name
    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "a valid bearer token is required",
        {"WWW-Authenticate": "Bearer"},
    )


async def connection(request: Request) -> AsyncGenerator[AsyncConnection]:
    """A database connection for one request."""
    connect: Connect = request.app.state.connect
    async with connect() as conn:
        yield conn


def board_key(board: str) -> tuple[int, int]:
    """Read `<site>-<board>`; anything else is a board that does not exist."""
    site, _, rcg = board.partition("-")
    if not (site.isdigit() and rcg.isdigit()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"no board {board}")
    return int(site), int(rcg)


Operator = Annotated[str, Depends(operator)]
Conn = Annotated[AsyncConnection, Depends(connection)]


class TierChangeRequest(BaseModel):
    """The new tier of a board."""

    tier: Tier


class Review(BaseModel):
    """The operator's decision about a discovered board."""

    tier: Tier | None = None
    category: Category | None = None


@router.get("/boards")
async def boards(
    _: Operator, conn: Conn, *, tier: Tier | None = None, pending: bool | None = None
) -> list[Board]:
    """List the registry's boards."""
    return await list_boards(conn, tier=tier, pending=pending)


@router.get("/boards/pending")
async def pending(_: Operator, conn: Conn) -> list[Pending]:
    """List the boards pending review."""
    return await pending_boards(conn)


@router.put("/boards/{board}/tier", status_code=status.HTTP_204_NO_CONTENT)
async def change_tier(board: str, body: TierChangeRequest, by: Operator, conn: Conn) -> None:
    """Change a board's tier, recorded under the token holder's name."""
    try:
        await set_tier(conn, *board_key(board), body.tier, by=by)
    except LookupError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error


@router.get("/boards/{board}/tier-changes")
async def tier_changes(board: str, _: Operator, conn: Conn) -> list[TierChange]:
    """List a board's tier changes, newest first."""
    return await tier_history(conn, *board_key(board))


@router.post("/boards/{board}/review", status_code=status.HTTP_204_NO_CONTENT)
async def review(board: str, body: Review, by: Operator, conn: Conn) -> None:
    """Clear a board's review mark, with its tier or category."""
    try:
        await accept(conn, *board_key(board), tier=body.tier, category=body.category, by=by)
    except LookupError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error


def admin_app(tokens: Mapping[str, str], connect: Connect) -> FastAPI:
    """Build the admin app; `tokens` maps each bearer token to the name its changes record."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.tokens = dict(tokens)
    app.state.connect = connect
    app.include_router(router)
    return app
