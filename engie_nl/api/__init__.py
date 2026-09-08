"""The rest of the gateway, grouped by what it is for.

:class:`~engie_nl.client.EngieClient` carries the reads a household actually
polls: user, consumption, meter readings, costs, day-ahead prices. Everything
else the app can reach lives here, one module per area, reachable as
``client.assets``, ``client.enode`` and so on.

Paths are written out at the call site rather than pulled from constants.py.
There are 148 of them and each is used once, so a constant would only add a
name to look up.

Every method that changes the account goes through
:meth:`~engie_nl.client.EngieClient._write`, which refuses unless the client was
built with ``allow_writes=True``.
"""

from __future__ import annotations

from .account import AccountApi
from .address import AddressApi
from .assets import AssetsApi
from .billing import BillingApi
from .enode import EnodeApi
from .ev import EvApi
from .happy_hour import HappyHourApi
from .legacy import LegacyApi
from .mandates import MandatesApi
from .meter import MeterApi
from .smart_charging import SmartChargingApi
from .solar import SolarApi
from .support import SupportApi
from .tariffs import TariffsApi

__all__ = [
    "AccountApi",
    "AddressApi",
    "AssetsApi",
    "BillingApi",
    "EnodeApi",
    "EvApi",
    "HappyHourApi",
    "LegacyApi",
    "MandatesApi",
    "MeterApi",
    "SmartChargingApi",
    "SolarApi",
    "SupportApi",
    "TariffsApi",
]
