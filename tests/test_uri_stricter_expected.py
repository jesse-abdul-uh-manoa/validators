# tests/test_uri_stricter_expected.py
"""
Stricter expectations for URI validation.

Overview
--------
This suite documents desired, stricter behavior for schemes that should have
structural validation beyond simple prefix checks. Where the current
implementation is known to be more permissive, tests are marked with
@pytest.mark.xfail(strict=True) so gaps are visible without breaking the run.

Scope
-----
The suite covers the following schemes and invariants:
- magnet: require at least one non-empty 'xt' parameter
- data:   enforce the comma separator between metadata and payload (and basic shape)
- urn:    require a valid NID and a non-empty NSS
- tel:    accept E.164-like shapes, reject alphabetic/punctuated forms
- ipfs:   (future) require identifiers to use valid multibase alphabets
- ipns:   (current) not implemented; should be rejected

Conventions
-----------
- Valid cases assert `validate_uri(value) is True`.
- Invalid cases assert `validate_uri(value) is not True` without relying on
  exact error messages (keeps tests stable across refactors).
- Only tests that *currently* fail are marked xfail; passing cases remain
  normal tests to avoid XPASS noise.

Maintenance
-----------
When stricter validation is implemented, remove xfail from the corresponding
tests. Keep the `stricter_expected` marker while tests are future-facing; drop
it when behavior is enforced by the implementation.
"""

import pytest
from validators import ValidationError
from validators.uri import uri as validate_uri  # import the function explicitly


# ------------------------------- magnet: -------------------------------------

@pytest.mark.stricter_expected
@pytest.mark.parametrize(
    "value",
    [
        # Common expectation: at least one 'xt' parameter with a nonempty URN.
        "magnet:?xt=urn:btih:abcdef1234567890&dn=Example",
        # Multiple 'xt' parameters occur in the wild and should remain acceptable.
        "magnet:?xt=urn:btih:abcdef1234567890&xt=urn:btih:1234&dn=Example",
    ],
    ids=["basic-with-xt", "multiple-xt"],
)
def test_magnet_accepts_xt_parameter(value):
    """Accept magnet URIs that provide one or more non-empty 'xt' parameters."""
    assert validate_uri(value) is True


@pytest.mark.stricter_expected
@pytest.mark.xfail(strict=True, reason="magnet: 'xt' must be present and nonempty")
@pytest.mark.parametrize(
    "value",
    [
        "magnet:?dn=NoExactTopic",        # missing xt
        "magnet:?xt=&dn=EmptyExactTopic", # empty xt
        "magnet:?xt=urn:btih:&dn=NoHash", # empty infohash after btih:
    ],
    ids=["missing-xt", "empty-xt", "empty-hash"],
)
def test_magnet_rejects_missing_or_empty_xt(value):
    """Reject magnet URIs that omit 'xt' or provide an empty value."""
    assert validate_uri(value) is not True


# -------------------------------- data: --------------------------------------

@pytest.mark.stricter_expected
@pytest.mark.parametrize(
    "value",
    [
        "data:text/plain,hello",                   # simple mediatype and data
        "data:text/plain;charset=utf-8,hello",     # parameterized mediatype
        "data:text/plain;base64,SGVsbG8=",         # base64 payload
        "data:;base64,SGVsbG8=",                   # default mediatype with base64
    ],
    ids=["simple", "charset", "base64", "default-mediatype"],
)
def test_data_uri_accepts_valid_shapes(value):
    """Accept well-formed data: URIs with proper metadata/payload separation."""
    assert validate_uri(value) is True


@pytest.mark.stricter_expected
@pytest.mark.xfail(strict=True, reason="data: must enforce comma separator and payload shape")
@pytest.mark.parametrize(
    "value",
    [
        "data:text/plain;base64SGVsbG8=",  # missing comma between metadata and payload
        "data:text/plain;bad=,hello",      # questionable/unsupported parameter shape
    ],
    ids=["missing-comma", "bad-parameter-shape"],
)
def test_data_uri_rejects_malformed_shapes(value):
    """Reject data: URIs that lack the comma separator or use malformed metadata."""
    assert validate_uri(value) is not True


# --------------------------------- urn: --------------------------------------

@pytest.mark.stricter_expected
@pytest.mark.parametrize(
    "value",
    [
        "urn:uuid:123e4567-e89b-12d3-a456-426655440000",  # UUID namespace
        "urn:ietf:rfc:2648",                              # IETF namespace example
    ],
    ids=["uuid", "ietf-rfc"],
)
def test_urn_accepts_valid_nid_and_nss(value):
    """Accept URNs with a valid NID and a non-empty NSS."""
    assert validate_uri(value) is True


@pytest.mark.stricter_expected
@pytest.mark.xfail(strict=True, reason="urn: NID must be valid; NSS must be nonempty")
@pytest.mark.parametrize(
    "value",
    [
        "urn::missingnid",  # empty nid
        "urn:1bad:thing",   # nid must start with a letter
        "urn:foo:",         # missing nss
    ],
    ids=["empty-nid", "bad-nid", "missing-nss"],
)
def test_urn_rejects_bad_nid_or_empty_nss(value):
    """Reject URNs with an invalid NID or an empty NSS."""
    assert validate_uri(value) is not True


# --------------------------------- tel: --------------------------------------

@pytest.mark.stricter_expected
@pytest.mark.parametrize(
    "value",
    [
        "tel:+14155552671",  # US example in basic E.164 format
        "tel:+81312345678",  # Japan example
    ],
    ids=["us-e164", "jp-e164"],
)
def test_tel_accepts_basic_e164_shapes(value):
    """Accept telephone URIs using a simple E.164-like format."""
    assert validate_uri(value) is True


@pytest.mark.stricter_expected
@pytest.mark.xfail(strict=True, reason="tel: subscriber number should be digits only in URI form")
@pytest.mark.parametrize(
    "value",
    [
        "tel:abc123",            # alphabetic characters not allowed in subscriber number
        "tel:+1(415)555-2671",   # punctuation not allowed at the URI layer
    ],
    ids=["letters", "punctuation"],
)
def test_tel_rejects_alphabetic_or_punctuated_numbers(value):
    """Reject telephone URIs that include letters or punctuation."""
    assert validate_uri(value) is not True


# -------------------------------- ipfs: --------------------------------------

@pytest.mark.stricter_expected
@pytest.mark.parametrize(
    "value",
    [
        "ipfs://bafybeigdyrzt",  # CIDv1-like example (placeholder shape)
    ],
    ids=["ipfs-cidv1"],
)
def test_ipfs_accepts_cid_like_identifier(value):
    """Accept ipfs: URIs that present a plausible CID identifier (future tightening expected)."""
    assert validate_uri(value) is True


@pytest.mark.stricter_expected
@pytest.mark.xfail(strict=True, reason="ipfs: identifier should use a valid multibase alphabet")
@pytest.mark.parametrize(
    "value",
    [
        "ipfs://%%%%",  # illegal characters for CID encodings
    ],
    ids=["bad-chars"],
)
def test_ipfs_rejects_illegal_identifier_characters(value):
    """Reject ipfs: URIs with characters outside accepted multibase alphabets."""
    assert validate_uri(value) is not True


# -------------------------------- ipns: --------------------------------------

@pytest.mark.stricter_expected
def test_ipns_is_unsupported_today():
    """
    Current contract: ipns is not implemented by validators.uri
    and should be rejected rather than silently accepted.
    """
    res = validate_uri("ipns://")
    assert res is not True and isinstance(res, ValidationError)
