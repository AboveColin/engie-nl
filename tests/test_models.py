"""Model coercion rules."""

from __future__ import annotations

from datetime import date, datetime

from engie_nl.models import (
    Consumption,
    ConsumptionSeries,
    DeliveryAddress,
    Mandate,
    MerPeriod,
    MeteringPoint,
    Reading,
    Register,
    _bool,
    _date,
    _dt,
    _int,
    _num,
)


def test_num_int_bool_tolerate_strings_and_empties() -> None:
    assert _num("0.27575") == 0.27575
    assert _num("") is None and _num(None) is None and _num("abc") is None
    assert _int("12") == 12 and _int(12.9) == 12 and _int(None) is None
    assert _bool("true") is True and _bool("0") is False and _bool(1) is True and _bool("x") is None


def test_date_and_datetime_parsing() -> None:
    assert _date("2026-09-09") == date(2026, 9, 9)
    assert _date("2026-09-09T00:00:00+02:00") == date(2026, 9, 9)
    assert _date("not a date") is None
    parsed = _dt("2026-09-09T13:00:00Z")
    assert isinstance(parsed, datetime) and parsed.utcoffset() is not None
    assert _dt("garbage") is None


def test_consumption_totals_are_none_when_no_parts() -> None:
    empty = Consumption.from_api({"date": "2026-09-01"})
    assert empty.total is None and empty.total_return is None
    gas = Consumption.from_api({"date": "2026-09-01", "normal": 2.5})
    assert gas.total == 2.5 and gas.low is None


def test_register_latest_ignores_undated() -> None:
    reg = Register.from_api({"name": "n", "readings": [{"value": 1}, {"date": "2026-01-02", "value": 2}, {"date": "2026-01-01", "value": 3}]})
    assert reg.latest is not None and reg.latest.value == 2
    assert Register.from_api({"name": "n", "readings": []}).latest is None
    assert Reading.from_api({}).day is None


def test_mandate_active_needs_version_and_no_end() -> None:
    assert Mandate.from_api({"ean": "1", "data": {"approval_version": "1"}}).active is True
    assert Mandate.from_api({"ean": "1", "data": {"approval_version": "1", "end_date": "2026-01-01"}}).active is False
    assert Mandate.from_api({"ean": "1", "data": {}}).active is False


def test_mer_period_accepts_both_spellings() -> None:
    assert MerPeriod.from_api({"id": "a", "startDate": "2026-08-01"}).start_date == date(2026, 8, 1)
    assert MerPeriod.from_api({"id": "a", "start_date": "2026-08-01"}).start_date == date(2026, 8, 1)


def test_engie_writes_an_unset_date_as_year_one() -> None:
    """The live /user record uses 0001-01-01T00:00:00+00:19 to mean "no data yet"."""
    point = MeteringPoint.from_api(
        {"ean": "871694840000000001", "type": "ELK", "has_data": False,
         "data_from": "0001-01-01T00:00:00+00:19", "data_to": "0001-01-01T00:00:00+00:19",
         "start_date": "2026-09-09T02:00:00+02:00"}
    )
    assert point.data_from is None
    assert point.data_to is None
    assert point.start_date == date(2026, 9, 9)


def test_date_needs_a_full_ten_characters() -> None:
    """The gateway sends "2026-09" for a MER period id; that is not a date."""
    assert _date("2026-09") is None
    assert _date("") is None


def test_delivery_address_lists_its_own_eans() -> None:
    """A customer with two addresses polls each one's EANs separately."""
    address = DeliveryAddress.from_api(
        {"id": "adr-0", "street": "Teststraat", "metering_points": [
            {"ean": "871694840000000001", "type": "ELK"},
            {"ean": "", "type": "GAS"},
            {"type": "GAS"},
        ]}
    )
    assert address.eans == ["871694840000000001"]


def test_a_consumption_error_that_is_not_an_object_is_kept_as_text() -> None:
    """The error key has been seen as an object and as a bare string."""
    assert ConsumptionSeries.from_api({"ean": "1", "error": "not-owned"}).error == "not-owned"
    assert ConsumptionSeries.from_api({"ean": "1", "error": None}).error is None
    assert ConsumptionSeries.from_api({"ean": "1", "error": {"detail": "no data"}}).error == "no data"
    assert ConsumptionSeries.from_api({"ean": "1", "error": {"details": "no data"}}).error == "no data"
