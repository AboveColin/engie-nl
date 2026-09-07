"""Okta login for the ENGIE customer app, without a phone.

The app logs in with Okta's browser PKCE flow and then sends the resulting Okta
access token straight to the gateway as ``Authorization: Bearer``. Nothing is
exchanged. So this module has one job: obtain and refresh an Okta token pair
for the app's public client.

ENGIE runs Okta **Identity Engine** (`/.well-known/okta-organization` answers
``"pipeline":"idx"``). That rules out the classic trick of passing a
``sessionToken`` to ``/authorize``: Identity Engine ignores the parameter and
serves its sign-in page instead. The supported headless path is the interaction
code flow, and :meth:`OktaAuth.login` walks it:

1. ``POST /oauth2/default/v1/interact`` returns an interaction handle.
2. ``POST /idp/idx/introspect`` turns that into a state handle and the first
   remediation, which for this org is ``identify`` and asks only for the email.
3. ``POST /idp/idx/identify`` with the email offers ``challenge-authenticator``.
4. ``POST /idp/idx/challenge/answer`` with the password returns an interaction
   code, which ``/v1/token`` exchanges for the token pair.

Each step is driven by the ``href`` the previous response advertises, so an
extra step ENGIE adds later shows up as a named remediation rather than a
silent failure. An account that needs another authenticator stops with
:class:`EngieMfaRequiredError` naming what Okta offered.

Two other ways in remain:

- :meth:`OktaAuth.password_grant`: the resource owner grant. The org lists it;
  whether this client has it enabled is unverified. One request answers.
- :meth:`OktaAuth.begin_browser_login` and :meth:`OktaAuth.finish_browser_login`:
  the user opens the URL, logs in with any factor, and pastes back the
  ``engie://login/okta/callback?code=...`` URL the browser could not open.

Refresh always goes through :meth:`OktaAuth.refresh` with the refresh token
(``offline_access`` is in the app's scope).
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import aiohttp

from .constants import (
    DEFAULT_TIMEOUT,
    IDX_HEADERS,
    OKTA_CLIENT_ID,
    OKTA_ISSUER,
    OKTA_ORG_URL,
    OKTA_REDIRECT_URI,
    OKTA_SCOPE,
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
        """Okta's ``/v1/authorize``, used only by the browser flow."""
        return f"{self.issuer}/v1/authorize"

    @property
    def token_url(self) -> str:
        """Okta's ``/v1/token``."""
        return f"{self.issuer}/v1/token"

    @property
    def interact_url(self) -> str:
        """Identity Engine's ``/v1/interact``, which starts a login transaction."""
        return f"{self.issuer}/v1/interact"

    @property
    def idx_introspect_url(self) -> str:
        """Identity Engine's ``/idp/idx/introspect``, which returns the first remediation."""
        return f"{self.org_url}/idp/idx/introspect"

    async def __aenter__(self) -> OktaAuth:
        return self

    # --- flows -------------------------------------------------------------

    async def login(self, username: str, password: str) -> TokenSet:
        """Log in with an email and password through the Identity Engine."""
        verifier, challenge = make_pkce_pair()
        handle = await self._interact(challenge)
        idx = await self._idx_post(self.idx_introspect_url, {"interactionHandle": handle}, "introspect")
        idx = await self._remediate(idx, "identify", {"identifier": username})
        if _remediation(idx, "challenge-authenticator") is None:
            idx = await self._select_password(idx)
        idx = await self._remediate(idx, "challenge-authenticator", {"credentials": {"passcode": password}})
        return await self._token_request(
            {
                "grant_type": "interaction_code",
                "client_id": self.client_id,
                "interaction_code": _interaction_code(idx),
                "code_verifier": verifier,
            }
        )

    async def _interact(self, challenge: str) -> str:
        """Start an Identity Engine transaction and return its interaction handle."""
        form = {
            "client_id": self.client_id,
            "scope": self.scope,
            "redirect_uri": self.redirect_uri,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": _b64url(secrets.token_bytes(16)),
        }
        session = await self._get_session()
        try:
            async with session.post(
                self.interact_url, data=form, headers={"Accept": "application/json"}, timeout=self._timeout
            ) as resp:
                data = await json_or_text(resp)
                status = resp.status
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise EngieNetworkError(f"Okta interact request failed: {err}") from err
        if status >= 400 or not isinstance(data, dict) or not data.get("interaction_handle"):
            raise EngieAuthError(f"Okta refused to start a login (HTTP {status}): {str(data)[:200]}")
        return str(data["interaction_handle"])

    async def _idx_post(self, url: str, payload: dict[str, Any], step: str) -> dict[str, Any]:
        """POST one IDX step and return its body, raising unless the login moved on.

        A failed step still carries a full IDX body, so the status is what
        decides and the message only sharpens the wording. Measured on
        2026-09-07: a wrong password is expected to come back as 401 with the
        reason in ``messages``, while a body Okta cannot parse comes back as 400
        with no ``messages`` at all. Checking only for a message let that 400
        through as success.
        """
        session = await self._get_session()
        try:
            async with session.post(
                url, data=json.dumps(payload), headers=IDX_HEADERS, timeout=self._timeout
            ) as resp:
                data = await json_or_text(resp)
                status = resp.status
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise EngieNetworkError(f"Okta IDX request failed: {err}") from err
        if not isinstance(data, dict):
            raise EngieAuthError(f"Okta IDX returned a non-JSON body (HTTP {status}): {str(data)[:200]}")
        errors = _idx_messages(data)
        if errors:
            raise EngieAuthError(f"Okta refused the {step} step: {errors}")
        if status >= 400:
            raise EngieAuthError(f"Okta refused the {step} step with HTTP {status} and gave no reason")
        return data

    async def _remediate(self, idx: dict[str, Any], name: str, values: dict[str, Any]) -> dict[str, Any]:
        """Answer one named remediation, following the href that IDX advertised for it."""
        step = _remediation(idx, name)
        if step is None:
            raise self._cannot_continue(idx, name)
        href = step.get("href")
        if not isinstance(href, str) or not href:
            raise EngieAuthError(f"Okta remediation {name} carries no href")
        return await self._idx_post(href, {**values, "stateHandle": _state_handle(idx)}, name)

    async def _select_password(self, idx: dict[str, Any]) -> dict[str, Any]:
        """Pick the password authenticator when Okta asks which one to use."""
        authenticator_id = _password_authenticator_id(idx)
        if authenticator_id is None:
            raise self._cannot_continue(idx, "challenge-authenticator")
        return await self._remediate(
            idx, "select-authenticator-authenticate", {"authenticator": {"id": authenticator_id}}
        )

    def _cannot_continue(self, idx: dict[str, Any], wanted: str) -> EngieAuthError:
        """Turn a missing remediation into the most specific error the response supports."""
        offered = [
            str(step.get("name"))
            for step in (idx.get("remediation", {}) or {}).get("value", [])
            if isinstance(step, dict)
        ]
        options = _authenticator_options(idx)
        if options:
            return EngieMfaRequiredError(
                f"Okta wants an authenticator this client cannot answer; it offered: {', '.join(options)}",
                status=",".join(offered) or "unknown",
                factors=[{"factorType": option} for option in options],
            )
        return EngieAuthError(f"Okta did not offer the {wanted} step; it offered {offered or 'nothing'}")

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


