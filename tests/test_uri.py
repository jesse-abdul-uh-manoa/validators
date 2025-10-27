# tests/test_uri.py
"""
Characterization tests for validators.uri

Purpose
-------
This suite records the *current* behavior of `validators.uri` so changes to the
implementation can be made safely later. These tests should all PASS today.

Conventions
-----------
- The `validators` package returns `True` on success and a `ValidationError`
  instance on failure (not literal False). For invalid cases, assert either:
  `result is not True` and/or `isinstance(result, ValidationError)`.
- `validators.uri.uri(...)` delegates to other validators for some schemes:
  - http/https/ftp → `validators.url.url`
  - mailto:        → `validators.email.email`
  - file:          → simple triple-slash check (no deep file path validation)
  - magnet:, tel:, data:, urn:, urc:, ipfs: → currently light/prefix checks
"""

# external
import pytest

# local
from validators import ValidationError
from validators.uri import uri as validate_uri  # import the *function*, not the module


# ------------------------------- URL delegation -------------------------------

@pytest.mark.parametrize(
    "value",
    [
        # A large representative set of URLs known to be accepted by url.py;
        # uri() should accept these as it delegates http/https/ftp to url().
        "http://foobar.dk",
        "http://foobar.museum/foobar",
        "http://fo.com",
        "http://FOO.com",
        "http://foo.com/blah_blah",
        "http://foo.com/blah_blah/",
        "http://foo.com/blah_blah_(wikipedia)",
        "http://foo.com/blah_blah_(wikipedia)_(again)",
        "http://www.example.com/wpstyle/?p=364",
        "https://www.example.com?bar=baz",
        "http://✪df.ws/123",
        "http://userid:password@example.com:8080",
        "http://userid:password@example.com:8080/",
        "http://userid@example.com",
        "http://userid@example.com/",
        "http://userid@example.com:8080",
        "http://userid@example.com:8080/",
        "http://userid:password@example.com",
        "http://userid:password@example.com/",
        "http://142.42.1.1/",
        "http://142.42.1.1:8080/",
        "http://➡.ws/䨹",
        "http://⌘.ws",
        "http://⌘.ws/",
        "http://foo.com/blah_(wikipedia)#cite-1",
        "http://foo.com/blah_(wikipedia)_blah#cite-1",
        "http://foo.com/unicode_(✪)_in_parens",
        "http://foo.com/(something)?after=parens",
        "http://☺.damowmow.com/",
        "http://code.google.com/events/#&product=browser",
        "http://j.mp",
        "ftp://foo.bar/baz",
        "http://foo.bar/?q=Test%20URL-encoded%20stuff",
        "http://مثال.إختبار",
        "http://例子.测试",
        "http://उदाहरण.परीक्षा",
        "http://www.😉.com",
        "http://😉.com/😁",
        "http://উদাহরণ.বাংলা",
        "http://xn--d5b6ci4b4b3a.xn--54b7fta0cc",
        "http://дом-м.рф/1/asdf",
        "http://xn----gtbybh.xn--p1ai/1/asdf",
        "http://1337.net",
        "http://a.b-c.de",
        "http://a.b--c.de/",
        "http://0.0.0.0",
        "http://224.1.1.1",
        "http://223.255.255.254",
        "http://10.1.1.0",
        "http://10.1.1.1",
        "http://10.1.1.254",
        "http://10.1.1.255",
        "http://127.0.0.1:8080",
        "http://127.0.10.150",
        "http://47.96.118.255:2333/",
        "http://[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80/index.html",
        "http://[1080:0:0:0:8:800:200C:417A]/index.html",
        "http://[3ffe:2a00:100:7031::1]",
        "http://[1080::8:800:200C:417A]/foo",
        "http://[::192.9.5.5]/ipng",
        "http://[::FFFF:129.144.52.38]:80/index.html",
        "http://[2010:836B:4179::836B:4179]",
        "http://foo.bar",
        "http://foo.bar/📍",
        "http://google.com:9/test",
        "http://5.196.190.0/",
        "http://username:password@example.com:4010/",
        "http://username:password@112.168.10.10:4010/",
        "http://base-test-site.local",
        "http://президент.рф/",
        "http://10.24.90.255:83/",
        "https://travel-usa.com/wisconsin/旅行/",
        "http://:::::::::::::@exmp.com",
        "http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com",
        "https://exchange.jetswap.finance/#/swap",
        "https://www.foo.com/bar#/baz/test",
        "https://matrix.to/#/!BSqRHgvCtIsGittkBG:talk.puri.sm/$1551464398853539kMJNP:matrix.org"
        "?via=talk.puri.sm&via=matrix.org&via=disroot.org",
        "https://example.org/path#2022%201040%20(Cornelius%20Morgan%20G).pdf",
    ],
)
def test_delegates_common_schemes_to_url_success(value: str):
    """URIs with http/https/ftp schemes are accepted via url() delegation."""
    assert validate_uri(value) is True


