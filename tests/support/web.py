"""A fake web for the collector's fetches: recorded answers by URL, every request remembered."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from bulletin.http import Response

if TYPE_CHECKING:
    from collections.abc import Mapping

    from bulletin.http import KeepBody


@dataclass
class Answer:
    status: int
    headers: dict[str, str] = field(default_factory=dict[str, str])
    body: bytes = b""


@dataclass
class Request:
    url: str
    headers: dict[str, str]
    body_read: bool


@dataclass
class FakeWeb:
    answers: dict[str, Answer]
    requests: list[Request] = field(default_factory=list[Request])

    async def __call__(
        self,
        url: str,
        /,
        *,
        headers: Mapping[str, str] | None = None,
        keep_body: KeepBody | None = None,
    ) -> Response:
        answer = self.answers[url]
        read = keep_body is None or keep_body(answer.status, answer.headers)
        self.requests.append(Request(url, dict(headers or {}), read))
        return Response(url, answer.status, answer.headers, answer.body if read else b"")
