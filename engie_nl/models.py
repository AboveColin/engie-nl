"""Typed models for the ENGIE gateway responses.

Each model has a ``from_api`` classmethod that maps the gateway's snake_case
JSON into a documented shape and keeps the original payload on ``raw`` for
anything not modelled yet. Field names follow the wire names so a reader can
match them against ``docs/engie-nl/ENDPOINTS_AND_MODELS.md`` without a
translation table.

Numbers are coerced with tolerance: the gateway is a PHP/Laravel service and
has been seen to return numbers as strings in other ENGIE surfaces. Missing
values are ``None``, never a guessed zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any


def _num(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    num = _num(value)
    return int(num) if num is not None else None


def _str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text != "" else None


def _bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        low = value.strip().lower()
        if low in ("true", "1", "yes"):
            return True
        if low in ("false", "0", "no"):
            return False
    return None


def _dt(value: Any) -> datetime | None:
    """Parse the gateway's ISO-8601 timestamps (``2026-09-01T00:00:00+02:00``)."""
    text = _str(value)
    if text is None:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _date(value: Any) -> date | None:
    """Parse a date, accepting a bare ``YYYY-MM-DD`` or a full timestamp."""
    if value is None:
        return None
    text: str = str(value).strip()
    if len(text) < 10:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


class EnergyType(StrEnum):
    """The gateway's one-letter energy type, used by the day-ahead endpoint."""

    ELECTRICITY = "E"
    GAS = "G"


class TransactionStatus(StrEnum):
    """Wire values of ``TransactionStatus`` in the app."""

    OPEN = "OPEN"
    PAID = "PAID"
    REFUNDED = "REFUNDED"
    REFUND_PENDING = "REFUND_PENDING"
    PENDING = "PENDING"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def parse(cls, value: Any) -> TransactionStatus:
        try:
            return cls(str(value).upper())
        except ValueError:
            return cls.UNKNOWN


# --- account ---------------------------------------------------------------


@dataclass
class ProductInfo:
    """A supply product on a metering point (``current_product`` / ``next_product``)."""

    name: str | None
    product_type: str | None
    start_date: date | None
    end_date: date | None
    signed_date: date | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ProductInfo:
        return cls(
            name=_str(data.get("name")),
            product_type=_str(data.get("product_type")),
            start_date=_date(data.get("start_date")),
            end_date=_date(data.get("end_date")),
            signed_date=_date(data.get("signed_date")),
            raw=data,
        )


@dataclass
class Tariffs:
    """Contract tariffs per metering point, EUR per kWh or m3, VAT included unless ``_ex``.

    Only the fields a dashboard needs are typed; ``raw`` holds all 52 keys the
    app models (see the reference doc under ``Tariffs``).
    """

    tariff_normal: float | None
    tariff_low: float | None
    tariff_single: float | None
    return_tariff_normal: float | None
    return_tariff_low: float | None
    return_tariff_single: float | None
    fixed_charge: float | None
    operator_fee: float | None
    tax: float | None
    tax_credit: float | None
    tax_renewable_energy: float | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Tariffs:
        return cls(
            tariff_normal=_num(data.get("tariff_normal")),
            tariff_low=_num(data.get("tariff_low")),
            tariff_single=_num(data.get("tariff_single")),
            return_tariff_normal=_num(data.get("return_tariff_normal")),
            return_tariff_low=_num(data.get("return_tariff_low")),
            return_tariff_single=_num(data.get("return_tariff_single")),
            fixed_charge=_num(data.get("fixed_charge")),
            operator_fee=_num(data.get("operator_fee")),
            tax=_num(data.get("tax")),
            tax_credit=_num(data.get("tax_credit")),
            tax_renewable_energy=_num(data.get("tax_renewable_energy")),
            raw=data,
        )


