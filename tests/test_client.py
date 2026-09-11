"""The gateway client against a loopback gateway."""

from __future__ import annotations

import asyncio
from datetime import date

import pytest

from engie_nl import (
    EngieRateLimited,
    EngieWriteBlocked,
    EngieApiError,
    EngieAuthError,
    EngieClient,
    EngieNetworkError,
    EnergyType,
    TokenSet,
    TransactionStatus,
)
from engie_nl.constants import APP_VERSION_CODE
from aiohttp import web

from tests.conftest import ACCESS, FakeServer, query_of

EAN_E = "871694840000000001"
EAN_G = "871694840000000002"


async def test_headers_and_bearer(server: FakeServer, client: EngieClient) -> None:
    server.json("/api/v1/user", {"customer_id": "K01234567"})
    await client.get_user()
    req = server.requests[-1]
    assert req.headers["Authorization"] == f"Bearer {ACCESS}"
    assert req.headers["X-Platform"] == "Android"
    assert req.headers["X-AppVersion"] == APP_VERSION_CODE
    assert req.headers["Accept"] == "application/json"
    assert req.headers["User-Agent"].startswith("ENGIE/")


async def test_get_user_maps_addresses(server: FakeServer, client: EngieClient) -> None:
    server.json(
        "/api/v1/user",
        {
            "customer_id": "K01234567",
            "email": "klant@example.com",
            "payment_method": "incasso",
            "delivery_addresses": [
                {
                    "id": "adr-1",
                    "street": "Straat",
                    "house_nr": "1",
                    "zip_code": "1234AB",
                    "city": "Stad",
                    "is_current_address": True,
                    "metering_points": [
                        {"ean": EAN_E, "type": "E", "smart": True, "single_tariff": False,
                         "sjv_normal": "1500", "sjv_low": 1500,
                         "current_product": {"name": "ENGIE Opgewekt", "start_date": "2026-09-09"},
                         "tariffs": {"tariff_normal": 0.27575, "tariff_low": 0.27575, "fixed_charge": 0.36838}},
                        {"ean": EAN_G, "type": "G", "smart": True},
                    ],
                }
            ],
        },
    )
    user = await client.get_user()
    assert user.customer_id == "K01234567"
    assert user.eans == [EAN_E, EAN_G]
    mp = user.metering_points[0]
    assert mp.kind == "E" and mp.smart is True and mp.single_tariff is False
    assert mp.sjv_normal == 1500
    assert mp.current_product is not None and mp.current_product.start_date == date(2026, 9, 9)
    assert mp.tariffs is not None and mp.tariffs.tariff_normal == pytest.approx(0.27575)
    assert user.metering_points[1].tariffs is None


async def test_get_consumptions_query_shape(server: FakeServer, client: EngieClient) -> None:
    server.json(
        "/api/v1/consumptions",
        [
            {"ean": EAN_E, "data": [
                {"date": "2026-09-01T00:00:00+02:00", "low": 3.5, "normal": 5.25, "return_low": 0, "return_normal": 1.0}
            ], "error": None},
            {"ean": EAN_G, "data": [], "error": {"fault_string": "no data yet"}},
        ],
    )
    series = await client.get_consumptions([EAN_E, EAN_G], start=date(2026, 9, 1), end=date(2026, 9, 7))
    q = query_of(server.requests[-1])
    assert q["from"] == ["2026-09-01"] and q["to"] == ["2026-09-07"]
    assert q["eans[]"] == [EAN_E, EAN_G]
    assert len(series) == 2
    day = series[0].data[0]
    assert day.day == date(2026, 9, 1)
    assert day.total == pytest.approx(8.75)
    assert day.total_return == pytest.approx(1.0)
    assert series[1].error == "no data yet"
    assert series[1].data == []


async def test_get_consumptions_default_window(server: FakeServer, client: EngieClient) -> None:
    server.json("/api/v1/consumptions", [])
    await client.get_consumptions(EAN_E, days=7)
    q = query_of(server.requests[-1])
    assert (date.fromisoformat(q["to"][0]) - date.fromisoformat(q["from"][0])).days == 7


