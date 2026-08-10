from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _date(value: object) -> pd.Timestamp | pd.NaT:
    return pd.to_datetime(value, errors="coerce").normalize()


def _delta(left: object, right: object) -> int | None:
    left_date, right_date = _date(left), _date(right)
    if pd.isna(left_date) or pd.isna(right_date):
        return None
    return int((left_date - right_date).days)


def _comparison_state(row: dict[str, object]) -> str:
    if row["identity_match_state"] == "TICKER_REUSE_CONFLICT":
        return "TICKER_REUSE_CONFLICT"
    if row["sec_boundary_state"] == "SCHEDULED_REQUIRES_CONFIRMATION":
        return "SEC_SCHEDULED_REQUIRES_CONFIRMATION"
    if row["sec_boundary_state"] == "OBSERVED_EXCHANGE_END_CANDIDATE":
        return "SEC_EXCHANGE_END_CANDIDATE_NOT_LEGAL_DELIST"
    if row["vendor_first_seen_to_daily_delta_days"] == 0:
        return "VENDOR_WINDOW_START_MATCHES_DAILY_PRESENCE"
    return "SOURCE_DATE_UNAVAILABLE_OR_NOT_COMPARABLE"


def run(config_path: Path) -> Path:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    master_path = Path(config["instrument_master_path"])
    presence_path = Path(config["market_presence_run"]) / "lifecycle_market_presence_bounds.parquet"
    review_path = Path(config["filing_review_run"]) / "target_interval_filing_review_ledger.parquet"
    output_root = Path(config["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    master = pd.read_parquet(master_path)
    presence = pd.read_parquet(presence_path)
    reviews = pd.read_parquet(review_path)
    tickers = sorted(presence["ticker"].unique())
    master = master[master["ticker"].isin(tickers)].copy()
    if len(master) != len(tickers) or master["ticker"].nunique() != len(tickers):
        raise ValueError("instrument master must resolve exactly one row per pilot ticker")

    reviewed = reviews.groupby("ticker", sort=False).agg(
        security_class_id=("security_class_id", "first"),
        sec_reviewed_filing_count=("accession_number", "count"),
        sec_source_accessions=("accession_number", lambda values: json.dumps(list(values))),
        sec_legal_list_date=("legal_list_date", "first"),
        sec_legal_delist_date=("legal_delist_date", "first"),
    )
    observed_end = reviews[reviews["boundary_authority"].eq("OBSERVED_EXCHANGE_TRADING_END_CANDIDATE")]
    scheduled_end = reviews[reviews["boundary_authority"].eq("SCHEDULED_EXCHANGE_TRADING_END_CANDIDATE")]
    observed_map = observed_end.set_index("ticker")["review_date"].to_dict()
    scheduled_map = scheduled_end.set_index("ticker")["review_date"].to_dict()

    joined = presence.merge(master, on=["ticker", "instrument_id"], how="left", validate="one_to_one")
    joined = joined.merge(reviewed, on="ticker", how="left", validate="one_to_one")
    rows = []
    conflicts = set(config["ticker_reuse_conflicts"])
    for record in joined.to_dict("records"):
        ticker = record["ticker"]
        sec_boundary_state = "NONE_ADMITTED"
        sec_exchange_end_candidate = None
        if ticker in observed_map:
            sec_boundary_state = "OBSERVED_EXCHANGE_END_CANDIDATE"
            sec_exchange_end_candidate = observed_map[ticker]
        elif ticker in scheduled_map:
            sec_boundary_state = "SCHEDULED_REQUIRES_CONFIRMATION"
            sec_exchange_end_candidate = scheduled_map[ticker]
        row = {
            "ticker": ticker,
            "cik": record["cik"],
            "instrument_id": record["instrument_id"],
            "security_class_id": record["security_class_id"],
            "vendor_window_source": "MASSIVE_POLYGON_HISTORICAL_REFERENCE_OBSERVATIONS",
            "vendor_first_seen_date": record["lt1b_first_seen_date"],
            "vendor_last_observed_date": record["lt1b_last_observed_date"],
            "vendor_overview_list_date": record["overview_list_date"],
            "vendor_delisted_utc": None,
            "vendor_delisted_source": "NOT_PRESENT_IN_INSTRUMENT_MASTER_V0_1",
            "target_identity_window_start": record["identity_window_start"],
            "target_identity_window_end": record["identity_window_end"],
            "target_identity_window_source": record["identity_window_source"],
            "market_first_daily_date": record["first_observed_daily_date"],
            "market_last_daily_date": record["last_observed_daily_date"],
            "market_first_trade_timestamp_source_naive": record["first_observed_trade_timestamp_source_naive"],
            "market_last_trade_timestamp_source_naive": record["last_observed_trade_timestamp_source_naive"],
            "market_trade_presence_state": record["trade_presence_state"],
            "sec_reviewed_filing_count": int(record["sec_reviewed_filing_count"]) if pd.notna(record["sec_reviewed_filing_count"]) else 0,
            "sec_source_accessions": record["sec_source_accessions"] if pd.notna(record["sec_source_accessions"]) else "[]",
            "sec_legal_list_date": record["sec_legal_list_date"],
            "sec_legal_delist_date": record["sec_legal_delist_date"],
            "sec_exchange_end_candidate": sec_exchange_end_candidate,
            "sec_boundary_state": sec_boundary_state,
            "identity_match_state": "TICKER_REUSE_CONFLICT" if ticker in conflicts else "TARGET_IDENTITY_MATCHED",
            "class_match_state": "TARGET_COMMON_STOCK_CLASS",
            "vendor_first_seen_to_identity_start_delta_days": _delta(record["lt1b_first_seen_date"], record["identity_window_start"]),
            "vendor_first_seen_to_daily_delta_days": _delta(record["lt1b_first_seen_date"], record["first_observed_daily_date"]),
            "vendor_last_observed_to_daily_delta_days": _delta(record["lt1b_last_observed_date"], record["last_observed_daily_date"]),
            "promotion_status": config["promotion_status"],
        }
        row["comparison_state"] = _comparison_state(row)
        row["quality_state"] = "PASS_WITH_RESTRICTIONS"
        rows.append(row)

    result = pd.DataFrame(rows).sort_values("ticker")
    output_path = output_root / "lifecycle_window_reconciliation.parquet"
    result.to_parquet(output_path, index=False)
    result.to_csv(output_root / "lifecycle_window_reconciliation.csv", index=False)
    manifest = {
        "run_id": output_root.name,
        "status": "PASS_WITH_RESTRICTIONS",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "policy_id": config["policy_id"],
        "row_count": len(result),
        "ticker_count": result["ticker"].nunique(),
        "comparison_state_counts": result["comparison_state"].value_counts().to_dict(),
        "identity_match_state_counts": result["identity_match_state"].value_counts().to_dict(),
        "sec_legal_list_dates_admitted": int(result["sec_legal_list_date"].notna().sum()),
        "sec_legal_delist_dates_admitted": int(result["sec_legal_delist_date"].notna().sum()),
        "input_hashes": {
            "instrument_master": _sha256(master_path),
            "market_presence": _sha256(presence_path),
            "filing_review": _sha256(review_path),
        },
        "output_sha256": _sha256(output_path),
        "parent_universe_scale_authorized": config["parent_universe_scale_authorized"],
    }
    (output_root / "final_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    print(run(args.config))


if __name__ == "__main__":
    main()
