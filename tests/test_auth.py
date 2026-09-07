"""The Okta flows against a loopback Okta."""

from __future__ import annotations

import hashlib
import base64
import time

import pytest
from aiohttp import web

from engie_nl import EngieAuthError, EngieMfaRequiredError, OktaAuth, TokenSet, make_pkce_pair
from tests.conftest import ACCESS, CODE, PASSWORD, REDIRECT, REFRESH, USERNAME, FakeServer


def test_pkce_pair_is_s256() -> None:
    verifier, challenge = make_pkce_pair()
    digest = hashlib.sha256(verifier.encode()).digest()
    assert challenge == base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
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


async def test_login_authn_then_pkce(okta_ok: FakeServer, auth: OktaAuth) -> None:
    ts = await auth.login(USERNAME, PASSWORD)
    assert ts.access_token == ACCESS
    assert ts.refresh_token == REFRESH
    assert ts.expires_at > time.time()
    paths = [r.path for r in okta_ok.requests]
    assert paths == ["/api/v1/authn", "/oauth2/default/v1/authorize", "/oauth2/default/v1/token"]
    authorize = okta_ok.requests[1].query
    assert authorize["redirect_uri"] == REDIRECT
    assert "offline_access" in authorize["scope"]
    exchange = okta_ok.forms[-1]
    assert exchange["grant_type"] == "authorization_code"
    assert exchange["code"] == CODE
    # The verifier sent must hash to the challenge that was sent.
    digest = hashlib.sha256(exchange["code_verifier"].encode()).digest()
    assert authorize["code_challenge"] == base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


async def test_login_wrong_password(okta_ok: FakeServer, auth: OktaAuth) -> None:
    with pytest.raises(EngieAuthError):
        await auth.login(USERNAME, "fout")
    assert [r.path for r in okta_ok.requests] == ["/api/v1/authn"]


async def test_login_mfa_required(server: FakeServer, auth: OktaAuth) -> None:
    server.json(
        "/api/v1/authn",
        {"status": "MFA_REQUIRED", "_embedded": {"factors": [{"factorType": "sms"}]}},
        method="POST",
    )
    with pytest.raises(EngieMfaRequiredError) as err:
        await auth.login(USERNAME, PASSWORD)
    assert err.value.status == "MFA_REQUIRED"
    assert err.value.factors == [{"factorType": "sms"}]


async def test_authorize_error_in_location(okta_ok: FakeServer, auth: OktaAuth) -> None:
    okta_ok.json("/api/v1/authn", {"status": "SUCCESS", "sessionToken": "other"}, method="POST")
    with pytest.raises(EngieAuthError, match="login_required"):
        await auth.login(USERNAME, PASSWORD)


async def test_authorize_without_redirect(okta_ok: FakeServer, auth: OktaAuth) -> None:
    okta_ok.handle("GET", "/oauth2/default/v1/authorize", lambda _r: web.Response(text="<html>login</html>"))
    with pytest.raises(EngieAuthError, match="did not redirect"):
        await auth.login(USERNAME, PASSWORD)


async def test_browser_login_roundtrip(okta_ok: FakeServer, auth: OktaAuth) -> None:
    started = auth.begin_browser_login()
    assert started.url.startswith(f"{auth.issuer}/v1/authorize?")
    assert f"state={started.state}" in started.url
    callback = f"{REDIRECT}?code={CODE}&state={started.state}"
    ts = await auth.finish_browser_login(callback, started)
    assert ts.access_token == ACCESS


async def test_browser_login_rejects_foreign_state(okta_ok: FakeServer, auth: OktaAuth) -> None:
    started = auth.begin_browser_login()
    with pytest.raises(EngieAuthError, match="state"):
        await auth.finish_browser_login(f"{REDIRECT}?code={CODE}&state=nope", started)


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
