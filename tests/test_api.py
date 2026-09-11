"""The endpoint groups, against the same loopback gateway the client tests use.

Most of the 130 methods in ``engie_nl/api/`` are one line: send a verb to a
path, hand the body to a model. What can go wrong is the verb, the path, the
model, and whether the write gate applies. Those four are a table, not 130
hand-written tests, so they are one.

The table is the assertion. The loopback server answers 404 to a path it was
not told about, and a 404 is an :class:`EngieApiError`, so a method that sends
anything other than the verb and path its row names fails the test.

Methods that build a query string or a form out of their arguments have real
logic in them and get their own test below the table.

Every value here is invented: EANs start 8716948400000000, ids are ``<thing>-0``,
and the one person is Jane Doe at test@example.com.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pytest
from aiohttp import web

from engie_nl import EngieApiError, EngieClient, EngieWriteBlocked
from engie_nl._parse import as_dicts
from engie_nl.generated import (
    AbstractBaseResponse,
    AccessTokenResponse,
    AddressMetaData,
    AircoResponse,
    ApprovalData,
    ArticlesResponse,
    BankDto,
    Car,
    ChangePasswordResponse,
    ChargingPolicy,
    ChargingStationResponse,
    CheckAccountResponse,
    CollectiveResponse,
    ContactData,
    DocumentsResponse,
    EdsnMeteringPoint,
    ElectricCarResponse,
    EnodeCharger,
    EnodeChargingSession,
    EnodeIntervention,
    EnodeLocation,
    EnodeSolarConfiguration,
    EnodeUser,
    EnodeVehicle,
    HappyHourSessionDTO,
    HappyHourSubscriptionModel,
    HappyHoursResponse,
    HeatPumpResponse,
    HomeBatteryResponse,
    InitialLoginResponse,
    InterestArea,
    LinkResponse,
    LoginDataTokenResponse,
    MGWCreateIDealTransactionResponse,
    MGWUpdateIDealStatusResponse,
    Measure,
    OpeningHoursResponse,
    P4,
    P4StatusResponse,
    PaymentInfo,
    PreCheck,
    PrepaymentResult,
    Pro6PPResponse,
    SettingsCardsResponse,
    SimpleResponse,
    SimpleStatus,
    SmartChargingSession,
    SolarPanelResponse,
    SolarPotential,
    StartVerificationResponse,
    UserInfoResponse,
    VehicleCreationResponse,
    WaitingTimes,
    WarmWelcomeResponse,
)

from tests.conftest import FakeServer, query_of

EAN_E = "871694840000000001"
EAN_G = "871694840000000002"
BODY = {"note": "a body this test does not read"}


@dataclass(frozen=True)
class Call:
    """One method, the verb and path it must reach, and what the model must become.

    ``model`` is the class the body has to end up as: ``None`` for the methods
    that hand the decoded body back untouched, a class for a single object, and
    ``[cls]`` for a list. Naming it catches a method wired to the wrong model,
    which no status code would.
    """

    group: str
    method: str
    verb: str
    path: str
    reply: Any
    model: Any = None
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.group}.{self.method}"

    @property
    def route(self) -> str:
        """The path as the server sees it. Seamly's two paths are written relative."""
        return "/" + self.path.lstrip("/")

    def bound(self, client: EngieClient) -> Any:
        return getattr(getattr(client, self.group), self.method)

    async def invoke(self, client: EngieClient) -> Any:
        return await self.bound(client)(*self.args, **self.kwargs)

    def check(self, result: Any) -> None:
        if self.model is None:
            assert result == self.reply
        elif isinstance(self.model, list):
            rows = as_dicts(self.reply)
            assert rows, f"{self.id} has no rows to parse"
            assert [type(item) for item in result] == [self.model[0]] * len(rows)
            assert [item.raw for item in result] == rows
        else:
            assert isinstance(result, self.model)
            assert result.raw == self.reply


# --- reads: no gate, and the gateway is asked with GET -----------------------