@dataclass
class MeteringPoint:
    """One EAN on a delivery address.

    ``kind`` is the gateway's ``type`` field. Its value set is not enumerated in
    the app; expect ``E`` and ``G`` or spelled-out words, and read ``raw`` if a
    new value shows up. ``smart`` says whether P4 (smart meter) data flows.
    """

    ean: str
    kind: str | None
    smart: bool | None
    single_tariff: bool | None
    readable: bool | None
    has_data: bool | None
    status: str | None
    status_code: str | None
    market_segment: str | None
    grid_owner_name: str | None
    grid_owner_ean: str | None
    meter_id: str | None
    start_date: date | None
    end_date: date | None
    data_from: date | None
    data_to: date | None
    prepayment_amount: float | None
    next_prepayment_amount: float | None
    sjv_normal: int | None
    sjv_low: int | None
    sjv_single: int | None
    sjv_return_normal: int | None
    sjv_return_low: int | None
    sjv_return_single: int | None
    current_product: ProductInfo | None
    next_product: ProductInfo | None
    tariffs: Tariffs | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MeteringPoint:
        cur = data.get("current_product")
        nxt = data.get("next_product")
        tar = data.get("tariffs")
        return cls(
            ean=str(data.get("ean", "")),
            kind=_str(data.get("type")),
            smart=_bool(data.get("smart")),
            single_tariff=_bool(data.get("single_tariff")),
            readable=_bool(data.get("readable")),
            has_data=_bool(data.get("has_data")),
            status=_str(data.get("status")),
            status_code=_str(data.get("status_code")),
            market_segment=_str(data.get("market_segment")),
            grid_owner_name=_str(data.get("grid_owner_name")),
            grid_owner_ean=_str(data.get("grid_owner_ean")),
            meter_id=_str(data.get("meter_id")),
            start_date=_date(data.get("start_date")),
            end_date=_date(data.get("end_date")),
            data_from=_date(data.get("data_from")),
            data_to=_date(data.get("data_to")),
            prepayment_amount=_num(data.get("prepayment_amount")),
            next_prepayment_amount=_num(data.get("next_prepayment_amount")),
            sjv_normal=_int(data.get("sjv_normal")),
            sjv_low=_int(data.get("sjv_low")),
            sjv_single=_int(data.get("sjv_single")),
            sjv_return_normal=_int(data.get("sjv_return_normal")),
            sjv_return_low=_int(data.get("sjv_return_low")),
            sjv_return_single=_int(data.get("sjv_return_single")),
            current_product=ProductInfo.from_api(cur) if isinstance(cur, dict) else None,
            next_product=ProductInfo.from_api(nxt) if isinstance(nxt, dict) else None,
            tariffs=Tariffs.from_api(tar) if isinstance(tar, dict) else None,
            raw=data,
        )


@dataclass
class DeliveryAddress:
    """A supply address with its metering points (``delivery_addresses[]``)."""

    id: str | None
    street: str | None
    house_nr: str | None
    house_nr_addition: str | None
    zip_code: str | None
    city: str | None
    is_current_address: bool | None
    metering_points: list[MeteringPoint]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DeliveryAddress:
        return cls(
            id=_str(data.get("id")),
            street=_str(data.get("street")),
            house_nr=_str(data.get("house_nr")),
            house_nr_addition=_str(data.get("house_nr_addition")),
            zip_code=_str(data.get("zip_code")),
            city=_str(data.get("city")),
            is_current_address=_bool(data.get("is_current_address")),
            metering_points=[
                MeteringPoint.from_api(mp) for mp in _list(data.get("metering_points")) if isinstance(mp, dict)
            ],
            raw=data,
        )

    @property
    def eans(self) -> list[str]:
        """EANs of this address, in gateway order."""
        return [mp.ean for mp in self.metering_points if mp.ean]


@dataclass
class User:
    """``GET /api/v1/user``: the customer, the contact details and the addresses."""

    customer_id: str | None
    contact_id: str | None
    email: str | None
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    phone: str | None
    mobile: str | None
    payment_method: str | None
    bank_account: str | None
    group: str | None
    street: str | None
    house_nr: str | None
    house_nr_addition: str | None
    zip_code: str | None
    city: str | None
    delivery_addresses: list[DeliveryAddress]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> User:
        return cls(
            customer_id=_str(data.get("customer_id")),
            contact_id=_str(data.get("contact_id")),
            email=_str(data.get("email")),
            first_name=_str(data.get("first_name")),
            middle_name=_str(data.get("middle_name")),
            last_name=_str(data.get("last_name")),
            phone=_str(data.get("phone")),
            mobile=_str(data.get("mobile")),
            payment_method=_str(data.get("payment_method")),
            bank_account=_str(data.get("bank_account")),
            group=_str(data.get("group")),
            street=_str(data.get("street")),
            house_nr=_str(data.get("house_nr")),
            house_nr_addition=_str(data.get("house_nr_addition")),
            zip_code=_str(data.get("zip_code")),
            city=_str(data.get("city")),
            delivery_addresses=[
                DeliveryAddress.from_api(a) for a in _list(data.get("delivery_addresses")) if isinstance(a, dict)
            ],
            raw=data,
        )

    @property
    def metering_points(self) -> list[MeteringPoint]:
        """Every metering point across all delivery addresses."""
        return [mp for a in self.delivery_addresses for mp in a.metering_points]

    @property
    def eans(self) -> list[str]:
        """Every EAN across all delivery addresses; the input for the per-EAN endpoints."""
        return [mp.ean for mp in self.metering_points if mp.ean]


