"""Requirement: School certificates (polling)."""

import hashlib
import ssl
import time
from importlib.resources import files

import pytest

from bulletin.tls import context_for

TWCA = "'TWCA Secure SSL Certification Authority'"


@pytest.mark.parametrize("host", ["www.academic.ntust.edu.tw", "student.ntust.edu.tw"])
def test_school_host_without_the_intermediate(host: str) -> None:
    """School certificates: only the strict flag is cleared, and TWCA's intermediate is bundled.

    The school's leaves lack a Subject Key Identifier, which the strict checks refuse, and
    www.academic leaves the intermediate out of its chain (checked 2026-10-11).
    """
    context = context_for(host)

    assert not context.verify_flags & ssl.VERIFY_X509_STRICT
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname
    assert any(TWCA in str(ca["subject"]) for ca in context.get_ca_certs())


@pytest.mark.parametrize("host", ["example.com", "ntust.edu.tw.example.com", "docs.google.com"])
def test_other_hosts_stay_strict(host: str) -> None:
    """School certificates: hosts outside the school keep the default strict verification."""
    context = context_for(host)

    assert context.verify_flags & ssl.VERIFY_X509_STRICT
    assert not any(TWCA in str(ca["subject"]) for ca in context.get_ca_certs())


def test_the_bundled_intermediate() -> None:
    """School certificates: the bundled certificate is TWCA's, valid for more than a year."""
    pem = files("bulletin").joinpath("twca-secure-ssl-ca.pem").read_text("ascii")
    block = pem[pem.index("-----BEGIN CERTIFICATE-----") :]
    context = ssl.create_default_context(cadata=block)
    [cert] = [ca for ca in context.get_ca_certs() if TWCA in str(ca["subject"])]

    # The certificate student.ntust.edu.tw sends after its own, as of 2026-10-11.
    assert hashlib.sha256(ssl.PEM_cert_to_DER_cert(block)).hexdigest() == (
        "1a2c75fd096e0499e9ff6ac74e526f61eaae3edfc8c2ea4436fee0c24d8b7d0e"
    )
    # It expires on 2030-10-16; replace it before then.
    assert ssl.cert_time_to_seconds(str(cert["notAfter"])) - time.time() > 365 * 86400