READS = [
    Call("account", "okta_userinfo", "GET", "/api/v1/okta/userinfo",
         {"customer_ids": ["K00000000"]}, UserInfoResponse),
    Call("account", "welcome", "GET", "/api/v1/user/welcome", {"title": "Welkom"}, WarmWelcomeResponse),
    Call("account", "areas_of_interest", "GET", "/api/v1/areas-of-interest",
         [{"id": "area-0", "name": "Besparen"}], [InterestArea]),
    Call("account", "activity_ping", "GET", "/api/v1/daily-user-activity-ping", {"status": "ok"}),

    Call("address", "idin_banks", "GET", "/api/v1/address-verification-methods/idin/available-banks",
         [{"name": "Testbank"}], [BankDto]),

    Call("assets", "solar_panels", "GET", "/api/v1/assets/solarpanels",
         [{"id": "asset-0"}], [SolarPanelResponse]),
    Call("assets", "heat_pumps", "GET", "/api/v1/assets/heatpumps",
         [{"id": "asset-0"}], [HeatPumpResponse]),
    Call("assets", "home_batteries", "GET", "/api/v1/assets/homebatteries",
         [{"id": "asset-0"}], [HomeBatteryResponse]),
    Call("assets", "electric_cars", "GET", "/api/v1/assets/electricalcars",
         [{"id": "asset-0"}], [ElectricCarResponse]),
    Call("assets", "charging_stations", "GET", "/api/v1/assets/chargingstations",
         [{"id": "asset-0"}], [ChargingStationResponse]),
    Call("assets", "aircos", "GET", "/api/v1/assets/aircos", [{"id": "asset-0"}], [AircoResponse]),

    Call("billing", "payment_status", "GET", "/api/v1/transaction/INV-0/payment",
         {"status": "PAID"}, PaymentInfo, args=("INV-0",)),
    Call("billing", "document", "GET", "/api/v2/document/DOC-0",
         {"reference": "DOC-0"}, DocumentsResponse, args=("DOC-0",)),
    Call("billing", "document_v1", "GET", "/api/v1/document/DOC-0",
         {"reference": "DOC-0"}, DocumentsResponse, args=("DOC-0",)),
    Call("billing", "ideal_status", "GET", "/api/v1/payments/ideal2/transactions/TX-0/updatestatus",
         {"status": "open"}, MGWUpdateIDealStatusResponse, args=("TX-0",)),

    Call("enode", "me", "GET", "/api/v1/enode/users/me", {"id": "enode-user-0"}, EnodeUser),
    Call("enode", "vehicles", "GET", "/api/v1/enode/users/me/vehicles",
         {"data": [{"id": "veh-0"}]}, [EnodeVehicle]),
    Call("enode", "vehicle", "GET", "/api/v1/enode/vehicles/veh-0",
         {"id": "veh-0"}, EnodeVehicle, args=("veh-0",)),
    Call("enode", "chargers", "GET", "/api/v1/enode/users/me/chargers",
         {"data": [{"id": "chg-0"}]}, [EnodeCharger]),
    Call("enode", "locations", "GET", "/api/v1/enode/users/me/locations",
         {"data": [{"id": "loc-0"}]}, [EnodeLocation]),
    Call("enode", "policies", "GET", "/api/v1/enode/flex/vehicle-policies",
         {"data": [{"id": "pol-0"}]}, [ChargingPolicy]),
    Call("enode", "policy", "GET", "/api/v1/enode/flex/vehicle-policies/pol-0",
         {"id": "pol-0"}, ChargingPolicy, args=("pol-0",)),
    Call("enode", "session", "GET", "/api/v1/enode/flex/vehicle-policies/pol-0/session",
         {"id": "ses-0"}, EnodeChargingSession, args=("pol-0",)),
    Call("enode", "solar_configurations", "GET", "/api/v1/enode/solar-configurations",
         {"data": [{"id": "cfg-0"}]}, [EnodeSolarConfiguration]),
    Call("enode", "solar_configuration", "GET", "/api/v1/enode/solar-configurations/cfg-0",
         {"id": "cfg-0"}, EnodeSolarConfiguration, args=("cfg-0",)),

    Call("happy_hour", "hours", "GET", "/api/v1/happyhours", {"happy_hours": []}, HappyHoursResponse),
    Call("happy_hour", "sessions", "GET", "/api/v1/happyhour/sessions",
         [{"id": "hh-0"}], [HappyHourSessionDTO]),
    Call("happy_hour", "subscriptions", "GET", "/api/v1/assets/happyhour",
         [{"id": "sub-0"}], [HappyHourSubscriptionModel]),

    Call("legacy", "okta_userinfo", "GET", "/api/v1/okta/userinfo",
         {"customer_ids": ["K00000000"]}, UserInfoResponse),

    Call("smart_charging", "cars", "GET", "/api/v2/smart-charging/cars",
         [{"id": "car-0"}], [Car]),
    Call("smart_charging", "sessions", "GET", "/api/v1/smart-charging/sessions",
         [{"id": "scs-0"}], [SmartChargingSession]),

    Call("support", "opening_hours", "GET", "/api/v1/opening-hours", {"days": []}, OpeningHoursResponse),
    Call("support", "waiting_time", "GET", "/api/v1/opening-hours/waiting-time",
         {"waiting_time": 0}, WaitingTimes),
    Call("support", "advice_article", "GET", "/api/v1/advice/articles/art-0",
         {"id": "art-0"}, Measure, args=("art-0",)),
    Call("support", "advice_changes", "GET", "/api/v1/advice/changes/rev-0",
         {"articles": []}, ArticlesResponse, args=("rev-0",)),
    Call("support", "chat_event", "GET", "event/conversation-started",
         {"ok": True}, args=("conversation-started",)),
]

# POSTs that read. They send a body because the EANs and the window are too
# long for a query string, so no write gate applies to them.
QUERIES = [
    Call("meter", "p4_readings", "POST", "/api/v1/readings",
         [{"ean": EAN_E}], [P4], args=(BODY,)),
    Call("meter", "p4_errors", "POST", "/api/v1/p4-errors",
         [{"ean": EAN_E}], [P4StatusResponse], args=(BODY,)),
]

# --- writes: every one of these is refused unless allow_writes=True ----------

