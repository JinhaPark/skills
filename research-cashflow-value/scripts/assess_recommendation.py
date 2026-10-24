#!/usr/bin/env python3
"""Audit one frozen recommendation using supplied, sourced observations.

No data fetching, investment scoring, qualitative thesis inference, or persistence.
The JSON contract is documented in references/assessment-policy.md.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo


def day(value):
    return dt.date.fromisoformat(value)


def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed


def number(value, label, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{label} must be positive")
    return value


def sourced(item, label):
    refs = item.get("source_refs", [])
    if not isinstance(refs, list) or not refs or not all(isinstance(x, str) and x.strip() for x in refs):
        raise ValueError(f"{label} requires source_refs")


def checked_price(item, as_of, label, base_currency):
    sourced(item, label)
    observed = timestamp(item["observed_at"])
    if observed > as_of:
        raise ValueError(f"{label} is after assessment cutoff")
    value = number(item["value"], label, positive=label == "entry")
    if value < 0 or (value == 0 and item.get("kind") != "terminal_proceeds"):
        raise ValueError("a zero endpoint requires documented terminal proceeds")
    if item.get("basis") not in {"split_adjusted_ex_dividend", "total_return_index"}:
        raise ValueError(f"{label} requires an explicit price/index basis")
    if not item.get("share_basis") or not item.get("currency"):
        raise ValueError(f"{label} requires share_basis and currency")
    fx = item.get("fx_to_base")
    number(fx, "fx_to_base", positive=True)
    if item["currency"] == base_currency:
        if fx != 1:
            raise ValueError("same-currency FX must equal 1")
    elif not item.get("fx_source_refs"):
        raise ValueError("foreign-currency FX requires sources")
    return observed


def returns(entry, endpoint, dividends, base_currency, as_of):
    start = checked_price(entry, as_of, "entry", base_currency)
    end = checked_price(endpoint, as_of, "endpoint", base_currency)
    if end < start:
        raise ValueError("endpoint precedes entry")
    for key in ("basis", "share_basis", "currency"):
        if entry[key] != endpoint[key]:
            raise ValueError(f"entry and endpoint {key} differ")
    initial = entry["value"] * entry["fx_to_base"]
    final = endpoint["value"] * endpoint["fx_to_base"]
    if entry["basis"] == "total_return_index":
        if dividends is not None:
            raise ValueError("do not add dividends to a total-return index")
        return {"price_return": None, "local_price_return": None, "total_return": final / initial - 1,
                "dividend_treatment": "reinvested in supplied total-return index",
                "price_return_na_reason": "total-return index does not isolate price appreciation"}
    price_return = final / initial - 1
    if dividends is None:
        return {"price_return": price_return, "local_price_return": endpoint["value"] / entry["value"] - 1, "total_return": None,
                "total_return_na_reason": "dividend cash, including verified zero, unavailable"}
    sourced(dividends, "dividends")
    if dividends.get("share_basis") != entry["share_basis"]:
        raise ValueError("dividends must use the same entry-share basis")
    if timestamp(dividends["period_start"]) != start or timestamp(dividends["period_end"]) != end:
        raise ValueError("dividend window must equal the holding window")
    if dividends.get("base_currency") != base_currency:
        raise ValueError("dividend base currency differs")
    cash = number(dividends["base_cash_per_entry_share"], "dividend cash")
    if cash < 0:
        raise ValueError("dividends cannot be negative")
    return {"price_return": price_return, "local_price_return": endpoint["value"] / entry["value"] - 1,
            "total_return": (final + cash) / initial - 1, "dividend_treatment": "cash received, not reinvested"}


def thesis_checks(criteria, observations, as_of):
    results = []
    ops = {">": lambda x, y: x > y, ">=": lambda x, y: x >= y,
           "<": lambda x, y: x < y, "<=": lambda x, y: x <= y,
           "==": lambda x, y: x == y}
    for criterion in criteria:
        ident = criterion["id"]
        if criterion.get("trigger_operator") not in ops:
            raise ValueError(f"unsupported thesis trigger for {ident}")
        threshold = number(criterion["trigger_threshold"], "trigger threshold")
        observation = observations.get(ident)
        if observation is None:
            status = "pending" if day(criterion["period_end"]) > as_of.date() else "unavailable"
            results.append({"id": ident, "status": status})
            continue
        sourced(observation, ident)
        available = timestamp(observation["available_at"])
        if available > as_of or day(observation["period_end"]) > as_of.date():
            raise ValueError(f"future thesis observation {ident}")
        if available.date() < day(observation["period_end"]):
            raise ValueError(f"thesis actual {ident} was available before its period ended")
        for key in ("metric_id", "period_end", "unit", "currency"):
            if observation.get(key) != criterion.get(key):
                raise ValueError(f"thesis observation {ident} has different {key}")
        actual = number(observation["value"], "thesis actual")
        triggered = ops[criterion["trigger_operator"]](actual, threshold)
        results.append({"id": ident, "status": "falsification_triggered" if triggered else "not_triggered",
                        "actual": actual, "threshold": threshold, "source_refs": observation["source_refs"]})
    return results


def join_publication(snapshot, receipt, snapshot_sha256, receipt_sha256, entry_event=None):
    """Join immutable source documents; hashes are computed from actual CLI bytes."""
    if receipt.get("status") != "delivered":
        raise ValueError("delivery receipt must confirm delivered")
    if receipt.get("report_id") != snapshot.get("report_id"):
        raise ValueError("snapshot and receipt report IDs differ")
    if receipt.get("recommendation_sha256") != snapshot_sha256:
        raise ValueError("receipt does not match original recommendation bytes")
    if not snapshot.get("frozen_report_sha256") or receipt.get("report_sha256") != snapshot["frozen_report_sha256"]:
        raise ValueError("receipt does not match the frozen report hash")
    if not receipt.get("report_reference"):
        raise ValueError("delivery receipt requires actual report reference")
    result = {**snapshot, "publication_status": "delivered", "publication_at": receipt["publication_at"],
              "report_reference": receipt["report_reference"],
              "input_provenance": {"recommendation_sha256": snapshot_sha256,
                                   "delivery_receipt_sha256": receipt_sha256,
                                   "report_sha256": snapshot["frozen_report_sha256"]}}
    if entry_event is not None:
        if snapshot.get("entry_convention") != "next_executable_close" or snapshot.get("entry") is not None:
            raise ValueError("entry events may only complete a frozen, unfilled executable-entry rule")
        result["entry"] = entry_event["entry"]
        result["entry_session"] = entry_event["entry_session"]
    return result


def assess(record, observations, as_of):
    cutoff = timestamp(as_of)
    result = {"schema_version": 1, "report_id": record["report_id"], "as_of": as_of,
              "qualitative_thesis_review_required": True}
    decision = record.get("recommendation")
    result["recommendation"] = decision
    result["buy_cohort_eligible"] = decision == "buy"
    if record.get("publication_status") != "delivered":
        raise ValueError("only confirmed published records enter the assessment cohort")
    if record.get("original_snapshot_available") is not True:
        return {**result, "status": "legacy_unavailable", "reason": "original recommendation snapshot unavailable; do not reconstruct targets from hindsight"}
    published = timestamp(record["publication_at"])
    if published > cutoff:
        raise ValueError("publication is after assessment cutoff")
    if decision not in {"buy", "watch", "avoid", "no_selection"}:
        raise ValueError("unsupported recommendation")
    if decision == "no_selection":
        return {**result, "status": "not_a_stock_recommendation", "reason": "evaluate process and reopening conditions separately"}
    horizon = day(record["target_horizon"]["end_date"])
    exchange_zone = ZoneInfo(record["target_horizon"]["exchange_timezone"])
    if horizon < published.astimezone(exchange_zone).date():
        raise ValueError("target horizon precedes publication")
    result["thesis_checks"] = thesis_checks(record.get("thesis_criteria", []), observations.get("thesis", {}), cutoff)
    entry = record.get("entry")
    if entry is None:
        return {**result, "status": "baseline_unavailable", "returns": None, "reason": "original entry or first executable entry observation unavailable"}
    entry_time = checked_price(entry, cutoff, "entry", record["base_currency"])
    convention = record.get("entry_convention")
    if convention not in {"publication_reference", "next_executable_close"}:
        raise ValueError("entry convention must be frozen explicitly")
    if convention == "next_executable_close":
        if entry_time < published:
            raise ValueError("executable entry cannot precede publication")
        session = record.get("entry_session")
        if not session or not session.get("source_refs"):
            return {**result, "status": "baseline_unavailable", "returns": None, "reason": "first eligible executable close is not evidenced"}
        sourced(session, "entry session")
        if record.get("entry_rule") != "first_eligible_session_close":
            raise ValueError("executable entry requires the frozen first-session rule")
        if timestamp(session["for_publication_at"]) != published or timestamp(session["close_at"]) != entry_time:
            raise ValueError("executable entry differs from evidenced first eligible close")
    elif entry_time > published:
        raise ValueError("publication reference price cannot follow publication")
    result["return_interpretation"] = "reference-price comparison; not a realized or executable trade" if convention == "publication_reference" else "hypothetical published-signal holding period; not an actual trade"
    result["target_horizon_end"] = horizon.isoformat()
    horizon_session = observations.get("horizon_session")
    if horizon_session is None or not horizon_session.get("source_refs"):
        if cutoff.astimezone(exchange_zone).date() >= horizon:
            return {**result, "status": "awaiting_horizon_data", "horizon_status": "unverified_session", "returns": None,
                    "reason": "original horizon first-session close is not evidenced"}
        horizon_close = None
    else:
        sourced(horizon_session, "horizon session")
        horizon_close = timestamp(horizon_session["close_at"])
        if horizon_session.get("for_date") != horizon.isoformat() or horizon_close.astimezone(exchange_zone).date() < horizon:
            raise ValueError("horizon session must map to the original horizon date")
    mature = horizon_close is not None and cutoff >= horizon_close
    result["horizon_status"] = "matured" if mature else "not_yet_matured"
    endpoint = observations.get("endpoint")
    if endpoint is None:
        return {**result, "status": "awaiting_horizon_data" if mature else "pending_horizon", "returns": None}
    end = checked_price(endpoint, cutoff, "endpoint", record["base_currency"])
    if mature:
        if end != horizon_close:
            raise ValueError("mature outcome requires the exact original horizon first-session close")
        if record["target_horizon"].get("market_close_rule") != "first_session_on_or_after":
            raise ValueError("unsupported horizon market-session rule")
        result["status"] = "matured"
    else:
        result["status"] = "interim"
    result["endpoint_at"] = endpoint["observed_at"]
    result["returns"] = returns(entry, endpoint, observations.get("dividends"), record["base_currency"], cutoff)
    benchmark = record.get("benchmark")
    benchmark_end = observations.get("benchmark_endpoint")
    result["benchmark_returns"] = None
    result["excess_total_return"] = None
    if benchmark and benchmark.get("entry") and benchmark_end:
        if timestamp(benchmark["entry"]["observed_at"]).date() != entry_time.date() or timestamp(benchmark_end["observed_at"]).date() != end.date():
            raise ValueError("benchmark must use the same holding window")
        bench_returns = returns(benchmark["entry"], benchmark_end, observations.get("benchmark_dividends"), record["base_currency"], cutoff)
        result["benchmark_returns"] = bench_returns
        if result["returns"]["total_return"] is not None and bench_returns["total_return"] is not None:
            if result["returns"].get("dividend_treatment") != bench_returns.get("dividend_treatment"):
                result["benchmark_na_reason"] = "dividend reinvestment conventions differ; align them before computing excess return"
            else:
                result["excess_total_return"] = result["returns"]["total_return"] - bench_returns["total_return"]
    else:
        result["benchmark_na_reason"] = "original benchmark or matching sourced observations unavailable"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recommendation", type=Path)
    parser.add_argument("observations", type=Path)
    parser.add_argument("--receipt", type=Path, help="Actual immutable delivery receipt required for full snapshots")
    parser.add_argument("--as-of", required=True, help="Timezone-aware timestamp")
    args = parser.parse_args()
    raw = args.recommendation.read_bytes()
    record = json.loads(raw)
    observation_raw = args.observations.read_bytes()
    observations = json.loads(observation_raw)
    if record.get("original_snapshot_available") is True:
        if args.receipt is None:
            parser.error("--receipt is required for a full original snapshot")
        receipt_raw = args.receipt.read_bytes()
        record = join_publication(record, json.loads(receipt_raw), hashlib.sha256(raw).hexdigest(),
                                  hashlib.sha256(receipt_raw).hexdigest(), observations.get("entry_event"))
        record["input_provenance"]["observations_sha256"] = hashlib.sha256(observation_raw).hexdigest()
    print(json.dumps(assess(record, observations, args.as_of), ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