async def test_get_consumptions_rejects_empty(client: EngieClient) -> None:
    with pytest.raises(ValueError):
        await client.get_consumptions([])


async def test_get_meter_readings(server: FakeServer, client: EngieClient) -> None:
    server.json(
        "/api/v2/meterstands",
        [{"ean": EAN_E, "data": [
            {"name": "Normaal", "type": "consumption", "sequence": 1, "readings": [
                {"date": "2026-09-01", "value": 12000, "source": "P4", "description": ""},
                {"date": "2026-09-08", "value": 12040, "source": "P4", "description": ""},
            ]},
        ]}],
    )
    readings = await client.get_meter_readings(EAN_E, start=date(2026, 9, 1), end=date(2026, 9, 8))
    q = query_of(server.requests[-1])
    assert q["start_date"] == ["2026-09-01"] and q["end_date"] == ["2026-09-08"]
    reg = readings[0].registers[0]
    assert reg.kind == "consumption"
    assert reg.latest is not None and reg.latest.value == 12040 and reg.latest.day == date(2026, 9, 8)


async def test_get_estimations(server: FakeServer, client: EngieClient) -> None:
    server.json(
        "/api/v1/estimations",
        {"prepayment_amount_current": 187, "prepayment_amount_advice": 195.5, "fault_string": None},
    )
    est = await client.get_estimations([EAN_E, EAN_G], amount=187)
    q = query_of(server.requests[-1])
    assert q["amount"] == ["187"]
    assert est.prepayment_amount_advice == pytest.approx(195.5)
    assert est.error is None


async def test_get_transactions(server: FakeServer, client: EngieClient) -> None:
    server.json(
        "/api/v1/transactions",
        {"transactions": [
            {"id": "t1", "date": "2026-10-01T00:00:00+02:00", "amount": -187.0, "status": "PAID", "type": "prepayment",
             "attachment": {"reference": "doc-1", "title": "Termijnnota"}},
            {"id": "t2", "date": "2026-11-01", "amount": -187.0, "status": "weird"},
        ]},
    )
    tx = await client.get_transactions()
    assert tx[0].status is TransactionStatus.PAID
    assert tx[0].attachment is not None and tx[0].attachment.reference == "doc-1"
    assert tx[1].status is TransactionStatus.UNKNOWN


async def test_get_day_ahead_prices(server: FakeServer, client: EngieClient) -> None:
    server.json(
        "/api/v1/tariffs/day-ahead",
        [{"bare_tariff_per_unit": 0.12, "bare_tariff_per_unit_ex": 0.0992,
          "start_date_time": "2026-09-08T00:00:00+02:00", "end_date_time": "2026-09-08T01:00:00+02:00", "type": "E"}],
    )
    prices = await client.get_day_ahead_prices(EnergyType.ELECTRICITY, start=date(2026, 9, 8), end=date(2026, 9, 9))
    q = query_of(server.requests[-1])
    assert q["type"] == ["E"]
    assert prices[0].price == pytest.approx(0.12)
    assert prices[0].start is not None and prices[0].start.hour == 0


async def test_get_mandates_and_outages(server: FakeServer, client: EngieClient) -> None:
    server.json("/api/v1/mandates", [{"ean": EAN_E, "data": {"approval_version": "2", "start_date": "2026-09-09"}}])
    server.json("/api/v1/outages", [{"id": "o1", "title": "Storing", "hyperlink": {"ref": "https://x", "text": "meer"}}])
    mandates = await client.get_mandates(EAN_E)
    assert mandates[0].active is True
    outages = await client.get_outages("K01234567")
    assert query_of(server.requests[-1])["customerId"] == ["K01234567"]
    assert outages[0].link_url == "https://x"


async def test_api_error_carries_body(server: FakeServer, client: EngieClient) -> None:
    server.json("/api/v1/user", {"fault_string": "boom"}, status=500)
    with pytest.raises(EngieApiError) as err:
        await client.get_user()
    assert err.value.status == 500
    assert err.value.body == {"fault_string": "boom"}