WRITES = [
    Call("account", "set_areas_of_interest", "PUT", "/api/v1/areas-of-interest",
         {"status": "ok"}, args=(BODY,)),
    Call("account", "update_customer", "PATCH", "/api/v2/customer",
         {"email": "test@example.com"}, ContactData, args=(BODY,)),
    Call("account", "change_password", "POST", "/api/v1/customers/me/change-password",
         {"status": "ok"}, ChangePasswordResponse, args=(BODY,)),
    Call("account", "set_password", "PUT", "/api/v1/auth/customers/me/password",
         {"status": "ok"}, args=(BODY,)),
    Call("account", "forgot_password", "POST", "/api/v1/customers/me/forgot-password",
         {"status": "ok"}, args=(BODY,)),
    Call("account", "forgot_username", "POST", "/api/v1/customers/me/forgot-username",
         {"status": "ok"}, args=(BODY,)),
    Call("account", "merge_customer", "POST", "/api/v1/customer/merge-customer",
         {"status": "ok"}, args=(BODY,)),
    Call("account", "merge_prospect", "POST", "/api/v1/customer/merge-prospect",
         {"status": "ok"}, args=(BODY,)),

    Call("address", "verify", "POST", "/api/v1/verify-address",
         {"status": "ok"}, SimpleResponse, args=("000000",)),
    Call("address", "start_idin", "POST", "/api/v1/address-verification-methods/idin/transactions",
         {"transaction_id": "idin-0"}, StartVerificationResponse, args=(BODY,)),
    Call("address", "start_letter_verification", "POST", "/api/v1/address-verification-methods/letter",
         {"status": "ok"}, args=(BODY,)),
    Call("address", "edsn_metering_points", "POST", "/api/v1/edsn",
         [{"ean": EAN_E}], [EdsnMeteringPoint], args=(BODY,)),
    Call("address", "move_contract", "POST", "/api/v1/contract/move", {"status": "ok"}, args=(BODY,)),
    Call("address", "set_contract_details", "PUT", "/api/v1/energy-contract-details/current",
         {"status": "ok"}, args=(BODY,)),
    Call("address", "extend_contract", "POST", "/api/v2/contract-agreements",
         {"status": "ok"}, args=(BODY,)),

    Call("assets", "add_solar_panels", "POST", "/api/v1/assets/solarpanels",
         {"id": "asset-0"}, SolarPanelResponse, args=(BODY,)),
    Call("assets", "update_solar_panels", "PUT", "/api/v1/assets/solarpanels/asset-0",
         {"status": "ok"}, args=("asset-0", BODY)),
    Call("assets", "delete_solar_panels", "DELETE", "/api/v1/assets/solarpanels/asset-0",
         {"status": "ok"}, args=("asset-0",)),
    Call("assets", "add_heat_pump", "POST", "/api/v1/assets/heatpumps",
         {"id": "asset-0"}, HeatPumpResponse, args=(BODY,)),
    Call("assets", "update_heat_pump", "PUT", "/api/v1/assets/heatpumps/asset-0",
         {"status": "ok"}, args=("asset-0", BODY)),
    Call("assets", "delete_heat_pump", "DELETE", "/api/v1/assets/heatpumps/asset-0",
         {"status": "ok"}, args=("asset-0",)),
    Call("assets", "add_home_battery", "POST", "/api/v1/assets/homebatteries",
         {"id": "asset-0"}, HomeBatteryResponse, args=(BODY,)),
    Call("assets", "update_home_battery", "PUT", "/api/v1/assets/homebatteries/asset-0",
         {"status": "ok"}, args=("asset-0", BODY)),
    Call("assets", "delete_home_battery", "DELETE", "/api/v1/assets/homebatteries/asset-0",
         {"status": "ok"}, args=("asset-0",)),
    Call("assets", "add_electric_car", "POST", "/api/v1/assets/electricalcars",
         {"id": "asset-0"}, ElectricCarResponse, args=(BODY,)),
    Call("assets", "update_electric_car", "PUT", "/api/v1/assets/electricalcars/asset-0",
         {"status": "ok"}, args=("asset-0", BODY)),
    Call("assets", "delete_electric_car", "DELETE", "/api/v1/assets/electricalcars/asset-0",
         {"status": "ok"}, args=("asset-0",)),
    Call("assets", "add_charging_station", "POST", "/api/v1/assets/chargingstations",
         {"id": "asset-0"}, ChargingStationResponse, args=(BODY,)),
    Call("assets", "update_charging_station", "PUT", "/api/v1/assets/chargingstations/asset-0",
         {"status": "ok"}, args=("asset-0", BODY)),
    Call("assets", "delete_charging_station", "DELETE", "/api/v1/assets/chargingstations/asset-0",
         {"status": "ok"}, args=("asset-0",)),
    Call("assets", "add_airco", "POST", "/api/v1/assets/aircos",
         {"id": "asset-0"}, AircoResponse, args=(BODY,)),
    Call("assets", "update_airco", "PUT", "/api/v1/assets/aircos/asset-0",
         {"status": "ok"}, args=("asset-0", BODY)),
    Call("assets", "delete_airco", "DELETE", "/api/v1/assets/aircos/asset-0",
         {"status": "ok"}, args=("asset-0",)),

    Call("billing", "start_ideal_payment", "POST", "/api/v1/payments/ideal2/transactions/new",
         {"transaction_id": "TX-0"}, MGWCreateIDealTransactionResponse, args=(BODY,)),

    Call("enode", "link", "POST", "/api/v1/enode/users/me/link",
         {"link_url": "https://link.example/start"}, LinkResponse, args=(BODY,)),
    Call("enode", "relink_asset", "POST", "/api/v1/enode/assets/veh-0/relink",
         {"link_url": "https://link.example/again"}, LinkResponse, args=("veh-0", BODY)),
    Call("enode", "unlink_vehicle", "DELETE", "/api/v1/enode/users/me/vendors/ven-0/vehicle",
         {"status": "ok"}, args=("ven-0",)),
    Call("enode", "unlink_charger", "DELETE", "/api/v1/enode/users/me/vendors/ven-0/charger",
         {"status": "ok"}, args=("ven-0",)),
    Call("enode", "update_charger", "PUT", "/api/v1/enode/chargers/chg-0",
         {"id": "chg-0"}, EnodeCharger, args=("chg-0", BODY)),
    Call("enode", "set_charger_location", "PUT", "/api/v1/enode/chargers/chg-0",
         {"id": "chg-0"}, EnodeCharger, args=("chg-0", BODY)),
    Call("enode", "create_location", "POST", "/api/v1/enode/users/me/locations",
         {"id": "loc-0"}, EnodeLocation, args=(BODY,)),
    Call("enode", "delete_location", "DELETE", "/api/v1/enode/locations/loc-0",
         {"id": "loc-0"}, EnodeLocation, args=("loc-0",)),
    Call("enode", "set_location_zone", "POST", "/api/v1/enode/flex/locations/loc-0",
         {"status": "ok"}, args=("loc-0", BODY)),
    Call("enode", "create_policy", "POST", "/api/v1/enode/flex/vehicle-policies",
         {"id": "pol-0"}, ChargingPolicy, args=(BODY,)),
    Call("enode", "update_policy", "PATCH", "/api/v1/enode/flex/vehicle-policies/pol-0",
         {"id": "pol-0"}, ChargingPolicy, args=("pol-0", BODY)),
    Call("enode", "delete_policy", "DELETE", "/api/v1/enode/flex/vehicle-policies/pol-0",
         {"status": "ok"}, args=("pol-0",)),
    Call("enode", "set_session_target", "PUT", "/api/v1/enode/flex/sessions/ses-0/target",
         {"status": "ok"}, args=("ses-0", BODY)),
    Call("enode", "create_solar_configuration", "POST", "/api/v1/enode/solar-configurations",
         {"id": "cfg-0"}, EnodeSolarConfiguration, args=(BODY,)),
    Call("enode", "update_solar_configuration", "PATCH", "/api/v1/enode/solar-configurations/cfg-0",
         {"id": "cfg-0"}, EnodeSolarConfiguration, args=("cfg-0", BODY)),
    Call("enode", "delete_solar_configuration", "DELETE", "/api/v1/enode/solar-configurations/cfg-0",
         {"status": "ok"}, args=("cfg-0",)),

    Call("ev", "request_charge_card", "POST", "/api/v1/ev/charge-card-requests",
         {"status": "ok"}, args=(BODY,)),
    Call("ev", "request_charging_station_contact", "POST", "/api/v1/ev/charging-station-contact-requests",
         {"status": "ok"}, args=(BODY,)),
    Call("ev", "request_charging_station_quote", "POST", "/api/v2/ev/charging-station-quotation-requests",
         {"status": "ok"}, args=(BODY,)),
    Call("ev", "request_white_paper", "POST", "/api/v1/ev/white-paper-requests",
         {"status": "ok"}, args=(BODY,)),

    Call("happy_hour", "subscribe", "POST", "/api/v1/assets/happyhour", {"status": "ok"}, args=(BODY,)),
    Call("happy_hour", "unsubscribe", "DELETE", "/api/v1/assets/happyhour/sub-0",
         {"status": "ok"}, args=("sub-0",)),
    Call("happy_hour", "request_payout", "POST", "/api/v1/happyhour/payout", {"status": "ok"}),

    Call("legacy", "okta_token", "POST", "/api/v1/okta/token",
         {"access_token": "gateway-access-0"}, LoginDataTokenResponse,
         kwargs={"customer_id": "K00000000", "reason": "login"}),
    Call("legacy", "create_account", "POST", "/api/v2/create-account",
         {"status": "ok"}, args=({"customer_nr": "00000000"},)),
    Call("legacy", "register_non_customer", "POST", "/api/v1/register/non-customer",
         {"access_token": "gateway-access-0"}, AccessTokenResponse,
         args=({"username": "test@example.com"},)),
    Call("legacy", "forgot_password", "POST", "/api/v1/forgot-password",
         {"status": "ok"}, args=("test@example.com",)),

    Call("meter", "add_readings", "POST", "/api/v1/meterstands", {"status": "ok"}, args=(BODY,)),
    Call("meter", "register_dongle", "POST", "/api/v1/p1/register", {"status": "ok"}, args=(BODY,)),
    Call("meter", "request_correction", "POST", "/api/v1/meterstands/correction-request",
         {"status": "ok"}, args=(BODY,)),

    Call("smart_charging", "create_mandate", "POST", "/api/v1/smart-charging/mandate",
         {"status": "ok"}, args=(BODY,)),
    Call("smart_charging", "report_unsupported_vehicle", "POST",
         "/api/v1/smart-charging/vehicle/not-supported", {"status": "ok"}, args=(BODY,)),
    Call("smart_charging", "request_payout", "POST", "/api/v1/smart-charging/payout-rewards",
         {"status": "ok"}),

    Call("support", "submit_questionnaire", "POST", "/api/v1/questionnaire",
         {"status": "ok"}, args=(BODY,)),

    Call("tariffs", "set_for_address", "PUT", "/api/v1/tariffs/adr-0",
         {"status": "ok"}, args=("adr-0", BODY)),
]


