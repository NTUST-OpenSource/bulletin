"""Requirement "Keys in turn" of the rendering capability."""

import pytest

from bulletin.keys import KeyRing

KEYS = ("key-one-0123456789", "key-two-0123456789")


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Keys in turn")
def test_two_keys() -> None:
    """Keys in turn: three requests use the first, the second and the first key."""
    ring = KeyRing(KEYS, limit=10)

    assert [ring.take(now) for now in (0.0, 1.0, 2.0)] == [0, 1, 0]


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Keys in turn")
def test_a_resting_key() -> None:
    """Keys in turn: after a 429 on the first key, the second carries on until the window ends."""
    ring = KeyRing(KEYS, limit=10)
    assert ring.take(0.0) == 0
    ring.rest(0, 1.0)

    assert [ring.take(now) for now in (2.0, 3.0, 59.0)] == [1, 1, 1]
    assert ring.take(60.0) == 0


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Keys in turn")
def test_every_key_full() -> None:
    """Keys in turn: when every key is at its limit or rests, rendering waits for the first."""
    ring = KeyRing(KEYS, limit=1)
    assert ring.take(0.0) == 0
    assert ring.take(10.0) == 1
    ring.rest(1, 10.0)

    assert ring.take(20.0) is None
    assert ring.wait(20.0) == 40.0
    assert ring.take(60.0) == 0


@pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="Keys in turn")
def test_an_error_that_quotes_a_key() -> None:
    """Keys in turn: an error text shows the key hidden and URLs cut to their origins."""
    ring = KeyRing(KEYS, limit=10)
    text = (
        f"API key {KEYS[1]} is not valid at"
        f" https://generativelanguage.googleapis.com/v1beta/models/m?key={KEYS[0]}."
    )

    assert ring.hide(text) == (
        "API key ... is not valid at https://generativelanguage.googleapis.com"
    )
