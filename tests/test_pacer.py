"""Requirement: Request budget (polling)."""

import asyncio

import pytest

from bulletin.pacer import Pacer


class FakeClock:
    """A clock that only moves when the code under test sleeps or a request takes time."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.now += max(seconds, 0)
        await asyncio.sleep(0)


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Request budget")
async def test_two_polls_due_at_once() -> None:
    """Request budget: the second request starts 2 s plus jitter after the first one finished."""
    clock = FakeClock()
    pacer = Pacer(clock=clock, sleep=clock.sleep, random=lambda: 0.5)
    spans: list[tuple[float, float]] = []

    async def request() -> None:
        async with pacer.slot():
            start = clock.now
            clock.now += 0.7  # the server takes its time
            await asyncio.sleep(0)
            spans.append((start, clock.now))

    await asyncio.gather(request(), request())

    (_, first_end), (second_start, _) = spans
    assert second_start - first_end == pytest.approx(2.5)
