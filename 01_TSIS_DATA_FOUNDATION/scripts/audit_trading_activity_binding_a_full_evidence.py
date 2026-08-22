"""Bounded, value-level audit of certified Trading Activity Binding A outputs.

This auditor deliberately does not rematerialize features.  It freezes a
deterministic shard x cohort sample from the certified 2,400 TARGET sessions,
reads every row for the selected sessions, and checks schemas, identities,
causality, missingness/state semantics, domains, and formulas that can be
replayed from the three materialized families.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


FAMILIES = ("current_state", "multiscale_contrast", "pit_baseline_and_surprise")
CURRENT_VARIABLES = (
    "eligible_trade_count", "eligible_share_volume", "eligible_dollar_volume",
    "trade_arrival_rate", "median_intertrade_duration_us",
    "p10_intertrade_duration_us", "largest_trade_volume_share",
    "active_subwindow_fraction", "max_subwindow_trade_share",
    "max_subwindow_volume_share", "consecutive_active_subwindows",
)
MULTISCALE_VARIABLES = ("activity_rate_multiscale_log_ratio",)
BASELINE_VARIABLES = (
    "trade_count_percentile_pit", "share_volume_percentile_pit",
    "dollar_volume_percentile_pit", "arrival_rate_percentile_pit",
    "trade_count_log_ratio_to_pit", "share_volume_log_ratio_to_pit",
    "dollar_volume_log_ratio_to_pit", "intertrade_duration_compression",
)
IDENTITY = {
    "feature_spec_id": "trading_activity_binding_a_exact_specification",
    "feature_version": "v0_2",
    "binding_id": "trading_activity_binding_a_candidate_v0_2",
    "scope_id": "legacy_rth_reconciled_event_time_research_only",
    "duplicate_policy_id": "PRESERVE_EXACT_DUPLICATES_PRIMARY_V0_1",
    "coverage_mode": "INFERRED_FROM_SUCCESSFUL_FULL_RTH_REQUEST",
    "lineage_manifest_id": "trading_activity_binding_a_multisession_pilot_lineage_v0_2",
}
BASELINE_MINIMUMS = {"B20": 15, "B60": 40, "B120": 80}
SUBWINDOW_SECONDS_BY_WINDOW = {5: 1, 15: 1, 30: 1, 60: 5, 300: 5}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jsonable(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        value = value.item()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


class Evidence:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []
        self.profiles: dict[tuple[str, str], dict[str, Any]] = {}
        self.states: Counter[tuple[str, str, str]] = Counter()
        self.examples: dict[tuple[str, str], list[Any]] = defaultdict(list)

    def check(
        self,
        family: str,
        name: str,
        evaluated: int,
        failures: int,
        target_id: str = "FULL_CERTIFIED_INVENTORY",
        detail: str = "",
    ) -> None:
        self.checks.append({
            "family": family, "check_id": name, "target_id": target_id,
            "evaluated_rows": int(evaluated), "failure_count": int(failures),
            "status": "PASS" if failures == 0 else "FAIL", "detail": detail,
        })

    def profile(self, family: str, frame: pd.DataFrame, variables: tuple[str, ...]) -> None:
        for column in variables:
            series = pd.to_numeric(frame[column], errors="coerce")
            valid = series.dropna()
            key = (family, column)
            item = self.profiles.setdefault(key, {
                "family": family, "variable": column, "row_count": 0,
                "non_null_count": 0, "null_count": 0, "zero_count": 0,
                "non_finite_count": 0, "minimum": None, "maximum": None,
            })
            item["row_count"] += len(series)
            item["non_null_count"] += int(series.notna().sum())
            item["null_count"] += int(series.isna().sum())
            item["zero_count"] += int(series.eq(0).sum())
            if not valid.empty:
                array = valid.to_numpy(dtype=float)
                item["non_finite_count"] += int((~np.isfinite(array)).sum())
                finite = array[np.isfinite(array)]
                if finite.size:
                    low, high = float(finite.min()), float(finite.max())
                    item["minimum"] = low if item["minimum"] is None else min(item["minimum"], low)
                    item["maximum"] = high if item["maximum"] is None else max(item["maximum"], high)
                    examples = self.examples[key]
                    for value in finite[: 5 - len(examples)]:
                        examples.append(float(value))

    def state_counts(self, family: str, frame: pd.DataFrame, columns: tuple[str, ...]) -> None:
        for column in columns:
            for value, count in frame[column].astype("string").fillna("<NULL>").value_counts().items():
                self.states[(family, column, str(value))] += int(count)


def failures_where(mask: pd.Series | np.ndarray) -> int:
    return int(np.asarray(pd.Series(mask).fillna(False), dtype=bool).sum())


def expected_subwindow_seconds(windows: pd.Series) -> pd.Series:
    """Return the exact Binding A v0.2 W-to-w contract."""
    return windows.map(SUBWINDOW_SECONDS_BY_WINDOW)


def not_close(left: pd.Series, right: pd.Series, *, atol: float = 1e-12) -> pd.Series:
    comparable = left.notna() & right.notna()
    result = pd.Series(False, index=left.index)
    result.loc[comparable] = ~np.isclose(
        left.loc[comparable].astype(float), right.loc[comparable].astype(float),
        rtol=1e-12, atol=atol,
    )
    return result


def read_columns(path: str, columns: list[str]) -> pd.DataFrame:
    # ParquetFile is intentional: source files live below Hive-looking
    # ticker=/session_date= paths while also carrying those columns internally.
    # Dataset discovery would merge the partition dictionary type with the
    # physical string field and can fail before any evidence is read.
    return pq.ParquetFile(path).read(
        columns=list(dict.fromkeys(columns))
    ).to_pandas()


def select_targets(reference: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    current = reference.loc[reference["family"].eq("current_state")].copy()
    targets = targets.copy()
    targets["session_date"] = targets["session_date"].astype(str)
    joined = current.merge(
        targets[["block_id", "cohort_id", "instrument_id", "session_date", "ticker_as_of_session"]],
        on=["block_id", "instrument_id", "session_date"], validate="one_to_one",
    )
    paths = reference.pivot(
        index=["block_id", "shard_index", "instrument_id", "ticker", "session_date", "is_early_close", "target_ordinal"],
        columns="family", values="source_path",
    ).reset_index()
    joined = joined.drop(columns=["source_path", "family", "is_early_close", "target_ordinal", "ticker"])
    joined = paths.merge(
        joined, on=["block_id", "shard_index", "instrument_id", "session_date"], validate="one_to_one"
    ).sort_values(["shard_index", "cohort_id", "target_ordinal", "instrument_id", "session_date"])
    primary = joined.groupby(["shard_index", "cohort_id"], sort=True).head(1)
    early = joined.loc[joined["is_early_close"]].groupby("shard_index", sort=True).head(1)
    selected = pd.concat([primary, early], ignore_index=True).drop_duplicates(
        ["instrument_id", "session_date"]
    ).sort_values(["shard_index", "cohort_id", "is_early_close", "target_ordinal"])
    selected["selection_reason"] = "SHARD_X_COHORT_SENTINEL"
    early_keys = set(zip(early["instrument_id"], early["session_date"]))
    selected.loc[
        [key in early_keys for key in zip(selected["instrument_id"], selected["session_date"])],
        "selection_reason",
    ] += "+EARLY_CLOSE_SENTINEL"
    return selected.reset_index(drop=True)


def audit_current(frame: pd.DataFrame, ev: Evidence, target_id: str) -> None:
    family = "current_state"
    ev.profile(family, frame, CURRENT_VARIABLES)
    ev.state_counts(family, frame, (
        "observation_state", "calculation_state", "duration_calculation_state",
        "concentration_calculation_state", "quality_state", "coverage_state",
    ))
    ev.check(family, "grain_unique", len(frame), int(frame.duplicated([
        "instrument_id", "session_date", "decision_timestamp", "window_seconds"
    ]).sum()), target_id)
    ev.check(family, "window_set_exact", len(frame), failures_where(~frame["window_seconds"].isin([5, 15, 30, 60, 300])), target_id)
    expected_subwindow = expected_subwindow_seconds(frame["window_seconds"])
    ev.check(
        family,
        "subwindow_contract_w_le_30_one_second_else_five_seconds",
        len(frame),
        failures_where(frame["subwindow_seconds"].ne(expected_subwindow)),
        target_id,
    )
    calculated = frame["calculation_state"].eq("CALCULATED")
    expected_rate = frame["eligible_trade_count"] / frame["window_seconds"]
    ev.check(family, "trade_arrival_rate_formula", int(calculated.sum()), failures_where(calculated & not_close(frame["trade_arrival_rate"], expected_rate)), target_id)
    for column in CURRENT_VARIABLES[:6]:
        ev.check(family, f"{column}_nonnegative", int(frame[column].notna().sum()), failures_where(frame[column].notna() & frame[column].lt(0)), target_id)
    for column in CURRENT_VARIABLES[6:10]:
        ev.check(family, f"{column}_unit_interval", int(frame[column].notna().sum()), failures_where(frame[column].notna() & ~frame[column].between(0, 1)), target_id)
    both_duration = frame["p10_intertrade_duration_us"].notna() & frame["median_intertrade_duration_us"].notna()
    ev.check(family, "p10_not_above_median_duration", int(both_duration.sum()), failures_where(both_duration & frame["p10_intertrade_duration_us"].gt(frame["median_intertrade_duration_us"])), target_id)
    max_consecutive = frame["window_seconds"] / frame["subwindow_seconds"]
    ev.check(family, "consecutive_subwindows_domain", int(frame["consecutive_active_subwindows"].notna().sum()), failures_where(frame["consecutive_active_subwindows"].notna() & ((frame["consecutive_active_subwindows"] < 0) | (frame["consecutive_active_subwindows"] > max_consecutive))), target_id)
    ev.check(family, "feature_input_is_pit", int(frame["feature_input_max_available_at"].notna().sum()), failures_where(frame["feature_input_max_available_at"].notna() & (frame["feature_input_max_available_at"] > frame["decision_timestamp"])), target_id)
    ev.check(family, "future_window_never_used", len(frame), failures_where(frame["future_window_used"].fillna(True)), target_id)
    not_calculated = ~calculated
    ev.check(family, "not_calculated_activity_is_null", int(not_calculated.sum()), failures_where(not_calculated & frame[list(CURRENT_VARIABLES[:4])].notna().any(axis=1)), target_id)
    zero = calculated & frame["eligible_trade_count"].eq(0)
    ev.check(family, "observed_zero_additive_measures_are_zero", int(zero.sum()), failures_where(zero & (frame[["eligible_share_volume", "eligible_dollar_volume", "trade_arrival_rate"]].fillna(np.nan) != 0).any(axis=1)), target_id)
    ev.check(family, "observed_zero_not_missing", int(zero.sum()), failures_where(zero & frame["observation_state"].ne("OBSERVED_ZERO")), target_id)
    for column, expected in IDENTITY.items():
        ev.check(family, f"identity_{column}", len(frame), failures_where(frame[column].astype("string").ne(expected)), target_id)


def audit_multiscale(frame: pd.DataFrame, current: pd.DataFrame, ev: Evidence, target_id: str) -> None:
    family = "multiscale_contrast"
    ev.profile(family, frame, MULTISCALE_VARIABLES)
    ev.state_counts(family, frame, ("calculation_state", "quality_state", "coverage_state"))
    ev.check(family, "grain_unique", len(frame), int(frame.duplicated([
        "instrument_id", "session_date", "decision_timestamp", "pair_id"
    ]).sum()), target_id)
    pairs = set(zip(frame["short_window_seconds"], frame["long_window_seconds"]))
    ev.check(family, "pair_set_exact", len(frame), 0 if pairs == {(5, 60), (15, 300)} else len(frame), target_id, str(sorted(pairs)))
    rates = current[["decision_timestamp", "window_seconds", "trade_arrival_rate", "feature_input_max_available_at"]]
    work = frame.merge(rates.rename(columns={
        "window_seconds": "short_window_seconds", "trade_arrival_rate": "short_rate",
        "feature_input_max_available_at": "short_available_at",
    }), on=["decision_timestamp", "short_window_seconds"], how="left", validate="many_to_one")
    work = work.merge(rates.rename(columns={
        "window_seconds": "long_window_seconds", "trade_arrival_rate": "long_rate",
        "feature_input_max_available_at": "long_available_at",
    }), on=["decision_timestamp", "long_window_seconds"], how="left", validate="many_to_one")
    valid = work["short_rate"].notna() & work["long_rate"].notna()
    expected = np.log((work["short_rate"] + 1.0 / work["long_window_seconds"]) / (work["long_rate"] + 1.0 / work["long_window_seconds"]))
    mismatch = valid & not_close(work["activity_rate_multiscale_log_ratio"], expected)
    mismatch |= valid & work["activity_rate_multiscale_log_ratio"].isna()
    mismatch |= ~valid & work["activity_rate_multiscale_log_ratio"].notna()
    ev.check(family, "activity_rate_multiscale_log_ratio_formula", len(work), failures_where(mismatch), target_id)
    ev.check(family, "formula_state_consistency", len(work), failures_where((valid & work["calculation_state"].ne("CALCULATED")) | (~valid & work["calculation_state"].ne("INPUT_NOT_CALCULATED"))), target_id)
    ev.check(family, "feature_input_is_pit", int(work["feature_input_max_available_at"].notna().sum()), failures_where(work["feature_input_max_available_at"].notna() & (work["feature_input_max_available_at"] > work["decision_timestamp"])), target_id)
    ev.check(family, "future_window_never_used", len(work), failures_where(work["future_window_used"].fillna(True)), target_id)
    for column, expected_value in IDENTITY.items():
        ev.check(family, f"identity_{column}", len(frame), failures_where(frame[column].astype("string").ne(expected_value)), target_id)


def audit_baseline(frame: pd.DataFrame, current: pd.DataFrame, ev: Evidence, target_id: str) -> None:
    family = "pit_baseline_and_surprise"
    ev.profile(family, frame, BASELINE_VARIABLES)
    ev.state_counts(family, frame, ("baseline_candidate_id", "baseline_calculation_state", "baseline_duration_calculation_state", "calculation_state"))
    ev.check(family, "grain_unique", len(frame), int(frame.duplicated([
        "instrument_id", "session_date", "decision_timestamp", "window_seconds", "baseline_candidate_id"
    ]).sum()), target_id)
    ev.check(family, "candidate_set_exact", len(frame), failures_where(~frame["baseline_candidate_id"].isin(BASELINE_MINIMUMS)), target_id)
    last_ref = pd.to_datetime(frame["last_reference_date"], errors="coerce")
    session = pd.to_datetime(frame["session_date"], errors="coerce")
    ev.check(family, "last_reference_strictly_prior", int(last_ref.notna().sum()), failures_where(last_ref.notna() & (last_ref >= session)), target_id)
    ev.check(family, "baseline_input_is_pit", int(frame["baseline_input_max_available_at"].notna().sum()), failures_where(frame["baseline_input_max_available_at"].notna() & (frame["baseline_input_max_available_at"] > frame["decision_timestamp"])), target_id)
    available = frame["baseline_calculation_state"].isin(["BASELINE_AVAILABLE", "BASELINE_ZERO_DOMINATED"])
    minimum = frame["baseline_candidate_id"].map(BASELINE_MINIMUMS)
    ev.check(family, "available_meets_minimum_sessions", int(available.sum()), failures_where(available & (frame["reference_session_count"] < minimum)), target_id)
    for column in BASELINE_VARIABLES[:4]:
        ev.check(family, f"{column}_unit_interval", int(frame[column].notna().sum()), failures_where(frame[column].notna() & ~frame[column].between(0, 1)), target_id)
    for label in ("trade_count", "share_volume", "dollar_volume", "arrival_rate"):
        total = frame[f"baseline_{label}_total_count"]
        zero = frame[f"baseline_{label}_zero_count"]
        positive = frame[f"baseline_{label}_positive_count"]
        fraction = frame[f"baseline_{label}_zero_fraction"]
        present = total.notna()
        ev.check(family, f"{label}_count_partition", int(present.sum()), failures_where(present & total.ne(zero + positive)), target_id)
        expected_fraction = zero / total.replace(0, np.nan)
        ev.check(family, f"{label}_zero_fraction_formula", int(expected_fraction.notna().sum()), failures_where(expected_fraction.notna() & not_close(fraction, expected_fraction)), target_id)
    cur = current[[
        "decision_timestamp", "window_seconds", "eligible_trade_count",
        "eligible_share_volume", "eligible_dollar_volume", "median_intertrade_duration_us",
    ]]
    work = frame.merge(cur, on=["decision_timestamp", "window_seconds"], how="left", validate="many_to_one")
    ratio_specs = (
        ("eligible_trade_count", "baseline_trade_count_unconditional_median", "trade_count_log_ratio_to_pit"),
        ("eligible_share_volume", "baseline_share_volume_unconditional_median", "share_volume_log_ratio_to_pit"),
        ("eligible_dollar_volume", "baseline_dollar_volume_unconditional_median", "dollar_volume_log_ratio_to_pit"),
    )
    for source, base, output in ratio_specs:
        valid = available & work[source].notna() & work[base].notna()
        expected = np.log((work[source] + 1.0) / (work[base] + 1.0))
        mismatch = valid & not_close(work[output], expected)
        mismatch |= valid & work[output].isna()
        mismatch |= ~valid & work[output].notna()
        ev.check(family, f"{output}_formula", len(work), failures_where(mismatch), target_id)
    duration_valid = available & work["median_intertrade_duration_us"].notna() & work["baseline_median_intertrade_duration_us"].notna()
    duration_expected = np.log((work["baseline_median_intertrade_duration_us"] + 1.0) / (work["median_intertrade_duration_us"] + 1.0))
    duration_mismatch = duration_valid & not_close(work["intertrade_duration_compression"], duration_expected)
    duration_mismatch |= duration_valid & work["intertrade_duration_compression"].isna()
    duration_mismatch |= ~duration_valid & work["intertrade_duration_compression"].notna()
    ev.check(family, "intertrade_duration_compression_formula", len(work), failures_where(duration_mismatch), target_id)
    ev.check(family, "future_window_never_used", len(work), failures_where(work["future_window_used"].fillna(True)), target_id)
    for column, expected_value in IDENTITY.items():
        ev.check(family, f"identity_{column}", len(frame), failures_where(frame[column].astype("string").ne(expected_value)), target_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certified-run-root", type=Path, required=True)
    parser.add_argument("--target-contexts", type=Path, required=True)
    parser.add_argument("--specification", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=False)
    artifacts = args.output_root / "artifacts"
    runtime = args.output_root / "runtime"
    artifacts.mkdir()
    runtime.mkdir()
    script_path = Path(__file__).resolve()
    reference_path = args.certified_run_root / "artifacts" / "verified_reference_manifest.parquet"
    final_path = args.certified_run_root / "runtime" / "final_manifest.json"
    pre = {
        "run_id": args.output_root.name, "status": "RUNNING", "started_at_utc": utc_now(),
        "audit_scope": "BOUNDED_DETERMINISTIC_SHARD_X_COHORT_VALUE_AUDIT",
        "certified_run_root": str(args.certified_run_root),
        "certified_final_manifest_sha256": sha256(final_path),
        "verified_reference_manifest_sha256": sha256(reference_path),
        "target_contexts": str(args.target_contexts),
        "target_contexts_sha256": sha256(args.target_contexts),
        "binding_a_specification": str(args.specification),
        "binding_a_specification_sha256": sha256(args.specification),
        "script_path": str(script_path), "script_sha256": sha256(script_path),
        "network_access": "PROHIBITED_AND_NOT_USED",
        "rematerialization": "NOT_EXECUTED",
    }
    (runtime / "pre_manifest.json").write_text(json.dumps(pre, indent=2), encoding="utf-8")
    reference = pq.read_table(reference_path).to_pandas()
    targets = pq.read_table(args.target_contexts).to_pandas()
    selected = select_targets(reference, targets)
    selected.to_parquet(artifacts / "selected_target_sessions.parquet", index=False)
    selected.to_csv(artifacts / "selected_target_sessions.csv", index=False)
    ev = Evidence()
    for family in FAMILIES:
        family_rows = reference.loc[reference["family"].eq(family)]
        ev.check(family, "certified_inventory_all_files_pass", len(family_rows), int(family_rows["status"].ne("PASS").sum()))
        ev.check(family, "certified_inventory_row_counts_exact", len(family_rows), int(family_rows["actual_rows"].ne(family_rows["expected_rows"]).sum()))
        ev.check(family, "single_schema_across_2400_targets", len(family_rows), max(0, family_rows["schema_sha256"].nunique() - 1))
    current_columns = list(IDENTITY) + [
        "instrument_id", "session_date", "decision_timestamp", "window_seconds",
        "subwindow_seconds", "observable_seconds", "input_event_count",
        "feature_input_max_available_at", "observation_state", "calculation_state",
        "duration_calculation_state", "concentration_calculation_state",
        "quality_state", "coverage_state", "degrading_event_count", "future_window_used",
        *CURRENT_VARIABLES,
    ]
    multiscale_columns = list(IDENTITY) + [
        "instrument_id", "session_date", "decision_timestamp", "pair_id",
        "short_window_seconds", "long_window_seconds", "feature_input_max_available_at",
        "calculation_state", "quality_state", "coverage_state", "future_window_used",
        *MULTISCALE_VARIABLES,
    ]
    baseline_diagnostics = []
    for label in ("trade_count", "share_volume", "dollar_volume", "arrival_rate"):
        baseline_diagnostics.extend([
            f"baseline_{label}_total_count", f"baseline_{label}_zero_count",
            f"baseline_{label}_positive_count", f"baseline_{label}_zero_fraction",
            f"baseline_{label}_unconditional_median",
        ])
    baseline_columns = list(IDENTITY) + [
        "instrument_id", "session_date", "decision_timestamp", "window_seconds",
        "baseline_candidate_id", "reference_session_count", "reference_observation_count",
        "first_reference_date", "last_reference_date", "baseline_input_max_available_at",
        "baseline_calculation_state", "baseline_duration_calculation_state",
        "baseline_median_intertrade_duration_us", "calculation_state", "future_window_used",
        *baseline_diagnostics, *BASELINE_VARIABLES,
    ]
    for ordinal, row in selected.iterrows():
        target_id = f"s{row.shard_index}:{row.cohort_id}:{row.instrument_id}:{row.session_date}"
        heartbeat = {
            "status": "RUNNING", "updated_at_utc": utc_now(),
            "completed_targets": int(ordinal), "total_targets": len(selected), "target_id": target_id,
        }
        (runtime / "heartbeat.json").write_text(json.dumps(heartbeat, indent=2), encoding="utf-8")
        current = read_columns(row["current_state"], current_columns)
        multiscale = read_columns(row["multiscale_contrast"], multiscale_columns)
        baseline = read_columns(row["pit_baseline_and_surprise"], baseline_columns)
        audit_current(current, ev, target_id)
        audit_multiscale(multiscale, current, ev, target_id)
        audit_baseline(baseline, current, ev, target_id)
    details = pd.DataFrame(ev.checks)
    summary = details.groupby(["family", "check_id"], as_index=False).agg(
        evaluated_rows=("evaluated_rows", "sum"), failure_count=("failure_count", "sum"),
        targets_evaluated=("target_id", "nunique"),
    )
    summary["status"] = np.where(summary["failure_count"].eq(0), "PASS", "FAIL")
    profiles = pd.DataFrame(ev.profiles.values()).sort_values(["family", "variable"])
    profiles["example_values"] = [json.dumps(ev.examples[(r.family, r.variable)]) for r in profiles.itertuples()]
    states = pd.DataFrame([
        {"family": key[0], "state_column": key[1], "state_value": key[2], "row_count": count}
        for key, count in sorted(ev.states.items())
    ])
    for name, frame in (("check_details", details), ("check_summary", summary), ("variable_profiles", profiles), ("state_counts", states)):
        frame.to_parquet(artifacts / f"{name}.parquet", index=False)
        frame.to_csv(artifacts / f"{name}.csv", index=False)
    hard_failures = int(summary["failure_count"].sum())
    final_status = "PASS_WITH_DECLARED_RESTRICTIONS" if hard_failures == 0 else "FAIL"
    final = {
        **pre, "status": final_status, "completed_at_utc": utc_now(),
        "selected_target_sessions": len(selected),
        "selected_by_shard": {str(k): int(v) for k, v in selected.groupby("shard_index").size().items()},
        "selected_by_cohort": {str(k): int(v) for k, v in selected.groupby("cohort_id").size().items()},
        "early_close_sessions": int(selected["is_early_close"].sum()),
        "check_count": len(summary), "hard_failure_count": hard_failures,
        "family_status": {family: ("PASS" if int(group["failure_count"].sum()) == 0 else "FAIL") for family, group in summary.groupby("family")},
        "declared_restrictions": [
            "Legacy RTH source remains research-only with simulated availability.",
            "Materialized percentile values are domain/state audited but not independently replayed from raw baseline observation vectors by this bounded auditor.",
            "Passing this evidence audit does not authorize canonical promotion or Binding B materialization.",
        ],
        "artifact_sha256": {path.name: sha256(path) for path in sorted(artifacts.iterdir()) if path.is_file()},
        "next_gate": "HUMAN_SCIENTIFIC_EVIDENCE_REVIEW",
    }
    (runtime / "heartbeat.json").write_text(json.dumps({
        "status": final_status, "updated_at_utc": utc_now(),
        "completed_targets": len(selected), "total_targets": len(selected),
    }, indent=2), encoding="utf-8")
    (runtime / "final_manifest.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    main()
