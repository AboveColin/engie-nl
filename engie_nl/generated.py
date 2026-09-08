"""Models generated from the ENGIE app's api-map.json. Do not edit by hand.

180 dataclasses covering every response the mapped endpoints return,
except the 19 in models.py, which are hand-written and carry behaviour.

Regenerate with tools/generate_models.py. Every field is optional: the
gateway omits keys freely, and a missing key must not raise. ``raw`` keeps
the response as it arrived, so a field the map did not know about is never
lost.
"""

# pylint: disable=too-many-lines,too-many-instance-attributes,line-too-long

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, TypeVar

from .models import _bool, _date, _dt, _int, _list, _num, _str
from .models import Consumption, Register, Tariffs, Transaction, TransactionStatus

_T = TypeVar("_T")


def _obj(value: Any, factory: Callable[[dict[str, Any]], _T]) -> _T | None:
    """A nested object, or None when the gateway sent anything else."""
    return factory(value) if isinstance(value, dict) else None


@dataclass
class AbstractBaseResponse:
    """``nl.engie.chat.network.models.AbstractBaseResponse``."""

    culture: str | None = None
    interaction_id: str | None = None
    result: Any = None
    session_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AbstractBaseResponse:
        return cls(
            culture=_str(data.get("culture")),
            interaction_id=_str(data.get("interaction_id")),
            result=data.get("result"),
            session_id=_str(data.get("session_id")),
            raw=data,
        )


@dataclass
class AccessTokenResponse:
    """``nl.engie.shared.account.models.AccessTokenResponse``."""

    access_token: str | None = None
    expires_in: int | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AccessTokenResponse:
        return cls(
            access_token=_str(data.get("access_token")),
            expires_in=_int(data.get("expires_in")),
            refresh_token=_str(data.get("refresh_token")),
            token_type=_str(data.get("token_type")),
            raw=data,
        )