async def test_401_refreshes_once_and_retries(okta_ok: FakeServer, client: EngieClient) -> None:
    seen: list[str] = []
    okta_ok.sequence("/api/v1/user", (401, {"message": "Unauthenticated."}), (200, {"customer_id": "K1"}))
    client._on_tokens_updated = lambda ts: seen.append(ts.access_token)  # pylint: disable=protected-access
    user = await client.get_user()
    assert user.customer_id == "K1"
    assert seen == ["okta-access-2"]
    gateway_calls = [r for r in okta_ok.requests if r.path == "/api/v1/user"]
    assert gateway_calls[-1].headers["Authorization"] == "Bearer okta-access-2"


async def test_401_twice_is_an_auth_error(okta_ok: FakeServer, client: EngieClient) -> None:
    okta_ok.json("/api/v1/user", {"message": "Unauthenticated."}, status=401)
    with pytest.raises(EngieAuthError):
        await client.get_user()


async def test_expired_token_refreshes_before_request(okta_ok: FakeServer, server: FakeServer) -> None:
    from engie_nl import OktaAuth  # pylint: disable=import-outside-toplevel

    auth = OktaAuth(client_id="0oatest", issuer=f"{server.url}/oauth2/default", org_url=server.url, timeout=5)
    stale = TokenSet(access_token="stale", refresh_token="okta-refresh-1", expires_at=1.0)
    server.json("/api/v1/user", {"customer_id": "K1"})
    async with EngieClient(stale, auth=auth, base_url=server.url, timeout=5) as c:
        await c.get_user()
        assert c.tokens.access_token == "okta-access-2"
    await auth.close()
    gateway_calls = [r for r in server.requests if r.path == "/api/v1/user"]
    assert len(gateway_calls) == 1
    assert gateway_calls[0].headers["Authorization"] == "Bearer okta-access-2"


async def test_expired_token_without_auth_is_auth_error(server: FakeServer) -> None:
    stale = TokenSet(access_token="stale", refresh_token=None, expires_at=1.0)
    server.json("/api/v1/user", {"message": "Unauthenticated."}, status=401)
    async with EngieClient(stale, base_url=server.url, timeout=5) as c:
        with pytest.raises(EngieAuthError):
            await c.get_user()


async def test_get_retries_a_stalled_request(server: FakeServer, tokens: TokenSet) -> None:
    """The gateway stalls at random; one attempt would lose the poll."""
    calls = {"n": 0}

    async def flaky(_request: web.Request) -> web.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            await asyncio.sleep(0.4)
        return web.json_response({"customer_id": "K1"})

    server.handle("GET", "/api/v1/user", flaky)
    async with EngieClient(tokens, base_url=server.url, timeout=0.1, retry_backoff=0) as client:
        user = await client.get_user()
    assert user.customer_id == "K1"
    assert calls["n"] == 3


async def test_get_gives_up_after_three_attempts(server: FakeServer, tokens: TokenSet) -> None:
    calls = {"n": 0}

    async def always_slow(_request: web.Request) -> web.Response:
        calls["n"] += 1
        await asyncio.sleep(0.4)
        return web.json_response({})

    server.handle("GET", "/api/v1/user", always_slow)
    async with EngieClient(tokens, base_url=server.url, timeout=0.1, retry_backoff=0) as client:
        with pytest.raises(EngieNetworkError):
            await client.get_user()
    assert calls["n"] == 3


async def test_an_error_status_is_not_retried(server: FakeServer, tokens: TokenSet) -> None:
    """A 500 is the gateway's answer, not a stall; retrying it only doubles the load."""
    calls = {"n": 0}

    def failing(_request: web.Request) -> web.Response:
        calls["n"] += 1
        return web.json_response({"fault_string": "boom"}, status=500)

    server.handle("GET", "/api/v1/user", failing)
    async with EngieClient(tokens, base_url=server.url, timeout=5, retry_backoff=0) as client:
        with pytest.raises(EngieApiError):
            await client.get_user()
    assert calls["n"] == 1


