"""Enode: the third-party layer that talks to EVs, chargers and inverters.

ENGIE proxies Enode rather than exposing it directly, so these paths sit on the
gateway and take the same bearer. The customer links a vendor account once, then
Enode reports the vehicle's charge level and can start or stop charging.

Responses come wrapped: a list endpoint answers ``{"data": [...]}``, which
:func:`~engie_nl.api._base.as_dicts` unwraps.
"""

from __future__ import annotations

from typing import Any

from ..generated import (
    ChargingPolicy,
    EnodeCharger,
    EnodeChargingSession,
    EnodeIntervention,
    EnodeLocation,
    EnodeSolarConfiguration,
    EnodeUser,
    EnodeVehicle,
    LinkResponse,
)
from ._base import ApiGroup, Params, parse_list, parse_one


class EnodeApi(ApiGroup):  # pylint: disable=too-many-public-methods
    """``client.enode``: linked vehicles, chargers, locations and charge policies."""

    # --- the linked user -----------------------------------------------------

    async def me(self) -> EnodeUser | None:
        """``GET /api/v1/enode/users/me``: whether this customer has linked anything.

        Answers HTTP 404 for a customer who has never linked a vendor, with
        Enode's own problem document rather than the gateway's error shape::

            {"type": "https://developers.enode.com/api/problems/not-found",
             "title": "User does not exist",
             "detail": "Could not find user with ID K0XXXXXXX"}

        Measured 2026-09-08. Read that as "nothing linked", not as an outage.
        The list endpoints answer 200 with an empty ``data`` for the same
        account, so prefer :meth:`vehicles` and :meth:`chargers` to test for a
        link.
        """
        return parse_one(await self._get("/api/v1/enode/users/me"), EnodeUser.from_api)

    async def link(self, body: Any) -> LinkResponse | None:
        """``POST /api/v1/enode/users/me/link``: start linking a vendor account.

        Returns the URL the customer opens to sign in with their car or charger
        vendor.
        """
        return parse_one(await self._write("POST", "/api/v1/enode/users/me/link", json_body=body), LinkResponse.from_api)

    async def relink_asset(self, asset_id: str, body: Any) -> LinkResponse | None:
        """``POST /api/v1/enode/assets/{assetId}/relink``: re-authorise one device."""
        data = await self._write("POST", f"/api/v1/enode/assets/{asset_id}/relink", json_body=body)
        return parse_one(data, LinkResponse.from_api)

    async def unlink_vehicle(self, vendor_id: str) -> Any:
        """``DELETE /api/v1/enode/users/me/vendors/{vendorId}/vehicle``."""
        return await self._write("DELETE", f"/api/v1/enode/users/me/vendors/{vendor_id}/vehicle")

    async def unlink_charger(self, vendor_id: str) -> Any:
        """``DELETE /api/v1/enode/users/me/vendors/{vendorId}/charger``."""
        return await self._write("DELETE", f"/api/v1/enode/users/me/vendors/{vendor_id}/charger")

    # --- vehicles and chargers -----------------------------------------------

    async def vehicles(self) -> list[EnodeVehicle]:
        """``GET /api/v1/enode/users/me/vehicles``."""
        return parse_list(await self._get("/api/v1/enode/users/me/vehicles"), EnodeVehicle.from_api)

    async def vehicle(self, vehicle_id: str) -> EnodeVehicle | None:
        """``GET /api/v1/enode/vehicles/{vehicleId}``: charge level and capabilities."""
        return parse_one(await self._get(f"/api/v1/enode/vehicles/{vehicle_id}"), EnodeVehicle.from_api)

    async def chargers(self) -> list[EnodeCharger]:
        """``GET /api/v1/enode/users/me/chargers``."""
        return parse_list(await self._get("/api/v1/enode/users/me/chargers"), EnodeCharger.from_api)

    async def update_charger(self, charger_id: str, body: Any) -> EnodeCharger | None:
        """``PUT /api/v1/enode/chargers/{chargerId}``."""
        data = await self._write("PUT", f"/api/v1/enode/chargers/{charger_id}", json_body=body)
        return parse_one(data, EnodeCharger.from_api)

    async def set_charger_location(self, charger_id: str, body: Any) -> EnodeCharger | None:
        """``PUT /api/v1/enode/chargers/{chargerId}``: put a charger at a location.

        The same path as :meth:`update_charger`; the app has two call sites with
        different bodies.
        """
        return await self.update_charger(charger_id, body)

    # --- locations -----------------------------------------------------------

    async def locations(self) -> list[EnodeLocation]:
        """``GET /api/v1/enode/users/me/locations``."""
        return parse_list(await self._get("/api/v1/enode/users/me/locations"), EnodeLocation.from_api)

    async def create_location(self, body: Any) -> EnodeLocation | None:
        """``POST /api/v1/enode/users/me/locations``."""
        data = await self._write("POST", "/api/v1/enode/users/me/locations", json_body=body)
        return parse_one(data, EnodeLocation.from_api)

    async def delete_location(self, location_id: str) -> EnodeLocation | None:
        """``DELETE /api/v1/enode/locations/{locationId}``."""
        data = await self._write("DELETE", f"/api/v1/enode/locations/{location_id}")
        return parse_one(data, EnodeLocation.from_api)

    async def set_location_zone(self, location_id: str, body: Any) -> Any:
        """``POST /api/v1/enode/flex/locations/{locationId}``: set the grid zone."""
        return await self._write("POST", f"/api/v1/enode/flex/locations/{location_id}", json_body=body)

    # --- charge policies and sessions ----------------------------------------

    async def policies(self) -> list[ChargingPolicy]:
        """``GET /api/v1/enode/flex/vehicle-policies``: the smart-charging rules."""
        return parse_list(await self._get("/api/v1/enode/flex/vehicle-policies"), ChargingPolicy.from_api)

    async def policy(self, policy_id: str) -> ChargingPolicy | None:
        """``GET /api/v1/enode/flex/vehicle-policies/{policyId}``."""
        data = await self._get(f"/api/v1/enode/flex/vehicle-policies/{policy_id}")
        return parse_one(data, ChargingPolicy.from_api)

    async def create_policy(self, body: Any) -> ChargingPolicy | None:
        """``POST /api/v1/enode/flex/vehicle-policies``."""
        data = await self._write("POST", "/api/v1/enode/flex/vehicle-policies", json_body=body)
        return parse_one(data, ChargingPolicy.from_api)

    async def update_policy(self, policy_id: str, body: Any) -> ChargingPolicy | None:
        """``PATCH /api/v1/enode/flex/vehicle-policies/{policyId}``."""
        data = await self._write("PATCH", f"/api/v1/enode/flex/vehicle-policies/{policy_id}", json_body=body)
        return parse_one(data, ChargingPolicy.from_api)

    async def delete_policy(self, policy_id: str) -> Any:
        """``DELETE /api/v1/enode/flex/vehicle-policies/{policyId}``."""
        return await self._write("DELETE", f"/api/v1/enode/flex/vehicle-policies/{policy_id}")

    async def sessions(
        self,
        *,
        vehicle_id: str | None = None,
        location_id: str | None = None,
        policy_id: str | None = None,
    ) -> list[EnodeChargingSession]:
        """``GET /api/v1/enode/flex/vehicle-policies/sessions``: past charge sessions."""
        params: Params = []
        if vehicle_id:
            params.append(("vehicleId", vehicle_id))
        if location_id:
            params.append(("locationId", location_id))
        if policy_id:
            params.append(("policyId", policy_id))
        data = await self._get("/api/v1/enode/flex/vehicle-policies/sessions", params or None)
        return parse_list(data, EnodeChargingSession.from_api)

    async def session(self, policy_id: str) -> EnodeChargingSession | None:
        """``GET /api/v1/enode/flex/vehicle-policies/{policyId}/session``: the live one."""
        data = await self._get(f"/api/v1/enode/flex/vehicle-policies/{policy_id}/session")
        return parse_one(data, EnodeChargingSession.from_api)

    async def set_session_target(self, session_id: str, body: Any) -> Any:
        """``PUT /api/v1/enode/flex/sessions/{sessionId}/target``: change the charge target.

        This commands a real charger.
        """
        return await self._write("PUT", f"/api/v1/enode/flex/sessions/{session_id}/target", json_body=body)

    # --- solar inverters -----------------------------------------------------

    async def solar_configurations(self) -> list[EnodeSolarConfiguration]:
        """``GET /api/v1/enode/solar-configurations``."""
        data = await self._get("/api/v1/enode/solar-configurations")
        return parse_list(data, EnodeSolarConfiguration.from_api)

    async def solar_configuration(self, config_id: str) -> EnodeSolarConfiguration | None:
        """``GET /api/v1/enode/solar-configurations/{id}``."""
        data = await self._get(f"/api/v1/enode/solar-configurations/{config_id}")
        return parse_one(data, EnodeSolarConfiguration.from_api)

    async def create_solar_configuration(self, body: Any) -> EnodeSolarConfiguration | None:
        """``POST /api/v1/enode/solar-configurations``."""
        data = await self._write("POST", "/api/v1/enode/solar-configurations", json_body=body)
        return parse_one(data, EnodeSolarConfiguration.from_api)

    async def update_solar_configuration(self, config_id: str, body: Any) -> EnodeSolarConfiguration | None:
        """``PATCH /api/v1/enode/solar-configurations/{id}``."""
        data = await self._write("PATCH", f"/api/v1/enode/solar-configurations/{config_id}", json_body=body)
        return parse_one(data, EnodeSolarConfiguration.from_api)

    async def delete_solar_configuration(self, config_id: str) -> Any:
        """``DELETE /api/v1/enode/solar-configurations/{id}``."""
        return await self._write("DELETE", f"/api/v1/enode/solar-configurations/{config_id}")

    # --- interventions -------------------------------------------------------

    async def intervention(self, intervention_id: str, *, language: str = "nl") -> EnodeIntervention | None:
        """``GET /api/v1/enode/interventions/{id}``: what the customer must fix.

        Enode raises one of these when a link breaks, for example when the
        vendor account needs signing in again.
        """
        data = await self._get(f"/api/v1/enode/interventions/{intervention_id}", [("language", language)])
        return parse_one(data, EnodeIntervention.from_api)
