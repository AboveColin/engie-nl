#!/usr/bin/env python3
"""Generate engie_nl/generated.py from the APK's api-map.json.

The map comes from the apk-reverse-engineering repo, which extracts every
Retrofit interface and every model reachable from one. This script turns the
model half into dataclasses so the client can return typed objects for all 148
endpoints instead of dicts for the 137 the curated models do not cover.

Run it after re-extracting a new APK, passing the map or setting
ENGIE_NL_API_MAP:

    python3 tools/generate_models.py path/to/api-map.json

The 19 models in models.py are hand-written and take precedence: they carry
behaviour the generator cannot infer, such as ConsumptionSeries.total or the
register classification. CURATED lists them so they are not emitted twice.
"""

from __future__ import annotations

import json
import keyword
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "engie_nl" / "generated.py"

# The map is extracted by a separate repo that is not published with this one.
# Point ENGIE_NL_API_MAP at its api-map.json; the fallback is a checkout sitting
# beside this one.
DEFAULT_MAP = Path(
    os.environ.get("ENGIE_NL_API_MAP")
    or REPO.parent / "apk-reverse-engineering/docs/engie-nl/api-map.json"
)

# Hand-written in models.py. The generator skips these names entirely.
CURATED = {
    "Consumption", "ConsumptionSeries", "DayAheadPrice", "DeliveryAddress",
    "DocumentRef", "EnergyType", "EstimationCosts", "Mandate", "MerPeriod",
    "MeteringPoint", "MeterReadings", "OutageMessage", "ProductInfo",
    "Reading", "Register", "Tariffs", "Transaction", "TransactionStatus",
    "User",
}

# json type -> (python annotation, coercion helper). A helper of None means the
# value is passed through untouched.
SCALARS = {
    "String": ("str | None", "_str"),
    "int": ("int | None", "_int"),
    "Integer": ("int | None", "_int"),
    "long": ("int | None", "_int"),
    "Long": ("int | None", "_int"),
    "float": ("float | None", "_num"),
    "Float": ("float | None", "_num"),
    "double": ("float | None", "_num"),
    "Double": ("float | None", "_num"),
    "BigDecimal": ("float | None", "_num"),
    "boolean": ("bool | None", "_bool"),
    "Boolean": ("bool | None", "_bool"),
    "DateTime": ("datetime | None", "_dt"),
    "Instant": ("datetime | None", "_dt"),
    "LocalDate": ("date | None", "_date"),
    "LocalDateTime": ("datetime | None", "_dt"),
}