@dataclass
class AddMeterstandItem:
    """``nl.engie.shared.network.models.meterstands.AddMeterstandItem``."""

    date: str | None = None
    ean: str | None = None
    meterstands: list[Meterstand] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AddMeterstandItem:
        return cls(
            date=_str(data.get("date")),
            ean=_str(data.get("ean")),
            meterstands=[Meterstand.from_api(d) for d in _list(data.get("meterstands")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class EvAddress:
    """``nl.engie.ev.network.model.Address``."""

    city: str | None = None
    country_code: str | None = None
    house_number: int | None = None
    house_number_addition: str | None = None
    street: str | None = None
    zip_code: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EvAddress:
        return cls(
            city=_str(data.get("city")),
            country_code=_str(data.get("country_code")),
            house_number=_int(data.get("house_number")),
            house_number_addition=_str(data.get("house_number_addition")),
            street=_str(data.get("street")),
            zip_code=_str(data.get("zip_code")),
            raw=data,
        )


@dataclass
class SharedAddress:
    """``nl.engie.shared.persistance.entities.Address``."""

    id: str | None = None
    is_current_address: bool | None = None
    last_updated: str | None = None
    status: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SharedAddress:
        return cls(
            id=_str(data.get("id")),
            is_current_address=_bool(data.get("is_current_address")),
            last_updated=_str(data.get("last_updated")),
            status=_str(data.get("status")),
            raw=data,
        )


@dataclass
class AddressMetaData:
    """``nl.engie.shared.persistance.entities.AddressMetaData``."""

    address_id: str | None = None
    construction_year: int | None = None
    energy_label: str | None = None
    last_updated: datetime | None = None
    sale_rent: str | None = None
    surface_size: int | None = None
    type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AddressMetaData:
        return cls(
            address_id=_str(data.get("address_id")),
            construction_year=_int(data.get("construction_year")),
            energy_label=_str(data.get("energy_label")),
            last_updated=_dt(data.get("last_updated")),
            sale_rent=_str(data.get("sale_rent")),
            surface_size=_int(data.get("surface_size")),
            type=_str(data.get("type")),
            raw=data,
        )


@dataclass
class AddressWithMeteringPoints:
    """``nl.engie.shared.network.models.AddressWithMeteringPoints``."""

    metering_points: list[MeteringPointWithTariffs] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AddressWithMeteringPoints:
        return cls(
            metering_points=[MeteringPointWithTariffs.from_api(d) for d in _list(data.get("metering_points")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class AircoRequest:
    """``nl.engie.engieplus.data.assets.network.dto.AircoRequest``."""

    address_id: str | None = None
    brand: Any = None
    type: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AircoRequest:
        return cls(
            address_id=_str(data.get("address_id")),
            brand=data.get("brand"),
            type=data.get("type"),
            raw=data,
        )


@dataclass
class AircoResponse:
    """``nl.engie.engieplus.data.assets.network.dto.AircoResponse``."""

    address_id: str | None = None
    brand: Any = None
    id: str | None = None
    type: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AircoResponse:
        return cls(
            address_id=_str(data.get("address_id")),
            brand=data.get("brand"),
            id=_str(data.get("id")),
            type=data.get("type"),
            raw=data,
        )


@dataclass
class AllowedRange:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.AllowedRange``."""

    k_w: AllowedRangeKW | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AllowedRange:
        return cls(
            k_w=_obj(data.get("k_w"), AllowedRangeKW.from_api),
            raw=data,
        )


@dataclass
class AllowedRangeKW:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.AllowedRangeKW``."""

    max: float | None = None
    min: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AllowedRangeKW:
        return cls(
            max=_num(data.get("max")),
            min=_num(data.get("min")),
            raw=data,
        )


@dataclass
class Approval:
    """``nl.engie.shared.persistance.entities.Approval``."""

    approval_brief_text: str | None = None
    approval_changes_text: str | None = None
    current_approval_version: str | None = None
    customer_number: str | None = None
    ean: str | None = None
    ean_grid: str | None = None
    customer_email: str | None = None
    end_date: str | None = None
    approval_full_text_url: str | None = None
    customer_name: str | None = None
    source_application: str | None = None
    start_date: str | None = None
    approval_version: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Approval:
        return cls(
            approval_brief_text=_str(data.get("approval_brief_text")),
            approval_changes_text=_str(data.get("approval_changes_text")),
            current_approval_version=_str(data.get("current_approval_version")),
            customer_number=_str(data.get("customer_number")),
            ean=_str(data.get("ean")),
            ean_grid=_str(data.get("ean_grid")),
            customer_email=_str(data.get("customer_email")),
            end_date=_str(data.get("end_date")),
            approval_full_text_url=_str(data.get("approval_full_text_url")),
            customer_name=_str(data.get("customer_name")),
            source_application=_str(data.get("source_application")),
            start_date=_str(data.get("start_date")),
            approval_version=_str(data.get("approval_version")),
            raw=data,
        )


@dataclass
class ApprovalData:
    """``nl.engie.shared.network.models.ApprovalData``."""

    data: Approval | None = None
    ean: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ApprovalData:
        return cls(
            data=_obj(data.get("data"), Approval.from_api),
            ean=_str(data.get("ean")),
            raw=data,
        )


@dataclass
class ArticlesResponse:
    """``nl.engie.advice.measures.network.model.ArticlesResponse``."""

    contains_all_changes: bool | None = None
    id: str | None = None
    insertions: list[Measure] = field(default_factory=list)
    removals: list[str] = field(default_factory=list)
    reorders: Any = None
    updates: list[Measure] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ArticlesResponse:
        return cls(
            contains_all_changes=_bool(data.get("contains_all_changes")),
            id=_str(data.get("id")),
            insertions=[Measure.from_api(d) for d in _list(data.get("insertions")) if isinstance(d, dict)],
            removals=[x for i in _list(data.get("removals")) if (x := _str(i)) is not None],
            reorders=data.get("reorders"),
            updates=[Measure.from_api(d) for d in _list(data.get("updates")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class BankAccount:
    """``nl.engie.ev.network.model.BankAccount``."""

    holder_full_name: str | None = None
    iban: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> BankAccount:
        return cls(
            holder_full_name=_str(data.get("holder_full_name")),
            iban=_str(data.get("iban")),
            raw=data,
        )


@dataclass
class BankDto:
    """``nl.engie.login_data.network.dto.BankDto``."""

    id: str | None = None
    name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> BankDto:
        return cls(
            id=_str(data.get("id")),
            name=_str(data.get("name")),
            raw=data,
        )


@dataclass
class BaseAddress:
    """``nl.engie.shared.persistance.models.BaseAddress``."""

    city: str | None = None
    house_nr: str | None = None
    house_nr_addition: str | None = None
    street: str | None = None
    zip_code: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> BaseAddress:
        return cls(
            city=_str(data.get("city")),
            house_nr=_str(data.get("house_nr")),
            house_nr_addition=_str(data.get("house_nr_addition")),
            street=_str(data.get("street")),
            zip_code=_str(data.get("zip_code")),
            raw=data,
        )


@dataclass
class BaseDocument:
    """``nl.engie.shared.persistance.models.BaseDocument``."""

    display_name: str | None = None
    name: str | None = None
    reference: str | None = None
    title: str | None = None
    type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> BaseDocument:
        return cls(
            display_name=_str(data.get("display_name")),
            name=_str(data.get("name")),
            reference=_str(data.get("reference")),
            title=_str(data.get("title")),
            type=_str(data.get("type")),
            raw=data,
        )


@dataclass
class BaseEnodeEntityResponse:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.BaseEnodeEntityResponse``."""

    data: list[Any] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> BaseEnodeEntityResponse:
        return cls(
            data=_list(data.get("data")),
            raw=data,
        )


@dataclass
class BaseResponse:
    """``nl.engie.chat.network.models.BaseResponse``."""

    output_type: str | None = None
    outputs: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> BaseResponse:
        return cls(
            output_type=_str(data.get("output_type")),
            outputs=data.get("outputs"),
            raw=data,
        )


@dataclass
class CMSColors:
    """``nl.engie.shared.network.models.CMSColors``."""

    dark: list[str] = field(default_factory=list)
    light: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CMSColors:
        return cls(
            dark=[x for i in _list(data.get("dark")) if (x := _str(i)) is not None],
            light=[x for i in _list(data.get("light")) if (x := _str(i)) is not None],
            raw=data,
        )


@dataclass
class Car:
    """``nl.engie.engieplus.data.smart_charging.registration.dto.Car``."""

    battery_capacity_in_kwh: float | None = None
    brand: str | None = None
    id: str | None = None
    is_chargeable: bool | None = None
    is_connectable: bool | None = None
    model: str | None = None
    range_in_km: int | None = None
    version: str | None = None
    year_if_known: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Car:
        return cls(
            battery_capacity_in_kwh=_num(data.get("battery_capacity_in_kwh")),
            brand=_str(data.get("brand")),
            id=_str(data.get("id")),
            is_chargeable=_bool(data.get("is_chargeable")),
            is_connectable=_bool(data.get("is_connectable")),
            model=_str(data.get("model")),
            range_in_km=_int(data.get("range_in_km")),
            version=_str(data.get("version")),
            year_if_known=_int(data.get("year_if_known")),
            raw=data,
        )


@dataclass
class ChangePasswordRequest:
    """``nl.engie.login_data.network.model.ChangePasswordRequest``."""

    current_password: str | None = None
    new_password: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChangePasswordRequest:
        return cls(
            current_password=_str(data.get("current_password")),
            new_password=_str(data.get("new_password")),
            raw=data,
        )


@dataclass
class ChangePasswordResponse:
    """``nl.engie.login_data.network.model.ChangePasswordResponse``."""

    message: str | None = None
    status: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChangePasswordResponse:
        return cls(
            message=_str(data.get("message")),
            status=_str(data.get("status")),
            raw=data,
        )


@dataclass
class ChannelInfo:
    """``nl.engie.contact.network.model.ChannelInfo``."""

    open_from: datetime | None = None
    status: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChannelInfo:
        return cls(
            open_from=_dt(data.get("open_from")),
            status=_str(data.get("status")),
            raw=data,
        )


@dataclass
class ChargeCardRequestBody:
    """``nl.engie.ev.network.model.ChargeCardRequestBody``."""

    address: SharedAddress | None = None
    amount_of_cards: int | None = None
    amount_of_droplets: int | None = None
    bank_account: BankAccount | None = None
    billing_address: SharedAddress | None = None
    customer: Customer | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChargeCardRequestBody:
        return cls(
            address=_obj(data.get("address"), SharedAddress.from_api),
            amount_of_cards=_int(data.get("amount_of_cards")),
            amount_of_droplets=_int(data.get("amount_of_droplets")),
            bank_account=_obj(data.get("bank_account"), BankAccount.from_api),
            billing_address=_obj(data.get("billing_address"), SharedAddress.from_api),
            customer=_obj(data.get("customer"), Customer.from_api),
            raw=data,
        )


@dataclass
class ChargingPolicy:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.ChargingPolicy``."""

    id: str | None = None
    last_observed_location_charge_limit: int | None = None
    restriction_schedule: list[PolicyRestrictionSchedule] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChargingPolicy:
        return cls(
            id=_str(data.get("id")),
            last_observed_location_charge_limit=_int(data.get("last_observed_location_charge_limit")),
            restriction_schedule=[PolicyRestrictionSchedule.from_api(d) for d in _list(data.get("restriction_schedule")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class ChargingStationRequest:
    """``nl.engie.engieplus.data.assets.network.dto.ChargingStationRequest``."""

    address_id: str | None = None
    brand: Any = None
    type: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChargingStationRequest:
        return cls(
            address_id=_str(data.get("address_id")),
            brand=data.get("brand"),
            type=data.get("type"),
            raw=data,
        )


@dataclass
class ChargingStationResponse:
    """``nl.engie.engieplus.data.assets.network.dto.ChargingStationResponse``."""

    address_id: str | None = None
    brand: Any = None
    id: str | None = None
    type: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChargingStationResponse:
        return cls(
            address_id=_str(data.get("address_id")),
            brand=data.get("brand"),
            id=_str(data.get("id")),
            type=data.get("type"),
            raw=data,
        )


@dataclass
class CheckAccountResponse:
    """``nl.engie.login_data.network.model.CheckAccountResponse``."""

    taken: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CheckAccountResponse:
        return cls(
            taken=_bool(data.get("taken")),
            raw=data,
        )


@dataclass
class ClientImportsProspectDataRequest:
    """``nl.engie.service.accountimport.readings.data.network.dto.ClientImportsProspectDataRequest``."""

    prospect_access_token: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ClientImportsProspectDataRequest:
        return cls(
            prospect_access_token=_str(data.get("prospect_access_token")),
            raw=data,
        )


@dataclass
class CollectiveResponse:
    """``nl.engie.shared.network.models.CollectiveResponse``."""

    agreement_image: str | None = None
    agreement_name_addition: str | None = None
    details_image: str | None = None
    details_text: str | None = None
    logo: str | None = None
    name: str | None = None
    onboarding_text: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CollectiveResponse:
        return cls(
            agreement_image=_str(data.get("agreement_image")),
            agreement_name_addition=_str(data.get("agreement_name_addition")),
            details_image=_str(data.get("details_image")),
            details_text=_str(data.get("details_text")),
            logo=_str(data.get("logo")),
            name=_str(data.get("name")),
            onboarding_text=_str(data.get("onboarding_text")),
            raw=data,
        )


@dataclass
class ConsumptionDetailData:
    """``nl.engie.shared.persistance.entities.ConsumptionDetailData``."""

    cost_low: float | None = None
    cost_low_ex: float | None = None
    cost_normal: float | None = None
    cost_normal_ex: float | None = None
    cost_return_low: float | None = None
    cost_return_low_ex: float | None = None
    cost_return_normal: float | None = None
    cost_return_normal_ex: float | None = None
    date: datetime | None = None
    ean: str | None = None
    low: int | None = None
    normal: int | None = None
    return_low: int | None = None
    return_normal: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ConsumptionDetailData:
        return cls(
            cost_low=_num(data.get("cost_low")),
            cost_low_ex=_num(data.get("cost_low_ex")),
            cost_normal=_num(data.get("cost_normal")),
            cost_normal_ex=_num(data.get("cost_normal_ex")),
            cost_return_low=_num(data.get("cost_return_low")),
            cost_return_low_ex=_num(data.get("cost_return_low_ex")),
            cost_return_normal=_num(data.get("cost_return_normal")),
            cost_return_normal_ex=_num(data.get("cost_return_normal_ex")),
            date=_dt(data.get("date")),
            ean=_str(data.get("ean")),
            low=_int(data.get("low")),
            normal=_int(data.get("normal")),
            return_low=_int(data.get("return_low")),
            return_normal=_int(data.get("return_normal")),
            raw=data,
        )


@dataclass
class ConsumptionDetails:
    """``nl.engie.shared.network.models.ConsumptionDetails``."""

    data: list[ConsumptionDetailData] = field(default_factory=list)
    ean: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ConsumptionDetails:
        return cls(
            data=[ConsumptionDetailData.from_api(d) for d in _list(data.get("data")) if isinstance(d, dict)],
            ean=_str(data.get("ean")),
            raw=data,
        )


@dataclass
class ConsumptionsData:
    """``nl.engie.shared.network.models.ConsumptionsData``."""

    data: list[Consumption] = field(default_factory=list)
    ean: str | None = None
    error: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ConsumptionsData:
        return cls(
            data=[Consumption.from_api(d) for d in _list(data.get("data")) if isinstance(d, dict)],
            ean=_str(data.get("ean")),
            error=data.get("error"),
            raw=data,
        )


@dataclass
class ContactData:
    """``nl.engie.shared.persistance.models.ContactData``."""

    email: str | None = None
    mobile: str | None = None
    phone: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContactData:
        return cls(
            email=_str(data.get("email")),
            mobile=_str(data.get("mobile")),
            phone=_str(data.get("phone")),
            raw=data,
        )


@dataclass
class ContactPreferences:
    """``nl.engie.contract_extension.network.model.ContactPreferences``."""

    digital: bool | None = None
    mail: bool | None = None
    phone: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContactPreferences:
        return cls(
            digital=_bool(data.get("digital")),
            mail=_bool(data.get("mail")),
            phone=_bool(data.get("phone")),
            raw=data,
        )


@dataclass
class ContactRequestBody:
    """``nl.engie.ev.network.model.ContactRequestBody``."""

    address_id: str | None = None
    company_name: str | None = None
    email_address: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContactRequestBody:
        return cls(
            address_id=_str(data.get("address_id")),
            company_name=_str(data.get("company_name")),
            email_address=_str(data.get("email_address")),
            first_name=_str(data.get("first_name")),
            last_name=_str(data.get("last_name")),
            phone_number=_str(data.get("phone_number")),
            raw=data,
        )


@dataclass
class ContractAddress:
    """``nl.engie.contract_extension.network.model.ContractAddress``."""

    city: str | None = None
    house_number: str | None = None
    house_number_addition: str | None = None
    is_residential: bool | None = None
    street: str | None = None
    zip_code: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContractAddress:
        return cls(
            city=_str(data.get("city")),
            house_number=_str(data.get("house_number")),
            house_number_addition=_str(data.get("house_number_addition")),
            is_residential=_bool(data.get("is_residential")),
            street=_str(data.get("street")),
            zip_code=_str(data.get("zip_code")),
            raw=data,
        )


@dataclass
class ContractExtension:
    """``nl.engie.contract_extension.network.model.ContractExtension``."""

    electricity_consumption_normal: int | None = None
    electricity_consumption_peak: int | None = None
    electricity_consumption_single: int | None = None
    electricity_redelivery_normal: int | None = None
    electricity_redelivery_peak: int | None = None
    electricity_redelivery_single: int | None = None
    extra_information: ContractOfferExtraInformation | None = None
    gas_consumption: int | None = None
    has_electricity_redelivery: bool | None = None
    opportunity_id: str | None = None
    pre_payment_amount: int | None = None
    product_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContractExtension:
        return cls(
            electricity_consumption_normal=_int(data.get("electricity_consumption_normal")),
            electricity_consumption_peak=_int(data.get("electricity_consumption_peak")),
            electricity_consumption_single=_int(data.get("electricity_consumption_single")),
            electricity_redelivery_normal=_int(data.get("electricity_redelivery_normal")),
            electricity_redelivery_peak=_int(data.get("electricity_redelivery_peak")),
            electricity_redelivery_single=_int(data.get("electricity_redelivery_single")),
            extra_information=_obj(data.get("extra_information"), ContractOfferExtraInformation.from_api),
            gas_consumption=_int(data.get("gas_consumption")),
            has_electricity_redelivery=_bool(data.get("has_electricity_redelivery")),
            opportunity_id=_str(data.get("opportunity_id")),
            pre_payment_amount=_int(data.get("pre_payment_amount")),
            product_id=_str(data.get("product_id")),
            raw=data,
        )


@dataclass
class ContractOfferExtraInformation:
    """``nl.engie.contract_extension.network.model.ContractOfferExtraInformation``."""

    bank_account_number: str | None = None
    billing_address: ContractAddress | None = None
    contact_preferences: ContactPreferences | None = None
    contract_start_date: str | None = None
    date_of_birth: str | None = None
    email_address: str | None = None
    first_name: str | None = None
    gender: str | None = None
    initials: str | None = None
    last_name: str | None = None
    legal_customer_type: Any = None
    payment_method: str | None = None
    phone_number: str | None = None
    supply_address: ContractAddress | None = None
    wants_single_tariff: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ContractOfferExtraInformation:
        return cls(
            bank_account_number=_str(data.get("bank_account_number")),
            billing_address=_obj(data.get("billing_address"), ContractAddress.from_api),
            contact_preferences=_obj(data.get("contact_preferences"), ContactPreferences.from_api),
            contract_start_date=_str(data.get("contract_start_date")),
            date_of_birth=_str(data.get("date_of_birth")),
            email_address=_str(data.get("email_address")),
            first_name=_str(data.get("first_name")),
            gender=_str(data.get("gender")),
            initials=_str(data.get("initials")),
            last_name=_str(data.get("last_name")),
            legal_customer_type=data.get("legal_customer_type"),
            payment_method=_str(data.get("payment_method")),
            phone_number=_str(data.get("phone_number")),
            supply_address=_obj(data.get("supply_address"), ContractAddress.from_api),
            wants_single_tariff=_bool(data.get("wants_single_tariff")),
            raw=data,
        )


@dataclass
class CreateEnodeLocationBody:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.CreateEnodeLocationBody``."""

    latitude: float | None = None
    longitude: float | None = None
    name: EnodeLocationName | None = None
    timezone_name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CreateEnodeLocationBody:
        return cls(
            latitude=_num(data.get("latitude")),
            longitude=_num(data.get("longitude")),
            name=_obj(data.get("name"), EnodeLocationName.from_api),
            timezone_name=_str(data.get("timezone_name")),
            raw=data,
        )


@dataclass
class CreateEnodeSolarConfiguration:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.CreateEnodeSolarConfiguration``."""

    location_id: str | None = None
    user_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CreateEnodeSolarConfiguration:
        return cls(
            location_id=_str(data.get("location_id")),
            user_id=_str(data.get("user_id")),
            raw=data,
        )


@dataclass
class CreateLinkBody:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.CreateLinkBody``."""

    language: str | None = None
    redirect_uri: str | None = None
    scopes: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CreateLinkBody:
        return cls(
            language=_str(data.get("language")),
            redirect_uri=_str(data.get("redirect_uri")),
            scopes=[x for i in _list(data.get("scopes")) if (x := _str(i)) is not None],
            raw=data,
        )


@dataclass
class CreatePolicyBody:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.CreatePolicyBody``."""

    location_id: str | None = None
    vehicle_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CreatePolicyBody:
        return cls(
            location_id=_str(data.get("location_id")),
            vehicle_id=_str(data.get("vehicle_id")),
            raw=data,
        )


@dataclass
class CurrentContract:
    """``nl.engie.shared.persistance.entities.CurrentContract``."""

    contractenddate: str | None = None
    customer_id: str | None = None
    fixedcostsperyearineuros: int | None = None
    prepaymentpermonthineuros: int | None = None
    suppliername: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CurrentContract:
        return cls(
            contractenddate=_str(data.get("contractEndDate")),
            customer_id=_str(data.get("customer_id")),
            fixedcostsperyearineuros=_int(data.get("fixedCostsPerYearInEuros")),
            prepaymentpermonthineuros=_int(data.get("prepaymentPerMonthInEuros")),
            suppliername=_str(data.get("supplierName")),
            raw=data,
        )


@dataclass
class Customer:
    """``nl.engie.ev.network.model.Customer``."""

    company_name: str | None = None
    email_address: str | None = None
    first_name: str | None = None
    is_male: bool | None = None
    last_name: str | None = None
    phone_number: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Customer:
        return cls(
            company_name=_str(data.get("company_name")),
            email_address=_str(data.get("email_address")),
            first_name=_str(data.get("first_name")),
            is_male=_bool(data.get("is_male")),
            last_name=_str(data.get("last_name")),
            phone_number=_str(data.get("phone_number")),
            raw=data,
        )


@dataclass
class DayAheadPriceDto:
    """``nl.engie.dynamictariffs.data.network.response.DayAheadPriceDto``."""

    bare_tariff_per_unit: float | None = None
    bare_tariff_per_unit_ex: float | None = None
    end_date_time: datetime | None = None
    start_date_time: datetime | None = None
    type: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DayAheadPriceDto:
        return cls(
            bare_tariff_per_unit=_num(data.get("bare_tariff_per_unit")),
            bare_tariff_per_unit_ex=_num(data.get("bare_tariff_per_unit_ex")),
            end_date_time=_dt(data.get("end_date_time")),
            start_date_time=_dt(data.get("start_date_time")),
            type=data.get("type"),
            raw=data,
        )


@dataclass
class Document:
    """``nl.engie.shared.persistance.entities.Document``."""

    attachments: list[Document] = field(default_factory=list)
    contents: str | None = None
    date: datetime | None = None
    last_read: datetime | None = None
    parent_reference: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Document:
        return cls(
            attachments=[Document.from_api(d) for d in _list(data.get("attachments")) if isinstance(d, dict)],
            contents=_str(data.get("contents")),
            date=_dt(data.get("date")),
            last_read=_dt(data.get("last_read")),
            parent_reference=_str(data.get("parent_reference")),
            raw=data,
        )


@dataclass
class DocumentsResponse:
    """``nl.engie.shared.network.models.DocumentsResponse``."""

    documents: list[Document] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DocumentsResponse:
        return cls(
            documents=[Document.from_api(d) for d in _list(data.get("documents")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class EdsnMeteringPoint:
    """``nl.engie.service.change_address.domain.model.EdsnMeteringPoint``."""

    ean: str | None = None
    grid_id: str | None = None
    market_segment: str | None = None
    portaal_energy_meter_id: str | None = None
    product: str | None = None
    product_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EdsnMeteringPoint:
        return cls(
            ean=_str(data.get("ean")),
            grid_id=_str(data.get("grid_id")),
            market_segment=_str(data.get("market_segment")),
            portaal_energy_meter_id=_str(data.get("portaal_energy_meter_id")),
            product=_str(data.get("product")),
            product_type=_str(data.get("product_type")),
            raw=data,
        )


@dataclass
class EdsnRequest:
    """``nl.engie.service.change_address.data.network.model.EdsnRequest``."""

    house_number: int | None = None
    house_number_addition: str | None = None
    postal_code: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EdsnRequest:
        return cls(
            house_number=_int(data.get("house_number")),
            house_number_addition=_str(data.get("house_number_addition")),
            postal_code=_str(data.get("postal_code")),
            raw=data,
        )


@dataclass
class ElectricCarRequest:
    """``nl.engie.engieplus.data.assets.network.dto.ElectricCarRequest``."""

    address_id: str | None = None
    brand: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ElectricCarRequest:
        return cls(
            address_id=_str(data.get("address_id")),
            brand=data.get("brand"),
            raw=data,
        )


@dataclass
class ElectricCarResponse:
    """``nl.engie.engieplus.data.assets.network.dto.ElectricCarResponse``."""

    address_id: str | None = None
    brand: Any = None
    id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ElectricCarResponse:
        return cls(
            address_id=_str(data.get("address_id")),
            brand=data.get("brand"),
            id=_str(data.get("id")),
            raw=data,
        )


@dataclass
class EnodeCapability:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeCapability``."""

    intervention_ids: list[str] = field(default_factory=list)
    is_capable: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeCapability:
        return cls(
            intervention_ids=[x for i in _list(data.get("intervention_ids")) if (x := _str(i)) is not None],
            is_capable=_bool(data.get("is_capable")),
            raw=data,
        )


@dataclass
class EnodeChargeRateLimitCapability:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargeRateLimitCapability``."""

    allowed_range: AllowedRange | None = None
    intervention_ids: list[str] = field(default_factory=list)
    is_capable: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargeRateLimitCapability:
        return cls(
            allowed_range=_obj(data.get("allowed_range"), AllowedRange.from_api),
            intervention_ids=[x for i in _list(data.get("intervention_ids")) if (x := _str(i)) is not None],
            is_capable=_bool(data.get("is_capable")),
            raw=data,
        )


@dataclass
class EnodeCharger:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeCharger``."""

    capabilities: EnodeChargerCapabilities | None = None
    charge_state: EnodeChargerChargeState | None = None
    id: str | None = None
    information: EnodeChargerInformation | None = None
    location: EnodeChargerLocation | None = None
    user_id: str | None = None
    vendor: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeCharger:
        return cls(
            capabilities=_obj(data.get("capabilities"), EnodeChargerCapabilities.from_api),
            charge_state=_obj(data.get("charge_state"), EnodeChargerChargeState.from_api),
            id=_str(data.get("id")),
            information=_obj(data.get("information"), EnodeChargerInformation.from_api),
            location=_obj(data.get("location"), EnodeChargerLocation.from_api),
            user_id=_str(data.get("user_id")),
            vendor=_str(data.get("vendor")),
            raw=data,
        )


@dataclass
class EnodeChargerCapabilities:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargerCapabilities``."""

    charge_state: EnodeCapability | None = None
    information: EnodeCapability | None = None
    set_charge_rate_limit: EnodeChargeRateLimitCapability | None = None
    set_max_current: EnodeCapability | None = None
    start_charging: EnodeCapability | None = None
    stop_charging: EnodeCapability | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargerCapabilities:
        return cls(
            charge_state=_obj(data.get("charge_state"), EnodeCapability.from_api),
            information=_obj(data.get("information"), EnodeCapability.from_api),
            set_charge_rate_limit=_obj(data.get("set_charge_rate_limit"), EnodeChargeRateLimitCapability.from_api),
            set_max_current=_obj(data.get("set_max_current"), EnodeCapability.from_api),
            start_charging=_obj(data.get("start_charging"), EnodeCapability.from_api),
            stop_charging=_obj(data.get("stop_charging"), EnodeCapability.from_api),
            raw=data,
        )


@dataclass
class EnodeChargerChargeState:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargerChargeState``."""

    charge_rate: float | None = None
    last_updated: datetime | None = None
    power_delivery_state: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargerChargeState:
        return cls(
            charge_rate=_num(data.get("charge_rate")),
            last_updated=_dt(data.get("last_updated")),
            power_delivery_state=_str(data.get("power_delivery_state")),
            raw=data,
        )


@dataclass
class EnodeChargerInformation:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargerInformation``."""

    brand: str | None = None
    model: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargerInformation:
        return cls(
            brand=_str(data.get("brand")),
            model=_str(data.get("model")),
            raw=data,
        )


@dataclass
class EnodeChargerLocation:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargerLocation``."""

    id: str | None = None
    last_updated: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargerLocation:
        return cls(
            id=_str(data.get("id")),
            last_updated=_dt(data.get("last_updated")),
            raw=data,
        )


@dataclass
class EnodeChargingSession:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSession``."""

    id: str | None = None
    location_id: str | None = None
    outcome: EnodeChargingSessionOutcome | None = None
    plugged_in_at: datetime | None = None
    plugged_out_at: datetime | None = None
    policy_id: str | None = None
    state: str | None = None
    statistics: EnodeChargingSessionStatistics | None = None
    target: EnodeChargingSessionTarget | None = None
    valuation: EnodeChargingSessionValuation | None = None
    vehicle_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSession:
        return cls(
            id=_str(data.get("id")),
            location_id=_str(data.get("location_id")),
            outcome=_obj(data.get("outcome"), EnodeChargingSessionOutcome.from_api),
            plugged_in_at=_dt(data.get("plugged_in_at")),
            plugged_out_at=_dt(data.get("plugged_out_at")),
            policy_id=_str(data.get("policy_id")),
            state=_str(data.get("state")),
            statistics=_obj(data.get("statistics"), EnodeChargingSessionStatistics.from_api),
            target=_obj(data.get("target"), EnodeChargingSessionTarget.from_api),
            valuation=_obj(data.get("valuation"), EnodeChargingSessionValuation.from_api),
            vehicle_id=_str(data.get("vehicle_id")),
            raw=data,
        )


@dataclass
class EnodeChargingSessionOutcome:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSessionOutcome``."""

    latest: EnodeChargingSessionOutcomeData | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSessionOutcome:
        return cls(
            latest=_obj(data.get("latest"), EnodeChargingSessionOutcomeData.from_api),
            raw=data,
        )


@dataclass
class EnodeChargingSessionOutcomeData:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSessionOutcomeData``."""

    battery_level_at_ready_by: int | None = None
    minimum_charge_target_reached_at: datetime | None = None
    state: str | None = None
    target_id: int | None = None
    type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSessionOutcomeData:
        return cls(
            battery_level_at_ready_by=_int(data.get("battery_level_at_ready_by")),
            minimum_charge_target_reached_at=_dt(data.get("minimum_charge_target_reached_at")),
            state=_str(data.get("state")),
            target_id=_int(data.get("target_id")),
            type=_str(data.get("type")),
            raw=data,
        )


@dataclass
class EnodeChargingSessionStatistics:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSessionStatistics``."""

    aggregated: EnodeChargingSessionStatisticsAggregated | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSessionStatistics:
        return cls(
            aggregated=_obj(data.get("aggregated"), EnodeChargingSessionStatisticsAggregated.from_api),
            raw=data,
        )


@dataclass
class EnodeChargingSessionStatisticsAggregated:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSessionStatisticsAggregated``."""

    battery_from: int | None = None
    battery_to: int | None = None
    kwh_sum: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSessionStatisticsAggregated:
        return cls(
            battery_from=_int(data.get("battery_from")),
            battery_to=_int(data.get("battery_to")),
            kwh_sum=_num(data.get("kwh_sum")),
            raw=data,
        )


@dataclass
class EnodeChargingSessionTarget:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSessionTarget``."""

    latest: EnodeChargingSessionTargetData | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSessionTarget:
        return cls(
            latest=_obj(data.get("latest"), EnodeChargingSessionTargetData.from_api),
            raw=data,
        )


@dataclass
class EnodeChargingSessionTargetData:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSessionTargetData``."""

    battery_reserve: int | None = None
    id: int | None = None
    minimum_charge_target: int | None = None
    ready_by: datetime | None = None
    source: str | None = None
    type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSessionTargetData:
        return cls(
            battery_reserve=_int(data.get("battery_reserve")),
            id=_int(data.get("id")),
            minimum_charge_target=_int(data.get("minimum_charge_target")),
            ready_by=_dt(data.get("ready_by")),
            source=_str(data.get("source")),
            type=_str(data.get("type")),
            raw=data,
        )


@dataclass
class EnodeChargingSessionValuation:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSessionValuation``."""

    currency: str | None = None
    tariff_cost: EnodeChargingSessionValuationTariffCost | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSessionValuation:
        return cls(
            currency=_str(data.get("currency")),
            tariff_cost=_obj(data.get("tariff_cost"), EnodeChargingSessionValuationTariffCost.from_api),
            raw=data,
        )


@dataclass
class EnodeChargingSessionValuationTariffCost:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeChargingSessionValuationTariffCost``."""

    actual: float | None = None
    baseline: float | None = None
    savings: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeChargingSessionValuationTariffCost:
        return cls(
            actual=_num(data.get("actual")),
            baseline=_num(data.get("baseline")),
            savings=_num(data.get("savings")),
            raw=data,
        )


@dataclass
class EnodeIntervention:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeIntervention``."""

    brand: str | None = None
    domain: str | None = None
    id: str | None = None
    resolution: EnodeInterventionResolution | None = None
    vendor: str | None = None
    vendor_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeIntervention:
        return cls(
            brand=_str(data.get("brand")),
            domain=_str(data.get("domain")),
            id=_str(data.get("id")),
            resolution=_obj(data.get("resolution"), EnodeInterventionResolution.from_api),
            vendor=_str(data.get("vendor")),
            vendor_type=_str(data.get("vendor_type")),
            raw=data,
        )


@dataclass
class EnodeInterventionResolution:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeInterventionResolution``."""

    access: str | None = None
    action: str | None = None
    agent: str | None = None
    description: str | None = None
    title: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeInterventionResolution:
        return cls(
            access=_str(data.get("access")),
            action=_str(data.get("action")),
            agent=_str(data.get("agent")),
            description=_str(data.get("description")),
            title=_str(data.get("title")),
            raw=data,
        )


@dataclass
class EnodeLinkedVendor:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeLinkedVendor``."""

    is_valid: bool | None = None
    vendor: str | None = None
    vendor_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeLinkedVendor:
        return cls(
            is_valid=_bool(data.get("is_valid")),
            vendor=_str(data.get("vendor")),
            vendor_type=_str(data.get("vendor_type")),
            raw=data,
        )


@dataclass
class EnodeLocation:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeLocation``."""

    created_at: datetime | None = None
    id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: EnodeLocationName | None = None
    timezone_name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeLocation:
        return cls(
            created_at=_dt(data.get("created_at")),
            id=_str(data.get("id")),
            latitude=_num(data.get("latitude")),
            longitude=_num(data.get("longitude")),
            name=_obj(data.get("name"), EnodeLocationName.from_api),
            timezone_name=_str(data.get("timezone_name")),
            raw=data,
        )


@dataclass
class EnodeLocationName:
    """``nl.engie.engieplus.data.smart_charging.charging_location.EnodeLocationName``."""

    ean: str | None = None
    house_number: str | None = None
    house_number_addition: str | None = None
    zip_code: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeLocationName:
        return cls(
            ean=_str(data.get("ean")),
            house_number=_str(data.get("house_number")),
            house_number_addition=_str(data.get("house_number_addition")),
            zip_code=_str(data.get("zip_code")),
            raw=data,
        )


@dataclass
class EnodeSessionTarget:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeSessionTarget``."""

    type: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeSessionTarget:
        return cls(
            type=data.get("type"),
            raw=data,
        )


@dataclass
class EnodeSolarConfiguration:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeSolarConfiguration``."""

    id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeSolarConfiguration:
        return cls(
            id=_str(data.get("id")),
            raw=data,
        )


@dataclass
class EnodeUser:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeUser``."""

    id: str | None = None
    linked_vendors: list[EnodeLinkedVendor] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeUser:
        return cls(
            id=_str(data.get("id")),
            linked_vendors=[EnodeLinkedVendor.from_api(d) for d in _list(data.get("linked_vendors")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class EnodeVehicle:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeVehicle``."""

    capabilities: EnodeVehicleCapabilities | None = None
    charge_state: EnodeVehicleChargeState | None = None
    id: str | None = None
    information: EnodeVehicleInformation | None = None
    is_reachable: bool | None = None
    location: EnodeVehicleLocation | None = None
    vendor: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeVehicle:
        return cls(
            capabilities=_obj(data.get("capabilities"), EnodeVehicleCapabilities.from_api),
            charge_state=_obj(data.get("charge_state"), EnodeVehicleChargeState.from_api),
            id=_str(data.get("id")),
            information=_obj(data.get("information"), EnodeVehicleInformation.from_api),
            is_reachable=_bool(data.get("is_reachable")),
            location=_obj(data.get("location"), EnodeVehicleLocation.from_api),
            vendor=_str(data.get("vendor")),
            raw=data,
        )


@dataclass
class EnodeVehicleCapabilities:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeVehicleCapabilities``."""

    charge_state: EnodeCapability | None = None
    information: EnodeCapability | None = None
    location: EnodeCapability | None = None
    odometer: EnodeCapability | None = None
    refresh_state: EnodeCapability | None = None
    set_max_current: EnodeCapability | None = None
    smart_charging: EnodeCapability | None = None
    start_charging: EnodeCapability | None = None
    stop_charging: EnodeCapability | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeVehicleCapabilities:
        return cls(
            charge_state=_obj(data.get("charge_state"), EnodeCapability.from_api),
            information=_obj(data.get("information"), EnodeCapability.from_api),
            location=_obj(data.get("location"), EnodeCapability.from_api),
            odometer=_obj(data.get("odometer"), EnodeCapability.from_api),
            refresh_state=_obj(data.get("refresh_state"), EnodeCapability.from_api),
            set_max_current=_obj(data.get("set_max_current"), EnodeCapability.from_api),
            smart_charging=_obj(data.get("smart_charging"), EnodeCapability.from_api),
            start_charging=_obj(data.get("start_charging"), EnodeCapability.from_api),
            stop_charging=_obj(data.get("stop_charging"), EnodeCapability.from_api),
            raw=data,
        )


@dataclass
class EnodeVehicleChargeState:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeVehicleChargeState``."""

    battery_capacity: float | None = None
    battery_level: float | None = None
    charge_limit: float | None = None
    charge_rate: float | None = None
    last_updated: datetime | None = None
    plugged_in_charger_id: str | None = None
    power_delivery_state: str | None = None
    range: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeVehicleChargeState:
        return cls(
            battery_capacity=_num(data.get("battery_capacity")),
            battery_level=_num(data.get("battery_level")),
            charge_limit=_num(data.get("charge_limit")),
            charge_rate=_num(data.get("charge_rate")),
            last_updated=_dt(data.get("last_updated")),
            plugged_in_charger_id=_str(data.get("plugged_in_charger_id")),
            power_delivery_state=_str(data.get("power_delivery_state")),
            range=_num(data.get("range")),
            raw=data,
        )


@dataclass
class EnodeVehicleInformation:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeVehicleInformation``."""

    brand: str | None = None
    display_name: str | None = None
    image_url: str | None = None
    model: str | None = None
    year: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeVehicleInformation:
        return cls(
            brand=_str(data.get("brand")),
            display_name=_str(data.get("display_name")),
            image_url=_str(data.get("image_url")),
            model=_str(data.get("model")),
            year=_int(data.get("year")),
            raw=data,
        )


@dataclass
class EnodeVehicleLocation:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.EnodeVehicleLocation``."""

    id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnodeVehicleLocation:
        return cls(
            id=_str(data.get("id")),
            raw=data,
        )


@dataclass
class Error:
    """``nl.engie.shared.network.models.Error``."""

    detail: Any = None
    details: Any = None
    fault_string: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Error:
        return cls(
            detail=data.get("detail"),
            details=data.get("details"),
            fault_string=_str(data.get("fault_string")),
            raw=data,
        )


@dataclass
class ExchangeTokenBody:
    """``nl.engie.p1.data.network.model.ExchangeTokenBody``."""

    external_provider_access_token: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ExchangeTokenBody:
        return cls(
            external_provider_access_token=_str(data.get("external_provider_access_token")),
            raw=data,
        )


@dataclass
class ForgotPasswordRequest:
    """``nl.engie.login_data.network.model.ForgotPasswordRequest``."""

    email_address: str | None = None
    username: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ForgotPasswordRequest:
        return cls(
            email_address=_str(data.get("email_address")),
            username=_str(data.get("username")),
            raw=data,
        )


@dataclass
class ForgotUsernameRequest:
    """``nl.engie.login_data.network.model.ForgotUsernameRequest``."""

    email_address: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ForgotUsernameRequest:
        return cls(
            email_address=_str(data.get("email_address")),
            raw=data,
        )


@dataclass
class HappyHour:
    """``nl.engie.happyhour.domain.model.HappyHour``."""

    end_date: datetime | None = None
    start_date: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HappyHour:
        return cls(
            end_date=_dt(data.get("end_date")),
            start_date=_dt(data.get("start_date")),
            raw=data,
        )


@dataclass
class HappyHourRegistrationRequest:
    """``nl.engie.happyhour.data.datasource.model.HappyHourRegistrationRequest``."""

    address_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HappyHourRegistrationRequest:
        return cls(
            address_id=_str(data.get("address_id")),
            raw=data,
        )


@dataclass
class HappyHourSessionDTO:
    """``nl.engie.happyhour.data.datasource.model.HappyHourSessionDTO``."""

    address_id: str | None = None
    amount: float | None = None
    amount_ex: float | None = None
    asset_id: str | None = None
    end_date: datetime | None = None
    invoiced_date: date | None = None
    price: float | None = None
    quantity: float | None = None
    requested_date: date | None = None
    settlement_status: str | None = None
    start_date: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HappyHourSessionDTO:
        return cls(
            address_id=_str(data.get("address_id")),
            amount=_num(data.get("amount")),
            amount_ex=_num(data.get("amount_ex")),
            asset_id=_str(data.get("asset_id")),
            end_date=_dt(data.get("end_date")),
            invoiced_date=_date(data.get("invoiced_date")),
            price=_num(data.get("price")),
            quantity=_num(data.get("quantity")),
            requested_date=_date(data.get("requested_date")),
            settlement_status=_str(data.get("settlement_status")),
            start_date=_dt(data.get("start_date")),
            raw=data,
        )


@dataclass
class HappyHourSubscriptionModel:
    """``nl.engie.happyhour.data.datasource.model.HappyHourSubscriptionModel``."""

    address_id: str | None = None
    id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HappyHourSubscriptionModel:
        return cls(
            address_id=_str(data.get("address_id")),
            id=_str(data.get("id")),
            raw=data,
        )


@dataclass
class HappyHoursResponse:
    """``nl.engie.happyhour.data.datasource.model.HappyHoursResponse``."""

    discount_percentage: int | None = None
    discount_threshold: float | None = None
    eligible: bool | None = None
    happy_hours: list[HappyHour] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HappyHoursResponse:
        return cls(
            discount_percentage=_int(data.get("discount_percentage")),
            discount_threshold=_num(data.get("discount_threshold")),
            eligible=_bool(data.get("eligible")),
            happy_hours=[HappyHour.from_api(d) for d in _list(data.get("happy_hours")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class HeatPumpRequest:
    """``nl.engie.engieplus.data.assets.network.dto.HeatPumpRequest``."""

    address_id: str | None = None
    brand: Any = None
    type: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HeatPumpRequest:
        return cls(
            address_id=_str(data.get("address_id")),
            brand=data.get("brand"),
            type=data.get("type"),
            raw=data,
        )


@dataclass
class HeatPumpResponse:
    """``nl.engie.engieplus.data.assets.network.dto.HeatPumpResponse``."""

    address_id: str | None = None
    brand: Any = None
    id: str | None = None
    type: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HeatPumpResponse:
        return cls(
            address_id=_str(data.get("address_id")),
            brand=data.get("brand"),
            id=_str(data.get("id")),
            type=data.get("type"),
            raw=data,
        )


@dataclass
class HomeBatteryRequest:
    """``nl.engie.engieplus.data.assets.network.dto.HomeBatteryRequest``."""

    address_id: str | None = None
    capacity: float | None = None
    loading_speed: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HomeBatteryRequest:
        return cls(
            address_id=_str(data.get("address_id")),
            capacity=_num(data.get("capacity")),
            loading_speed=_num(data.get("loading_speed")),
            raw=data,
        )


@dataclass
class HomeBatteryResponse:
    """``nl.engie.engieplus.data.assets.network.dto.HomeBatteryResponse``."""

    address_id: str | None = None
    capacity: float | None = None
    id: str | None = None
    loading_speed: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> HomeBatteryResponse:
        return cls(
            address_id=_str(data.get("address_id")),
            capacity=_num(data.get("capacity")),
            id=_str(data.get("id")),
            loading_speed=_num(data.get("loading_speed")),
            raw=data,
        )


@dataclass
class Hyperlink:
    """``nl.engie.shared.persistance.models.push.Hyperlink``."""

    ref: str | None = None
    text: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Hyperlink:
        return cls(
            ref=_str(data.get("ref")),
            text=_str(data.get("text")),
            raw=data,
        )


@dataclass
class InitialLoginResponse:
    """``nl.engie.login_domain.model.InitialLoginResponse``."""

    birth_date: str | None = None
    email: str | None = None
    mobile_nr: str | None = None
    phone_nr: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> InitialLoginResponse:
        return cls(
            birth_date=_str(data.get("birth_date")),
            email=_str(data.get("email")),
            mobile_nr=_str(data.get("mobile_nr")),
            phone_nr=_str(data.get("phone_nr")),
            raw=data,
        )


@dataclass
class InterestArea:
    """``nl.engie.shared.network.models.InterestArea``."""

    code: str | None = None
    description: str | None = None
    is_interested: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> InterestArea:
        return cls(
            code=_str(data.get("code")),
            description=_str(data.get("description")),
            is_interested=_bool(data.get("is_interested")),
            raw=data,
        )


@dataclass
class LinkResponse:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.LinkResponse``."""

    link_token: str | None = None
    link_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> LinkResponse:
        return cls(
            link_token=_str(data.get("link_token")),
            link_url=_str(data.get("link_url")),
            raw=data,
        )


@dataclass
class MGWAccount:
    """``nl.engie.login_data.network.model.MGWAccount``."""

    customer_id: str | None = None
    subtitle: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MGWAccount:
        return cls(
            customer_id=_str(data.get("customer_id")),
            subtitle=_str(data.get("subtitle")),
            raw=data,
        )


@dataclass
class MGWCreateIDealTransactionRequest:
    """``nl.engie.transactions.data.network.model.MGWCreateIDealTransactionRequest``."""

    amount: float | None = None
    currency: str | None = None
    description: str | None = None
    entrance_code: str | None = None
    issuer_id: str | None = None
    purchase_id: str | None = None
    return_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MGWCreateIDealTransactionRequest:
        return cls(
            amount=_num(data.get("amount")),
            currency=_str(data.get("currency")),
            description=_str(data.get("description")),
            entrance_code=_str(data.get("entrance_code")),
            issuer_id=_str(data.get("issuer_id")),
            purchase_id=_str(data.get("purchase_id")),
            return_url=_str(data.get("return_url")),
            raw=data,
        )


@dataclass
class MGWCreateIDealTransactionResponse:
    """``nl.engie.transactions.data.network.model.MGWCreateIDealTransactionResponse``."""

    acquirer_id: str | None = None
    amount: float | None = None
    currency: str | None = None
    description: str | None = None
    entrance_code: str | None = None
    issuer_authentication_url: str | None = None
    issuer_id: str | None = None
    purchase_id: str | None = None
    status: int | None = None
    status_date_timestamp: datetime | None = None
    transaction_create_date_timestamp: datetime | None = None
    transaction_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MGWCreateIDealTransactionResponse:
        return cls(
            acquirer_id=_str(data.get("acquirer_id")),
            amount=_num(data.get("amount")),
            currency=_str(data.get("currency")),
            description=_str(data.get("description")),
            entrance_code=_str(data.get("entrance_code")),
            issuer_authentication_url=_str(data.get("issuer_authentication_url")),
            issuer_id=_str(data.get("issuer_id")),
            purchase_id=_str(data.get("purchase_id")),
            status=_int(data.get("status")),
            status_date_timestamp=_dt(data.get("status_date_timestamp")),
            transaction_create_date_timestamp=_dt(data.get("transaction_create_date_timestamp")),
            transaction_id=_str(data.get("transaction_id")),
            raw=data,
        )


@dataclass
class MGWTariff:
    """``nl.engie.shared.cost_calculation.data.dto.MGWTariff``."""

    date_end: datetime | None = None
    date_start: datetime | None = None
    description: str | None = None
    ean: str | None = None
    id: str | None = None
    price_ex: float | None = None
    tariff_type: Any = None
    tax: float | None = None
    unit_of_measure: Any = None
    use_for_feed_in: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MGWTariff:
        return cls(
            date_end=_dt(data.get("date_end")),
            date_start=_dt(data.get("date_start")),
            description=_str(data.get("description")),
            ean=_str(data.get("ean")),
            id=_str(data.get("id")),
            price_ex=_num(data.get("price_ex")),
            tariff_type=data.get("tariff_type"),
            tax=_num(data.get("tax")),
            unit_of_measure=data.get("unit_of_measure"),
            use_for_feed_in=data.get("use_for_feed_in"),
            raw=data,
        )


@dataclass
class MGWTariffPeriod:
    """``nl.engie.shared.cost_calculation.data.dto.MGWTariffPeriod``."""

    date_from: datetime | None = None
    date_to: datetime | None = None
    ean: str | None = None
    is_single: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MGWTariffPeriod:
        return cls(
            date_from=_dt(data.get("date_from")),
            date_to=_dt(data.get("date_to")),
            ean=_str(data.get("ean")),
            is_single=_bool(data.get("is_single")),
            raw=data,
        )


@dataclass
class MGWTariffsResponse:
    """``nl.engie.shared.cost_calculation.data.dto.MGWTariffsResponse``."""

    tariffs: list[MGWTariff] = field(default_factory=list)
    types: list[MGWTariffPeriod] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MGWTariffsResponse:
        return cls(
            tariffs=[MGWTariff.from_api(d) for d in _list(data.get("tariffs")) if isinstance(d, dict)],
            types=[MGWTariffPeriod.from_api(d) for d in _list(data.get("types")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class MGWUpdateIDealStatusResponse:
    """``nl.engie.transactions.data.network.model.MGWUpdateIDealStatusResponse``."""

    acquirer_id: str | None = None
    amount: float | None = None
    currency: str | None = None
    description: str | None = None
    entrance_code: str | None = None
    issuer_authentication_url: str | None = None
    issuer_id: str | None = None
    purchase_id: str | None = None
    status: int | None = None
    status_date_timestamp: datetime | None = None
    transaction_create_date_timestamp: datetime | None = None
    transaction_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MGWUpdateIDealStatusResponse:
        return cls(
            acquirer_id=_str(data.get("acquirer_id")),
            amount=_num(data.get("amount")),
            currency=_str(data.get("currency")),
            description=_str(data.get("description")),
            entrance_code=_str(data.get("entrance_code")),
            issuer_authentication_url=_str(data.get("issuer_authentication_url")),
            issuer_id=_str(data.get("issuer_id")),
            purchase_id=_str(data.get("purchase_id")),
            status=_int(data.get("status")),
            status_date_timestamp=_dt(data.get("status_date_timestamp")),
            transaction_create_date_timestamp=_dt(data.get("transaction_create_date_timestamp")),
            transaction_id=_str(data.get("transaction_id")),
            raw=data,
        )


@dataclass
class MandateWithDetails:
    """``nl.engie.engieplus.data.smart_charging.registration.dto.MandateWithDetails``."""

    address_city: str | None = None
    address_house_number: str | None = None
    address_house_number_addition: str | None = None
    address_street: str | None = None
    address_zip_code: str | None = None
    contact_id: str | None = None
    delivery_agreement_id: str | None = None
    ean: str | None = None
    email_address: str | None = None
    full_name: str | None = None
    vehicle_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MandateWithDetails:
        return cls(
            address_city=_str(data.get("address_city")),
            address_house_number=_str(data.get("address_house_number")),
            address_house_number_addition=_str(data.get("address_house_number_addition")),
            address_street=_str(data.get("address_street")),
            address_zip_code=_str(data.get("address_zip_code")),
            contact_id=_str(data.get("contact_id")),
            delivery_agreement_id=_str(data.get("delivery_agreement_id")),
            ean=_str(data.get("ean")),
            email_address=_str(data.get("email_address")),
            full_name=_str(data.get("full_name")),
            vehicle_id=_str(data.get("vehicle_id")),
            raw=data,
        )


@dataclass
class Measure:
    """``nl.engie.advice.measures.persistance.entities.Measure``."""

    article_name: str | None = None
    blue_tag_icon: str | None = None
    blue_tag_title: str | None = None
    category_id: str | None = None
    category_name: str | None = None
    construction_year_from: int | None = None
    construction_year_until: int | None = None
    cta_title: str | None = None
    cta_url: str | None = None
    dakscan_color: CMSColors | None = None
    dakscan_theme: str | None = None
    disclaimer_text: str | None = None
    green_tag_icon: str | None = None
    green_tag_title: str | None = None
    id: str | None = None
    image_url: str | None = None
    is_flagged_new_until: datetime | None = None
    main_text: str | None = None
    name: str | None = None
    short_sub_title: str | None = None
    short_title: str | None = None
    show_dakscan: bool | None = None
    show_disclaimer: bool | None = None
    show_ev_rekenmodule: bool | None = None
    show_for_building_types: list[str] = field(default_factory=list)
    show_for_connection_types: list[str] = field(default_factory=list)
    show_for_customer_types: list[str] = field(default_factory=list)
    show_for_energy_labels: list[str] = field(default_factory=list)
    show_for_interested_in_topics: list[str] = field(default_factory=list)
    show_for_not_interested_in_topics: list[str] = field(default_factory=list)
    show_for_property_owner_ship_type: str | None = None
    show_for_solar_powered: bool | None = None
    show_tip_block: bool | None = None
    show_usp_block: bool | None = None
    sort_order: int | None = None
    sub_title: str | None = None
    surface_from: int | None = None
    surface_until: int | None = None
    tip_color: CMSColors | None = None
    tip_cta_title: str | None = None
    tip_cta_url: str | None = None
    tip_main_text: str | None = None
    tip_title: str | None = None
    title: str | None = None
    usp_cta_title: str | None = None
    usp_cta_url: str | None = None
    usp_list: list[str] = field(default_factory=list)
    usp_title: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Measure:
        return cls(
            article_name=_str(data.get("article_name")),
            blue_tag_icon=_str(data.get("blue_tag_icon")),
            blue_tag_title=_str(data.get("blue_tag_title")),
            category_id=_str(data.get("category_id")),
            category_name=_str(data.get("category_name")),
            construction_year_from=_int(data.get("construction_year_from")),
            construction_year_until=_int(data.get("construction_year_until")),
            cta_title=_str(data.get("cta_title")),
            cta_url=_str(data.get("cta_url")),
            dakscan_color=_obj(data.get("dakscan_color"), CMSColors.from_api),
            dakscan_theme=_str(data.get("dakscan_theme")),
            disclaimer_text=_str(data.get("disclaimer_text")),
            green_tag_icon=_str(data.get("green_tag_icon")),
            green_tag_title=_str(data.get("green_tag_title")),
            id=_str(data.get("id")),
            image_url=_str(data.get("image_url")),
            is_flagged_new_until=_dt(data.get("is_flagged_new_until")),
            main_text=_str(data.get("main_text")),
            name=_str(data.get("name")),
            short_sub_title=_str(data.get("short_sub_title")),
            short_title=_str(data.get("short_title")),
            show_dakscan=_bool(data.get("show_dakscan")),
            show_disclaimer=_bool(data.get("show_disclaimer")),
            show_ev_rekenmodule=_bool(data.get("show_ev_rekenmodule")),
            show_for_building_types=[x for i in _list(data.get("show_for_building_types")) if (x := _str(i)) is not None],
            show_for_connection_types=[x for i in _list(data.get("show_for_connection_types")) if (x := _str(i)) is not None],
            show_for_customer_types=[x for i in _list(data.get("show_for_customer_types")) if (x := _str(i)) is not None],
            show_for_energy_labels=[x for i in _list(data.get("show_for_energy_labels")) if (x := _str(i)) is not None],
            show_for_interested_in_topics=[x for i in _list(data.get("show_for_interested_in_topics")) if (x := _str(i)) is not None],
            show_for_not_interested_in_topics=[x for i in _list(data.get("show_for_not_interested_in_topics")) if (x := _str(i)) is not None],
            show_for_property_owner_ship_type=_str(data.get("show_for_property_owner_ship_type")),
            show_for_solar_powered=_bool(data.get("show_for_solar_powered")),
            show_tip_block=_bool(data.get("show_tip_block")),
            show_usp_block=_bool(data.get("show_usp_block")),
            sort_order=_int(data.get("sort_order")),
            sub_title=_str(data.get("sub_title")),
            surface_from=_int(data.get("surface_from")),
            surface_until=_int(data.get("surface_until")),
            tip_color=_obj(data.get("tip_color"), CMSColors.from_api),
            tip_cta_title=_str(data.get("tip_cta_title")),
            tip_cta_url=_str(data.get("tip_cta_url")),
            tip_main_text=_str(data.get("tip_main_text")),
            tip_title=_str(data.get("tip_title")),
            title=_str(data.get("title")),
            usp_cta_title=_str(data.get("usp_cta_title")),
            usp_cta_url=_str(data.get("usp_cta_url")),
            usp_list=[x for i in _list(data.get("usp_list")) if (x := _str(i)) is not None],
            usp_title=_str(data.get("usp_title")),
            raw=data,
        )


@dataclass
class MerItem:
    """``nl.engie.shared.persistance.entities.MerItem``."""

    id: str | None = None
    startdate: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MerItem:
        return cls(
            id=_str(data.get("id")),
            startdate=_str(data.get("startDate")),
            raw=data,
        )


@dataclass
class MeteorologicalContext:
    """``nl.engie.shared.network.models.MeteorologicalContext``."""

    sunrise_at: str | None = None
    sunset_at: str | None = None
    weather_description: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MeteorologicalContext:
        return cls(
            sunrise_at=_str(data.get("sunrise_at")),
            sunset_at=_str(data.get("sunset_at")),
            weather_description=data.get("weather_description"),
            raw=data,
        )


@dataclass
class MeterStatusData:
    """``nl.engie.p1.data.network.model.MeterStatusData``."""

    electricity: str | None = None
    gas: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MeterStatusData:
        return cls(
            electricity=_str(data.get("electricity")),
            gas=_str(data.get("gas")),
            raw=data,
        )


@dataclass
class MeterStatusResponse:
    """``nl.engie.p1.data.network.model.MeterStatusResponse``."""

    data: MeterStatusData | None = None
    status: str | None = None
    timestamp: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MeterStatusResponse:
        return cls(
            data=_obj(data.get("data"), MeterStatusData.from_api),
            status=_str(data.get("status")),
            timestamp=_dt(data.get("timestamp")),
            raw=data,
        )


@dataclass
class MeteringPointRegister:
    """``nl.engie.shared.network.models.MeteringPointRegister``."""

    id: str | None = None
    metering_direction: str | None = None
    tariff_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MeteringPointRegister:
        return cls(
            id=_str(data.get("id")),
            metering_direction=_str(data.get("metering_direction")),
            tariff_type=_str(data.get("tariff_type")),
            raw=data,
        )


@dataclass
class MeteringPointWithTariffs:
    """``nl.engie.shared.network.models.MeteringPointWithTariffs``."""

    registers: list[MeteringPointRegister] = field(default_factory=list)
    tariffs: Tariffs | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MeteringPointWithTariffs:
        return cls(
            registers=[MeteringPointRegister.from_api(d) for d in _list(data.get("registers")) if isinstance(d, dict)],
            tariffs=_obj(data.get("tariffs"), Tariffs.from_api),
            raw=data,
        )


@dataclass
class Meterstand:
    """``nl.engie.shared.network.models.meterstands.Meterstand``."""

    name: str | None = None
    sequence: int | None = None
    value: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Meterstand:
        return cls(
            name=_str(data.get("name")),
            sequence=_int(data.get("sequence")),
            value=_int(data.get("value")),
            raw=data,
        )


@dataclass
class MeterstandsResponse:
    """``nl.engie.shared.network.models.meterstands.MeterstandsResponse``."""

    data: list[Register] = field(default_factory=list)
    ean: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MeterstandsResponse:
        return cls(
            data=[Register.from_api(d) for d in _list(data.get("data")) if isinstance(d, dict)],
            ean=_str(data.get("ean")),
            raw=data,
        )


@dataclass
class MoveContractCorrespondenceAddress:
    """``nl.engie.service.change_address.data.network.model.MoveContractCorrespondenceAddress``."""

    city: str | None = None
    house_number: str | None = None
    house_number_addition: str | None = None
    postal_code: str | None = None
    street: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MoveContractCorrespondenceAddress:
        return cls(
            city=_str(data.get("city")),
            house_number=_str(data.get("house_number")),
            house_number_addition=_str(data.get("house_number_addition")),
            postal_code=_str(data.get("postal_code")),
            street=_str(data.get("street")),
            raw=data,
        )


@dataclass
class MoveContractDeliveryAddressFrom:
    """``nl.engie.service.change_address.data.network.model.MoveContractDeliveryAddressFrom``."""

    electricity_agreement_id: str | None = None
    gas_agreement_id: str | None = None
    id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MoveContractDeliveryAddressFrom:
        return cls(
            electricity_agreement_id=_str(data.get("electricity_agreement_id")),
            gas_agreement_id=_str(data.get("gas_agreement_id")),
            id=_str(data.get("id")),
            raw=data,
        )


@dataclass
class MoveContractDeliveryAddressTo:
    """``nl.engie.service.change_address.data.network.model.MoveContractDeliveryAddressTo``."""

    city: str | None = None
    electricity_metering_point_ean: str | None = None
    gas_metering_point_ean: str | None = None
    house_number: str | None = None
    house_number_addition: str | None = None
    is_residential: bool | None = None
    postal_code: str | None = None
    street: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MoveContractDeliveryAddressTo:
        return cls(
            city=_str(data.get("city")),
            electricity_metering_point_ean=_str(data.get("electricity_metering_point_ean")),
            gas_metering_point_ean=_str(data.get("gas_metering_point_ean")),
            house_number=_str(data.get("house_number")),
            house_number_addition=_str(data.get("house_number_addition")),
            is_residential=_bool(data.get("is_residential")),
            postal_code=_str(data.get("postal_code")),
            street=_str(data.get("street")),
            raw=data,
        )


@dataclass
class MoveContractFrom:
    """``nl.engie.service.change_address.data.network.model.MoveContractFrom``."""

    delivery_address: MoveContractDeliveryAddressFrom | None = None
    departure_date: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MoveContractFrom:
        return cls(
            delivery_address=_obj(data.get("delivery_address"), MoveContractDeliveryAddressFrom.from_api),
            departure_date=_str(data.get("departure_date")),
            raw=data,
        )


@dataclass
class MoveContractRequest:
    """``nl.engie.service.change_address.data.network.model.MoveContractRequest``."""

    contact_phone_number: str | None = None
    from_: MoveContractFrom | None = None
    to: MoveContractTo | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MoveContractRequest:
        return cls(
            contact_phone_number=_str(data.get("contact_phone_number")),
            from_=_obj(data.get("from"), MoveContractFrom.from_api),
            to=_obj(data.get("to"), MoveContractTo.from_api),
            raw=data,
        )


@dataclass
class MoveContractTo:
    """``nl.engie.service.change_address.data.network.model.MoveContractTo``."""

    arrival_date: str | None = None
    correspondence_address: MoveContractCorrespondenceAddress | None = None
    delivery_address: MoveContractDeliveryAddressTo | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> MoveContractTo:
        return cls(
            arrival_date=_str(data.get("arrival_date")),
            correspondence_address=_obj(data.get("correspondence_address"), MoveContractCorrespondenceAddress.from_api),
            delivery_address=_obj(data.get("delivery_address"), MoveContractDeliveryAddressTo.from_api),
            raw=data,
        )


@dataclass
class NotSupportedVehicleRequest:
    """``nl.engie.engieplus.data.smart_charging.registration.dto.NotSupportedVehicleRequest``."""

    car_brand: str | None = None
    car_model: str | None = None
    contact_id: str | None = None
    email_address: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> NotSupportedVehicleRequest:
        return cls(
            car_brand=_str(data.get("car_brand")),
            car_model=_str(data.get("car_model")),
            contact_id=_str(data.get("contact_id")),
            email_address=_str(data.get("email_address")),
            raw=data,
        )


@dataclass
class OpeningHoursResponse:
    """``nl.engie.contact.network.OpeningHoursResponse``."""

    callcenter: ChannelInfo | None = None
    facebook: ChannelInfo | None = None
    livechat: ChannelInfo | None = None
    updated_at: datetime | None = None
    whatsapp: ChannelInfo | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> OpeningHoursResponse:
        return cls(
            callcenter=_obj(data.get("callcenter"), ChannelInfo.from_api),
            facebook=_obj(data.get("facebook"), ChannelInfo.from_api),
            livechat=_obj(data.get("livechat"), ChannelInfo.from_api),
            updated_at=_dt(data.get("updated_at")),
            whatsapp=_obj(data.get("whatsapp"), ChannelInfo.from_api),
            raw=data,
        )


@dataclass
class OutageMeterTypes:
    """``nl.engie.shared.persistance.models.push.OutageMeterTypes``."""

    conventional: bool | None = None
    smart: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> OutageMeterTypes:
        return cls(
            conventional=_bool(data.get("conventional")),
            smart=_bool(data.get("smart")),
            raw=data,
        )


@dataclass
class Output:
    """``nl.engie.chat.network.models.Output``."""

    dialog_path: str | None = None
    faq_question: str | None = None
    interaction_value: str | None = None
    is_default: bool | None = None
    kba_id: int | None = None
    output_id: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Output:
        return cls(
            dialog_path=_str(data.get("dialog_path")),
            faq_question=_str(data.get("faq_question")),
            interaction_value=_str(data.get("interaction_value")),
            is_default=_bool(data.get("is_default")),
            kba_id=_int(data.get("kba_id")),
            output_id=_int(data.get("output_id")),
            raw=data,
        )


@dataclass
class P4:
    """``nl.engie.shared.network.models.P4``."""

    data: UsageData | None = None
    ean: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> P4:
        return cls(
            data=_obj(data.get("data"), UsageData.from_api),
            ean=_str(data.get("ean")),
            raw=data,
        )


@dataclass
class P4Request:
    """``nl.engie.shared.network.models.P4Request``."""

    ean: str | None = None
    end_date: str | None = None
    start_date: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> P4Request:
        return cls(
            ean=_str(data.get("ean")),
            end_date=_str(data.get("end_date")),
            start_date=_str(data.get("start_date")),
            raw=data,
        )


@dataclass
class P4StatusData:
    """``nl.engie.shared.network.models.P4StatusData``."""

    date: datetime | None = None
    error_code: str | None = None
    error_description: str | None = None
    status: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> P4StatusData:
        return cls(
            date=_dt(data.get("date")),
            error_code=_str(data.get("error_code")),
            error_description=_str(data.get("error_description")),
            status=_str(data.get("status")),
            raw=data,
        )


@dataclass
class P4StatusResponse:
    """``nl.engie.shared.network.models.P4StatusResponse``."""

    data: list[P4StatusData] = field(default_factory=list)
    ean: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> P4StatusResponse:
        return cls(
            data=[P4StatusData.from_api(d) for d in _list(data.get("data")) if isinstance(d, dict)],
            ean=_str(data.get("ean")),
            raw=data,
        )


@dataclass
class PatchEnodeSolarConfiguration:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.PatchEnodeSolarConfiguration``."""

    azimuth: int | None = None
    capacity: float | None = None
    tilt: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PatchEnodeSolarConfiguration:
        return cls(
            azimuth=_int(data.get("azimuth")),
            capacity=_num(data.get("capacity")),
            tilt=_int(data.get("tilt")),
            raw=data,
        )


@dataclass
class PatchPolicyBody:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.PatchPolicyBody``."""

    battery_reserve: int | None = None
    schedule: PolicySchedule | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PatchPolicyBody:
        return cls(
            battery_reserve=_int(data.get("battery_reserve")),
            schedule=_obj(data.get("schedule"), PolicySchedule.from_api),
            raw=data,
        )


@dataclass
class PaymentInfo:
    """``nl.engie.shared.network.models.PaymentInfo``."""

    is_paid: bool | None = None
    payment_possible: bool | None = None
    status: Any = None
    status_description: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PaymentInfo:
        return cls(
            is_paid=_bool(data.get("is_paid")),
            payment_possible=_bool(data.get("payment_possible")),
            status=data.get("status"),
            status_description=_str(data.get("status_description")),
            raw=data,
        )


@dataclass
class PeriodDetails:
    """``nl.engie.shared.network.models.PeriodDetails``."""

    ean_code: str | None = None
    end_date: datetime | None = None
    start_date: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PeriodDetails:
        return cls(
            ean_code=_str(data.get("ean_code")),
            end_date=_dt(data.get("end_date")),
            start_date=_dt(data.get("start_date")),
            raw=data,
        )


@dataclass
class PhoneOptInRequest:
    """``nl.engie.shared.network.models.PhoneOptInRequest``."""

    phone_opt_in: bool | None = None
    phone_opt_in_source: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PhoneOptInRequest:
        return cls(
            phone_opt_in=_bool(data.get("phone_opt_in")),
            phone_opt_in_source=_str(data.get("phone_opt_in_source")),
            raw=data,
        )


@dataclass
class PolicyRestrictionSchedule:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.PolicyRestrictionSchedule``."""

    end_time: Any = None
    start_time: Any = None
    type: str | None = None
    weekdays: list[int] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PolicyRestrictionSchedule:
        return cls(
            end_time=data.get("end_time"),
            start_time=data.get("start_time"),
            type=_str(data.get("type")),
            weekdays=[x for i in _list(data.get("weekdays")) if (x := _int(i)) is not None],
            raw=data,
        )


@dataclass
class PolicySchedule:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.PolicySchedule``."""

    friday: Schedule | None = None
    monday: Schedule | None = None
    saturday: Schedule | None = None
    sunday: Schedule | None = None
    thursday: Schedule | None = None
    tuesday: Schedule | None = None
    wednesday: Schedule | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PolicySchedule:
        return cls(
            friday=_obj(data.get("friday"), Schedule.from_api),
            monday=_obj(data.get("monday"), Schedule.from_api),
            saturday=_obj(data.get("saturday"), Schedule.from_api),
            sunday=_obj(data.get("sunday"), Schedule.from_api),
            thursday=_obj(data.get("thursday"), Schedule.from_api),
            tuesday=_obj(data.get("tuesday"), Schedule.from_api),
            wednesday=_obj(data.get("wednesday"), Schedule.from_api),
            raw=data,
        )


@dataclass
class PreCheck:
    """``nl.engie.shared.network.models.solar.PreCheck``."""

    data: PreCheckData | None = None
    ean: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PreCheck:
        return cls(
            data=_obj(data.get("data"), PreCheckData.from_api),
            ean=_str(data.get("ean")),
            raw=data,
        )


@dataclass
class PreCheckData:
    """``nl.engie.shared.network.models.solar.PreCheckData``."""

    result: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PreCheckData:
        return cls(
            result=_str(data.get("result")),
            raw=data,
        )


@dataclass
class PrepaymentChange:
    """``nl.engie.shared.network.models.PrepaymentChange``."""

    from_: int | None = None
    to: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PrepaymentChange:
        return cls(
            from_=_int(data.get("from")),
            to=_int(data.get("to")),
            raw=data,
        )


@dataclass
class PrepaymentResult:
    """``nl.engie.shared.network.models.PrepaymentResult``."""

    data: PrepaymentChange | None = None
    ean: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PrepaymentResult:
        return cls(
            data=_obj(data.get("data"), PrepaymentChange.from_api),
            ean=_str(data.get("ean")),
            raw=data,
        )


@dataclass
class Pro6PPError:
    """``nl.engie.shared.network.models.pro6pp.Pro6PPError``."""

    message: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Pro6PPError:
        return cls(
            message=_str(data.get("message")),
            raw=data,
        )


@dataclass
class Pro6PPResponse:
    """``nl.engie.shared.network.models.pro6pp.Pro6PPResponse``."""

    error: Pro6PPError | None = None
    status: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Pro6PPResponse:
        return cls(
            error=_obj(data.get("error"), Pro6PPError.from_api),
            status=_str(data.get("status")),
            raw=data,
        )


@dataclass
class ProspectImportsClientDataRequest:
    """``nl.engie.service.accountimport.readings.data.network.dto.ProspectImportsClientDataRequest``."""

    customer_access_token: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ProspectImportsClientDataRequest:
        return cls(
            customer_access_token=_str(data.get("customer_access_token")),
            raw=data,
        )


@dataclass
class QuestionnaireBody:
    """``nl.engie.shared.network.models.QuestionnaireBody``."""

    answers: Any = None
    ean: str | None = None
    questionnaire: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> QuestionnaireBody:
        return cls(
            answers=data.get("answers"),
            ean=_str(data.get("ean")),
            questionnaire=_str(data.get("questionnaire")),
            raw=data,
        )


@dataclass
class QuoteRequestBody:
    """``nl.engie.ev.network.model.QuoteRequestBody``."""

    charging_points_count: str | None = None
    charging_points_delivery_time: str | None = None
    company: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    salutation: str | None = None
    supply_address_city: str | None = None
    supply_address_house_number: str | None = None
    supply_address_house_number_addition: str | None = None
    supply_address_postcode: str | None = None
    supply_address_street: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> QuoteRequestBody:
        return cls(
            charging_points_count=_str(data.get("charging_points_count")),
            charging_points_delivery_time=_str(data.get("charging_points_delivery_time")),
            company=_str(data.get("company")),
            email=_str(data.get("email")),
            first_name=_str(data.get("first_name")),
            last_name=_str(data.get("last_name")),
            phone_number=_str(data.get("phone_number")),
            salutation=_str(data.get("salutation")),
            supply_address_city=_str(data.get("supply_address_city")),
            supply_address_house_number=_str(data.get("supply_address_house_number")),
            supply_address_house_number_addition=_str(data.get("supply_address_house_number_addition")),
            supply_address_postcode=_str(data.get("supply_address_postcode")),
            supply_address_street=_str(data.get("supply_address_street")),
            raw=data,
        )


@dataclass
class RegisterRequest:
    """``nl.engie.p1.data.network.model.RegisterRequest``."""

    email_address: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> RegisterRequest:
        return cls(
            email_address=_str(data.get("email_address")),
            first_name=_str(data.get("first_name")),
            last_name=_str(data.get("last_name")),
            raw=data,
        )


@dataclass
class RegisterSSOBody:
    """``nl.engie.p1.data.network.model.RegisterSSOBody``."""

    external_provider_access_token: str | None = None
    primary_identifier: str | None = None
    primary_identifier_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> RegisterSSOBody:
        return cls(
            external_provider_access_token=_str(data.get("external_provider_access_token")),
            primary_identifier=_str(data.get("primary_identifier")),
            primary_identifier_type=_str(data.get("primary_identifier_type")),
            raw=data,
        )


@dataclass
class RelinkBody:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.RelinkBody``."""

    language: str | None = None
    redirect_uri: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> RelinkBody:
        return cls(
            language=_str(data.get("language")),
            redirect_uri=_str(data.get("redirect_uri")),
            raw=data,
        )


@dataclass
class Schedule:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.Schedule``."""

    deadline: str | None = None
    minimum_charge_target: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Schedule:
        return cls(
            deadline=_str(data.get("deadline")),
            minimum_charge_target=_int(data.get("minimum_charge_target")),
            raw=data,
        )


@dataclass
class SetChargerLocationBody:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.SetChargerLocationBody``."""

    location_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SetChargerLocationBody:
        return cls(
            location_id=_str(data.get("location_id")),
            raw=data,
        )


@dataclass
class SetEnodeLocationZoneBody:
    """``nl.engie.engieplus.data.smart_charging.network.dto.enode.SetEnodeLocationZoneBody``."""

    zone_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SetEnodeLocationZoneBody:
        return cls(
            zone_id=_str(data.get("zone_id")),
            raw=data,
        )


@dataclass
class SettingsCardsResponse:
    """``nl.engie.shared.network.models.SettingsCardsResponse``."""

    show_deposit_price_ceiling_info: bool | None = None
    show_inzicht_dakscan_card: bool | None = None
    show_inzicht_ev_leads_card: bool | None = None
    show_inzicht_smart_charging_invitation_card: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SettingsCardsResponse:
        return cls(
            show_deposit_price_ceiling_info=_bool(data.get("show_deposit_price_ceiling_info")),
            show_inzicht_dakscan_card=_bool(data.get("show_inzicht_dakscan_card")),
            show_inzicht_ev_leads_card=_bool(data.get("show_inzicht_ev_leads_card")),
            show_inzicht_smart_charging_invitation_card=_bool(data.get("show_inzicht_smart_charging_invitation_card")),
            raw=data,
        )


@dataclass
class SimpleResponse:
    """``nl.engie.shared.network.models.SimpleResponse``."""

    code: str | None = None
    success: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SimpleResponse:
        return cls(
            code=_str(data.get("code")),
            success=_bool(data.get("success")),
            raw=data,
        )


@dataclass
class SimpleStatus:
    """``nl.engie.shared.network.models.SimpleStatus``."""

    status: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SimpleStatus:
        return cls(
            status=_str(data.get("status")),
            raw=data,
        )


@dataclass
class SmartChargingSession:
    """``nl.engie.engieplus.data.smart_charging.network.dto.egw.SmartChargingSession``."""

    address_id: str | None = None
    amount: float | None = None
    amount_ex: float | None = None
    asset_id: str | None = None
    end_date: datetime | None = None
    invoiced_date: date | None = None
    price: float | None = None
    quantity: float | None = None
    requested_date: date | None = None
    settlement_status: str | None = None
    start_date: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SmartChargingSession:
        return cls(
            address_id=_str(data.get("address_id")),
            amount=_num(data.get("amount")),
            amount_ex=_num(data.get("amount_ex")),
            asset_id=_str(data.get("asset_id")),
            end_date=_dt(data.get("end_date")),
            invoiced_date=_date(data.get("invoiced_date")),
            price=_num(data.get("price")),
            quantity=_num(data.get("quantity")),
            requested_date=_date(data.get("requested_date")),
            settlement_status=_str(data.get("settlement_status")),
            start_date=_dt(data.get("start_date")),
            raw=data,
        )


@dataclass
class SolarPanelRequest:
    """``nl.engie.engieplus.data.assets.network.dto.SolarPanelRequest``."""

    address_id: str | None = None
    quantity: int | None = None
    watt_peak: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SolarPanelRequest:
        return cls(
            address_id=_str(data.get("address_id")),
            quantity=_int(data.get("quantity")),
            watt_peak=_num(data.get("watt_peak")),
            raw=data,
        )


@dataclass
class SolarPanelResponse:
    """``nl.engie.engieplus.data.assets.network.dto.SolarPanelResponse``."""

    address_id: str | None = None
    id: str | None = None
    quantity: int | None = None
    watt_peak: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SolarPanelResponse:
        return cls(
            address_id=_str(data.get("address_id")),
            id=_str(data.get("id")),
            quantity=_int(data.get("quantity")),
            watt_peak=_num(data.get("watt_peak")),
            raw=data,
        )


@dataclass
class SolarPotential:
    """``nl.engie.shared.network.models.solar.SolarPotential``."""

    data: SolarPotentialData | None = None
    ean: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SolarPotential:
        return cls(
            data=_obj(data.get("data"), SolarPotentialData.from_api),
            ean=_str(data.get("ean")),
            raw=data,
        )


@dataclass
class SolarPotentialData:
    """``nl.engie.shared.network.models.solar.SolarPotentialData``."""

    annual_savings_c_o2: int | None = None
    annual_savings_cost: int | None = None
    annual_savings_k_wh: int | None = None
    c_o2_savings: SolarSavings | None = None
    cost_savings: SolarSavings | None = None
    ean: str | None = None
    k_wh_savings: SolarSavings | None = None
    payback_period: float | None = None
    price_excl_vat: int | None = None
    price_incl_vat: int | None = None
    solar_panel_count: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SolarPotentialData:
        return cls(
            annual_savings_c_o2=_int(data.get("annual_savings_c_o2")),
            annual_savings_cost=_int(data.get("annual_savings_cost")),
            annual_savings_k_wh=_int(data.get("annual_savings_k_wh")),
            c_o2_savings=_obj(data.get("c_o2_savings"), SolarSavings.from_api),
            cost_savings=_obj(data.get("cost_savings"), SolarSavings.from_api),
            ean=_str(data.get("ean")),
            k_wh_savings=_obj(data.get("k_wh_savings"), SolarSavings.from_api),
            payback_period=_num(data.get("payback_period")),
            price_excl_vat=_int(data.get("price_excl_vat")),
            price_incl_vat=_int(data.get("price_incl_vat")),
            solar_panel_count=_int(data.get("solar_panel_count")),
            raw=data,
        )


@dataclass
class SolarSavings:
    """``nl.engie.shared.network.models.solar.SolarSavings``."""

    f_04: int | None = None
    f_08: int | None = None
    f_12: int | None = None
    f_02: int | None = None
    f_01: int | None = None
    f_07: int | None = None
    f_06: int | None = None
    f_03: int | None = None
    f_05: int | None = None
    f_11: int | None = None
    f_10: int | None = None
    f_09: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SolarSavings:
        return cls(
            f_04=_int(data.get("04")),
            f_08=_int(data.get("08")),
            f_12=_int(data.get("12")),
            f_02=_int(data.get("02")),
            f_01=_int(data.get("01")),
            f_07=_int(data.get("07")),
            f_06=_int(data.get("06")),
            f_03=_int(data.get("03")),
            f_05=_int(data.get("05")),
            f_11=_int(data.get("11")),
            f_10=_int(data.get("10")),
            f_09=_int(data.get("09")),
            raw=data,
        )


@dataclass
class StartVerificationRequest:
    """``nl.engie.login_data.network.StartVerificationRequest``."""

    chosen_bank_id: str | None = None
    return_urls: VerificationReturnUrls | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StartVerificationRequest:
        return cls(
            chosen_bank_id=_str(data.get("chosen_bank_id")),
            return_urls=_obj(data.get("return_urls"), VerificationReturnUrls.from_api),
            raw=data,
        )


@dataclass
class StartVerificationResponse:
    """``nl.engie.login_data.network.StartVerificationResponse``."""

    authentication_return_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StartVerificationResponse:
        return cls(
            authentication_return_url=_str(data.get("authentication_return_url")),
            raw=data,
        )


@dataclass
class StartVerificationViaLetterRequest:
    """``nl.engie.login_data.network.model.StartVerificationViaLetterRequest``."""

    address_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StartVerificationViaLetterRequest:
        return cls(
            address_id=_str(data.get("address_id")),
            raw=data,
        )


@dataclass
class TariffsBody:
    """``nl.engie.shared.network.models.TariffsBody``."""

    cost_gas: float | None = None
    cost_power: float | None = None
    cost_power_low: float | None = None
    cost_return: float | None = None
    cost_return_low: float | None = None
    delivery: bool | None = None
    type: str | None = None
    usage_gas: int | None = None
    usage_power: int | None = None
    usage_power_low: int | None = None
    usage_return: int | None = None
    usage_return_low: int | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TariffsBody:
        return cls(
            cost_gas=_num(data.get("cost_gas")),
            cost_power=_num(data.get("cost_power")),
            cost_power_low=_num(data.get("cost_power_low")),
            cost_return=_num(data.get("cost_return")),
            cost_return_low=_num(data.get("cost_return_low")),
            delivery=_bool(data.get("delivery")),
            type=_str(data.get("type")),
            usage_gas=_int(data.get("usage_gas")),
            usage_power=_int(data.get("usage_power")),
            usage_power_low=_int(data.get("usage_power_low")),
            usage_return=_int(data.get("usage_return")),
            usage_return_low=_int(data.get("usage_return_low")),
            raw=data,
        )


@dataclass
class LoginDataTokenResponse:
    """``nl.engie.login_data.network.model.TokenResponse``."""

    access_token: str | None = None
    expires_in: int | None = None
    token_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> LoginDataTokenResponse:
        return cls(
            access_token=_str(data.get("access_token")),
            expires_in=_int(data.get("expires_in")),
            token_type=_str(data.get("token_type")),
            raw=data,
        )


@dataclass
class P1TokenResponse:
    """``nl.engie.p1.data.network.model.TokenResponse``."""

    access_token: str | None = None
    expires_in: int | None = None
    id_token: str | None = None
    refresh_token: str | None = None
    scope: list[str] = field(default_factory=list)
    token_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> P1TokenResponse:
        return cls(
            access_token=_str(data.get("access_token")),
            expires_in=_int(data.get("expires_in")),
            id_token=_str(data.get("id_token")),
            refresh_token=_str(data.get("refresh_token")),
            scope=[x for i in _list(data.get("scope")) if (x := _str(i)) is not None],
            token_type=_str(data.get("token_type")),
            raw=data,
        )


@dataclass
class TransactionsResponse:
    """``nl.engie.shared.network.models.TransactionsResponse``."""

    transactions: list[Transaction] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TransactionsResponse:
        return cls(
            transactions=[Transaction.from_api(d) for d in _list(data.get("transactions")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class UpdateContractDetailsRequest:
    """``nl.engie.login_data.network.UpdateContractDetailsRequest``."""

    contractenddate: str | None = None
    fixedcostsperyearineuros: int | None = None
    prepaymentpermonthineuros: int | None = None
    suppliername: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UpdateContractDetailsRequest:
        return cls(
            contractenddate=_str(data.get("contractEndDate")),
            fixedcostsperyearineuros=_int(data.get("fixedCostsPerYearInEuros")),
            prepaymentpermonthineuros=_int(data.get("prepaymentPerMonthInEuros")),
            suppliername=_str(data.get("supplierName")),
            raw=data,
        )


@dataclass
class UpdatePasswordRequest:
    """``nl.engie.login_data.network.model.UpdatePasswordRequest``."""

    hint: str | None = None
    password: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UpdatePasswordRequest:
        return cls(
            hint=_str(data.get("hint")),
            password=_str(data.get("password")),
            raw=data,
        )


@dataclass
class Usage:
    """``nl.engie.shared.network.models.Usage``."""

    peak: bool | None = None
    start_date: datetime | None = None
    value: float | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Usage:
        return cls(
            peak=_bool(data.get("peak")),
            start_date=_dt(data.get("start_date")),
            value=_num(data.get("value")),
            raw=data,
        )


@dataclass
class UsageData:
    """``nl.engie.shared.network.models.UsageData``."""

    return_: list[Usage] = field(default_factory=list)
    type: str | None = None
    unit: str | None = None
    usage: list[Usage] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UsageData:
        return cls(
            return_=[Usage.from_api(d) for d in _list(data.get("return")) if isinstance(d, dict)],
            type=_str(data.get("type")),
            unit=_str(data.get("unit")),
            usage=[Usage.from_api(d) for d in _list(data.get("usage")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class UserInfoResponse:
    """``nl.engie.login_data.network.model.UserInfoResponse``."""

    accounts: list[MGWAccount] = field(default_factory=list)
    is_employee: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UserInfoResponse:
        return cls(
            accounts=[MGWAccount.from_api(d) for d in _list(data.get("accounts")) if isinstance(d, dict)],
            is_employee=_bool(data.get("is_employee")),
            raw=data,
        )


@dataclass
class UserWithAddresses:
    """``nl.engie.shared.network.models.UserWithAddresses``."""

    current_contract: CurrentContract | None = None
    delivery_addresses: list[AddressWithMeteringPoints] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UserWithAddresses:
        return cls(
            current_contract=_obj(data.get("current_contract"), CurrentContract.from_api),
            delivery_addresses=[AddressWithMeteringPoints.from_api(d) for d in _list(data.get("delivery_addresses")) if isinstance(d, dict)],
            raw=data,
        )


@dataclass
class VehicleCreationResponse:
    """``nl.engie.engieplus.data.smart_charging.registration.dto.VehicleCreationResponse``."""

    vehicle_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> VehicleCreationResponse:
        return cls(
            vehicle_id=_str(data.get("vehicle_id")),
            raw=data,
        )


@dataclass
class VerificationReturnUrls:
    """``nl.engie.login_data.network.VerificationReturnUrls``."""

    on_failure: str | None = None
    on_success: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> VerificationReturnUrls:
        return cls(
            on_failure=_str(data.get("on_failure")),
            on_success=_str(data.get("on_success")),
            raw=data,
        )


@dataclass
class WaitingTimes:
    """``nl.engie.contact.network.WaitingTimes``."""

    business_waiting_time: int | None = None
    customer_waiting_time: int | None = None
    updated_at: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> WaitingTimes:
        return cls(
            business_waiting_time=_int(data.get("business_waiting_time")),
            customer_waiting_time=_int(data.get("customer_waiting_time")),
            updated_at=_dt(data.get("updated_at")),
            raw=data,
        )


@dataclass
class WarmWelcomeResponse:
    """``nl.engie.shared.network.models.WarmWelcomeResponse``."""

    message: str | None = None
    meteorological_context: MeteorologicalContext | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> WarmWelcomeResponse:
        return cls(
            message=_str(data.get("message")),
            meteorological_context=_obj(data.get("meteorological_context"), MeteorologicalContext.from_api),
            raw=data,
        )


@dataclass
class WhitePaperRequestBody:
    """``nl.engie.ev.network.model.WhitePaperRequestBody``."""

    email_address: str | None = None
    first_name_or_letters: str | None = None
    last_name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> WhitePaperRequestBody:
        return cls(
            email_address=_str(data.get("email_address")),
            first_name_or_letters=_str(data.get("first_name_or_letters")),
            last_name=_str(data.get("last_name")),
            raw=data,
        )


__all__ = [
    "AbstractBaseResponse",
    "AccessTokenResponse",
    "AddMeterstandItem",
    "EvAddress",
    "SharedAddress",
    "AddressMetaData",
    "AddressWithMeteringPoints",
    "AircoRequest",
    "AircoResponse",
    "AllowedRange",
    "AllowedRangeKW",
    "Approval",
    "ApprovalData",
    "ArticlesResponse",
    "BankAccount",
    "BankDto",
    "BaseAddress",
    "BaseDocument",
    "BaseEnodeEntityResponse",
    "BaseResponse",
    "CMSColors",
    "Car",
    "ChangePasswordRequest",
    "ChangePasswordResponse",
    "ChannelInfo",
    "ChargeCardRequestBody",
    "ChargingPolicy",
    "ChargingStationRequest",
    "ChargingStationResponse",
    "CheckAccountResponse",
    "ClientImportsProspectDataRequest",
    "CollectiveResponse",
    "ConsumptionDetailData",
    "ConsumptionDetails",
    "ConsumptionsData",
    "ContactData",
    "ContactPreferences",
    "ContactRequestBody",
    "ContractAddress",
    "ContractExtension",
    "ContractOfferExtraInformation",
    "CreateEnodeLocationBody",
    "CreateEnodeSolarConfiguration",
    "CreateLinkBody",
    "CreatePolicyBody",
    "CurrentContract",
    "Customer",
    "DayAheadPriceDto",
    "Document",
    "DocumentsResponse",
    "EdsnMeteringPoint",
    "EdsnRequest",
    "ElectricCarRequest",
    "ElectricCarResponse",
    "EnodeCapability",
    "EnodeChargeRateLimitCapability",
    "EnodeCharger",
    "EnodeChargerCapabilities",
    "EnodeChargerChargeState",
    "EnodeChargerInformation",
    "EnodeChargerLocation",
    "EnodeChargingSession",
    "EnodeChargingSessionOutcome",
    "EnodeChargingSessionOutcomeData",
    "EnodeChargingSessionStatistics",
    "EnodeChargingSessionStatisticsAggregated",
    "EnodeChargingSessionTarget",
    "EnodeChargingSessionTargetData",
    "EnodeChargingSessionValuation",
    "EnodeChargingSessionValuationTariffCost",
    "EnodeIntervention",
    "EnodeInterventionResolution",
    "EnodeLinkedVendor",
    "EnodeLocation",
    "EnodeLocationName",
    "EnodeSessionTarget",
    "EnodeSolarConfiguration",
    "EnodeUser",
    "EnodeVehicle",
    "EnodeVehicleCapabilities",
    "EnodeVehicleChargeState",
    "EnodeVehicleInformation",
    "EnodeVehicleLocation",
    "Error",
    "ExchangeTokenBody",
    "ForgotPasswordRequest",
    "ForgotUsernameRequest",
    "HappyHour",
    "HappyHourRegistrationRequest",
    "HappyHourSessionDTO",
    "HappyHourSubscriptionModel",
    "HappyHoursResponse",
    "HeatPumpRequest",
    "HeatPumpResponse",
    "HomeBatteryRequest",
    "HomeBatteryResponse",
    "Hyperlink",
    "InitialLoginResponse",
    "InterestArea",
    "LinkResponse",
    "MGWAccount",
    "MGWCreateIDealTransactionRequest",
    "MGWCreateIDealTransactionResponse",
    "MGWTariff",
    "MGWTariffPeriod",
    "MGWTariffsResponse",
    "MGWUpdateIDealStatusResponse",
    "MandateWithDetails",
    "Measure",
    "MerItem",
    "MeteorologicalContext",
    "MeterStatusData",
    "MeterStatusResponse",
    "MeteringPointRegister",
    "MeteringPointWithTariffs",
    "Meterstand",
    "MeterstandsResponse",
    "MoveContractCorrespondenceAddress",
    "MoveContractDeliveryAddressFrom",
    "MoveContractDeliveryAddressTo",
    "MoveContractFrom",
    "MoveContractRequest",
    "MoveContractTo",
    "NotSupportedVehicleRequest",
    "OpeningHoursResponse",
    "OutageMeterTypes",
    "Output",
    "P4",
    "P4Request",
    "P4StatusData",
    "P4StatusResponse",
    "PatchEnodeSolarConfiguration",
    "PatchPolicyBody",
    "PaymentInfo",
    "PeriodDetails",
    "PhoneOptInRequest",
    "PolicyRestrictionSchedule",
    "PolicySchedule",
    "PreCheck",
    "PreCheckData",
    "PrepaymentChange",
    "PrepaymentResult",
    "Pro6PPError",
    "Pro6PPResponse",
    "ProspectImportsClientDataRequest",
    "QuestionnaireBody",
    "QuoteRequestBody",
    "RegisterRequest",
    "RegisterSSOBody",
    "RelinkBody",
    "Schedule",
    "SetChargerLocationBody",
    "SetEnodeLocationZoneBody",
    "SettingsCardsResponse",
    "SimpleResponse",
    "SimpleStatus",
    "SmartChargingSession",
    "SolarPanelRequest",
    "SolarPanelResponse",
    "SolarPotential",
    "SolarPotentialData",
    "SolarSavings",
    "StartVerificationRequest",
    "StartVerificationResponse",
    "StartVerificationViaLetterRequest",
    "TariffsBody",
    "LoginDataTokenResponse",
    "P1TokenResponse",
    "TransactionsResponse",
    "UpdateContractDetailsRequest",
    "UpdatePasswordRequest",
    "Usage",
    "UsageData",
    "UserInfoResponse",
    "UserWithAddresses",
    "VehicleCreationResponse",
    "VerificationReturnUrls",
    "WaitingTimes",
    "WarmWelcomeResponse",
    "WhitePaperRequestBody",
]
