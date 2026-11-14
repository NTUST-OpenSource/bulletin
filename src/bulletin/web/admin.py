"""The admin API: tier changes and board review, behind bearer tokens, on the admin listener."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from contextlib import AbstractAsyncContextManager

    from fastapi import FastAPI
    from psycopg import AsyncConnection

type Connect = Callable[[], AbstractAsyncContextManager[AsyncConnection]]


def admin_app(tokens: Mapping[str, str], connect: Connect) -> FastAPI:
    """Build the admin app; `tokens` maps each bearer token to the name its changes record."""
    raise NotImplementedError
