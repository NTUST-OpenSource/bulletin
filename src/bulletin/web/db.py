"""The database connection each request of the web apps gets."""

from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager
from typing import Annotated

from fastapi import Depends, Request
from psycopg import AsyncConnection

type Connect = Callable[[], AbstractAsyncContextManager[AsyncConnection]]


async def connection(request: Request) -> AsyncGenerator[AsyncConnection]:
    """A database connection for one request."""
    connect: Connect = request.app.state.connect
    async with connect() as conn:
        yield conn


Conn = Annotated[AsyncConnection, Depends(connection)]
