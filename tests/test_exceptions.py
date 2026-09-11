"""What a caller can read off an error.

:attr:`EngieApiError.detail` is the one with work in it: the gateway has four
error formats and a Home Assistant repair message shows whichever arrived.
"""

from __future__ import annotations

from engie_nl import (
    EngieApiError,
    EngieAuthError,
    EngieError,
    EngieMfaRequiredError,
    EngieNetworkError,
    EngieRateLimited,
    EngieWriteBlocked,
)


def test_detail_reads_each_shape_the_gateway_sends() -> None:
    """All four measured on one account, 2026-09-07 and 2026-09-08."""
    assert EngieApiError("x", status=400, body={"message": "not-owned"}).detail == "not-owned"
    assert EngieApiError("x", status=500, body={"fault_string": "TechnicalError"}).detail == "TechnicalError"
    assert EngieApiError("x", status=400, body={"error_description": "bad scope"}).detail == "bad scope"
    assert EngieApiError("x", status=400, body={"error": "invalid_grant"}).detail == "invalid_grant"


def test_detail_flattens_a_laravel_validation_body() -> None:
    """/tariffs with no dates answers 422 and names every missing field."""
    body = {"message": "The given data was invalid.",
            "errors": {"date_from": ["date_from is required"], "date_to": "date_to is required"}}
    assert EngieApiError("x", status=422, body=body).detail == "date_from is required; date_to is required"


def test_detail_prefers_the_message_over_an_empty_errors_block() -> None:
    body = {"message": "not-owned", "errors": {}}
    assert EngieApiError("x", status=400, body=body).detail == "not-owned"


def test_detail_falls_back_to_the_raw_body_and_then_to_none() -> None:
    assert EngieApiError("x", status=502, body="Bad Gateway").detail == "Bad Gateway"
    assert EngieApiError("x", status=500, body=None).detail is None
    assert EngieApiError("x", status=500, body="").detail is None
    # A dict with none of the four keys, and a key whose value is not a string.
    assert EngieApiError("x", status=500, body={"unrelated": 1, "message": 7}).detail is None


def test_str_names_the_status_and_the_detail_when_there_is_one() -> None:
    with_detail = EngieApiError("GET /api/v1/user failed", status=404, body={"message": "no route"})
    assert str(with_detail) == "GET /api/v1/user failed (HTTP 404): no route"
    assert str(EngieApiError("GET /api/v1/user failed", status=404)) == "GET /api/v1/user failed (HTTP 404)"


def test_mfa_error_carries_what_okta_offered() -> None:
    err = EngieMfaRequiredError("pick one", status="MFA_REQUIRED", factors=[{"factorType": "Email"}])
    assert err.status == "MFA_REQUIRED" and err.factors == [{"factorType": "Email"}]
    assert EngieMfaRequiredError("pick one", status="MFA_ENROLL").factors == []


def test_rate_limit_is_transient_and_not_an_auth_failure() -> None:
    """Home Assistant stops the coordinator on an auth failure; a 429 must not do that."""
    err = EngieRateLimited("slow down", retry_after=60.0)
    assert isinstance(err, EngieNetworkError) and not isinstance(err, EngieAuthError)
    assert err.retry_after == 60.0
    assert EngieRateLimited("slow down").retry_after is None


def test_every_error_is_an_engie_error_and_keeps_its_message() -> None:
    """One except clause catches the package, and .message is the text as given."""
    for err in (EngieApiError("a", status=500), EngieAuthError("b"), EngieNetworkError("c"),
                EngieWriteBlocked("d"), EngieRateLimited("e"),
                EngieMfaRequiredError("f", status="MFA_REQUIRED")):
        assert isinstance(err, EngieError)
        assert err.message == str(err).split(" (HTTP ", maxsplit=1)[0]