@pytest.mark.parametrize(
    "value",
    [
        # A representative set that url.py rejects; uri() should reject as well.
        "foobar.dk",
        "http://127.0.0/asdf",
        "http://foobar.d",
        "http://foobar.12",
        "htp://foobar.com",
        "http://foobar..com",
        "http://fo..com",
        "http://",
        "http://.",
        "http://..",
        "http://../",
        "http://?",
        "http://??",
        "http://??/",
        "http://#",
        "http://##",
        "http://##/",
        "http://foo.bar?q=Spaces should be encoded",
        "//",
        "//a",
        "///a",
        "///",
        "http:///a",
        "foo.com",
        "rdar://1234",
        "h://test",
        "http:// shouldfail.com",
        ":// should fail",
        "http://foo.bar/foo(bar)baz quux",
        "http://-error-.invalid/",
        "http://www.\ufffd.ch",
        "http://-a.b.co",
        "http://a.b-.co",
        "http://1.1.1.1.1",
        "http://123.123.123",
        "http://.www.foo.bar/",
        "http://www.foo.bar./",
        "http://.www.foo.bar./",
        "http://127.12.0.260",
        'http://example.com/">user@example.com',
        "http://[2010:836B:4179::836B:4179",          # missing bracket
        "http://2010:836B:4179::836B:4179",           # missing brackets
        "http://2010:836B:4179::836B:4179:80/index.html",
        "https://example.org?q=search');alert(document.domain);",
        # lenient-query shapes (accepted in some modes) — still rejected here
        "https://www.example.com/foo/?bar=baz&inga=42&quux",
        "https://foo.com/img/bar/baz.jpg?-62169987208",
        "https://foo.bar.net/baz.php?-/inga/test-lenient-query/",
        "https://example.com/foo/?bar#!baz/inga/8SA-M3as7A8",
        # Very long pathological inputs that url() guards against (ReDoS hardening)
        "http://0." + "00." * 60 + "00",  # synthetic repeated octets
        (
            "http://172.20.201.135-10.10.10.1656172.20.11.80-10."
            "10.10.1746172.16.9.13-192.168.17.68610.10.10.226-192."
            "168.17.64610.10.10.226-192.168.17.63610.10.10.226-192."
            "168.17.62610.10.10.226-192.168.17.61610.10.10.226-192."
            "168.17.60610.10.10.226-192.168.17.59610.10.10.226-192."
            "168.17.57610.10.10.226-192.168.17.56610.10.10.226-192."
            "168.17.55610.10.10.226-192.168.17.54610.10.10.226-192."
            "168.17.53610.10.10.226-192.168.17.52610.10.10.226-192."
            "168.17.51610.10.10.195-10.10.10.2610.10.10.194-192.168.17.685172.20.11.52-10.10."
            "10.195510.10.10.226-192.168.17.50510.10.10.186-172.20."
            "11.1510.10.10.165-198.41.0.54192.168.84.1-192.168.17."
            "684192.168.222.1-192.168.17.684172.20.11.52-10.10.10."
            "174410.10.10.232-172.20.201.198410.10.10.228-172.20.201."
            "1983192.168.17.135-10.10.10.1423192.168.17.135-10.10.10."
            "122310.10.10.224-172.20.201.198310.10.10.195-172.20.11."
            "1310.10.10.160-172.20.201.198310.10.10.142-192.168.17."
            "1352192.168.22.207-10.10.10.2242192.168.17.66-10.10.10."
            "1122192.168.17.135-10.10.10.1122192.168.17.129-10.10.10."
            "1122172.20.201.198-10.10.10.2282172.20.201.198-10.10.10."
            "2242172.20.201.1-10.10.10.1652172.20.11.2-10.10.10.1412172."
            "16.8.229-12.162.170.196210.10.10.212-192.168.22.133"
        ),
    ],
)
def test_delegates_common_schemes_to_url_fail(value: str):
    """URIs rejected by url() should be rejected via uri() delegation as well."""
    assert isinstance(validate_uri(value), ValidationError)


# --------------------------------- mailto: -----------------------------------

