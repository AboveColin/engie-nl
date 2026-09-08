"""Solar potential and the quote request behind it."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ..generated import PreCheck, SolarPotential
from ._base import ApiGroup, Params, eans_param, parse_list


class SolarApi(ApiGroup):
    """``client.solar``: what a roof could produce, and asking for a quote."""

    async def potential(self, eans: Iterable[str] | str) -> list[SolarPotential]:
        """``GET /api/v1/solar-potential``: modelled yield for the address behind an EAN."""
        return parse_list(await self._get("/api/v1/solar-potential", eans_param(eans)), SolarPotential.from_api)

    async def pre_check(self, eans: Iterable[str] | str) -> list[PreCheck]:
        """``GET /api/v1/solar-potential-pre-check``: whether a full calculation is possible."""
        return parse_list(await self._get("/api/v1/solar-potential-pre-check", eans_param(eans)), PreCheck.from_api)

    async def request_quote(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        zip_code: str,
        street: str,
        city: str,
        house_nr: str,
        house_nr_addition: str = "",
        middle_name: str = "",
        comment: str = "",
        standard_period_quantity: str = "",
    ) -> Any:
        """``POST /api/v1/solar-quote``: ask a salesperson to call back.

        A write because it creates a lead against the customer's own contact
        details, not because it changes energy data.
        """
        form: Params = [
            ("first_name", first_name),
            ("middle_name", middle_name),
            ("last_name", last_name),
            ("email", email),
            ("phone", phone),
            ("zip_code", zip_code),
            ("street", street),
            ("city", city),
            ("house_nr", house_nr),
            ("house_nr_addition", house_nr_addition),
            ("comment", comment),
            ("standard_period_quantity", standard_period_quantity),
        ]
        return await self._write("POST", "/api/v1/solar-quote", form=form)

    async def request_home_scan(self, body: dict[str, str]) -> Any:
        """``POST /api/v1/woning-scan``: book a home energy survey.

        The form keys are ``zip_code``, ``house_nr``, ``house_nr_addition``,
        ``preferred_day[]``, ``preferred_moment[]`` and ``type``.
        """
        return await self._write("POST", "/api/v1/woning-scan", form=list(body.items()))

    async def request_energy_scan(self, body: dict[str, str]) -> Any:
        """``POST /api/v1/energie-scan``: the longer survey with usage figures.

        Its form keys are nested, for example ``contact_person[first_name]`` and
        ``usage_per_year[energy_in_kwh]``, and are sent verbatim.
        """
        return await self._write("POST", "/api/v1/energie-scan", form=list(body.items()))