# --- consumption -------------------------------------------------------------


@dataclass
class Consumption:
    """One day of consumption for one EAN.

    Electricity has ``normal`` and ``low`` (normaal/dal) in kWh and the
    ``return_*`` pair for teruglevering. Gas fills only ``normal`` in m3.
    """

    day: date | None
    normal: float | None
    low: float | None
    return_normal: float | None
    return_low: float | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Consumption:
        return cls(
            day=_date(data.get("date")),
            normal=_num(data.get("normal")),
            low=_num(data.get("low")),
            return_normal=_num(data.get("return_normal")),
            return_low=_num(data.get("return_low")),
            raw=data,
        )

    @property
    def total(self) -> float | None:
        """``normal + low``; ``None`` when neither register reported."""
        parts = [v for v in (self.normal, self.low) if v is not None]
        return sum(parts) if parts else None

    @property
    def total_return(self) -> float | None:
        """``return_normal + return_low``; ``None`` when neither reported."""
        parts = [v for v in (self.return_normal, self.return_low) if v is not None]
        return sum(parts) if parts else None


@dataclass
class ConsumptionSeries:
    """``GET /api/v1/consumptions`` for one EAN."""

    ean: str
    data: list[Consumption]
    error: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ConsumptionSeries:
        err = data.get("error")
        error: str | None = None
        if isinstance(err, dict):
            # "message" is what the live gateway sends ({"message": "not-owned"}
            # for a connection ENGIE does not supply yet); the other three come
            # from the app's Error model.
            error = (
                _str(err.get("message"))
                or _str(err.get("fault_string"))
                or _str(err.get("detail"))
                or _str(err.get("details"))
            )
        elif err is not None:
            error = _str(err)
        return cls(
            ean=str(data.get("ean", "")),
            data=[Consumption.from_api(c) for c in _list(data.get("data")) if isinstance(c, dict)],
            error=error,
            raw=data,
        )


@dataclass
class Reading:
    """One meter reading. ``value`` is whole kWh or m3 as the gateway sends it."""

    day: date | None
    value: int | None
    source: str | None
    description: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Reading:
        return cls(
            day=_date(data.get("date")),
            value=_int(data.get("value")),
            source=_str(data.get("source")),
            description=_str(data.get("description")),
            raw=data,
        )


@dataclass
class Register:
    """A meter register (telwerk): normaal, dal, or their return counterparts."""

    name: str | None
    kind: str | None
    sequence: int | None
    readings: list[Reading]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Register:
        return cls(
            name=_str(data.get("name")),
            kind=_str(data.get("type")),
            sequence=_int(data.get("sequence")),
            readings=[Reading.from_api(r) for r in _list(data.get("readings")) if isinstance(r, dict)],
            raw=data,
        )

    @property
    def latest(self) -> Reading | None:
        """The most recent dated reading; undated rows are ignored."""
        dated = [r for r in self.readings if r.day is not None]
        return max(dated, key=lambda r: r.day or date.min) if dated else None


@dataclass
class MeterReadings:
    """``GET /api/v2/meterstands`` for one EAN."""

    ean: str
    registers: list[Register]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MeterReadings:
        return cls(
            ean=str(data.get("ean", "")),
            registers=[Register.from_api(r) for r in _list(data.get("data")) if isinstance(r, dict)],
            raw=data,
        )


# --- money -------------------------------------------------------------------


@dataclass
class EstimationCosts:
    """``GET /api/v1/estimations``: termijnbedrag advice and the projected year bill.

    Every amount also exists with an ``_ex_vat`` twin in ``raw``.
    """

    prepayment_amount_current: float | None
    prepayment_amount_advice: float | None
    prepayment_amount_min: float | None
    prepayment_amount_max: float | None
    to_pay_amount_min: float | None
    to_pay_amount_max: float | None
    to_pay_balance_amount: float | None
    total_estimated_nota_amount: float | None
    total_estimated_prepayment_amount: float | None
    total_paid_pre_payment_amount: float | None
    number_of_prepayments_left: float | None
    error: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EstimationCosts:
        return cls(
            prepayment_amount_current=_num(data.get("prepayment_amount_current")),
            prepayment_amount_advice=_num(data.get("prepayment_amount_advice")),
            prepayment_amount_min=_num(data.get("prepayment_amount_min")),
            prepayment_amount_max=_num(data.get("prepayment_amount_max")),
            to_pay_amount_min=_num(data.get("to_pay_amount_min")),
            to_pay_amount_max=_num(data.get("to_pay_amount_max")),
            to_pay_balance_amount=_num(data.get("to_pay_balance_amount")),
            total_estimated_nota_amount=_num(data.get("total_estimated_nota_amount")),
            total_estimated_prepayment_amount=_num(data.get("total_estimated_prepayment_amount")),
            total_paid_pre_payment_amount=_num(data.get("total_paid_pre_payment_amount")),
            number_of_prepayments_left=_num(data.get("number_of_prepayments_left")),
            error=_str(data.get("fault_string")) or _str(data.get("error")),
            raw=data,
        )


