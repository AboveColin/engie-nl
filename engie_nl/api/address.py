"""Addresses: looking one up, proving you live there, and moving the contract."""

from __future__ import annotations

from typing import Any

from ..generated import (
    AddressMetaData,
    BankDto,
    EdsnMeteringPoint,
    Pro6PPResponse,
    SimpleResponse,
    StartVerificationResponse,
)
from ._base import ApiGroup, Params, parse_list, parse_one


class AddressApi(ApiGroup):
    """``client.address``: postcode lookup, iDIN verification and a move."""

    # --- reads ---------------------------------------------------------------

    async def lookup(self, *, zip_code: str, house_number: str, addition: str = "") -> Pro6PPResponse | None:
        """``GET /api/v1/address``: postcode to street and city, through Pro6PP."""
        params: Params = [("nl_sixpp", zip_code), ("streetnumber", house_number)]
        if addition:
            params.append(("extension", addition))
        return parse_one(await self._get("/api/v1/address", params), Pro6PPResponse.from_api)

    async def metadata(self, *, zip_code: str, house_nr: str, addition: str = "") -> AddressMetaData | None:
        """``GET /api/v1/address-metadata``: what ENGIE knows about a connection there."""
        params: Params = [("zipCode", zip_code), ("houseNr", house_nr)]
        if addition:
            params.append(("houseNrAddition", addition))
        return parse_one(await self._get("/api/v1/address-metadata", params), AddressMetaData.from_api)

    async def idin_banks(self) -> list[BankDto]:
        """``GET /api/v1/address-verification-methods/idin/available-banks``.

        iDIN proves identity through a bank login. This lists the banks that
        support it.
        """
        data = await self._get("/api/v1/address-verification-methods/idin/available-banks")
        return parse_list(data, BankDto.from_api)

    # --- writes --------------------------------------------------------------

    async def verify(self, code: str) -> SimpleResponse | None:
        """``POST /api/v1/verify-address``: submit the code from the verification letter."""
        data = await self._write("POST", "/api/v1/verify-address", form=[("code", code)])
        return parse_one(data, SimpleResponse.from_api)

    async def start_idin(self, body: Any) -> StartVerificationResponse | None:
        """``POST /api/v1/address-verification-methods/idin/transactions``: begin iDIN."""
        data = await self._write("POST", "/api/v1/address-verification-methods/idin/transactions", json_body=body)
        return parse_one(data, StartVerificationResponse.from_api)

    async def start_letter_verification(self, body: Any) -> Any:
        """``POST /api/v1/address-verification-methods/letter``: post a code instead."""
        return await self._write("POST", "/api/v1/address-verification-methods/letter", json_body=body)

    async def edsn_metering_points(self, body: Any) -> list[EdsnMeteringPoint]:
        """``POST /api/v1/edsn``: the EANs the national register holds for an address.

        A POST that reads, but it is gated with the writes because it queries
        the national register on the customer's behalf during a move.
        """
        return parse_list(await self._write("POST", "/api/v1/edsn", json_body=body), EdsnMeteringPoint.from_api)

    async def move_contract(self, body: Any) -> Any:
        """``POST /api/v1/contract/move``: move the contract to another address.

        This ends supply at one address and starts it at another.
        """
        return await self._write("POST", "/api/v1/contract/move", json_body=body)

    async def set_contract_details(self, body: Any) -> Any:
        """``PUT /api/v1/energy-contract-details/current``: file the current contract's details."""
        return await self._write("PUT", "/api/v1/energy-contract-details/current", json_body=body)

    async def extend_contract(self, body: Any) -> Any:
        """``POST /api/v2/contract-agreements``: accept an extension offer."""
        return await self._write("POST", "/api/v2/contract-agreements", json_body=body)