async def test_consumption_error_reads_the_live_message_key(server: FakeServer, client: EngieClient) -> None:
    """The live gateway sends {"message": "not-owned"}, not the app's fault_string."""
    server.json("/api/v1/consumptions", [{"ean": EAN_E, "data": [], "error": {"message": "not-owned"}}])
    series = await client.get_consumptions(EAN_E, days=1)
    assert series[0].error == "not-owned"


async def test_a_write_is_refused_by_default(server: FakeServer, client: EngieClient) -> None:
    """POST /api/v1/meterstands files a reading with the supplier who bills you."""
    with pytest.raises(EngieWriteBlocked) as err:
        await client.meter.add_readings({"eans": [EAN_E]})
    assert "allow_writes=True" in str(err.value)
    assert not [r for r in server.requests if r.method != "GET"]


async def test_a_write_goes_through_when_allowed(server: FakeServer, tokens: TokenSet) -> None:
    server.json("/api/v1/meterstands", {"ok": True}, method="POST")
    async with EngieClient(tokens, base_url=server.url, timeout=5, allow_writes=True) as c:
        await c.meter.add_readings({"eans": [EAN_E]})
    assert server.requests[-1].method == "POST"


async def test_a_post_that_reads_needs_no_permission(server: FakeServer, client: EngieClient) -> None:
    """POST /api/v1/p4-errors sends a body to read P4 status back; it changes nothing."""
    server.json("/api/v1/p4-errors", [{"ean": EAN_E}], method="POST")
    await client.meter.p4_errors({"eans": [EAN_E]})
    assert server.requests[-1].path == "/api/v1/p4-errors"


async def test_tariffs_sends_both_dates_and_the_ean_array(server: FakeServer, client: EngieClient) -> None:
    server.json("/api/v1/tariffs", {"tariffs": [{"ean": EAN_E, "price_ex": 0.22787, "tax": 0.04788,
                                                 "tariff_type": "PEAK", "unit_of_measure": "PER_UNIT"}],
                                    "types": [{"ean": EAN_E, "is_single": False}]})
    result = await client.tariffs.get(EAN_E, start=date(2026, 9, 9), end=date(2026, 10, 31))
    q = query_of(server.requests[-1])
    assert q["date_from"] == ["2026-09-09"] and q["date_to"] == ["2026-10-31"]
    assert q["eans[]"] == [EAN_E]
    assert result is not None
    assert result.tariffs[0].price_ex == pytest.approx(0.22787)
    assert result.tariffs[0].tariff_type == "PEAK"
    assert result.types[0].is_single is False


async def test_a_429_is_not_an_auth_failure(server: FakeServer, tokens: TokenSet) -> None:
    """A rate limit must not reach a caller as "your credentials are wrong".

    Home Assistant turns EngieAuthError into ConfigEntryAuthFailed, which stops
    the coordinator until a human logs in again. On 2026-09-09 one 429 from
    Okta did exactly that for 21 hours.
    """
    calls = {"n": 0}

    def limited(_request: web.Request) -> web.Response:
        calls["n"] += 1
        return web.json_response({}, status=429, headers={"Retry-After": "60"})

    server.handle("GET", "/api/v1/user", limited)
    async with EngieClient(tokens, base_url=server.url, timeout=5, retry_backoff=0) as client:
        with pytest.raises(EngieRateLimited) as err:
            await client.get_user()
    assert not isinstance(err.value, EngieAuthError)
    assert isinstance(err.value, EngieNetworkError)
    # One attempt, not three: retrying a rate limit extends it.
    assert calls["n"] == 1


async def test_okta_429_on_refresh_is_a_rate_limit(okta_ok: FakeServer, tokens: TokenSet) -> None:
    from engie_nl import OktaAuth  # pylint: disable=import-outside-toplevel

    okta_ok.json("/oauth2/default/v1/token", {}, status=429, method="POST")
    auth = OktaAuth(client_id="0oatest", issuer=f"{okta_ok.url}/oauth2/default",
                    org_url=okta_ok.url, timeout=5)
    stale = TokenSet(access_token="stale", refresh_token="okta-refresh-1", expires_at=1.0)
    with pytest.raises(EngieRateLimited) as err:
        await auth.refresh(stale)
    await auth.close()
    assert err.value.retry_after == 60.0 or err.value.retry_after is None


