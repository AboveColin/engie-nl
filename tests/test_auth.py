"""The Okta flows against a loopback Identity Engine."""

from __future__ import annotations

import base64
import hashlib
import time

import pytest

from aiohttp import web

from engie_nl import (
    EngieAuthError,
    EngieEmailCodeRequired,
    EngieMfaRequiredError,
    EngieNetworkError,
    EngieRateLimited,
    OktaAuth,
    TokenSet,
    make_pkce_pair,
)
from engie_nl.auth import (
    _answer_href,
    _authenticator_by_method,
    _authenticator_field,
    _authenticator_options,
    _interaction_code,
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


def test_a_token_response_without_a_usable_expiry_gets_an_hour() -> None:
    """Okta always sends expires_in; a value that will not parse must not kill the login."""
    now = 1_000_000.0
    for expires_in in ("soon", None, [3600]):
        ts = TokenSet.from_token_response({"access_token": "a", "expires_in": expires_in}, now=now)
        assert ts.expires_at == now + 3600.0
    assert TokenSet.from_token_response({"access_token": "a"}, now=now).expires_at == now + 3600.0


def test_from_dict_fills_in_what_a_half_written_store_left_out() -> None:
    rebuilt = TokenSet.from_dict({"access_token": "a"})
    assert rebuilt.refresh_token is None and rebuilt.expires_at == 0.0
    assert rebuilt.token_type == "Bearer" and rebuilt.scope is None and rebuilt.id_token is None


async def test_okta_auth_is_its_own_context_manager(server: FakeServer) -> None:
    async with OktaAuth(client_id="0oatest", issuer=f"{server.url}/oauth2/default",
                        org_url=server.url, timeout=5) as auth:
        assert auth.authorize_url == f"{server.url}/oauth2/default/v1/authorize"
        assert auth.token_url == f"{server.url}/oauth2/default/v1/token"
        assert auth.interact_url == f"{server.url}/oauth2/default/v1/interact"
        assert auth.idx_introspect_url == f"{server.url}/idp/idx/introspect"
        session = await auth._get_session()  # pylint: disable=protected-access
    assert session.closed


async def test_an_unreachable_org_is_a_network_error_not_a_login_failure() -> None:
    """Home Assistant retries a network error and stops the coordinator on an auth one."""
    auth = OktaAuth(client_id="0oatest", issuer="http://127.0.0.1:1/oauth2/default",
                    org_url="http://127.0.0.1:1", timeout=5)
    with pytest.raises(EngieNetworkError, match="interact request failed"):
        await auth.login(USERNAME, PASSWORD)
    with pytest.raises(EngieNetworkError, match="token request failed"):
        await auth.refresh(TokenSet(access_token="x", refresh_token=REFRESH, expires_at=0))
    await auth.close()


async def test_an_unreachable_idx_step_is_a_network_error(okta_ok: FakeServer, auth: OktaAuth) -> None:
    """Each step follows the href the last one advertised, so one step can be elsewhere."""
    okta_ok.json(
        "/idp/idx/introspect",
        idx_body(okta_ok.url, remediation("identify", "http://127.0.0.1:1", "/idp/idx/identify",
                                          [{"name": "identifier"}])),
        method="POST",
    )
    with pytest.raises(EngieNetworkError, match="IDX request failed"):
        await auth.login(USERNAME, PASSWORD)


async def test_an_idx_body_that_is_not_json_is_an_auth_error(okta_ok: FakeServer, auth: OktaAuth) -> None:
    """Okta serves its sign-in page as HTML when a request is not the one it expected."""
    okta_ok.handle("POST", "/idp/idx/introspect", lambda _r: web.Response(text="<html>sign in</html>"))
    with pytest.raises(EngieAuthError, match="non-JSON body"):
        await auth.login(USERNAME, PASSWORD)


async def test_an_introspect_without_identify_names_what_was_offered(
    okta_ok: FakeServer, auth: OktaAuth
) -> None:
    okta_ok.json("/idp/idx/introspect", idx_body(okta_ok.url), method="POST")
    with pytest.raises(EngieAuthError, match="did not offer the identify step"):
        await auth.login(USERNAME, PASSWORD)


async def test_a_remediation_without_an_href_is_an_auth_error(okta_ok: FakeServer, auth: OktaAuth) -> None:
    """Every step is driven by the href the last one gave; without it there is nowhere to go."""
    step = remediation("identify", okta_ok.url, "/idp/idx/identify", [{"name": "identifier"}])
    del step["href"]
    okta_ok.json("/idp/idx/introspect", idx_body(okta_ok.url, step), method="POST")
    with pytest.raises(EngieAuthError, match="carries no href"):
        await auth.login(USERNAME, PASSWORD)


async def test_an_idx_body_without_a_state_handle_is_an_auth_error(
    okta_ok: FakeServer, auth: OktaAuth
) -> None:
    """The state handle ties one step to the next; a body without one cannot be answered."""
    body = idx_body(okta_ok.url, remediation("identify", okta_ok.url, "/idp/idx/identify",
                                             [{"name": "identifier"}]))
    del body["stateHandle"]
    okta_ok.json("/idp/idx/introspect", body, method="POST")
    with pytest.raises(EngieAuthError, match="carries no stateHandle"):
        await auth.login(USERNAME, PASSWORD)


async def test_refresh_asks_for_the_scope_the_grant_has(okta_ok: FakeServer, auth: OktaAuth) -> None:
    """Asking for the full app scope on refresh is refused, an hour into every session."""
    granted = "offline_access email profile openid"
    await auth.refresh(TokenSet(access_token="old", refresh_token=REFRESH, expires_at=0, scope=granted))
    assert okta_ok.forms[-1]["scope"] == granted

    await auth.refresh(TokenSet(access_token="old", refresh_token=REFRESH, expires_at=0))
    assert "scope" not in okta_ok.forms[-1]


async def test_a_callback_without_a_code_is_an_auth_error(okta_ok: FakeServer, auth: OktaAuth) -> None:
    started = auth.begin_browser_login()
    with pytest.raises(EngieAuthError, match="carries no code"):
        await auth.finish_browser_login(f"{REDIRECT}?state={started.state}", started)


async def test_a_bare_code_is_exchanged_without_a_state_check(okta_ok: FakeServer, auth: OktaAuth) -> None:
    """A user who pastes only the code, because the browser showed nothing else."""
    started = auth.begin_browser_login()
    ts = await auth.finish_browser_login(CODE, started)
    assert ts.access_token == ACCESS
    assert okta_ok.forms[-1]["grant_type"] == "authorization_code"


async def test_a_server_error_from_the_token_endpoint_is_transient(
    okta_ok: FakeServer, auth: OktaAuth
) -> None:
    """A 5xx is Okta declining to answer now, not Okta rejecting the credentials."""
    okta_ok.json("/oauth2/default/v1/token", {"error": "internal"}, status=503, method="POST")
    with pytest.raises(EngieNetworkError) as err:
        await auth.refresh(TokenSet(access_token="old", refresh_token=REFRESH, expires_at=0))
    assert not isinstance(err.value, EngieAuthError)
    assert "503" in str(err.value)


async def test_a_non_json_token_body_is_an_auth_error(okta_ok: FakeServer, auth: OktaAuth) -> None:
    okta_ok.handle("POST", "/oauth2/default/v1/token", lambda _r: web.Response(text="Service Unavailable"))
    with pytest.raises(EngieAuthError, match="non-JSON body"):
        await auth.refresh(TokenSet(access_token="old", refresh_token=REFRESH, expires_at=0))


async def test_retry_after_is_read_when_it_is_a_number_and_ignored_when_it_is_not(
    okta_ok: FakeServer, auth: OktaAuth
) -> None:
    """Okta may send an HTTP-date instead of seconds; that is not a number of seconds."""
    stale = TokenSet(access_token="old", refresh_token=REFRESH, expires_at=0)

    okta_ok.handle("POST", "/oauth2/default/v1/token",
                   lambda _r: web.json_response({}, status=429, headers={"Retry-After": "120"}))
    with pytest.raises(EngieRateLimited) as err:
        await auth.refresh(stale)
    assert err.value.retry_after == 120.0

    okta_ok.handle("POST", "/oauth2/default/v1/token",
                   lambda _r: web.json_response({}, status=429,
                                                headers={"Retry-After": "Wed, 09 Sep 2026 13:00:00 GMT"}))
    with pytest.raises(EngieRateLimited) as err:
        await auth.refresh(stale)
    assert err.value.retry_after is None

    okta_ok.handle("POST", "/oauth2/default/v1/token", lambda _r: web.json_response({}, status=429))
    with pytest.raises(EngieRateLimited) as err:
        await auth.refresh(stale)
    assert err.value.retry_after is None


# --- the IDX readers, against the bodies Okta is known to send ---------------


def test_authenticator_field_skips_the_fields_that_are_not_the_picker() -> None:
    """The remediation carries stateHandle and the picker side by side."""
    picker = {"name": "authenticator", "type": "object", "options": []}
    step = {"name": "select-authenticator-authenticate", "value": [
        {"name": "stateHandle", "value": STATE_HANDLE}, "not a dict", picker]}
    idx = {"remediation": {"value": [step]}}
    assert _authenticator_field(idx) is picker

    without = {"remediation": {"value": [
        {"name": "select-authenticator-authenticate", "value": [{"name": "stateHandle"}]}]}}
    assert _authenticator_field(without) is None
    assert _authenticator_options(without) == []
    assert _authenticator_by_method(without, "email") is None


def test_authenticator_by_method_skips_an_option_it_cannot_answer() -> None:
    """Matched on methodType, not the label, because the label is Dutch on this org."""
    options = [
        "not a dict",
        {"label": "Email", "value": {"form": {"value": [
            {"name": "id", "value": EMAIL_AUTHENTICATOR_ID},
            {"name": "methodType", "value": "email"}]}}},
        {"label": "Password", "value": {"form": {"value": [
            {"name": "id", "value": 0},
            {"name": "methodType", "value": "password"}]}}},
    ]
    idx = {"remediation": {"value": [{"name": "select-authenticator-authenticate", "value": [
        {"name": "authenticator", "options": options}]}]}}
    assert _authenticator_by_method(idx, "email") == {"id": EMAIL_AUTHENTICATOR_ID, "methodType": "email"}
    # The password option's id is not a string, so there is nothing to send back.
    assert _authenticator_by_method(idx, "password") is None
    assert _authenticator_options(idx) == ["Email", "Password"]


def test_answer_href_says_so_when_there_is_nowhere_to_send_the_code() -> None:
    with pytest.raises(EngieAuthError, match="offered nowhere to send it"):
        _answer_href({"remediation": {"value": [{"name": "challenge-authenticator"}]}})
    with pytest.raises(EngieAuthError, match="offered nowhere to send it"):
        _answer_href({})


def test_interaction_code_skips_a_field_whose_value_is_not_a_code() -> None:
    success = {"successWithInteractionCode": {"value": [
        "not a dict",
        {"name": "grant_type", "value": "interaction_code"},
        {"name": "interaction_code", "value": ""},
        {"name": "interaction_code", "value": INTERACTION_CODE},
    ]}}
    assert _interaction_code(success) == INTERACTION_CODE


def test_interaction_code_reports_what_okta_asks_for_instead() -> None:
    """The password was accepted but the login is not finished; say what is left."""
    idx = {"remediation": {"value": [{"name": "select-authenticator-enroll"}, "not a dict"]}}
    with pytest.raises(EngieAuthError, match="select-authenticator-enroll"):
        _interaction_code(idx)
    with pytest.raises(EngieAuthError, match="nothing this client understands"):
        _interaction_code({})
