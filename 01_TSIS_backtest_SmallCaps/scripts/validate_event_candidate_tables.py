from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


DAILY_DATASET_ID = "daily_strategy_candidate_events_table_v0_1"
INTRADAY_DATASET_ID = "intraday_1m_strategy_candidate_events_table_v0_1"
VALIDATOR_CONTRACT_ID = "event_candidate_table_validators_contract_v0_1"
VALIDATOR_VERSION = "event_candidate_table_validators_executable_v0_1"

PROHIBITED_PREFIXES = (
    "outcome__",
    "label__",
    "reward__",
    "action__",
    "policy__",
    "fill__",
    "pnl__",
    "future__",
)
POST_EVENT_TOKENS = (
    "mfe",
    "mae",
    "winner",
    "loser",
    "realized_pnl",
    "future_return",
    "forward_return",
)

COMMON_REQUIRED = {
    "event_id",
    "event_table_id",
    "event_schema_version",
    "event_definition_id",
    "event_definition_version",
    "event_family",
    "event_type",
    "event_anchor_role",
    "instrument_id",
    "ticker",
    "session_date",
    "event_date",
    "market_timezone",
    "is_common_stock",
    "is_lt1b_operational",
    "instrument_identity_temporal_match",
    "calendar_session_valid",
    "as_of_utc",
    "event_availability_utc",
    "event_timestamp_policy",
    "decision_timestamp_policy_id",
    "source_data_availability_cutoff_utc",
    "source_candidate_dataset_id",
    "source_manifest_path",
    "event_definition_params_bundle",
    "trigger_observables_bundle",
    "definition_cutoff_policy_version",
    "definition_is_parametric",
    "definition_is_alphaevolve_candidate",
    "event_quality_state",
    "event_selection_state",
    "event_anchor_quality_state",
    "valid_for_event_windows_candidate",
    "valid_for_event_state_candidate",
    "valid_for_pattern_discovery_candidate",
    "valid_for_backtest_event_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_rl_state_candidate",
    "valid_for_alphaevolve_candidate",
    "full_universe_claim",
    "contains_outcome_information",
    "contains_label_information",
    "contains_reward_information",
    "execution_truth",
    "requires_asof_filter",
    "materialization_scope",
    "quality_policy_version",
    "schema_version",
    "build_run_id",
    "created_at_utc",
    "source_instrument_master_path",
    "source_market_calendar_path",
}
DAILY_REQUIRED = COMMON_REQUIRED | {"daily_event_id", "contains_intraday_timestamp_claim"}
INTRADAY_REQUIRED = COMMON_REQUIRED | {
    "intraday_event_id",
    "event_session_phase",
    "event_timestamp_utc",
    "event_bar_ts_utc",
    "event_bar_end_utc",
    "event_bar_size",
    "detection_timestamp_utc",
    "uses_incomplete_bar",
    "source_price_view",
    "source_quote_guarded_repair_manifest",
    "source_quote_guarded_run_id",
    "quote_guarded_view",
    "raw_event_detected",
    "quote_guarded_event_confirmed",
}

DAILY_POLICIES = {
    "date_level",
    "session_open_available",
    "session_close_available",
    "intraday_proven",
    "research_replay_proxy",
}
INTRADAY_POLICIES = {"closed_1m_bar", "live_bar_policy", "research_replay_proxy"}


@dataclass(frozen=True)
class Failure:
    validator_id: str
    severity: str
    primary_key_value: str | None
    event_id: str | None
    event_definition_id: str | None
    event_table_id: str | None
    column_name: str | None
    observed_value: str | None
    expected_rule: str
    failure_message: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except Exception:
        pass
    return isinstance(value, str) and value.strip() == ""


def _true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return bool(value)


