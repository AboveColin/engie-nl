"""ENGIE's own smart-charging programme, separate from the Enode plumbing.

Enode is how ENGIE reaches the car. This is the programme the customer signs up
to: a mandate, a vehicle, and the sessions that earn a payout.
"""

from __future__ import annotations

from typing import Any

from ..generated import Car, SmartChargingSession, VehicleCreationResponse
from ._base import ApiGroup, Params, parse_list, parse_one


class SmartChargingApi(ApiGroup):
    """``client.smart_charging``: enrolment, vehicles and reward sessions."""

    # --- reads ---------------------------------------------------------------

    async def cars(self) -> list[Car]:
        """``GET /api/v2/smart-charging/cars``: the models the programme supports.

        **Gone from the server.** Measured 2026-09-08: HTTP 404 ``{"message":
        "The route api/v2/smart-charging/cars could not be found."}``.
        """
        return parse_list(await self._get("/api/v2/smart-charging/cars"), Car.from_api)

    async def sessions(self) -> list[SmartChargingSession]:
        """``GET /api/v1/smart-charging/sessions``: sessions and what they earned."""
        return parse_list(await self._get("/api/v1/smart-charging/sessions"), SmartChargingSession.from_api)

    # --- writes --------------------------------------------------------------

    async def create_mandate(self, body: Any) -> Any:
        """``POST /api/v1/smart-charging/mandate``: join the programme."""
        return await self._write("POST", "/api/v1/smart-charging/mandate", json_body=body)

    async def delete_mandate(
        self, *, contact_id: str, email_address: str, delivery_agreement_id: str
    ) -> Any:
        """``DELETE /api/v1/smart-charging/mandate``: leave the programme."""
        params: Params = [
            ("contact_id", contact_id),
            ("email_address", email_address),
            ("delivery_agreement_id", delivery_agreement_id),
        ]
        return await self._write("DELETE", "/api/v1/smart-charging/mandate", params=params)

    async def delete_user(self, *, contact_id: str, email_address: str) -> Any:
        """``DELETE /api/v1/smart-charging/user``: remove the enrolment entirely."""
        params: Params = [("contact_id", contact_id), ("email_address", email_address)]
        return await self._write("DELETE", "/api/v1/smart-charging/user", params=params)

    async def create_vehicle(self, car_id: str) -> VehicleCreationResponse | None:
        """``POST /api/v1/smart-charging/vehicle``: register which car it is."""
        data = await self._write("POST", "/api/v1/smart-charging/vehicle", form=[("car_id", car_id)])
        return parse_one(data, VehicleCreationResponse.from_api)

    async def report_unsupported_vehicle(self, body: Any) -> Any:
        """``POST /api/v1/smart-charging/vehicle/not-supported``: tell ENGIE a car is missing."""
        return await self._write("POST", "/api/v1/smart-charging/vehicle/not-supported", json_body=body)

    async def request_payout(self) -> Any:
        """``POST /api/v1/smart-charging/payout-rewards``: pay out what the sessions earned.

        The app declares this path twice, once on its smart-charging API and
        once on its gateway API, with the same effect.
        """
        return await self._write("POST", "/api/v1/smart-charging/payout-rewards")