def _answer(server: FakeServer, call: Call) -> None:
    server.json(call.route, call.reply, method=call.verb)


@pytest.mark.parametrize("call", READS + QUERIES, ids=[c.id for c in READS + QUERIES])
async def test_a_read_reaches_its_path_and_becomes_its_model(
    server: FakeServer, client: EngieClient, call: Call
) -> None:
    _answer(server, call)
    call.check(await call.invoke(client))
    assert (server.requests[-1].method, server.requests[-1].path) == (call.verb, call.route)


@pytest.mark.parametrize("call", WRITES, ids=[c.id for c in WRITES])
async def test_a_write_reaches_its_path_when_it_is_allowed(
    server: FakeServer, writer: EngieClient, call: Call
) -> None:
    _answer(server, call)
    call.check(await call.invoke(writer))
    assert (server.requests[-1].method, server.requests[-1].path) == (call.verb, call.route)


@pytest.mark.parametrize("call", WRITES, ids=[c.id for c in WRITES])
async def test_a_write_is_refused_without_allow_writes(
    server: FakeServer, client: EngieClient, call: Call
) -> None:
    """The gate is in one place so a new endpoint cannot forget it; prove it per endpoint."""
    _answer(server, call)
    with pytest.raises(EngieWriteBlocked) as err:
        await call.invoke(client)
    assert f"{call.verb} {call.path}" in str(err.value)
    assert "allow_writes=True" in str(err.value)
    assert server.requests == []