def _state_handle(idx: dict[str, Any]) -> str:
    """The token that ties one IDX step to the next."""
    handle = idx.get("stateHandle")
    if not isinstance(handle, str) or not handle:
        raise EngieAuthError("Okta IDX response carries no stateHandle")
    return handle


def _remediation(idx: dict[str, Any], name: str) -> dict[str, Any] | None:
    """The named remediation from an IDX response, or ``None`` when it is not offered."""
    block = idx.get("remediation")
    steps = block.get("value", []) if isinstance(block, dict) else []
    for step in steps:
        if isinstance(step, dict) and step.get("name") == name:
            return step
    return None


def _idx_messages(idx: dict[str, Any]) -> str:
    """Okta's own error text for a step, already localised (Dutch on this org)."""
    block = idx.get("messages")
    values = block.get("value", []) if isinstance(block, dict) else []
    texts = [
        str(message.get("message"))
        for message in values
        if isinstance(message, dict) and message.get("message") and message.get("class", "ERROR") == "ERROR"
    ]
    return "; ".join(texts)


def _authenticator_field(idx: dict[str, Any]) -> dict[str, Any] | None:
    step = _remediation(idx, "select-authenticator-authenticate")
    if step is None:
        return None
    for field in step.get("value", []):
        if isinstance(field, dict) and field.get("name") == "authenticator":
            return field
    return None


def _authenticator_options(idx: dict[str, Any]) -> list[str]:
    """Labels of the authenticators Okta offered, for example ``["Email", "Password"]``."""
    field = _authenticator_field(idx)
    if field is None:
        return []
    return [str(option.get("label")) for option in field.get("options", []) if isinstance(option, dict)]


def _password_authenticator_id(idx: dict[str, Any]) -> str | None:
    """The id of the password authenticator among the offered options."""
    field = _authenticator_field(idx)
    if field is None:
        return None
    for option in field.get("options", []):
        if not isinstance(option, dict):
            continue
        form = (option.get("value") or {}).get("form") or {}
        entries = {
            entry.get("name"): entry.get("value") for entry in form.get("value", []) if isinstance(entry, dict)
        }
        if entries.get("methodType") == "password" or str(option.get("label", "")).lower() == "password":
            identifier = entries.get("id")
            if isinstance(identifier, str):
                return identifier
    return None


def _interaction_code(idx: dict[str, Any]) -> str:
    """The one-time code a finished IDX transaction hands to ``/v1/token``."""
    success = idx.get("successWithInteractionCode")
    fields = success.get("value", []) if isinstance(success, dict) else []
    for field in fields:
        if isinstance(field, dict) and field.get("name") == "interaction_code":
            code = field.get("value")
            if isinstance(code, str) and code:
                return code
    block = idx.get("remediation")
    offered = [
        str(step.get("name"))
        for step in (block.get("value", []) if isinstance(block, dict) else [])
        if isinstance(step, dict)
    ]
    raise EngieAuthError(
        "Okta accepted the password but did not finish the login; it now asks for "
        f"{offered or 'nothing this client understands'}"
    )