async def test_a_window_that_runs_backwards_is_refused(client: EngieClient) -> None:
    """An end before the start asks the gateway for nothing, so fail before asking."""
    with pytest.raises(ValueError, match="start must not be after end"):
        await client.get_consumptions(EAN_E, start=date(2026, 9, 8), end=date(2026, 9, 1))


async def test_a_client_without_auth_cannot_refresh(server: FakeServer) -> None:
    """An expired token and nothing to refresh it with is a login, not a retry."""
    stale = TokenSet(access_token="stale", refresh_token="okta-refresh-1", expires_at=1.0)
    async with EngieClient(stale, base_url=server.url, timeout=5) as c:
        with pytest.raises(EngieAuthError, match="no OktaAuth was given"):
            await c.refresh_tokens()
    assert server.requests == []


async def test_an_async_tokens_callback_is_awaited(okta_ok: FakeServer, client: EngieClient) -> None:
    """Home Assistant persists the pair with an async store; a coroutine must not be dropped."""
    saved: list[str] = []

    async def store(new: TokenSet) -> None:
        saved.append(new.access_token)

    client._on_tokens_updated = store  # pylint: disable=protected-access
    okta_ok.sequence("/api/v1/user", (401, {"message": "Unauthenticated."}), (200, {"customer_id": "K1"}))
    await client.get_user()
    assert saved == ["okta-access-2"]


async def test_user_and_estimations_refuse_a_body_that_is_not_an_object(
    server: FakeServer, client: EngieClient
) -> None:
    """Both return a single record; a list means the gateway answered something else."""
    server.json("/api/v1/user", [])
    server.json("/api/v1/estimations", [])
    with pytest.raises(EngieApiError, match="unexpected /user body"):
        await client.get_user()
    with pytest.raises(EngieApiError, match="unexpected /estimations body"):
        await client.get_estimations(EAN_E, amount=180)


async def test_transactions_and_documents_accept_both_envelopes(
    server: FakeServer, client: EngieClient
) -> None:
    """Both endpoints have been seen bare and wrapped in a named key."""
    server.json("/api/v1/transactions", [{"id": "t1", "amount": -180.0, "status": "PAID"}])
    assert [t.id for t in await client.get_transactions()] == ["t1"]

    server.json("/api/v1/documents", {"documents": [{"reference": "DOC-0", "title": "Termijnnota"}]})
    wrapped = await client.get_documents()
    assert [d.reference for d in wrapped] == ["DOC-0"]

    server.json("/api/v1/documents", [{"reference": "DOC-1", "title": "Jaarnota"}])
    assert [d.reference for d in await client.get_documents()] == ["DOC-1"]


async def test_mer_periods_and_opening_hours(server: FakeServer, client: EngieClient) -> None:
    server.json("/api/v1/mer/periods", [{"id": "2026-08", "startDate": "2026-08-01"}])
    periods = await client.get_mer_periods()
    assert periods[0].id == "2026-08" and periods[0].start_date == date(2026, 8, 1)

    # No model yet, so the body comes back as the gateway sent it.
    server.json("/api/v1/opening-hours", {"days": [{"day": "monday", "open": "08:00"}]})
    assert await client.get_opening_hours() == {"days": [{"day": "monday", "open": "08:00"}]}


async def test_day_ahead_prices_default_to_today_and_tomorrow(
    server: FakeServer, client: EngieClient
) -> None:
    server.json("/api/v1/tariffs/day-ahead", [])
    await client.get_day_ahead_prices("G")
    q = query_of(server.requests[-1])
    assert q["type"] == ["G"]
    assert (date.fromisoformat(q["end_date"][0]) - date.fromisoformat(q["start_date"][0])).days == 1
    assert date.fromisoformat(q["start_date"][0]) == date.today()