def _ts(value: Any) -> pd.Timestamp | None:
    if _missing(value):
        return None
    parsed = pd.Timestamp(value)
    if parsed.tzinfo is None:
        parsed = parsed.tz_localize("UTC")
    return parsed.tz_convert("UTC")


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("rows") if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError("JSON input must be a rows object or a list")
        return [dict(row) for row in rows]
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path).to_dict(orient="records")
    raise ValueError(f"unsupported input suffix: {path.suffix}")


def _primary_column(dataset_id: str) -> str:
    return "daily_event_id" if dataset_id == DAILY_DATASET_ID else "intraday_event_id"


def _required_columns(dataset_id: str) -> set[str]:
    return DAILY_REQUIRED if dataset_id == DAILY_DATASET_ID else INTRADAY_REQUIRED


def _allowed_policies(dataset_id: str) -> set[str]:
    return DAILY_POLICIES if dataset_id == DAILY_DATASET_ID else INTRADAY_POLICIES


def _add(
    failures: list[Failure],
    *,
    validator_id: str,
    severity: str,
    row: dict[str, Any] | None,
    dataset_id: str,
    column: str | None,
    observed: Any,
    rule: str,
    message: str,
) -> None:
    row = row or {}
    primary = row.get(_primary_column(dataset_id))
    failures.append(
        Failure(
            validator_id=validator_id,
            severity=severity,
            primary_key_value=None if _missing(primary) else str(primary),
            event_id=None if _missing(row.get("event_id")) else str(row.get("event_id")),
            event_definition_id=None
            if _missing(row.get("event_definition_id"))
            else str(row.get("event_definition_id")),
            event_table_id=None if _missing(row.get("event_table_id")) else str(row.get("event_table_id")),
            column_name=column,
            observed_value=None if _missing(observed) else str(observed),
            expected_rule=rule,
            failure_message=message,
        )
    )


def _check_presence(rows: list[dict[str, Any]], dataset_id: str, failures: list[Failure]) -> None:
    present = set().union(*(row.keys() for row in rows)) if rows else set()
    for column in sorted(_required_columns(dataset_id) - present):
        _add(
            failures,
            validator_id="event_bad_missing_required_column",
            severity="hard_fail",
            row=None,
            dataset_id=dataset_id,
            column=column,
            observed=None,
            rule="all required schema columns must be present",
            message=f"missing required column: {column}",
        )


def _check_row_required(row: dict[str, Any], dataset_id: str, failures: list[Failure]) -> None:
    nullable = {"thresholds_bundle", "source_quote_guarded_run_id"}
    for column in sorted(_required_columns(dataset_id)):
        if column in nullable:
            continue
        if column in row and _missing(row.get(column)):
            _add(
                failures,
                validator_id=f"event_bad_missing_{column}",
                severity="hard_fail",
                row=row,
                dataset_id=dataset_id,
                column=column,
                observed=row.get(column),
                rule="required values must be non-empty unless explicitly nullable",
                message=f"missing required value: {column}",
            )