@dataclass
class DocumentRef:
    """A document reference as attached to a transaction or listed by ``/documents``."""

    reference: str | None
    name: str | None
    display_name: str | None
    title: str | None
    kind: str | None
    day: date | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DocumentRef:
        return cls(
            reference=_str(data.get("reference")),
            name=_str(data.get("name")),
            display_name=_str(data.get("display_name")),
            title=_str(data.get("title")),
            kind=_str(data.get("type")),
            day=_date(data.get("date")),
            raw=data,
        )


@dataclass
class Transaction:
    """An invoice or payment line from ``GET /api/v1/transactions``."""

    id: str | None
    day: date | None
    amount: float | None
    balance: float | None
    description: str | None
    info: str | None
    kind: str | None
    status: TransactionStatus
    status_description: str | None
    payment_possible: bool | None
    attachment: DocumentRef | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Transaction:
        att = data.get("attachment")
        return cls(
            id=_str(data.get("id")),
            day=_date(data.get("date")),
            amount=_num(data.get("amount")),
            balance=_num(data.get("balance")),
            description=_str(data.get("description")),
            info=_str(data.get("info")),
            kind=_str(data.get("type")),
            status=TransactionStatus.parse(data.get("status")),
            status_description=_str(data.get("status_description")),
            payment_possible=_bool(data.get("payment_possible")),
            attachment=DocumentRef.from_api(att) if isinstance(att, dict) else None,
            raw=data,
        )


@dataclass
class DayAheadPrice:
    """One hour (electricity) or one day (gas) of the dynamic tariff.

    ``price`` is ``bare_tariff_per_unit`` (VAT included), ``price_ex`` the
    same without VAT. Neither includes energiebelasting or the supplier fee.
    """

    start: datetime | None
    end: datetime | None
    price: float | None
    price_ex: float | None
    energy_type: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DayAheadPrice:
        return cls(
            start=_dt(data.get("start_date_time")),
            end=_dt(data.get("end_date_time")),
            price=_num(data.get("bare_tariff_per_unit")),
            price_ex=_num(data.get("bare_tariff_per_unit_ex")),
            energy_type=_str(data.get("type")),
            raw=data,
        )


# --- misc --------------------------------------------------------------------


@dataclass
class Mandate:
    """P4 data mandate (machtiging slimme meterdata) per EAN, ``GET /api/v1/mandates``."""

    ean: str
    approval_version: str | None
    current_approval_version: str | None
    start_date: date | None
    end_date: date | None
    source_application: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Mandate:
        inner = _dict(data.get("data"))
        return cls(
            ean=str(data.get("ean") or inner.get("ean") or ""),
            approval_version=_str(inner.get("approval_version")),
            current_approval_version=_str(inner.get("current_approval_version")),
            start_date=_date(inner.get("start_date")),
            end_date=_date(inner.get("end_date")),
            source_application=_str(inner.get("source_application")),
            raw=data,
        )

    @property
    def active(self) -> bool:
        """A mandate exists and has not been ended."""
        return bool(self.approval_version) and self.end_date is None


@dataclass
class OutageMessage:
    """A storing / maintenance notice, ``GET /api/v1/outages``."""

    id: str | None
    title: str | None
    description: str | None
    start: datetime | None
    end: datetime | None
    link_text: str | None
    link_url: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> OutageMessage:
        link = _dict(data.get("hyperlink"))
        return cls(
            id=_str(data.get("id")),
            title=_str(data.get("title")),
            description=_str(data.get("description")),
            start=_dt(data.get("start_date")),
            end=_dt(data.get("end_date")),
            link_text=_str(link.get("text")),
            link_url=_str(link.get("ref")),
            raw=data,
        )


@dataclass
class MerPeriod:
    """A monthly energy report period, ``GET /api/v1/mer/periods``."""

    id: str | None
    start_date: date | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MerPeriod:
        return cls(
            id=_str(data.get("id")),
            start_date=_date(data.get("start_date") or data.get("startDate")),
            raw=data,
        )
