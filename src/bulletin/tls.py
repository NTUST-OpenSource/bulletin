"""TLS for the school's hosts, whose certificate chains Python's strict X.509 checks refuse."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ssl


def context_for(host: str) -> ssl.SSLContext:
    """Return the TLS context for requests to `host`."""
    raise NotImplementedError