def _check_identity(rows: list[dict[str, Any]], dataset_id: str, failures: list[Failure]) -> None:
    primary = _primary_column(dataset_id)
    grain = (
        ["event_definition_id", "session_date", "instrument_id", "event_anchor_role"]
        if dataset_id == DAILY_DATASET_ID
        else ["event_definition_id", "event_timestamp_utc", "instrument_id", "event_anchor_role"]
    )
    primary_seen: dict[str, dict[str, Any]] = {}
    grain_seen: dict[tuple[Any, ...], dict[str, Any]] = {}
    primary_dupes: set[str] = set()
    grain_dupes: set[tuple[Any, ...]] = set()

    for row in rows:
        if _missing(row.get("event_id")):
            _add(failures, validator_id="event_bad_missing_event_id", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_id", observed=row.get("event_id"), rule="event_id is required", message="missing event_id")
        if _missing(row.get(primary)):
            _add(failures, validator_id="event_bad_missing_primary_id", severity="hard_fail", row=row, dataset_id=dataset_id, column=primary, observed=row.get(primary), rule=f"{primary} is required", message=f"missing {primary}")
        else:
            key = str(row[primary])
            if key in primary_seen:
                primary_dupes.add(key)
            else:
                primary_seen[key] = row
        values = tuple(row.get(column) for column in grain)
        if all(not _missing(value) for value in values):
            if values in grain_seen:
                grain_dupes.add(values)
            else:
                grain_seen[values] = row
        if row.get("event_table_id") != dataset_id:
            _add(failures, validator_id="event_bad_event_table_id_mismatch", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_table_id", observed=row.get("event_table_id"), rule=f"event_table_id == {dataset_id}", message="event_table_id does not match dataset")
        for column in ("schema_version", "event_schema_version"):
            if row.get(column) != dataset_id:
                _add(failures, validator_id="event_bad_schema_version_mismatch", severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule=f"{column} == {dataset_id}", message=f"{column} does not match dataset")
        if not _true(row.get("instrument_identity_temporal_match")):
            _add(failures, validator_id="event_bad_instrument_identity_temporal_match", severity="hard_fail", row=row, dataset_id=dataset_id, column="instrument_identity_temporal_match", observed=row.get("instrument_identity_temporal_match"), rule="instrument_identity_temporal_match must be true", message="invalid instrument identity temporal match")
        if not _true(row.get("calendar_session_valid")):
            _add(failures, validator_id="event_bad_calendar_session", severity="hard_fail", row=row, dataset_id=dataset_id, column="calendar_session_valid", observed=row.get("calendar_session_valid"), rule="calendar_session_valid must be true", message="invalid market calendar session")

    for key in sorted(primary_dupes):
        _add(failures, validator_id="event_bad_duplicate_primary_id", severity="hard_fail", row=primary_seen[key], dataset_id=dataset_id, column=primary, observed=key, rule="primary id must be unique", message=f"duplicate {primary}: {key}")
    for values in sorted(grain_dupes):
        _add(failures, validator_id="event_bad_duplicate_declared_grain", severity="hard_fail", row=grain_seen[values], dataset_id=dataset_id, column=",".join(grain), observed="|".join(str(item) for item in values), rule="declared logical grain must be unique", message="duplicate logical grain")


def _check_definition(row: dict[str, Any], dataset_id: str, failures: list[Failure]) -> None:
    for column, validator_id in (
        ("event_definition_id", "event_bad_missing_event_definition_id"),
        ("event_definition_version", "event_bad_missing_event_definition_version"),
        ("event_definition_params_bundle", "event_bad_missing_definition_params_bundle"),
        ("trigger_observables_bundle", "event_bad_missing_trigger_observables_bundle"),
    ):
        if _missing(row.get(column)):
            _add(failures, validator_id=validator_id, severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule=f"{column} is required", message=f"missing {column}")

    threshold_columns = [column for column in row if "threshold" in column.lower() and column != "thresholds_bundle"]
    if threshold_columns and _missing(row.get("thresholds_bundle")):
        _add(failures, validator_id="event_bad_threshold_without_definition", severity="hard_fail", row=row, dataset_id=dataset_id, column="thresholds_bundle", observed=None, rule="threshold fields require thresholds_bundle", message="threshold fields exist without thresholds_bundle")
    for column in row:
        lower = column.lower()
        if "best_threshold" in lower or "threshold_discovered" in lower:
            _add(failures, validator_id="event_bad_best_threshold_as_truth", severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule="best/discovered threshold cannot be event truth", message="best threshold encoded as truth")


def _check_time(row: dict[str, Any], dataset_id: str, failures: list[Failure]) -> None:
    as_of = _ts(row.get("as_of_utc"))
    for column, validator_id in (
        ("event_availability_utc", "event_bad_future_availability"),
        ("source_data_availability_cutoff_utc", "event_bad_source_cutoff_future"),
        ("detection_timestamp_utc", "event_bad_detection_after_asof"),
    ):
        value = _ts(row.get(column))
        if value is not None and as_of is not None and value > as_of:
            _add(failures, validator_id=validator_id, severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule=f"{column} <= as_of_utc", message=f"{column} is after as_of_utc")

    policy = row.get("event_timestamp_policy")
    if _missing(policy):
        _add(failures, validator_id="event_bad_missing_timestamp_policy", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_timestamp_policy", observed=policy, rule="event_timestamp_policy is required", message="missing event timestamp policy")
    elif str(policy) not in _allowed_policies(dataset_id):
        _add(failures, validator_id="event_bad_unknown_timestamp_policy", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_timestamp_policy", observed=policy, rule=f"policy in {sorted(_allowed_policies(dataset_id))}", message="unknown timestamp policy")

    for column, validator_id in (
        ("decision_timestamp_policy_id", "event_bad_decision_timestamp_policy_missing"),
        ("definition_cutoff_policy_version", "event_bad_cutoff_policy_version_missing"),
    ):
        if _missing(row.get(column)):
            _add(failures, validator_id=validator_id, severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule=f"{column} is required", message=f"missing {column}")


def _check_lineage(row: dict[str, Any], dataset_id: str, failures: list[Failure]) -> None:
    if _missing(row.get("source_candidate_dataset_id")):
        _add(failures, validator_id="event_bad_missing_source_candidate_dataset", severity="hard_fail", row=row, dataset_id=dataset_id, column="source_candidate_dataset_id", observed=row.get("source_candidate_dataset_id"), rule="source_candidate_dataset_id is required", message="missing source candidate dataset id")
    direct = row.get("source_candidate_dataset_id") == "direct_event_definition_source"
    if not direct and _missing(row.get("source_candidate_id")):
        _add(failures, validator_id="event_bad_missing_source_candidate", severity="hard_fail", row=row, dataset_id=dataset_id, column="source_candidate_id", observed=row.get("source_candidate_id"), rule="scanner/source-derived events require source_candidate_id", message="missing source candidate id")
    for column, validator_id in (
        ("source_manifest_path", "event_bad_missing_source_manifest"),
        ("build_run_id", "event_bad_missing_build_run_id"),
        ("created_at_utc", "event_bad_missing_created_at"),
        ("materialization_scope", "event_bad_missing_materialization_scope"),
    ):
        if _missing(row.get(column)):
            _add(failures, validator_id=validator_id, severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule=f"{column} is required", message=f"missing {column}")


def _check_prohibitions(row: dict[str, Any], dataset_id: str, failures: list[Failure]) -> None:
    for column in row:
        lower = column.lower()
        if column.startswith(PROHIBITED_PREFIXES):
            _add(failures, validator_id="event_bad_prohibited_prefix", severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule="outcome/label/reward/action/policy/fill/pnl/future prefixes are prohibited", message="prohibited column prefix")
        if any(token in lower for token in POST_EVENT_TOKENS):
            _add(failures, validator_id="event_bad_post_event_metric_inline", severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule="post-event metrics must live in outcomes/evaluators", message="post-event metric appears inline")
    for column, validator_id in (
        ("contains_outcome_information", "event_bad_outcome_inline"),
        ("contains_label_information", "event_bad_label_inline"),
        ("contains_reward_information", "event_bad_reward_inline"),
        ("execution_truth", "event_bad_execution_truth"),
    ):
        if _true(row.get(column)):
            _add(failures, validator_id=validator_id, severity="hard_fail", row=row, dataset_id=dataset_id, column=column, observed=row.get(column), rule=f"{column} must be false", message=f"{column} is true")


def _check_consumer_gates(row: dict[str, Any], dataset_id: str, failures: list[Failure]) -> None:
    if _true(row.get("valid_for_ml_feature_candidate")):
        _add(failures, validator_id="event_bad_ml_feature_gate", severity="hard_fail", row=row, dataset_id=dataset_id, column="valid_for_ml_feature_candidate", observed=row.get("valid_for_ml_feature_candidate"), rule="event candidates are not ML features until legal event_state exists", message="ML feature gate opened too early")
    if _true(row.get("valid_for_rl_state_candidate")):
        _add(failures, validator_id="event_bad_rl_state_gate", severity="hard_fail", row=row, dataset_id=dataset_id, column="valid_for_rl_state_candidate", observed=row.get("valid_for_rl_state_candidate"), rule="RL state candidate requires transition/state contract", message="RL gate opened too early")
    if _true(row.get("alphaevolve_evaluator_production_enabled")):
        _add(failures, validator_id="event_bad_alphaevolve_production_gate", severity="hard_fail", row=row, dataset_id=dataset_id, column="alphaevolve_evaluator_production_enabled", observed=row.get("alphaevolve_evaluator_production_enabled"), rule="AlphaEvolve production evaluator remains disabled", message="AlphaEvolve production gate opened too early")
    if _true(row.get("valid_for_event_state_candidate")) and not _true(row.get("valid_for_event_windows_candidate")):
        _add(failures, validator_id="event_bad_event_state_gate", severity="hard_fail", row=row, dataset_id=dataset_id, column="valid_for_event_state_candidate", observed=row.get("valid_for_event_state_candidate"), rule="event_state candidate requires event_windows candidate path", message="event_state gate opened without event_windows gate")
    if _true(row.get("full_universe_claim")):
        _add(failures, validator_id="event_bad_full_universe_claim", severity="hard_fail", row=row, dataset_id=dataset_id, column="full_universe_claim", observed=row.get("full_universe_claim"), rule="full_universe_claim requires denominator/certification", message="full universe claim without promotion evidence")


def _check_daily(row: dict[str, Any], dataset_id: str, failures: list[Failure]) -> None:
    if row.get("event_date") != row.get("session_date"):
        _add(failures, validator_id="daily_event_bad_session_date_event_date_mismatch", severity="review_fail", row=row, dataset_id=dataset_id, column="event_date", observed=row.get("event_date"), rule="event_date should match session_date unless reason declared", message="event_date differs from session_date")
    intraday_claim = _true(row.get("contains_intraday_timestamp_claim"))
    policy = row.get("event_timestamp_policy")
    if intraday_claim and _missing(row.get("event_timestamp_utc")):
        _add(failures, validator_id="daily_event_bad_intraday_claim_without_source", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_timestamp_utc", observed=row.get("event_timestamp_utc"), rule="intraday timestamp claim requires event_timestamp_utc and intraday source", message="intraday claim without timestamp")
    if intraday_claim or policy == "intraday_proven":
        lineage = " ".join(str(row.get(column, "")) for column in ("source_candidate_dataset_id", "source_manifest_path", "source_intraday_table_path", "trigger_source_bar_file"))
        if all(token not in lineage.lower() for token in ("intraday", "1m", "ohlcv")):
            _add(failures, validator_id="daily_event_bad_intraday_claim_without_source", severity="hard_fail", row=row, dataset_id=dataset_id, column="source_manifest_path", observed=row.get("source_manifest_path"), rule="intraday timestamp claim requires intraday/1m lineage", message="intraday claim has no intraday lineage")
    if intraday_claim and policy in {"date_level", "session_close_available"}:
        _add(failures, validator_id="daily_event_bad_eod_proxy_as_intraday_truth", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_timestamp_policy", observed=policy, rule="date/session policies cannot be promoted as intraday truth", message="daily proxy promoted as intraday truth")


def _check_intraday(row: dict[str, Any], dataset_id: str, failures: list[Failure]) -> None:
    if str(row.get("event_bar_size")) != "1m":
        _add(failures, validator_id="intraday_event_bad_bar_size", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_bar_size", observed=row.get("event_bar_size"), rule="event_bar_size == 1m", message="intraday event is not anchored to 1m bar")
    as_of = _ts(row.get("as_of_utc"))
    bar_end = _ts(row.get("event_bar_end_utc"))
    if row.get("event_timestamp_policy") == "closed_1m_bar" and bar_end is not None and as_of is not None and bar_end > as_of:
        _add(failures, validator_id="intraday_event_bad_bar_not_closed", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_bar_end_utc", observed=row.get("event_bar_end_utc"), rule="event_bar_end_utc <= as_of_utc under closed_1m_bar", message="1m bar is not closed at as_of")
    if _true(row.get("uses_incomplete_bar")):
        _add(failures, validator_id="intraday_event_bad_uncontracted_live_bar", severity="hard_fail", row=row, dataset_id=dataset_id, column="uses_incomplete_bar", observed=row.get("uses_incomplete_bar"), rule="uses_incomplete_bar must be false until live policy is contracted", message="uses incomplete live bar without contracted live policy")

    qg_claim = row.get("source_price_view") == "ohlcv_1m_quote_guarded" or _true(row.get("quote_guarded_view"))
    canonical = row.get("event_selection_state") == "candidate" or _true(row.get("valid_for_event_windows_candidate"))
    if qg_claim and _missing(row.get("source_quote_guarded_repair_manifest")):
        _add(failures, validator_id="intraday_event_bad_missing_quote_guarded_manifest", severity="hard_fail", row=row, dataset_id=dataset_id, column="source_quote_guarded_repair_manifest", observed=row.get("source_quote_guarded_repair_manifest"), rule="quote-guarded rows require repair manifest", message="missing quote-guarded repair manifest")
    if canonical and not _true(row.get("quote_guarded_view")):
        _add(failures, validator_id="intraday_event_bad_qg_view_false_for_canonical", severity="hard_fail", row=row, dataset_id=dataset_id, column="quote_guarded_view", observed=row.get("quote_guarded_view"), rule="canonical intraday candidate requires quote_guarded_view=true", message="canonical candidate is not quote-guarded")
    if canonical and not _true(row.get("quote_guarded_event_confirmed")):
        _add(failures, validator_id="intraday_event_bad_quote_guarded_not_confirmed", severity="hard_fail", row=row, dataset_id=dataset_id, column="quote_guarded_event_confirmed", observed=row.get("quote_guarded_event_confirmed"), rule="canonical intraday candidate requires quote_guarded_event_confirmed=true", message="quote-guarded did not confirm event")
    if _true(row.get("raw_event_detected")) and not _true(row.get("quote_guarded_event_confirmed")) and canonical:
        _add(failures, validator_id="intraday_event_bad_raw_only_promoted", severity="hard_fail", row=row, dataset_id=dataset_id, column="event_selection_state", observed=row.get("event_selection_state"), rule="raw-only events cannot be candidate/promoted", message="raw-only event was marked consumible")
        _add(failures, validator_id="intraday_event_bad_raw_spike_selected", severity="hard_fail", row=row, dataset_id=dataset_id, column="quote_guarded_event_confirmed", observed=row.get("quote_guarded_event_confirmed"), rule="raw spike must be rejected unless quote-guarded confirms", message="raw spike selected without quote-guarded confirmation")
    if qg_claim and _missing(row.get("source_quote_guarded_run_id")):
        _add(failures, validator_id="intraday_event_bad_qg_lineage_missing_run_id", severity="review_fail", row=row, dataset_id=dataset_id, column="source_quote_guarded_run_id", observed=row.get("source_quote_guarded_run_id"), rule="quote-guarded rows should preserve run id", message="missing quote-guarded run id")


def validate_rows(rows: list[dict[str, Any]], dataset_id: str, dataset_path: Path | None = None) -> dict[str, Any]:
    if dataset_id not in {DAILY_DATASET_ID, INTRADAY_DATASET_ID}:
        raise ValueError(f"unsupported dataset id: {dataset_id}")
    failures: list[Failure] = []
    if not rows:
        _add(failures, validator_id="event_bad_empty_input", severity="hard_fail", row=None, dataset_id=dataset_id, column=None, observed=0, rule="input must contain rows", message="empty event candidate input")
    else:
        _check_presence(rows, dataset_id, failures)
        _check_identity(rows, dataset_id, failures)
        for row in rows:
            _check_row_required(row, dataset_id, failures)
            _check_definition(row, dataset_id, failures)
            _check_time(row, dataset_id, failures)
            _check_lineage(row, dataset_id, failures)
            _check_prohibitions(row, dataset_id, failures)
            _check_consumer_gates(row, dataset_id, failures)
            if dataset_id == DAILY_DATASET_ID:
                _check_daily(row, dataset_id, failures)
            else:
                _check_intraday(row, dataset_id, failures)

    hard = [failure for failure in failures if failure.severity == "hard_fail"]
    review = [failure for failure in failures if failure.severity == "review_fail"]
    warnings = [failure for failure in failures if failure.severity == "warning"]
    return {
        "validator_run_id": f"{VALIDATOR_VERSION}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "validator_contract_id": VALIDATOR_CONTRACT_ID,
        "validator_version": VALIDATOR_VERSION,
        "validated_dataset_id": dataset_id,
        "validated_dataset_path": str(dataset_path) if dataset_path else None,
        "row_count": len(rows),
        "hard_fail_count": len(hard),
        "review_fail_count": len(review),
        "warning_count": len(warnings),
        "status": "passed" if not hard else "failed",
        "materialization_allowed": not hard,
        "promotion_allowed": not hard and not review,
        "ml_ready_dataset_enabled": False,
        "rl_training_dataset_enabled": False,
        "alphaevolve_evaluator_enabled": False,
        "created_at_utc": _utc_now(),
        "failures": [asdict(failure) for failure in failures],
    }


def contract_status() -> dict[str, Any]:
    module_root = Path(__file__).resolve().parents[1]
    required = {
        "event_candidate_table_validators_contract": "01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md",
        "daily_schema_contract": "01_foundations/canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md",
        "intraday_schema_contract": "01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md",
        "event_candidate_tables_contract": "01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md",
    }
    contracts = {
        key: {"relative_path": rel, "exists": (module_root / rel).exists()}
        for key, rel in required.items()
    }
    return {
        "validator_contract_id": VALIDATOR_CONTRACT_ID,
        "validator_version": VALIDATOR_VERSION,
        "status": "executable_validator_defined_for_fixture_scope",
        "real_tables_materialized": False,
        "validates_real_table_when_available": True,
        "fixture_scope": True,
        "writes_official_output": False,
        "daily_dataset_id": DAILY_DATASET_ID,
        "intraday_dataset_id": INTRADAY_DATASET_ID,
        "required_contracts": contracts,
        "missing_contracts": [key for key, item in contracts.items() if not item["exists"]],
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate TSIS event candidate tables or fixtures.")
    parser.add_argument("--dataset-id", choices=[DAILY_DATASET_ID, INTRADAY_DATASET_ID])
    parser.add_argument("--input", type=Path)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--results-output", type=Path)
    parser.add_argument("--contract-check-only", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.contract_check_only:
        payload = contract_status()
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if not payload["missing_contracts"] else 1

    if args.dataset_id is None or args.input is None:
        parser.error("--dataset-id and --input are required unless --contract-check-only is used")

    rows = _read_rows(args.input)
    summary = validate_rows(rows, args.dataset_id, args.input)
    if args.summary_output:
        _write_json(args.summary_output, {key: value for key, value in summary.items() if key != "failures"})
    if args.results_output:
        _write_json(args.results_output, {"failures": summary["failures"]})
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    return 0 if summary["hard_fail_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