def camel(text: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[._-]", text) if part)


def snake(name: str) -> str:
    """A model field's wire name to a Python attribute name."""
    out = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    out = re.sub(r"_+", "_", out)
    if not out or out[0].isdigit():
        out = f"f_{out}"
    if keyword.iskeyword(out) or out in {"raw", "from_api"}:
        out = f"{out}_"
    return out


def resolve_names(models: dict[str, dict[str, Any]]) -> dict[str, str]:
    """FQN to the Python class name, disambiguating repeated simple names.

    Two pairs collide in the 6.9.2 map: TokenResponse (the MGW one and the
    Net2Grid one, with different fields) and Address (the EV request one and the
    stored one). A collision takes the first package segment under nl.engie as a
    prefix, so nl.engie.p1.* TokenResponse becomes P1TokenResponse.
    """
    counts = Counter(v["name"] for v in models.values())
    names: dict[str, str] = {}
    for fqn, model in models.items():
        name = model["name"]
        if counts[name] > 1:
            parts = fqn.split(".")
            zone = parts[2] if len(parts) > 2 and parts[0] == "nl" else parts[0]
            name = camel(zone) + name
        names[fqn] = name
    return names


def annotate(field_type: str, by_name: dict[str, str]) -> tuple[str, str]:
    """A field's type to (annotation, expression template with {v} for the value)."""
    field_type = (field_type or "").strip()
    inner = re.match(r"^(?:List|ArrayList|Set)<(.+)>$", field_type)
    if inner:
        item = inner.group(1).strip()
        if item in SCALARS:
            ann, helper = SCALARS[item]
            base = ann.replace(" | None", "")
            return f"list[{base}]", f"[x for i in _list({{v}}) if (x := {helper}(i)) is not None]"
        if item in by_name:
            cls = by_name[item]
            return f"list[{cls}]", f"[{cls}.from_api(d) for d in _list({{v}}) if isinstance(d, dict)]"
        return "list[Any]", "_list({v})"
    if field_type in SCALARS:
        ann, helper = SCALARS[field_type]
        return ann, f"{helper}({{v}})"
    if field_type in by_name:
        cls = by_name[field_type]
        return f"{cls} | None", f"_obj({{v}}, {cls}.from_api)"
    # Enums stay strings: an unknown value from a newer app must not raise.
    return "Any", "{v}"


def render(models: dict[str, dict[str, Any]]) -> str:
    names = resolve_names(models)
    # An enum is a bare value on the wire, not an object, so it maps to a string.
    by_name = {
        m["name"]: names[fqn]
        for fqn, m in models.items()
        if m["kind"] == "class" and names[fqn] not in CURATED
    }
    for fqn, m in models.items():
        if m["kind"] == "class":
            by_name.setdefault(names[fqn], names[fqn])

    emitted = [
        (names[fqn], m)
        for fqn, m in sorted(models.items(), key=lambda kv: kv[1]["name"])
        if m["kind"] == "class" and names[fqn] not in CURATED
    ]

    used_curated = sorted(
        {
            inner
            for _, model in emitted
            for f in model.get("fields", [])
            for inner in [re.sub(r"^(?:List|ArrayList|Set)<(.+)>$", r"\1", (f["type"] or "").strip())]
            if inner in CURATED
        }
    )

    lines = [
        '"""Models generated from the ENGIE app\'s api-map.json. Do not edit by hand.',
        "",
        f"{len(emitted)} dataclasses covering every response the mapped endpoints return,",
        "except the 19 in models.py, which are hand-written and carry behaviour.",
        "",
        "Regenerate with tools/generate_models.py. Every field is optional: the",
        "gateway omits keys freely, and a missing key must not raise. ``raw`` keeps",
        "the response as it arrived, so a field the map did not know about is never",
        "lost.",
        '"""',
        "",
        "# pylint: disable=too-many-lines,too-many-instance-attributes,line-too-long",
        "",
        "from __future__ import annotations",
        "",
        "from collections.abc import Callable",
        "from dataclasses import dataclass, field",
        "from datetime import date, datetime",
        "from typing import Any, TypeVar",
        "",
        "from .models import _bool, _date, _dt, _int, _list, _num, _str",
        *(
            [f"from .models import {', '.join(used_curated)}"]
            if used_curated
            else []
        ),
        "",
        "_T = TypeVar(\"_T\")",
        "",
        "",
        "def _obj(value: Any, factory: Callable[[dict[str, Any]], _T]) -> _T | None:",
        '    """A nested object, or None when the gateway sent anything else."""',
        "    return factory(value) if isinstance(value, dict) else None",
    ]

    for cls, model in emitted:
        fields = model.get("fields", [])
        lines.append("")
        lines.append("")
        lines.append("@dataclass")
        lines.append(f"class {cls}:")
        doc = f'    """``{model["fqn"]}``.'
        if not fields:
            lines.append(doc + ' The app declares no fields on it."""')
            lines.append("")
            lines.append("    raw: dict[str, Any] = field(default_factory=dict, repr=False)")
            lines.append("")
            lines.append("    @classmethod")
            lines.append(f"    def from_api(cls, data: dict[str, Any]) -> {cls}:")
            lines.append("        return cls(raw=data)")
            continue
        lines.append(doc + '"""')
        lines.append("")
        seen: set[str] = set()
        body: list[tuple[str, str, str]] = []
        for f in fields:
            attr = snake(f["json"])
            while attr in seen:
                attr += "_"
            seen.add(attr)
            ann, expr = annotate(f["type"], by_name)
            body.append((attr, ann, expr.replace("{v}", f'data.get("{f["json"]}")')))
        for attr, ann, _ in body:
            default = " = field(default_factory=list)" if ann.startswith("list[") else " = None"
            lines.append(f"    {attr}: {ann}{default}")
        lines.append("    raw: dict[str, Any] = field(default_factory=dict, repr=False)")
        lines.append("")
        lines.append("    @classmethod")
        lines.append(f"    def from_api(cls, data: dict[str, Any]) -> {cls}:")
        lines.append("        return cls(")
        for attr, _, expr in body:
            lines.append(f"            {attr}={expr},")
        lines.append("            raw=data,")
        lines.append("        )")

    lines.append("")
    lines.append("")
    lines.append("__all__ = [")
    for cls, _ in emitted:
        lines.append(f'    "{cls}",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAP
    if not source.exists():
        print(f"api-map.json not found at {source}", file=sys.stderr)
        return 1
    models = json.loads(source.read_text())["models"]
    OUT.write_text(render(models))
    count = sum(
        1 for m in models.values() if m["kind"] == "class" and m["name"] not in CURATED
    )
    print(f"wrote {OUT.relative_to(REPO)}: {count} dataclasses from {source.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
