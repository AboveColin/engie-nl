"""Devices the customer has told ENGIE about.

Six kinds, each with the same four operations. These are declarations, not
telemetry: ENGIE uses them to tailor advice, and nothing here reads a device.
"""

from __future__ import annotations

from typing import Any

from ..generated import (
    AircoResponse,
    ChargingStationResponse,
    ElectricCarResponse,
    HeatPumpResponse,
    HomeBatteryResponse,
    SolarPanelResponse,
)
from ._base import ApiGroup, parse_list, parse_one


class AssetsApi(ApiGroup):  # pylint: disable=too-many-public-methods
    """``client.assets``: declared solar panels, heat pumps, batteries and cars."""

    # --- solar panels --------------------------------------------------------

    async def solar_panels(self) -> list[SolarPanelResponse]:
        """``GET /api/v1/assets/solarpanels``."""
        return parse_list(await self._get("/api/v1/assets/solarpanels"), SolarPanelResponse.from_api)

    async def add_solar_panels(self, body: Any) -> SolarPanelResponse | None:
        """``POST /api/v1/assets/solarpanels``."""
        data = await self._write("POST", "/api/v1/assets/solarpanels", json_body=body)
        return parse_one(data, SolarPanelResponse.from_api)

    async def update_solar_panels(self, asset_id: str, body: Any) -> Any:
        """``PUT /api/v1/assets/solarpanels/{id}``."""
        return await self._write("PUT", f"/api/v1/assets/solarpanels/{asset_id}", json_body=body)

    async def delete_solar_panels(self, asset_id: str) -> Any:
        """``DELETE /api/v1/assets/solarpanels/{id}``."""
        return await self._write("DELETE", f"/api/v1/assets/solarpanels/{asset_id}")

    # --- heat pumps ----------------------------------------------------------

    async def heat_pumps(self) -> list[HeatPumpResponse]:
        """``GET /api/v1/assets/heatpumps``."""
        return parse_list(await self._get("/api/v1/assets/heatpumps"), HeatPumpResponse.from_api)

    async def add_heat_pump(self, body: Any) -> HeatPumpResponse | None:
        """``POST /api/v1/assets/heatpumps``."""
        data = await self._write("POST", "/api/v1/assets/heatpumps", json_body=body)
        return parse_one(data, HeatPumpResponse.from_api)

    async def update_heat_pump(self, asset_id: str, body: Any) -> Any:
        """``PUT /api/v1/assets/heatpumps/{id}``."""
        return await self._write("PUT", f"/api/v1/assets/heatpumps/{asset_id}", json_body=body)

    async def delete_heat_pump(self, asset_id: str) -> Any:
        """``DELETE /api/v1/assets/heatpumps/{id}``."""
        return await self._write("DELETE", f"/api/v1/assets/heatpumps/{asset_id}")

    # --- home batteries ------------------------------------------------------

    async def home_batteries(self) -> list[HomeBatteryResponse]:
        """``GET /api/v1/assets/homebatteries``."""
        return parse_list(await self._get("/api/v1/assets/homebatteries"), HomeBatteryResponse.from_api)

    async def add_home_battery(self, body: Any) -> HomeBatteryResponse | None:
        """``POST /api/v1/assets/homebatteries``."""
        data = await self._write("POST", "/api/v1/assets/homebatteries", json_body=body)
        return parse_one(data, HomeBatteryResponse.from_api)

    async def update_home_battery(self, asset_id: str, body: Any) -> Any:
        """``PUT /api/v1/assets/homebatteries/{id}``."""
        return await self._write("PUT", f"/api/v1/assets/homebatteries/{asset_id}", json_body=body)

    async def delete_home_battery(self, asset_id: str) -> Any:
        """``DELETE /api/v1/assets/homebatteries/{id}``."""
        return await self._write("DELETE", f"/api/v1/assets/homebatteries/{asset_id}")

    # --- electric cars -------------------------------------------------------

    async def electric_cars(self) -> list[ElectricCarResponse]:
        """``GET /api/v1/assets/electricalcars``."""
        return parse_list(await self._get("/api/v1/assets/electricalcars"), ElectricCarResponse.from_api)

    async def add_electric_car(self, body: Any) -> ElectricCarResponse | None:
        """``POST /api/v1/assets/electricalcars``."""
        data = await self._write("POST", "/api/v1/assets/electricalcars", json_body=body)
        return parse_one(data, ElectricCarResponse.from_api)

    async def update_electric_car(self, asset_id: str, body: Any) -> Any:
        """``PUT /api/v1/assets/electricalcars/{id}``."""
        return await self._write("PUT", f"/api/v1/assets/electricalcars/{asset_id}", json_body=body)

    async def delete_electric_car(self, asset_id: str) -> Any:
        """``DELETE /api/v1/assets/electricalcars/{id}``."""
        return await self._write("DELETE", f"/api/v1/assets/electricalcars/{asset_id}")

    # --- charging stations ---------------------------------------------------

    async def charging_stations(self) -> list[ChargingStationResponse]:
        """``GET /api/v1/assets/chargingstations``."""
        return parse_list(
            await self._get("/api/v1/assets/chargingstations"), ChargingStationResponse.from_api
        )

    async def add_charging_station(self, body: Any) -> ChargingStationResponse | None:
        """``POST /api/v1/assets/chargingstations``."""
        data = await self._write("POST", "/api/v1/assets/chargingstations", json_body=body)
        return parse_one(data, ChargingStationResponse.from_api)

    async def update_charging_station(self, asset_id: str, body: Any) -> Any:
        """``PUT /api/v1/assets/chargingstations/{id}``."""
        return await self._write("PUT", f"/api/v1/assets/chargingstations/{asset_id}", json_body=body)

    async def delete_charging_station(self, asset_id: str) -> Any:
        """``DELETE /api/v1/assets/chargingstations/{id}``."""
        return await self._write("DELETE", f"/api/v1/assets/chargingstations/{asset_id}")

    # --- air conditioning ----------------------------------------------------

    async def aircos(self) -> list[AircoResponse]:
        """``GET /api/v1/assets/aircos``."""
        return parse_list(await self._get("/api/v1/assets/aircos"), AircoResponse.from_api)

    async def add_airco(self, body: Any) -> AircoResponse | None:
        """``POST /api/v1/assets/aircos``."""
        data = await self._write("POST", "/api/v1/assets/aircos", json_body=body)
        return parse_one(data, AircoResponse.from_api)

    async def update_airco(self, asset_id: str, body: Any) -> Any:
        """``PUT /api/v1/assets/aircos/{id}``."""
        return await self._write("PUT", f"/api/v1/assets/aircos/{asset_id}", json_body=body)

    async def delete_airco(self, asset_id: str) -> Any:
        """``DELETE /api/v1/assets/aircos/{id}``."""
        return await self._write("DELETE", f"/api/v1/assets/aircos/{asset_id}")
