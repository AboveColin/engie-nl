"""The Okta flows against a loopback Identity Engine."""

from __future__ import annotations

import base64
import hashlib
import time

import pytest

from engie_nl import (
    EngieAuthError,
    EngieEmailCodeRequired,
    EngieMfaRequiredError,
    OktaAuth,
    TokenSet,
    make_pkce_pair,
)
from tests.conftest import (
    ACCESS,
    CODE,
    EMAIL_AUTHENTICATOR_ID,
    EMAIL_CODE,
    INTERACTION_CODE,
    PASSWORD,
    PASSWORD_AUTHENTICATOR_ID,
    REDIRECT,
    REFRESH,
    STATE_HANDLE,
    USERNAME,
    FakeServer,
    idx_body,
    remediation,
    select_authenticator,
)

IDX_STEPS = [
    "/oauth2/default/v1/interact",
    "/idp/idx/introspect",
    "/idp/idx/identify",
    "/idp/idx/challenge/answer",
    "/oauth2/default/v1/token",
]


def _challenge_of(verifier: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()


def test_pkce_pair_is_s256() -> None:
    verifier, challenge = make_pkce_pair()
    assert challenge == _challenge_of(verifier)
    assert 43 <= len(verifier) <= 128


def test_tokenset_roundtrip_and_expiry() -> None:
    now = 1_000_000.0
    ts = TokenSet.from_token_response({"access_token": "a", "refresh_token": "r", "expires_in": 3600}, now=now)
    assert ts.expires_at == now + 3600
    assert not ts.is_expired(now=now)
    assert ts.is_expired(now=now + 3600 - 30)  # inside the 60 s margin
    assert TokenSet.from_dict(ts.to_dict()) == ts


def test_tokenset_requires_access_token() -> None:
    with pytest.raises(EngieAuthError):
        TokenSet.from_token_response({"expires_in": 10})


async def test_login_walks_the_idx_flow(okta_ok: FakeServer, auth: OktaAuth) -> None:
    ts = await auth.login(USERNAME, PASSWORD)
    assert ts.access_token == ACCESS
    assert ts.refresh_token == REFRESH
    assert ts.expires_at > time.time()
    assert okta_ok.paths == IDX_STEPS

    interact = okta_ok.forms[0]
    assert interact["code_challenge_method"] == "S256"
    assert interact["redirect_uri"] == REDIRECT
    assert "offline_access" in interact["scope"]

    introspect, identify, answer = okta_ok.jsons
    assert introspect == {"interactionHandle": "ih-1"}
    assert identify == {"identifier": USERNAME, "stateHandle": STATE_HANDLE}
    assert answer == {"credentials": {"passcode": PASSWORD}, "stateHandle": STATE_HANDLE}

    exchange = okta_ok.forms[-1]
    assert exchange["grant_type"] == "interaction_code"
    assert exchange["interaction_code"] == INTERACTION_CODE
    # The verifier sent to /token must match the challenge sent to /interact.
    assert _challenge_of(exchange["code_verifier"]) == interact["code_challenge"]


async def test_login_never_touches_authorize(okta_ok: FakeServer, auth: OktaAuth) -> None:
    """Identity Engine serves HTML at /authorize, so the password flow must not go there."""
    await auth.login(USERNAME, PASSWORD)
    assert "/oauth2/default/v1/authorize" not in okta_ok.paths


async def test_login_wrong_password_reports_oktas_own_words(okta_ok: FakeServer, auth: OktaAuth) -> None:
    with pytest.raises(EngieAuthError, match="Authenticatie mislukt"):
        await auth.login(USERNAME, "fout")
    assert okta_ok.paths == IDX_STEPS[:4]


async def test_login_selects_the_password_authenticator_when_asked(
    okta_ok: FakeServer, auth: OktaAuth
) -> None:
    """Some accounts get the picker instead of the password challenge; pick Password."""
    base = okta_ok.url
    okta_ok.json("/idp/idx/identify", idx_body(base, select_authenticator(base, "Email", "Password")), method="POST")
    okta_ok.json(
        "/idp/idx/challenge",
        idx_body(base, remediation("challenge-authenticator", base, "/idp/idx/challenge/answer",
                                   [{"name": "credentials", "type": "object"}])),
        method="POST",
    )
    ts = await auth.login(USERNAME, PASSWORD)
    assert ts.access_token == ACCESS
    assert "/idp/idx/challenge" in okta_ok.paths
    select = okta_ok.jsons[2]
    assert select == {
        "authenticator": {"id": PASSWORD_AUTHENTICATOR_ID, "methodType": "password"},
        "stateHandle": STATE_HANDLE,
    }


async def test_login_without_a_password_option_raises_mfa(okta_ok: FakeServer, auth: OktaAuth) -> None:
    base = okta_ok.url
    okta_ok.json("/idp/idx/identify", idx_body(base, select_authenticator(base, "Email")), method="POST")
    with pytest.raises(EngieMfaRequiredError) as err:
        await auth.login(USERNAME, PASSWORD)
    assert err.value.factors == [{"factorType": "Email"}]
    assert "Email" in str(err.value)


async def test_login_with_no_usable_remediation_says_what_was_offered(
    okta_ok: FakeServer, auth: OktaAuth
) -> None:
    okta_ok.json("/idp/idx/identify", idx_body(okta_ok.url), method="POST")
    with pytest.raises(EngieAuthError, match="did not offer"):
        await auth.login(USERNAME, PASSWORD)


async def test_idx_400_without_a_message_is_still_a_failure(okta_ok: FakeServer, auth: OktaAuth) -> None:
    """A body Okta cannot parse answers 400 with no messages; that is not progress."""
    okta_ok.json("/idp/idx/challenge/answer", idx_body(okta_ok.url), status=400, method="POST")
    with pytest.raises(EngieAuthError, match="HTTP 400"):
        await auth.login(USERNAME, PASSWORD)


async def test_extra_step_after_the_password_is_named(okta_ok: FakeServer, auth: OktaAuth) -> None:
    """If Okta wants an enrollment after the password, say which one."""
    base = okta_ok.url
    okta_ok.json(
        "/idp/idx/challenge/answer",
        idx_body(base, remediation("select-authenticator-enroll", base, "/idp/idx/credential/enroll", [])),
        method="POST",
    )
    with pytest.raises(EngieAuthError, match="select-authenticator-enroll"):
        await auth.login(USERNAME, PASSWORD)


async def test_login_stops_on_the_email_code_after_sending_it(okta_mfa: FakeServer, auth: OktaAuth) -> None:
    """The real org's shape: password accepted, then a code that only the mailbox has."""
    with pytest.raises(EngieEmailCodeRequired) as err:
        await auth.login(USERNAME, PASSWORD)
    challenge = err.value.challenge
    assert challenge.answer_href.endswith("/idp/idx/challenge/answer")
    assert challenge.state_handle == STATE_HANDLE

    # login() must have asked Okta to send the mail before raising, or the user
    # would be told to read a code that was never sent.
    assert okta_mfa.jsons[-1] == {
        "authenticator": {"id": EMAIL_AUTHENTICATOR_ID, "methodType": "email"},
        "stateHandle": STATE_HANDLE,
    }

    ts = await auth.submit_email_code(challenge, f"  {EMAIL_CODE} ")
    assert ts.access_token == ACCESS
    exchange = okta_mfa.forms[-1]
    assert exchange["grant_type"] == "interaction_code"
    # The verifier must be the one from the first half, carried on the challenge.
    assert _challenge_of(exchange["code_verifier"]) == okta_mfa.forms[0]["code_challenge"]


async def test_wrong_email_code_reports_oktas_words(okta_mfa: FakeServer, auth: OktaAuth) -> None:
    with pytest.raises(EngieEmailCodeRequired) as err:
        await auth.login(USERNAME, PASSWORD)
    with pytest.raises(EngieAuthError, match="Ongeldige code"):
        await auth.submit_email_code(err.value.challenge, "000000")


async def test_email_code_required_is_an_auth_error(okta_mfa: FakeServer, auth: OktaAuth) -> None:
    """Callers that only catch EngieAuthError must not treat it as a crash."""
    with pytest.raises(EngieAuthError):
        await auth.login(USERNAME, PASSWORD)


async def test_interact_refusal_is_an_auth_error(okta_ok: FakeServer, auth: OktaAuth) -> None:
    okta_ok.json("/oauth2/default/v1/interact", {"error": "invalid_client"}, status=400, method="POST")
    with pytest.raises(EngieAuthError, match="refused to start a login"):
        await auth.login(USERNAME, PASSWORD)


async def test_browser_login_roundtrip(okta_ok: FakeServer, auth: OktaAuth) -> None:
    started = auth.begin_browser_login()
    assert started.url.startswith(f"{auth.issuer}/v1/authorize?")
    assert f"state={started.state}" in started.url
    ts = await auth.finish_browser_login(f"{REDIRECT}?code={CODE}&state={started.state}", started)
    assert ts.access_token == ACCESS


async def test_browser_login_rejects_foreign_state(okta_ok: FakeServer, auth: OktaAuth) -> None:
    started = auth.begin_browser_login()
    with pytest.raises(EngieAuthError, match="state"):
        await auth.finish_browser_login(f"{REDIRECT}?code={CODE}&state=nope", started)


async def test_browser_login_surfaces_an_error_callback(okta_ok: FakeServer, auth: OktaAuth) -> None:
    started = auth.begin_browser_login()
    callback = f"{REDIRECT}?error=access_denied&error_description=nope&state={started.state}"
    with pytest.raises(EngieAuthError, match="access_denied"):
        await auth.finish_browser_login(callback, started)


async def test_refresh_keeps_old_refresh_token_when_not_rotated(okta_ok: FakeServer, auth: OktaAuth) -> None:
    okta_ok.json("/oauth2/default/v1/token", {"access_token": "new", "expires_in": 60}, method="POST")
    ts = await auth.refresh(TokenSet(access_token="old", refresh_token=REFRESH, expires_at=0))
    assert ts.access_token == "new"
    assert ts.refresh_token == REFRESH


async def test_refresh_without_refresh_token(auth: OktaAuth) -> None:
    with pytest.raises(EngieAuthError, match="log in again"):
        await auth.refresh(TokenSet(access_token="x", refresh_token=None, expires_at=0))


async def test_password_grant_not_enabled(okta_ok: FakeServer, auth: OktaAuth) -> None:
    with pytest.raises(EngieAuthError, match="unsupported_grant_type"):
        await auth.password_grant(USERNAME, PASSWORD)
