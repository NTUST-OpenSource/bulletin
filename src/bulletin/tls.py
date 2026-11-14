"""TLS for the school's hosts, whose certificate chains Python's strict X.509 checks refuse."""

import ssl
from functools import cache
from importlib.resources import files

# TWCA's intermediate, which www.academic.ntust.edu.tw leaves out of its chain.
INTERMEDIATE = "twca-secure-ssl-ca.pem"


@cache
def school_context() -> ssl.SSLContext:
    """Verify certificates and host names, without the strict X.509 checks.

    Python 3.13 made `VERIFY_X509_STRICT` a default, and the school's certificates lack a Subject
    Key Identifier, which those checks refuse (checked on 2026-10-11). The context also holds
    TWCA's public intermediate, valid until 2030-10-16, for the host that does not send it.
    """
    context = ssl.create_default_context()
    context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    context.load_verify_locations(
        cadata=files("bulletin").joinpath(INTERMEDIATE).read_text("ascii")
    )
    return context


@cache
def default_context() -> ssl.SSLContext:
    """Python's default, strict verification."""
    return ssl.create_default_context()


def context_for(host: str) -> ssl.SSLContext:
    """Return the TLS context for requests to `host`: relaxed for `*.ntust.edu.tw` only."""
    if host == "ntust.edu.tw" or host.endswith(".ntust.edu.tw"):
        return school_context()
    return default_context()
