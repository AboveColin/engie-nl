"""Account creation and the gateway's own token endpoints.

None of this is how the app signs in today. The app uses Okta, and
:class:`~engie_nl.auth.OktaAuth` implements that. What is here is the older
gateway-native authentication that the code still declares, plus the signup
flow, which is unauthenticated.

The password grant below has **no caller anywhere in the app**. It is mapped so
the surface is complete, and because a server-side endpoint with no client is
worth knowing about, but nothing should be built on it: if ENGIE removes it,
nothing in the app breaks and nobody will notice until your code does.
"""

from __future__ import annotations

from typing import Any

from ..constants import MGW_CLIENT_ID, MGW_CLIENT_SECRET
from ..generated import (
    AccessTokenResponse,
    CheckAccountResponse,
    InitialLoginResponse,
    LoginDataTokenResponse,
    UserInfoResponse,
)
from ._base import ApiGroup, Params, parse_one


class LegacyApi(ApiGroup):
    """``client.legacy``: pre-Okta authentication and account creation."""

    # --- the gateway's own tokens --------------------------------------------

    async def okta_token(self, *, customer_id: str, reason: str) -> LoginDataTokenResponse | None:
        """``POST /api/v1/okta/token``: exchange an Okta token for a gateway one.

        Dead code in 6.9.2. The gateway takes the Okta access token as its own
        bearer, which is why nothing calls this. Kept mapped because it exists.
        """
        form: Params = [("customer_id", customer_id), ("reason", reason)]
        data = await self._write("POST", "/api/v1/okta/token", form=form)
        return parse_one(data, LoginDataTokenResponse.from_api)

    async def okta_userinfo(self) -> UserInfoResponse | None:
        """``GET /api/v1/okta/userinfo``. Same as :meth:`client.account.okta_userinfo`."""
        return parse_one(await self._get("/api/v1/okta/userinfo"), UserInfoResponse.from_api)

    async def password_grant(
        self,
        *,
        username: str,
        password: str,
        customer: bool = True,
        recaptcha_token: str | None = None,
        recaptcha_key: str | None = None,
    ) -> AccessTokenResponse | None:
        """``POST /api/v1/auth/customer`` or ``/api/v1/auth/non-customer``.

        The client id and secret are compiled into the public APK, so they
        identify the app rather than a person. Untested against the live
        gateway: no call site exists to copy, and trying it would send real
        credentials down a path nothing else uses.
        """
        form: Params = [
            ("username", username),
            ("password", password),
            ("grant_type", "password"),
            ("client_id", MGW_CLIENT_ID),
            ("client_secret", MGW_CLIENT_SECRET),
        ]
        headers = {}
        if recaptcha_token:
            headers["X-GRE-Token"] = recaptcha_token
        if recaptcha_key:
            headers["X-GRE-Key"] = recaptcha_key
        if customer:
            data = await self._write("POST", "/api/v1/auth/customer", form=form, headers=headers or None)
        else:
            data = await self._write("POST", "/api/v1/auth/non-customer", form=form, headers=headers or None)
        return parse_one(data, AccessTokenResponse.from_api)

    async def refresh_grant(self, refresh_token: str, *, customer: bool = True) -> AccessTokenResponse | None:
        """``POST /api/v1/auth/customer/refresh`` or ``/api/v1/auth/non-customer/refresh``."""
        form: Params = [
            ("refresh_token", refresh_token),
            ("grant_type", "refresh_token"),
            ("client_id", MGW_CLIENT_ID),
            ("client_secret", MGW_CLIENT_SECRET),
        ]
        if customer:
            data = await self._write("POST", "/api/v1/auth/customer/refresh", form=form)
        else:
            data = await self._write("POST", "/api/v1/auth/non-customer/refresh", form=form)
        return parse_one(data, AccessTokenResponse.from_api)

    # --- signup --------------------------------------------------------------

    async def check_account(
        self,
        *,
        customer_nr: str = "",
        postal_code: str = "",
        house_nr: str = "",
        username: str = "",
        iban_last_three: str = "",
    ) -> CheckAccountResponse | None:
        """``POST /api/v3/check-account``: does an account already exist for these details."""
        form: Params = [
            ("customer_nr", customer_nr),
            ("postal_code", postal_code),
            ("house_nr", house_nr),
            ("username", username),
            ("iban_last_three", iban_last_three),
        ]
        return parse_one(await self._write("POST", "/api/v3/check-account", form=form), CheckAccountResponse.from_api)

    async def initial_login(
        self, *, customer_nr: str, zip_code: str, house_nr: str, iban_last_three: str
    ) -> InitialLoginResponse | None:
        """``POST /api/v1/initial-login``: prove ownership of a paper account."""
        form: Params = [
            ("customer_nr", customer_nr),
            ("zip_code", zip_code),
            ("house_nr", house_nr),
            ("iban_last_three", iban_last_three),
        ]
        return parse_one(await self._write("POST", "/api/v1/initial-login", form=form), InitialLoginResponse.from_api)

    async def create_account(self, fields: dict[str, str]) -> Any:
        """``POST /api/v2/create-account``: turn a customer number into a login."""
        return await self._write("POST", "/api/v2/create-account", form=list(fields.items()))

    async def register_non_customer(self, fields: dict[str, str]) -> AccessTokenResponse | None:
        """``POST /api/v1/register/non-customer``: sign up without a contract."""
        data = await self._write("POST", "/api/v1/register/non-customer", form=list(fields.items()))
        return parse_one(data, AccessTokenResponse.from_api)

    async def forgot_password(self, email: str) -> Any:
        """``POST /api/v1/forgot-password``: the unauthenticated reset."""
        return await self._write("POST", "/api/v1/forgot-password", form=[("email", email)])
