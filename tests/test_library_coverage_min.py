# tests/test_library_coverage_min.py
# Purpose: Demonstrate coverage of libraries used by the system with
# small, stable tests through public APIs. Each test asserts one thing.

from urllib.parse import urlsplit
import idna
import ipaddress

from validators.uri import uri as validate_uri
from validators import domain, ValidationError
from validators.ip_address import ipv4, ipv6


def test_url_ipv6_host_parses_and_is_accepted():
    """Stdlib urlsplit parses; validator accepts via url() path."""
    s = "http://[2001:db8::1]/a?x=1#frag"
    _ = urlsplit(s)  # test stdlib without asserting on it
    assert validate_uri(s) is True


def test_domain_accepts_idna_punycode():
    """IDNA encodes Unicode domain to ACE; validator accepts the ACE form."""
    unicode_dom = "bücher.example"
    ascii_domain = idna.encode(unicode_dom).decode()
    assert domain(ascii_domain) is True


def test_domain_rejects_illegal_percent_in_label():
    """Validator rejects domains with illegal characters (e.g., '%')."""
    res = domain("exa%mple.com")
    assert res is not True and isinstance(res, ValidationError)


def test_ipv4_accepts_ipaddress_object():
    """Passing a pre-parsed IPv4Address exercises the object short-circuit path."""
    assert ipv4(ipaddress.IPv4Address("1.2.3.4")) is True


def test_ipv6_accepts_ipaddress_object():
    """Passing a pre-parsed IPv6Address exercises the object short-circuit path."""
    assert ipv6(ipaddress.IPv6Address("2001:db8::1")) is True