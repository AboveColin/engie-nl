#!/usr/bin/env python3
"""Read-only probe of the ENGIE gateway with the stored token pair.

Calls /user, /consumptions (7 days), /meterstands (30 days), /estimations,
/transactions, /mandates, /tariffs/day-ahead and /mer/periods. Writes each
raw response to ``tests/fixtures/_live/<name>.json`` (gitignored) and prints a
one-line summary per endpoint. Nothing here writes to ENGIE.

Redact before promoting a fixture into ``tests/fixtures/``: EANs, customer id,
names, address, email, bank account, document references.
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engie_nl import EngieApiError, EngieClient, EnergyType, OktaAuth, TokenSet  # noqa: E402
from scripts.login import TOKEN_FILE, save  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "_live"


def dump(name: str, payload: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


async def main() -> int:
    if not TOKEN_FILE.exists():
        print(f"no tokens at {TOKEN_FILE}; run scripts/login.py first")
        return 1
    tokens = TokenSet.from_dict(json.loads(TOKEN_FILE.read_text(encoding="utf-8")))

    async with OktaAuth() as auth:
        async with EngieClient(tokens, auth=auth, on_tokens_updated=save) as client:
            user = await client.get_user()
            dump("user", user.raw)
            eans = user.eans
            print(f"/user            ok  customer={'set' if user.customer_id else 'MISSING'} eans={len(eans)} "
                  f"addresses={len(user.delivery_addresses)}")
            for mp in user.metering_points:
                print(f"   ean …{mp.ean[-4:]} type={mp.kind} smart={mp.smart} single_tariff={mp.single_tariff} "
                      f"product={mp.current_product.name if mp.current_product else None}")

            today = date.today()
            checks = [
                ("consumptions", lambda: client.get_consumptions(eans, start=today - timedelta(days=7), end=today)),
                ("meterstands", lambda: client.get_meter_readings(eans, start=today - timedelta(days=30), end=today)),
                ("estimations", lambda: client.get_estimations(eans, amount=int(
                    next((mp.prepayment_amount for mp in user.metering_points if mp.prepayment_amount), 0) or 0))),
                ("transactions", client.get_transactions),
                ("mandates", lambda: client.get_mandates(eans)),
                ("day_ahead_E", lambda: client.get_day_ahead_prices(EnergyType.ELECTRICITY)),
                ("day_ahead_G", lambda: client.get_day_ahead_prices(EnergyType.GAS)),
                ("mer_periods", client.get_mer_periods),
                ("outages", lambda: client.get_outages(user.customer_id)),
            ]
            for name, call in checks:
                if not eans and name in ("consumptions", "meterstands", "estimations", "mandates"):
                    print(f"/{name:<15} skipped, no EANs")
                    continue
                try:
                    result = await call()
                except EngieApiError as err:
                    dump(name, {"status": err.status, "body": err.body})
                    print(f"/{name:<15} HTTP {err.status}  {str(err.body)[:120]}")
                    continue
                raw = [r.raw for r in result] if isinstance(result, list) else result.raw
                dump(name, raw)
                count = len(result) if isinstance(result, list) else 1
                extra = ""
                if name == "consumptions":
                    extra = " rows=" + ",".join(str(len(s.data)) for s in result)
                if name == "meterstands":
                    extra = " registers=" + ",".join(str(len(m.registers)) for m in result)
                print(f"/{name:<15} ok  items={count}{extra}")
    print(f"raw responses in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