@pytest.mark.parametrize("call", READS + QUERIES, ids=[c.id for c in READS + QUERIES])
async def test_a_read_is_not_gated(server: FakeServer, client: EngieClient, call: Call) -> None:
    """A read on a read-only client must reach the gateway, not raise."""
    _answer(server, call)
    await call.invoke(client)
    assert len(server.requests) == 1


def test_the_table_covers_every_public_method(client: EngieClient) -> None:
    """A new endpoint added to a group and not to a table would slip through silently."""
    tabled = {call.id for call in READS + QUERIES + WRITES} | {
        # Their arguments build a query string or a form, so they are tested
        # below with the shape they must send.
        "account.settings_cards", "address.lookup", "address.metadata", "account.set_payment_info",
        "billing.mer_report", "billing.set_prepayment", "enode.sessions", "enode.intervention",
        "legacy.password_grant", "legacy.refresh_grant", "legacy.check_account", "legacy.initial_login",
        "mandates.grant", "mandates.withdraw", "meter.delete_readings", "meter.activate_dongle",
        "smart_charging.delete_mandate", "smart_charging.delete_user", "smart_charging.create_vehicle",
        "solar.potential", "solar.pre_check", "solar.request_quote", "solar.request_home_scan",
        "solar.request_energy_scan", "support.collective", "support.chat_categories",
        "support.send_feedback", "tariffs.get",
    }
    groups = ["account", "address", "assets", "billing", "enode", "ev", "happy_hour", "legacy",
              "mandates", "meter", "smart_charging", "solar", "support", "tariffs"]
    actual = {
        f"{group}.{name}"
        for group in groups
        for name in dir(getattr(client, group))
        if not name.startswith("_") and callable(getattr(getattr(client, group), name))
    }
    assert actual - tabled == set(), f"untested endpoint methods: {sorted(actual - tabled)}"


# --- the methods that build a query string -----------------------------------


async def test_settings_cards_adds_the_optional_address_parts(
    server: FakeServer, client: EngieClient
) -> None:
    server.json("/api/v1/settings/cards", {"cards": []})
    await client.account.settings_cards(zip_code="0000AA", house_number="1")
    assert query_of(server.requests[-1]) == {"address[zip_code]": ["0000AA"], "address[house_number]": ["1"]}

    result = await client.account.settings_cards(
        zip_code="0000AA", house_number="1", house_number_addition="A", customer_type="consumer"
    )
    assert query_of(server.requests[-1]) == {
        "address[zip_code]": ["0000AA"], "address[house_number]": ["1"],
        "address[house_number_addition]": ["A"], "customerType": ["consumer"],
    }
    assert isinstance(result, SettingsCardsResponse)


