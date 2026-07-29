"""Contracts for the TSIS run preflight gate."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping


NON_EMPIRICAL_TEST_FIXTURE = "NON_EMPIRICAL_TEST_FIXTURE"
TSIS_REAL_DATA_FIXTURE = "TSIS_REAL_DATA_FIXTURE"


@dataclass(frozen=True)
class PreflightFailure:
    code: str
    message: str


@dataclass(frozen=True)
class MissingDataPolicy:
    policy_id: str
    on_missing_bar: str = "EMIT_GAP_WITHOUT_IMPUTATION"
    on_required_open_missing: str = "FAIL_TICKER_DAY"
    on_required_close_missing: str = "FAIL_TICKER_DAY"
    imputation_allowed: bool = False
    gap_event_emitted: bool = True


@dataclass(frozen=True)
class CorporateActionPolicy:
    policy_id: str
    source_dataset_id: str | None = None
    source_snapshot: str | None = None
    on_effective_action_inside_ticker_day: str = "EXCLUDE_TICKER_DAY"
    on_unknown_action_state: str = "DECLARE_LIMITATION"


@dataclass(frozen=True)
class CandidateConsumptionPolicy:
    candidate_dataset_id: str
    candidate_physical_root: Path
    authorization_basis: str
    accepted_validation_manifest: Path | None
    promotion_authorization: bool
    permitted_run_purposes: tuple[str, ...]
    accepted_limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunDataRequest:
    run_id: str
    run_purpose: str
    dataset_id: str
    signal_price_view: str
    execution_price_view: str
    valuation_price_view: str
    universe_id: str
    date_start: date
    date_end: date
    session_policy: str
    timezone: str
    calendar_id: str
    missing_data_policy: MissingDataPolicy
    corporate_action_policy: CorporateActionPolicy
    symbols_optional: tuple[str, ...] = ()
    candidate_consumption_policy: CandidateConsumptionPolicy | None = None
    fixture_kind: str = NON_EMPIRICAL_TEST_FIXTURE
    fixture_id: str | None = None


@dataclass(frozen=True)
class PriceViewBinding:
    role: str
    price_view: str
    physical_root: Path
    allowed_use: str
    validation_manifest: Path | None = None
    execution_semantics_state: str | None = None


@dataclass(frozen=True)
class PriceViewAuthorization:
    price_view: str
    physical_root: Path
    validation_manifest: Path | None = None
    signal_allowed_use: str = "allowed_controlled"
    execution_allowed_use: str = "proxy_allowed_for_engine_mechanics_only"
    valuation_allowed_use: str = "allowed_controlled"
    execution_semantics_state: str | None = "pending_execution_semantics_review"

    def bind(self, role: str) -> PriceViewBinding:
        if role not in {"signal", "execution", "valuation"}:
            raise ValueError(f"unknown price-view role: {role}")
        allowed_use = getattr(self, f"{role}_allowed_use")
        execution_state = self.execution_semantics_state if role == "execution" else None
        return PriceViewBinding(
            role=role,
            price_view=self.price_view,
            physical_root=self.physical_root,
            allowed_use=allowed_use,
            validation_manifest=self.validation_manifest,
            execution_semantics_state=execution_state,
        )


@dataclass(frozen=True)
class PriceViewPolicy:
    signal: PriceViewBinding
    execution: PriceViewBinding
    valuation: PriceViewBinding
    raw_lineage: str | None = None
    known_limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class DatasetDefinition:
    dataset_id: str
    dataset_version: str
    physical_root: Path
    schema_version: str
    allowed_price_views: Mapping[str, PriceViewAuthorization]
    is_candidate: bool = False
    validation_manifest: Path | None = None
    raw_lineage: str | None = None
    known_limitations: tuple[str, ...] = ()
    source_contract_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class UniverseDefinition:
    universe_id: str
    universe_run_id: str
    selection_rule: str
    symbols: tuple[str, ...]
    source_snapshot: str | None = None
    source_hash: str | None = None
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResolvedDataContext:
    dataset_id: str
    dataset_version: str
    resolved_physical_root: Path
    schema_version: str
    price_view_policy: PriceViewPolicy
    universe_dataset_id: str
    universe_run_id: str
    universe_filter_policy: str
    selected_symbols: tuple[str, ...]
    calendar_id: str
    session_policy: str
    timezone: str
    data_quality_state: str
    candidate_consumption_policy: CandidateConsumptionPolicy | None
    known_limitations: tuple[str, ...]
    source_contract_paths: tuple[Path, ...]


@dataclass(frozen=True)
class MarketDataBar1m:
    ticker: str
    ts_start: datetime
    ts_end: datetime
    available_at: datetime
    session_label: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    price_view: str
    quality_flags: tuple[str, ...] = ()
    source_partition_id: str | None = None
    source_file: Path | None = None

    def is_observable_at(self, decision_timestamp: datetime) -> bool:
        return decision_timestamp >= self.available_at


@dataclass(frozen=True)
class DataPreflightReport:
    resolved: bool
    run_id: str
    dataset_id: str
    fixture_kind: str
    generated_at_utc: str
    context_resolution_status: str = "NOT_RESOLVED"
    physical_inspection_status: str = "NOT_EXECUTED"
    preflight_status: str = "PREFLIGHT_FAIL"
    failure: PreflightFailure | None = None
    resolved_physical_root: Path | None = None
    price_view_policy: PriceViewPolicy | None = None
    universe_policy: Mapping[str, Any] | None = None
    date_range: Mapping[str, str] | None = None
    session_policy: str | None = None
    timezone: str | None = None
    calendar_id: str | None = None
    candidate_consumption_policy: CandidateConsumptionPolicy | None = None
    rows_available: int | None = None
    symbols_available: tuple[str, ...] = ()
    missing_data_policy: MissingDataPolicy | None = None
    corporate_action_policy: CorporateActionPolicy | None = None
    missing_data_summary: Mapping[str, Any] | None = None
    corporate_action_screen: Mapping[str, Any] | None = None
    physical_inspection: Mapping[str, Any] | None = None
    source_partitions_or_files_consumed: tuple[Path, ...] = ()
    snapshot_or_content_hashes: Mapping[str, str] | None = None
    known_limitations: tuple[str, ...] = ()
    resolved_context: ResolvedDataContext | None = None

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: to_jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    return value


