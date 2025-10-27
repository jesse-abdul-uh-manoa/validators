# tests/test_range_of_inputs_min.py
"""
Range-of-inputs coverage for public validators, including adversarial cases.

Design principles
- One assertion per test for granular reporting and clear failure messages.
- Validators return True for valid inputs; for invalid inputs they return a
  ValidationError instance via the project's validator decorator.
- Known gaps in current behavior are captured with @pytest.mark.xfail(strict=True)
  so they are visible in reports without breaking the build. Remove xfail
  when the implementation tightens and the assertions begin to pass.
"""

import pytest
from validators import ValidationError, domain, email
from validators.uri import uri as validate_uri
from validators.ip_address import ipv4, ipv6


# ---------------------------- Benign inputs ----------------------------------

def test_url_benign_example():
    """Accept a typical HTTP URL with path, query, and fragment."""
    assert validate_uri("http://example.com/a?x=1#frag") is True


def test_email_benign_example():
    """Accept a standard mailbox address."""
    assert email("alice@example.com") is True


def test_domain_benign_example():
    """Accept a simple ASCII domain name."""
    assert domain("example.com") is True


def test_ipv4_benign_example():
    """Accept an IPv4 address from the TEST-NET-3 documentation block."""
    assert ipv4("203.0.113.10") is True


def test_ipv6_benign_example():
    """Accept an IPv6 address from the 2001:db8::/32 documentation prefix."""
    assert ipv6("2001:db8::1") is True


# ------------------------ Malicious / malformed inputs -----------------------

def test_url_space_in_host_invalid():
    """Reject a URL whose host contains a space character."""
    res = validate_uri("http://exa mple.com")
    assert res is not True and isinstance(res, ValidationError)


def test_domain_illegal_percent_invalid():
    """Reject a domain label containing an illegal '%'."""
    res = domain("exa%mple.com")
    assert res is not True and isinstance(res, ValidationError)


def test_email_null_byte_invalid():
    """Reject an email address containing a null byte in the domain part."""
    res = email("nul@�evil.com")
    assert res is not True and isinstance(res, ValidationError)


def test_ipv6_triple_colon_invalid_single():
    """Reject an IPv6 address with invalid triple-colon compression."""
    res = ipv6("2001:db8:::1")
    assert res is not True and isinstance(res, ValidationError)


# --------- Adversarial inputs currently accepted (desired rejections) --------
# Marked xfail to document desired behavior without failing current runs.

@pytest.mark.xfail(
    strict=True,
    reason="Percent-encoding should be enforced; uri() delegates without strict_query",
)
def test_url_bad_percent_escape_desired_rejection():
    """Bad percent-escape should be rejected once strict query checks are enforced."""
    assert validate_uri("http://example.com/%zz") is not True


@pytest.mark.xfail(strict=True, reason="magnet: xt should be required and nonempty")
def test_magnet_missing_xt_desired_rejection_missing_xt():
    """Missing 'xt' parameter in magnet URI should be rejected under stricter rules."""
    assert validate_uri("magnet:?dn=NoExactTopic") is not True


@pytest.mark.xfail(strict=True, reason="magnet: xt should be required and nonempty")
def test_magnet_missing_xt_desired_rejection_empty_xt():
    """Empty 'xt' parameter value in magnet URI should be rejected under stricter rules."""
    assert validate_uri("magnet:?xt=&dn=EmptyExactTopic") is not True


@pytest.mark.xfail(strict=True, reason="data: must enforce comma separator")
def test_data_missing_comma_desired_rejection():
    """Missing comma between metadata and payload should render data: URI invalid."""
    assert validate_uri("data:text/plain;base64SGVsbG8=") is not True