async def test_address_lookup_and_metadata_send_their_own_key_names(
    server: FakeServer, client: EngieClient
) -> None:
    """Two lookups of the same thing, and ENGIE names the parameters differently in each."""
    server.json("/api/v1/address", {"street": "Teststraat", "city": "Teststad"})
    server.json("/api/v1/address-metadata", {"has_connection": True})

    found = await client.address.lookup(zip_code="0000AA", house_number="1")
    assert query_of(server.requests[-1]) == {"nl_sixpp": ["0000AA"], "streetnumber": ["1"]}
    assert isinstance(found, Pro6PPResponse)

    await client.address.lookup(zip_code="0000AA", house_number="1", addition="A")
    assert query_of(server.requests[-1])["extension"] == ["A"]

    meta = await client.address.metadata(zip_code="0000AA", house_nr="1")
    assert query_of(server.requests[-1]) == {"zipCode": ["0000AA"], "houseNr": ["1"]}
    assert isinstance(meta, AddressMetaData)

    await client.address.metadata(zip_code="0000AA", house_nr="1", addition="A")
    assert query_of(server.requests[-1])["houseNrAddition"] == ["A"]


async def test_mer_report_comes_back_as_text(server: FakeServer, client: EngieClient) -> None:
    """The body is a file, not JSON, so the decoder hands back the text."""
    server.handle("GET", "/api/v1/mer/periods/2026-08/report", lambda _r: web.Response(text="%PDF-1.4"))
    assert await client.billing.mer_report("2026-08") == "%PDF-1.4"


async def test_enode_sessions_sends_only_the_filters_it_was_given(
    server: FakeServer, client: EngieClient
) -> None:
    server.json("/api/v1/enode/flex/vehicle-policies/sessions", {"data": [{"id": "ses-0"}]})

    sessions = await client.enode.sessions()
    assert server.requests[-1].query_string == ""
    assert [type(s) for s in sessions] == [EnodeChargingSession]

    await client.enode.sessions(vehicle_id="veh-0", location_id="loc-0", policy_id="pol-0")
    assert query_of(server.requests[-1]) == {
        "vehicleId": ["veh-0"], "locationId": ["loc-0"], "policyId": ["pol-0"]
    }

    await client.enode.sessions(policy_id="pol-0")
    assert query_of(server.requests[-1]) == {"policyId": ["pol-0"]}


async def test_enode_intervention_defaults_to_dutch(server: FakeServer, client: EngieClient) -> None:
    server.json("/api/v1/enode/interventions/int-0", {"id": "int-0"})
    result = await client.enode.intervention("int-0")
    assert query_of(server.requests[-1]) == {"language": ["nl"]}
    assert isinstance(result, EnodeIntervention)

    await client.enode.intervention("int-0", language="en")
    assert query_of(server.requests[-1]) == {"language": ["en"]}


async def test_collective_sends_both_ids(server: FakeServer, client: EngieClient) -> None:
    server.json("/api/v1/collective", {"id": "cmp-0"})
    result = await client.support.collective(campaign_id="cmp-0", broker_id="brk-0")
    assert query_of(server.requests[-1]) == {"campaignId": ["cmp-0"], "brokerId": ["brk-0"]}
    assert isinstance(result, CollectiveResponse)


async def test_chat_categories_sends_the_profile_filter_only_when_set(
    server: FakeServer, client: EngieClient
) -> None:
    """Seamly's paths are relative, because they hang off a different base_url."""
    server.json("/classifications/cls-0/categories", {"culture": "nl-NL"})
    result = await client.support.chat_categories("cls-0")
    assert server.requests[-1].query_string == ""
    assert isinstance(result, AbstractBaseResponse)

    await client.support.chat_categories("cls-0", profiles="engie")
    assert query_of(server.requests[-1]) == {"dim.Profiles": ["engie"]}


async def test_solar_potential_and_pre_check_take_one_ean_or_many(
    server: FakeServer, client: EngieClient
) -> None:
    server.json("/api/v1/solar-potential", [{"ean": EAN_E}])
    server.json("/api/v1/solar-potential-pre-check", [{"ean": EAN_E}])

    potential = await client.solar.potential(EAN_E)
    assert query_of(server.requests[-1]) == {"eans[]": [EAN_E]}
    assert [type(p) for p in potential] == [SolarPotential]

    checks = await client.solar.pre_check([EAN_E, EAN_G])
    assert query_of(server.requests[-1]) == {"eans[]": [EAN_E, EAN_G]}
    assert [type(c) for c in checks] == [PreCheck]


async def test_smart_charging_deletes_identify_the_enrolment_by_query(
    server: FakeServer, writer: EngieClient
) -> None:
    server.json("/api/v1/smart-charging/mandate", {"status": "ok"}, method="DELETE")
    server.json("/api/v1/smart-charging/user", {"status": "ok"}, method="DELETE")

    await writer.smart_charging.delete_mandate(
        contact_id="con-0", email_address="test@example.com", delivery_agreement_id="da-0"
    )
    assert query_of(server.requests[-1]) == {
        "contact_id": ["con-0"], "email_address": ["test@example.com"], "delivery_agreement_id": ["da-0"]
    }

    await writer.smart_charging.delete_user(contact_id="con-0", email_address="test@example.com")
    assert query_of(server.requests[-1]) == {
        "contact_id": ["con-0"], "email_address": ["test@example.com"]
    }