@pytest.mark.parametrize(
    "value",
    [
        # Valid mailboxes (mailto: delegates to email())
        "mailto:email@here.com",
        "mailto:weirder-email@here.and.there.com",
        "mailto:email@127.local.home.arpa",
        "mailto:example@valid-----hyphens.com",
        "mailto:example@valid-with-hyphens.com",
        "mailto:test@domain.with.idn.tld.उदाहरण.परीक्षा",
        "mailto:email@localhost.in",
        "mailto:Łókaść@email.com",
        "mailto:łemłail@here.com",
        "mailto:email@localdomain.org",
        'mailto:"\\\011"@here.com',
    ],
)
def test_mailto_validated_via_email_success(value: str):
    """mailto: is validated using `validators.email.email` and should accept these."""
    assert validate_uri(value) is True


@pytest.mark.parametrize(
    "value",
    [
        # Invalid mailboxes (mailto: delegates to email())
        None,
        "mailto:",
        "mailto:abc",
        "mailto:abc@",
        "mailto:abc@bar",
        "mailto:a @x.cz",  # unquoted space
        "mailto:abc@.com",
        "mailto:something@@somewhere.com",
        "mailto:email@127.0.0.1",
        "mailto:example@invalid-.com",
        "mailto:example@-invalid.com",
        "mailto:example@inv-.alid-.com",
        "mailto:example@inv-.-alid.com",
        # excessively long local part
        "mailto:john56789.john56789.john56789.john56789.john56789.john56789.john5@example.com",
        # quoted-string not allowed with raw CR
        'mailto:"test@test"@example.com',
        'mailto:"\\\012"@here.com',  # CR not allowed
        # Non-quoted space/semicolon not allowed
        "mailto:stephen smith@example.com",
        "mailto:stephen;smith@example.com",
    ],
)
def test_mailto_validated_via_email_fail(value):
    """mailto: invalid addresses should return a ValidationError via email()."""
    assert isinstance(validate_uri(value), ValidationError)


# ---------------------------------- file: ------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        # Current behavior: requires 'file:///' prefix; path contents are not deeply validated.
        "file:///folder/file_name.ext",
        r"file:///C:\Windows\folder\file.txt",
        "file:///linux/folder/file.sh",
    ],
)
def test_file_requires_triple_slash_success(value: str):
    """file: URIs with 'file:///' prefix are accepted."""
    assert validate_uri(value) is True


@pytest.mark.parametrize(
    "value",
    [
        # Missing or malformed triple slash after 'file:' should be rejected.
        "file:folder///file_name",
        "file://folder/file_name",
        "file:/test/filename",
        "file:/test/file name",
        "file::///test/file_name",
    ],
)
def test_file_requires_triple_slash_fail(value: str):
    """file: URIs without the required 'file:///' prefix are rejected."""
    assert isinstance(validate_uri(value), ValidationError)


# ---------------------------------- ipfs: ------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        # Current behavior: `ipfs:` is treated as a simple prefix check ("ipfs://").
        # No CID semantics are validated today.
        "ipfs://fec289aafcdab3194baec38/file_name.ext",
        "ipfs://fec289aafcdab3194baec38/file.txt",
        "ipfs://linux/folder/ipfs.sh",
    ],
)
def test_ipfs_prefix_check_success(value: str):
    """ipfs: URIs with 'ipfs://' prefix are accepted (no deeper checks today)."""
    assert validate_uri(value) is True


@pytest.mark.parametrize(
    "value",
    [
        # Missing or malformed slashes after the scheme are rejected by the simple prefix check.
        "ipfs:folder//ipfs_name",
        "ipfs:/test/ipfsname",
        "ipfs:://test/ipfs_name",
    ],
)
def test_ipfs_prefix_check_fail(value: str):
    """ipfs: URIs without a proper 'ipfs://' prefix are rejected."""
    assert isinstance(validate_uri(value), ValidationError)


# ------------------------------- light schemes -------------------------------

def test_magnet_accepts_any_query_right_now():
    """magnet: is accepted based on prefix with minimal query validation."""
    assert validate_uri("magnet:?this=is-not-actually-checked") is True


def test_tel_accepts_any_query_right_now():
    """tel: is accepted based on prefix with minimal number validation."""
    assert validate_uri("tel:this-is-not-actually-checked") is True


def test_data_accepts_any_query_right_now():
    """data: is accepted based on prefix; metadata/payload are not strictly validated."""
    assert validate_uri("data:this-is-not-actually-checked") is True


def test_urn_accepts_any_query_right_now():
    """urn: is accepted based on prefix; NID/NSS structure is not enforced yet."""
    assert validate_uri("urn:this-is-not-actually-checked") is True


def test_urc_accepts_any_query_right_now():
    """urc: is accepted based on prefix with no additional validation."""
    assert validate_uri("urc:this-is-not-actually-checked") is True
