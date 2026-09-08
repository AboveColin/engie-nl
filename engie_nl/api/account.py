"""Profile, contact details, credentials and app settings."""

from __future__ import annotations

from typing import Any

from ..generated import (
    ChangePasswordResponse,
    ContactData,
    InterestArea,
    SettingsCardsResponse,
    UserInfoResponse,
    WarmWelcomeResponse,
)
from ._base import ApiGroup, Params, parse_list, parse_one


class AccountApi(ApiGroup):
    """``client.account``: who the customer is and what they have set."""

    # --- reads ---------------------------------------------------------------

    async def okta_userinfo(self) -> UserInfoResponse | None:
        """``GET /api/v1/okta/userinfo``: the customer numbers this login can see.

        An Okta login can carry more than one ENGIE account, which is why the
        app asks before it picks one.

        **Gone from the server.** Measured 2026-09-08 with a valid session: HTTP
        404 ``{"message": "The route api/v1/okta/userinfo could not be found."}``.
        That is the gateway's router saying the path does not exist, which is a
        different 404 from a live endpoint reporting no such record. It belongs
        to the same retired family as ``POST /api/v1/okta/token``: both exist in
        the APK and neither is reachable.
        """
        return parse_one(await self._get("/api/v1/okta/userinfo"), UserInfoResponse.from_api)

    async def welcome(self) -> WarmWelcomeResponse | None:
        """``GET /api/v1/user/welcome``: the onboarding card shown to a new customer."""
        return parse_one(await self._get("/api/v1/user/welcome"), WarmWelcomeResponse.from_api)

    async def settings_cards(
        self,
        *,
        zip_code: str,
        house_number: str,
        house_number_addition: str | None = None,
        customer_type: str | None = None,
    ) -> SettingsCardsResponse | None:
        """``GET /api/v1/settings/cards``: which feature cards the app shows for an address."""
        params: Params = [
            ("address[zip_code]", zip_code),
            ("address[house_number]", house_number),
        ]
        if house_number_addition:
            params.append(("address[house_number_addition]", house_number_addition))
        if customer_type:
            params.append(("customerType", customer_type))
        return parse_one(await self._get("/api/v1/settings/cards", params), SettingsCardsResponse.from_api)

    async def areas_of_interest(self) -> list[InterestArea]:
        """``GET /api/v1/areas-of-interest``: the topics the customer opted into."""
        return parse_list(await self._get("/api/v1/areas-of-interest"), InterestArea.from_api)

    async def activity_ping(self) -> Any:
        """``GET /api/v1/daily-user-activity-ping``: the app's once-a-day liveness beacon.

        It reports app usage to ENGIE. Nothing here needs it; it is mapped so
        the surface is complete.
        """
        return await self._get("/api/v1/daily-user-activity-ping")

    # --- writes --------------------------------------------------------------

    async def set_areas_of_interest(self, body: Any) -> Any:
        """``PUT /api/v1/areas-of-interest``."""
        return await self._write("PUT", "/api/v1/areas-of-interest", json_body=body)

    async def update_customer(self, body: Any) -> ContactData | None:
        """``PATCH /api/v2/customer``: change phone, email or opt-in flags."""
        return parse_one(await self._write("PATCH", "/api/v2/customer", json_body=body), ContactData.from_api)

    async def set_payment_info(self, *, bank_account: str, payment_method: str) -> Any:
        """``PUT /api/v1/payment-info``: change the IBAN or the payment method.

        Returned raw. The app's model for this response is called ``User`` and
        is a different shape from the ``UserWithAddresses`` that
        :meth:`~engie_nl.client.EngieClient.get_user` returns, so parsing it
        into the same class would be wrong.
        """
        form: Params = [("bank_account", bank_account), ("payment_method", payment_method)]
        return await self._write("PUT", "/api/v1/payment-info", form=form)

    async def change_password(self, body: Any) -> ChangePasswordResponse | None:
        """``POST /api/v1/customers/me/change-password`` for a signed-in customer."""
        data = await self._write("POST", "/api/v1/customers/me/change-password", json_body=body)
        return parse_one(data, ChangePasswordResponse.from_api)

    async def set_password(self, body: Any) -> Any:
        """``PUT /api/v1/auth/customers/me/password``."""
        return await self._write("PUT", "/api/v1/auth/customers/me/password", json_body=body)

    async def forgot_password(self, body: Any) -> Any:
        """``POST /api/v1/customers/me/forgot-password``: send a reset mail."""
        return await self._write("POST", "/api/v1/customers/me/forgot-password", json_body=body)

    async def forgot_username(self, body: Any, *, api_version: str = "v1") -> Any:
        """``POST /api/{apiVersion}/customers/me/forgot-username``."""
        return await self._write("POST", f"/api/{api_version}/customers/me/forgot-username", json_body=body)

    async def merge_customer(self, body: Any) -> Any:
        """``POST /api/v1/customer/merge-customer``: link a second ENGIE account."""
        return await self._write("POST", "/api/v1/customer/merge-customer", json_body=body)

    async def merge_prospect(self, body: Any) -> Any:
        """``POST /api/v1/customer/merge-prospect``."""
        return await self._write("POST", "/api/v1/customer/merge-prospect", json_body=body)