async def test_delete_readings_names_the_day_and_the_eans(
    server: FakeServer, writer: EngieClient
) -> None:
    """Withdrawing a filed reading: the wrong date here withdraws the wrong day."""
    server.json("/api/v1/meterstands", {"status": "ok"}, method="DELETE")
    await writer.meter.delete_readings([EAN_E, EAN_G], day=date(2026, 9, 8))
    assert query_of(server.requests[-1]) == {"date": ["2026-09-08"], "eans[]": [EAN_E, EAN_G]}


# --- the methods that build a form -------------------------------------------


async def test_set_payment_info_sends_the_iban_as_a_form(
    server: FakeServer, writer: EngieClient
) -> None:
    server.json("/api/v1/payment-info", {"status": "ok"}, method="PUT")
    await writer.account.set_payment_info(bank_account="NL00BANK0000000000", payment_method="incasso")
    assert server.forms[-1] == {"bank_account": "NL00BANK0000000000", "payment_method": "incasso"}


async def test_set_prepayment_sends_a_whole_euro_amount_per_ean(
    server: FakeServer, writer: EngieClient
) -> None:
    """This changes a direct debit, so the amount has to arrive as sent."""
    server.json("/api/v1/prepayment", [{"ean": EAN_E, "status": "ok"}], method="PUT")
    results = await writer.billing.set_prepayment([EAN_E, EAN_G], amount=180)
    assert server.multi_forms[-1] == {"amount": ["180"], "eans[]": [EAN_E, EAN_G]}
    assert [type(r) for r in results] == [PrepaymentResult]


async def test_mandate_grant_and_withdraw_carry_every_ean(
    server: FakeServer, writer: EngieClient
) -> None:
    """Withdrawing thins out the daily meter feed, so it must hit every EAN asked for."""
    server.json("/api/v1/mandates", [{"approval_version": "2"}], status=200, method="POST")
    server.json("/api/v1/withdraw-mandates", {"status": "ok"}, method="POST")

    granted = await writer.mandates.grant([EAN_E, EAN_G], current_version="2")
    assert server.multi_forms[-1] == {"eans[]": [EAN_E, EAN_G], "currentVersion": ["2"]}
    assert [type(g) for g in granted] == [ApprovalData]

    await writer.mandates.withdraw(EAN_E)
    assert server.multi_forms[-1] == {"eans[]": [EAN_E]}


async def test_activate_dongle_and_create_vehicle_send_one_field(
    server: FakeServer, writer: EngieClient
) -> None:
    server.json("/api/v1/p1/activate", {"status": "ok"}, method="POST")
    server.json("/api/v1/smart-charging/vehicle", {"id": "veh-0"}, method="POST")

    await writer.meter.activate_dongle("dongle-0")
    assert server.forms[-1] == {"dongle_id": "dongle-0"}

    created = await writer.smart_charging.create_vehicle("car-0")
    assert server.forms[-1] == {"car_id": "car-0"}
    assert isinstance(created, VehicleCreationResponse)


async def test_address_verify_sends_the_letter_code(server: FakeServer, writer: EngieClient) -> None:
    server.json("/api/v1/verify-address", {"status": "ok"}, method="POST")
    await writer.address.verify("000000")
    assert server.forms[-1] == {"code": "000000"}


async def test_send_feedback_and_the_scans_send_their_keys_verbatim(
    server: FakeServer, writer: EngieClient
) -> None:
    """The scan forms carry nested key names like ``usage_per_year[energy_in_kwh]``."""
    server.json("/api/v1/feedback", {"status": "ok"}, method="POST")
    server.json("/api/v1/woning-scan", {"status": "ok"}, method="POST")
    server.json("/api/v1/energie-scan", {"status": "ok"}, method="POST")

    reported = await writer.support.send_feedback({"feedback_type": "bug", "device": "Pixel 7"})
    assert server.forms[-1] == {"feedback_type": "bug", "device": "Pixel 7"}
    assert isinstance(reported, SimpleStatus)

    await writer.solar.request_home_scan({"zip_code": "0000AA", "house_nr": "1"})
    assert server.forms[-1] == {"zip_code": "0000AA", "house_nr": "1"}

    await writer.solar.request_energy_scan({"contact_person[first_name]": "Jane",
                                            "usage_per_year[energy_in_kwh]": "0"})
    assert server.forms[-1] == {"contact_person[first_name]": "Jane",
                                "usage_per_year[energy_in_kwh]": "0"}


async def test_solar_quote_sends_every_field_including_the_blank_ones(
    server: FakeServer, writer: EngieClient
) -> None:
    """The gateway rejects a form with a key missing, so the optional ones go as empty."""
    server.json("/api/v1/solar-quote", {"status": "ok"}, method="POST")
    await writer.solar.request_quote(
        first_name="Jane", last_name="Doe", email="test@example.com", phone="0000000000",
        zip_code="0000AA", street="Teststraat", city="Teststad", house_nr="1",
    )
    assert server.forms[-1] == {
        "first_name": "Jane", "middle_name": "", "last_name": "Doe", "email": "test@example.com",
        "phone": "0000000000", "zip_code": "0000AA", "street": "Teststraat", "city": "Teststad",
        "house_nr": "1", "house_nr_addition": "", "comment": "", "standard_period_quantity": "",
    }


