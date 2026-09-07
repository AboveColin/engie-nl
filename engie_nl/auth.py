"""Okta login for the ENGIE customer app, without a phone.

The app logs in with Okta's browser PKCE flow and then sends the resulting Okta
access token straight to the gateway as ``Authorization: Bearer``. Nothing is
exchanged. So this module has one job: obtain and refresh an Okta token pair
for the app's public client.

Three ways in, in the order to try them:

1. :meth:`OktaAuth.login`: username and password through Okta's classic Authn
   API, then ``/authorize`` with the returned ``sessionToken`` and PKCE. Works
   for any public client; fails with :class:`EngieMfaRequiredError` when the
   account has a second factor.
2. :meth:`OktaAuth.password_grant`: the resource owner password grant. The
   Okta org lists it; whether this client has it enabled is unknown until
   tried. One request answers.
3. :meth:`OktaAuth.begin_browser_login` and :meth:`OktaAuth.finish_browser_login`:
   the user opens the URL, logs in (MFA included), and pastes back the
   ``engie://login/okta/callback?code=...`` URL the browser could not open.

Refresh always goes through :meth:`OktaAuth.refresh` with the refresh token
(``offline_access`` is in the app's scope).
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import secrets
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import aiohttp

from .constants import (
    DEFAULT_TIMEOUT,
    OKTA_AUTHN_URL,
    OKTA_AUTHORIZE_URL,
    OKTA_CLIENT_ID,
    OKTA_ISSUER,
    OKTA_ORG_URL,
    OKTA_REDIRECT_URI,
    OKTA_SCOPE,
    OKTA_TOKEN_URL,
    TOKEN_REFRESH_MARGIN,
)
from ._http import SessionOwner, json_or_text
from .exceptions import EngieAuthError, EngieMfaRequiredError, EngieNetworkError


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def make_pkce_pair() -> tuple[str, str]:
    """Return ``(code_verifier, code_challenge)`` for S256."""
    verifier = _b64url(secrets.token_bytes(48))
    challenge = _b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


@dataclass
class TokenSet:
    """An Okta token pair plus the moment the access token stops working.

    ``expires_at`` is a Unix timestamp. Persist ``to_dict()`` and never the
    password; the refresh token is what keeps the session alive.
    """

    access_token: str
    refresh_token: str | None
    expires_at: float
    token_type: str = "Bearer"
    scope: str | None = None
    id_token: str | None = None

    @classmethod
    def from_token_response(cls, data: dict[str, Any], now: float | None = None) -> TokenSet:
        """Build from Okta's ``/v1/token`` body; ``expires_in`` becomes an absolute ``expires_at``."""
        access = data.get("access_token")
        if not isinstance(access, str) or not access:
            raise EngieAuthError("token response has no access_token")
        expires_in = data.get("expires_in")
        try:
            ttl = float(expires_in) if expires_in is not None else 3600.0
        except (TypeError, ValueError):
            ttl = 3600.0
        return cls(
            access_token=access,
            refresh_token=data.get("refresh_token") or None,
            expires_at=(now if now is not None else time.time()) + ttl,
            token_type=str(data.get("token_type") or "Bearer"),
            scope=data.get("scope") or None,
            id_token=data.get("id_token") or None,
        )

    def is_expired(self, margin: float = TOKEN_REFRESH_MARGIN, now: float | None = None) -> bool:
        """True when the access token is within ``margin`` seconds of ``expires_at``."""
        return (now if now is not None else time.time()) >= self.expires_at - margin

    def to_dict(self) -> dict[str, Any]:
        """A JSON-safe copy for a token store; the inverse of :meth:`from_dict`."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "token_type": self.token_type,
            "scope": self.scope,
            "id_token": self.id_token,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenSet:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            access_token=str(data["access_token"]),
            refresh_token=data.get("refresh_token") or None,
            expires_at=float(data.get("expires_at") or 0),
            token_type=str(data.get("token_type") or "Bearer"),
            scope=data.get("scope") or None,
            id_token=data.get("id_token") or None,
        )


@dataclass
class BrowserLogin:
    """What :meth:`OktaAuth.begin_browser_login` hands out.

    Open ``url`` in a browser. Keep ``verifier`` and ``state``; both are
    needed to finish. Neither is secret in the sense of a password, but the
    verifier is single-use and must match the challenge in ``url``.
    """

    url: str
    state: str
    verifier: str


class OktaAuth(SessionOwner):
    """Obtain and refresh Okta tokens for the ENGIE app's public client."""

    def __init__(
        self,
        session: aiohttp.ClientSession | None = None,
        *,
        client_id: str = OKTA_CLIENT_ID,
        issuer: str = OKTA_ISSUER,
        org_url: str = OKTA_ORG_URL,
        redirect_uri: str = OKTA_REDIRECT_URI,
        scope: str = OKTA_SCOPE,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(session, timeout)
        self.client_id = client_id
        self.issuer = issuer.rstrip("/")
        self.org_url = org_url.rstrip("/")
        self.redirect_uri = redirect_uri
        self.scope = scope

    # The defaults are module constants so a test can point one instance at a
    # loopback server; the URLs derive from issuer/org_url at call time.
    @property
    def authorize_url(self) -> str:
        """Okta's ``/v1/authorize`` for this issuer."""
        return OKTA_AUTHORIZE_URL if self.issuer == OKTA_ISSUER else f"{self.issuer}/v1/authorize"

    @property
    def token_url(self) -> str:
        """Okta's ``/v1/token`` for this issuer."""
        return OKTA_TOKEN_URL if self.issuer == OKTA_ISSUER else f"{self.issuer}/v1/token"

    @property
    def authn_url(self) -> str:
        """The org-level classic Authn API, ``/api/v1/authn``."""
        return OKTA_AUTHN_URL if self.org_url == OKTA_ORG_URL else f"{self.org_url}/api/v1/authn"

    async def __aenter__(self) -> OktaAuth:
        return self

    # --- flows -------------------------------------------------------------

    async def login(self, username: str, password: str) -> TokenSet:
        """Username and password through the Authn API, then PKCE with the session token."""
        session_token = await self.authn(username, password)
        verifier, challenge = make_pkce_pair()
        state = _b64url(secrets.token_bytes(16))
        code = await self._authorize_with_session_token(session_token, challenge, state)
        return await self.exchange_code(code, verifier)

    async def authn(self, username: str, password: str) -> str:
        """``POST /api/v1/authn``; returns Okta's one-time ``sessionToken``."""
        payload = {
            "username": username,
            "password": password,
            "options": {"multiOptionalFactorEnroll": False, "warnBeforePasswordExpired": False},
        }
        status, data = await self._post_json(self.authn_url, payload)
        code = _okta_error_code(data)
        detail = _okta_error_summary(data) or "no detail"
        # Okta answers E0000004 for a wrong password and for a locked or
        # deactivated account alike, on purpose, so that an attacker cannot
        # enumerate accounts. Naming the code is the only thing that lets the
        # reader tell a typo from a state a retry will never fix.
        if status == 401 or (status >= 400 and code == "E0000004"):
            raise EngieAuthError(f"Okta rejected the login (HTTP {status}, {code or 'no code'}): {detail}")
        if status >= 400:
            raise EngieAuthError(f"Okta authn failed (HTTP {status}, {code or 'no code'}): {detail}")
        tx_status = str(data.get("status") or "")
        if tx_status == "SUCCESS":
            token = data.get("sessionToken")
            if isinstance(token, str) and token:
                return token
            raise EngieAuthError("Okta authn succeeded without a sessionToken")
        if tx_status.startswith("MFA") or tx_status in ("PASSWORD_EXPIRED", "PASSWORD_WARN", "LOCKED_OUT"):
            factors = data.get("_embedded", {}).get("factors") if isinstance(data.get("_embedded"), dict) else None
            raise EngieMfaRequiredError(
                f"Okta needs more than a password for this account ({tx_status})",
                status=tx_status,
                factors=factors if isinstance(factors, list) else None,
            )
        raise EngieAuthError(f"Okta authn ended in unexpected status {tx_status!r}")

    async def _authorize_with_session_token(self, session_token: str, challenge: str, state: str) -> str:
        # Send no `prompt` parameter. With `prompt=none` Okta looks for an
        # existing browser SSO cookie and refuses with `login_required` before
        # it ever reads the sessionToken, which is the only session a scripted
        # client has. Measured against login.engie.nl on 2026-09-07.
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "sessionToken": session_token,
        }
        session = await self._get_session()
        try:
            async with session.get(
                self.authorize_url, params=params, allow_redirects=False, timeout=self._timeout
            ) as resp:
                location = resp.headers.get("Location")
                status = resp.status
                body = await resp.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise EngieNetworkError(f"Okta authorize request failed: {err}") from err
        if not location:
            raise EngieAuthError(f"Okta authorize did not redirect (HTTP {status}): {body[:200]}")
        return self._code_from_callback(location, expected_state=state)

    def begin_browser_login(self) -> BrowserLogin:
        """Build the authorize URL for a human to open; finish with :meth:`finish_browser_login`."""
        verifier, challenge = make_pkce_pair()
        state = _b64url(secrets.token_bytes(16))
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        return BrowserLogin(url=f"{self.authorize_url}?{urlencode(params)}", state=state, verifier=verifier)

    async def finish_browser_login(self, callback: str, login: BrowserLogin) -> TokenSet:
        """Exchange the pasted ``engie://login/okta/callback?code=...`` URL (or bare code)."""
        code = callback if "://" not in callback and "?" not in callback else self._code_from_callback(
            callback, expected_state=login.state
        )
        return await self.exchange_code(code, login.verifier)

    async def exchange_code(self, code: str, verifier: str) -> TokenSet:
        """Turn an authorization code and its PKCE verifier into a token pair."""
        return await self._token_request(
            {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "code": code,
                "code_verifier": verifier,
            }
        )

    async def password_grant(self, username: str, password: str) -> TokenSet:
        """Resource owner password grant. Raises :class:`EngieAuthError` if the client forbids it."""
        return await self._token_request(
            {
                "grant_type": "password",
                "client_id": self.client_id,
                "scope": self.scope,
                "username": username,
                "password": password,
            }
        )

    async def refresh(self, tokens: TokenSet) -> TokenSet:
        """Get a fresh access token. Okta may rotate the refresh token; keep the returned one."""
        if not tokens.refresh_token:
            raise EngieAuthError("no refresh token; log in again")
        new = await self._token_request(
            {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "scope": self.scope,
                "refresh_token": tokens.refresh_token,
            }
        )
        if new.refresh_token is None:
            new.refresh_token = tokens.refresh_token
        return new

    # --- plumbing ----------------------------------------------------------

    def _code_from_callback(self, url: str, *, expected_state: str | None) -> str:
        query = parse_qs(urlparse(url).query)
        if "error" in query:
            desc = query.get("error_description", [""])[0]
            raise EngieAuthError(f"Okta returned {query['error'][0]}: {desc}")
        code = query.get("code", [None])[0]
        if not code:
            raise EngieAuthError("callback URL carries no code")
        state = query.get("state", [None])[0]
        if expected_state is not None and state != expected_state:
            raise EngieAuthError("callback state does not match; start the login again")
        return code

    async def _token_request(self, form: dict[str, str]) -> TokenSet:
        session = await self._get_session()
        try:
            async with session.post(
                self.token_url,
                data=form,
                headers={"Accept": "application/json"},
                timeout=self._timeout,
            ) as resp:
                data = await json_or_text(resp)
                if resp.status >= 400:
                    err = data.get("error") if isinstance(data, dict) else None
                    desc = data.get("error_description") if isinstance(data, dict) else None
                    raise EngieAuthError(f"Okta token endpoint answered {resp.status}: {err or ''} {desc or ''}".strip())
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise EngieNetworkError(f"Okta token request failed: {err}") from err
        if not isinstance(data, dict):
            raise EngieAuthError("Okta token endpoint returned a non-JSON body")
        return TokenSet.from_token_response(data)

    async def _post_json(self, url: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        session = await self._get_session()
        try:
            async with session.post(
                url,
                json=payload,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=self._timeout,
            ) as resp:
                data = await json_or_text(resp)
                return resp.status, data if isinstance(data, dict) else {"_text": data}
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise EngieNetworkError(f"Okta request failed: {err}") from err


def _okta_error_code(data: dict[str, Any]) -> str | None:
    code = data.get("errorCode")
    return str(code) if code else None


def _okta_error_summary(data: dict[str, Any]) -> str | None:
    summary = data.get("errorSummary")
    causes = data.get("errorCauses")
    if isinstance(causes, list) and causes and isinstance(causes[0], dict):
        cause = causes[0].get("errorSummary")
        if cause:
            return f"{summary}: {cause}" if summary else str(cause)
    return str(summary) if summary else None
