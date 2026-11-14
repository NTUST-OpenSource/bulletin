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
        if headers and "Range" in headers and answer.status == 200 and "/var/file/" in url:
            # /var/file/ honours a range for its first byte, as the school's servers do.
            total = len(answer.body)
            answer = Answer(206, {"Content-Range": f"bytes 0-0/{total}"}, answer.body[:1])
        read = keep_body is None or keep_body(answer.status, answer.headers)
        self.requests.append(Request(url, dict(headers or {}), read))
        return Response(url, answer.status, answer.headers, answer.body if read else b"")