# --- legacy: the pre-Okta gateway auth, which picks a path per argument -------


async def test_password_grant_picks_the_customer_or_non_customer_path(
    server: FakeServer, writer: EngieClient
) -> None:
    server.json("/api/v1/auth/customer", {"access_token": "gateway-access-0"}, method="POST")
    server.json("/api/v1/auth/non-customer", {"access_token": "gateway-access-0"}, method="POST")

    granted = await writer.legacy.password_grant(username="test@example.com", password="not-a-password")
    assert server.requests[-1].path == "/api/v1/auth/customer"
    assert server.forms[-1]["grant_type"] == "password"
    # The client id and secret identify the app, not a person; they are in the APK.
    assert server.forms[-1]["client_id"] == "1"
    assert isinstance(granted, AccessTokenResponse)
    assert "X-GRE-Token" not in server.requests[-1].headers

    await writer.legacy.password_grant(
        username="test@example.com", password="not-a-password", customer=False,
        recaptcha_token="recaptcha-0", recaptcha_key="recaptcha-key-0",
    )
    assert server.requests[-1].path == "/api/v1/auth/non-customer"
    assert server.requests[-1].headers["X-GRE-Token"] == "recaptcha-0"
    assert server.requests[-1].headers["X-GRE-Key"] == "recaptcha-key-0"


async def test_refresh_grant_picks_the_same_pair_of_paths(
    server: FakeServer, writer: EngieClient
) -> None:
    server.json("/api/v1/auth/customer/refresh", {"access_token": "gateway-access-1"}, method="POST")
    server.json("/api/v1/auth/non-customer/refresh", {"access_token": "gateway-access-1"}, method="POST")

    refreshed = await writer.legacy.refresh_grant("gateway-refresh-0")
    assert server.requests[-1].path == "/api/v1/auth/customer/refresh"
    assert server.forms[-1]["refresh_token"] == "gateway-refresh-0"
    assert isinstance(refreshed, AccessTokenResponse)

    await writer.legacy.refresh_grant("gateway-refresh-0", customer=False)
    assert server.requests[-1].path == "/api/v1/auth/non-customer/refresh"


async def test_check_account_and_initial_login_send_the_paper_account_details(
    server: FakeServer, writer: EngieClient
) -> None:
    server.json("/api/v3/check-account", {"exists": False}, method="POST")
    server.json("/api/v1/initial-login", {"status": "ok"}, method="POST")

    checked = await writer.legacy.check_account(customer_nr="00000000", postal_code="0000AA")
    assert server.forms[-1] == {"customer_nr": "00000000", "postal_code": "0000AA",
                                "house_nr": "", "username": "", "iban_last_three": ""}
    assert isinstance(checked, CheckAccountResponse)

    started = await writer.legacy.initial_login(
        customer_nr="00000000", zip_code="0000AA", house_nr="1", iban_last_three="000"
    )
    assert server.forms[-1] == {"customer_nr": "00000000", "zip_code": "0000AA",
                                "house_nr": "1", "iban_last_three": "000"}
    assert isinstance(started, InitialLoginResponse)


async def test_forgot_username_takes_the_api_version_from_the_caller(
    server: FakeServer, writer: EngieClient
) -> None:
    server.json("/api/v2/customers/me/forgot-username", {"status": "ok"}, method="POST")
    await writer.account.forgot_username(BODY, api_version="v2")
    assert server.requests[-1].path == "/api/v2/customers/me/forgot-username"


# --- the shapes the gateway sends that are not the happy one -----------------


async def test_a_list_endpoint_that_answers_an_object_gives_an_empty_list(
    server: FakeServer, client: EngieClient
) -> None:
    """``parse_list`` refuses to guess, so a body it does not recognise is no rows."""
    server.json("/api/v1/assets/solarpanels", {"message": "The route could not be found."})
    assert await client.assets.solar_panels() == []


async def test_an_object_endpoint_that_answers_a_list_gives_none(
    server: FakeServer, client: EngieClient
) -> None:
    server.json("/api/v1/enode/users/me", [])
    assert await client.enode.me() is None


async def test_an_ean_method_refuses_an_empty_list_before_asking(
    server: FakeServer, client: EngieClient
) -> None:
    with pytest.raises(ValueError, match="at least one EAN"):
        await client.solar.potential([])
    assert server.requests == []


async def test_a_missing_route_surfaces_the_gateways_own_words(
    server: FakeServer, client: EngieClient
) -> None:
    """Three mapped endpoints are gone from the server; a caller should see why."""
    server.json("/api/v2/smart-charging/cars",
                {"message": "The route api/v2/smart-charging/cars could not be found."}, status=404)
    with pytest.raises(EngieApiError) as err:
        await client.smart_charging.cars()
    assert err.value.status == 404
    assert err.value.detail == "The route api/v2/smart-charging/cars could not be found."
