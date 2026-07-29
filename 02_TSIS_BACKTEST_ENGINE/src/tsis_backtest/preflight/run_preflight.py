"""RunPreflight implementation for the first DATA gate."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .contracts import (
    CandidateConsumptionPolicy,
    DataPreflightReport,
    DatasetDefinition,
    PreflightFailure,
    PriceViewBinding,
    PriceViewPolicy,
    ResolvedDataContext,
    RunDataRequest,
    TSIS_REAL_DATA_FIXTURE,
)
from .manifests import write_preflight_outputs
from .real_data_inspector import PHYSICAL_INSPECTION_PASS, PhysicalDataInspection
from .registries import DatasetRegistry, UniverseRegistry


SAFE_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class RunPreflight:
    def __init__(
        self,
        dataset_registry: DatasetRegistry,
        universe_registry: UniverseRegistry,
        output_root: Path | None = None,
        generated_at_utc: str | None = None,
        real_data_inspector: object | None = None,
    ) -> None:
        self._dataset_registry = dataset_registry
        self._universe_registry = universe_registry
        self._output_root = output_root
        self._generated_at_utc = generated_at_utc
        self._real_data_inspector = real_data_inspector

    def run(self, request: RunDataRequest) -> DataPreflightReport:
        generated_at = self._generated_at()
        run_id_failure = self._validate_run_id(request, generated_at)
        if run_id_failure is not None:
            return run_id_failure

        run_output_root = self._resolve_run_output_root(request)
        if run_output_root is not None and run_output_root.exists() and any(run_output_root.iterdir()):
            return self._fail(
                request,
                generated_at,
                "RUN_OUTPUT_NOT_EMPTY",
                "run output directory already exists and is not empty",
            )

        report = self._resolve(request, generated_at)
        if run_output_root is not None:
            write_preflight_outputs(report, run_output_root)
        return report

    def _resolve(self, request: RunDataRequest, generated_at: str) -> DataPreflightReport:
        if request.date_start > request.date_end:
            return self._fail(request, generated_at, "INVALID_DATE_RANGE", "date_start is after date_end")

        dataset = self._dataset_registry.resolve(request.dataset_id)
        if dataset is None:
            return self._fail(request, generated_at, "DATASET_NOT_FOUND", "dataset is not registered")

        if not dataset.physical_root.exists():
            return self._fail(request, generated_at, "DATASET_ROOT_NOT_FOUND", "dataset physical root does not exist")

        universe = self._universe_registry.resolve(request.universe_id)
        if universe is None:
            return self._fail(request, generated_at, "UNIVERSE_NOT_FOUND", "universe is not registered")

        candidate_policy = self._validate_candidate_policy(request, dataset, generated_at)
        if isinstance(candidate_policy, DataPreflightReport):
            return candidate_policy

        signal = self._bind_price_view(request, dataset, "signal", request.signal_price_view, generated_at)
        if isinstance(signal, DataPreflightReport):
            return signal
        execution = self._bind_price_view(request, dataset, "execution", request.execution_price_view, generated_at)
        if isinstance(execution, DataPreflightReport):
            return execution
        valuation = self._bind_price_view(request, dataset, "valuation", request.valuation_price_view, generated_at)
        if isinstance(valuation, DataPreflightReport):
            return valuation

        selected_symbols = tuple(request.symbols_optional or universe.symbols)
        missing_symbols = tuple(symbol for symbol in selected_symbols if symbol not in universe.symbols)
        if missing_symbols:
            return self._fail(
                request,
                generated_at,
                "SYMBOL_NOT_IN_UNIVERSE",
                "requested symbols are not present in the resolved universe: " + ",".join(missing_symbols),
            )

        limitations = tuple(dataset.known_limitations) + tuple(universe.limitations)
        if candidate_policy is not None:
            limitations = limitations + tuple(candidate_policy.accepted_limitations)

        price_view_policy = PriceViewPolicy(
            signal=signal,
            execution=execution,
            valuation=valuation,
            raw_lineage=dataset.raw_lineage,
            known_limitations=limitations,
        )
        universe_policy = {
            "universe_id": universe.universe_id,
            "universe_run_id": universe.universe_run_id,
            "selection_rule": universe.selection_rule,
            "source_snapshot": universe.source_snapshot,
            "source_hash": universe.source_hash,
            "limitations": universe.limitations,
        }
        date_range = {
            "date_start": request.date_start.isoformat(),
            "date_end": request.date_end.isoformat(),
        }
        context = ResolvedDataContext(
            dataset_id=dataset.dataset_id,
            dataset_version=dataset.dataset_version,
            resolved_physical_root=dataset.physical_root,
            schema_version=dataset.schema_version,
            price_view_policy=price_view_policy,
            universe_dataset_id=universe.universe_id,
            universe_run_id=universe.universe_run_id,
            universe_filter_policy=universe.selection_rule,
            selected_symbols=selected_symbols,
            calendar_id=request.calendar_id,
            session_policy=request.session_policy,
            timezone=request.timezone,
            data_quality_state=self._data_quality_state(dataset),
            candidate_consumption_policy=candidate_policy,
            known_limitations=limitations,
            source_contract_paths=dataset.source_contract_paths,
        )
        if request.fixture_kind == TSIS_REAL_DATA_FIXTURE:
            if self._real_data_inspector is None:
                return DataPreflightReport(
                    resolved=False,
                    run_id=request.run_id,
                    dataset_id=request.dataset_id,
                    fixture_kind=request.fixture_kind,
                    generated_at_utc=generated_at,
                    context_resolution_status="CONTEXT_RESOLVED",
                    physical_inspection_status="NOT_IMPLEMENTED",
                    preflight_status="PREFLIGHT_FAIL",
                    failure=PreflightFailure(
                        code="PHYSICAL_INSPECTION_NOT_IMPLEMENTED",
                        message="TSIS_REAL_DATA_FIXTURE requires a physical data inspector before preflight can pass",
                    ),
                    resolved_physical_root=dataset.physical_root,
                    price_view_policy=price_view_policy,
                    universe_policy=universe_policy,
                    date_range=date_range,
                    session_policy=request.session_policy,
                    timezone=request.timezone,
                    calendar_id=request.calendar_id,
                    candidate_consumption_policy=candidate_policy,
                    rows_available=None,
                    symbols_available=selected_symbols,
                    missing_data_policy=request.missing_data_policy,
                    corporate_action_policy=request.corporate_action_policy,
                    missing_data_summary={
                        "inspection_status": "not_implemented",
                        "policy_id": request.missing_data_policy.policy_id,
                    },
                    corporate_action_screen={
                        "inspection_status": "not_implemented",
                        "policy_id": request.corporate_action_policy.policy_id,
                    },
                    known_limitations=limitations,
                    resolved_context=context,
                )
            inspection = self._real_data_inspector.inspect(request, context)
            return self._report_from_real_data_inspection(
                request=request,
                generated_at=generated_at,
                dataset=dataset,
                candidate_policy=candidate_policy,
                price_view_policy=price_view_policy,
                universe_policy=universe_policy,
                date_range=date_range,
                selected_symbols=selected_symbols,
                limitations=limitations,
                context=context,
                inspection=inspection,
            )
        return DataPreflightReport(
            resolved=True,
            run_id=request.run_id,
            dataset_id=request.dataset_id,
            fixture_kind=request.fixture_kind,
            generated_at_utc=generated_at,
            context_resolution_status="CONTEXT_RESOLVED",
            physical_inspection_status="SYNTHETIC_NOT_REQUIRED",
            preflight_status="PREFLIGHT_PASS",
            resolved_physical_root=dataset.physical_root,
            price_view_policy=price_view_policy,
            universe_policy=universe_policy,
            date_range=date_range,
            session_policy=request.session_policy,
            timezone=request.timezone,
            calendar_id=request.calendar_id,
            candidate_consumption_policy=candidate_policy,
            rows_available=None,
            symbols_available=selected_symbols,
            missing_data_policy=request.missing_data_policy,
            corporate_action_policy=request.corporate_action_policy,
            missing_data_summary={
                "inspection_status": "not_implemented",
                "policy_id": request.missing_data_policy.policy_id,
            },
            corporate_action_screen={
                "inspection_status": "not_implemented",
                "policy_id": request.corporate_action_policy.policy_id,
            },
            known_limitations=limitations,
            resolved_context=context,
        )

    def _report_from_real_data_inspection(
        self,
        request: RunDataRequest,
        generated_at: str,
        dataset: DatasetDefinition,
        candidate_policy: CandidateConsumptionPolicy | None,
        price_view_policy: PriceViewPolicy,
        universe_policy: dict[str, object],
        date_range: dict[str, str],
        selected_symbols: tuple[str, ...],
        limitations: tuple[str, ...],
        context: ResolvedDataContext,
        inspection: PhysicalDataInspection,
    ) -> DataPreflightReport:
        resolved = inspection.inspection_status == PHYSICAL_INSPECTION_PASS
        failure = None
        if not resolved:
            failure = PreflightFailure(
                code="PHYSICAL_INSPECTION_FAILED",
                message="physical inspection failed: " + ",".join(inspection.failure_codes),
            )
        known_limitations = limitations + tuple(inspection.limitations)
        return DataPreflightReport(
            resolved=resolved,
            run_id=request.run_id,
            dataset_id=request.dataset_id,
            fixture_kind=request.fixture_kind,
            generated_at_utc=generated_at,
            context_resolution_status="CONTEXT_RESOLVED",
            physical_inspection_status=inspection.inspection_status,
            preflight_status="PREFLIGHT_PASS" if resolved else "PREFLIGHT_FAIL",
            failure=failure,
            resolved_physical_root=dataset.physical_root,
            price_view_policy=price_view_policy,
            universe_policy=universe_policy,
            date_range=date_range,
            session_policy=request.session_policy,
            timezone=request.timezone,
            calendar_id=request.calendar_id,
            candidate_consumption_policy=candidate_policy,
            rows_available=inspection.rows_available,
            symbols_available=selected_symbols,
            missing_data_policy=request.missing_data_policy,
            corporate_action_policy=request.corporate_action_policy,
            missing_data_summary=inspection.missing_data_summary,
            corporate_action_screen=inspection.corporate_action_screen.to_dict(),
            physical_inspection=inspection.to_dict(),
            source_partitions_or_files_consumed=inspection.files_consumed,
            snapshot_or_content_hashes=inspection.content_hashes,
            known_limitations=known_limitations,
            resolved_context=context,
        )

    def _validate_candidate_policy(
        self,
        request: RunDataRequest,
        dataset: DatasetDefinition,
        generated_at: str,
    ) -> CandidateConsumptionPolicy | DataPreflightReport | None:
        if not dataset.is_candidate:
            return request.candidate_consumption_policy

        policy = request.candidate_consumption_policy
        if policy is None:
            return self._fail(request, generated_at, "CANDIDATE_POLICY_REQUIRED", "candidate dataset requires explicit consumption policy")
        if policy.candidate_dataset_id != dataset.dataset_id:
            return self._fail(request, generated_at, "CANDIDATE_DATASET_MISMATCH", "candidate policy dataset does not match request dataset")
        if _norm(policy.candidate_physical_root) != _norm(dataset.physical_root):
            return self._fail(request, generated_at, "CANDIDATE_ROOT_MISMATCH", "candidate physical root does not match dataset definition")
        if dataset.validation_manifest is None:
            return self._fail(
                request,
                generated_at,
                "CANDIDATE_REGISTERED_VALIDATION_MANIFEST_REQUIRED",
                "candidate dataset definition requires a registered validation manifest",
            )
        if policy.accepted_validation_manifest is None:
            return self._fail(request, generated_at, "CANDIDATE_VALIDATION_MANIFEST_REQUIRED", "candidate dataset requires accepted validation manifest")
        if _norm(policy.accepted_validation_manifest) != _norm(dataset.validation_manifest):
            return self._fail(
                request,
                generated_at,
                "CANDIDATE_VALIDATION_MANIFEST_MISMATCH",
                "accepted validation manifest does not match the dataset registered validation manifest",
            )
        if not policy.accepted_validation_manifest.exists():
            return self._fail(request, generated_at, "CANDIDATE_VALIDATION_MANIFEST_NOT_FOUND", "candidate validation manifest path does not exist")
        if request.run_purpose not in policy.permitted_run_purposes:
            return self._fail(request, generated_at, "CANDIDATE_RUN_PURPOSE_NOT_PERMITTED", "run purpose is not permitted for this candidate")
        return policy

    def _bind_price_view(
        self,
        request: RunDataRequest,
        dataset: DatasetDefinition,
        role: str,
        price_view: str,
        generated_at: str,
    ) -> PriceViewBinding | DataPreflightReport:
        authorization = dataset.allowed_price_views.get(price_view)
        if authorization is None:
            return self._fail(request, generated_at, "PRICE_VIEW_NOT_AUTHORIZED", f"{role} price view is not authorized: {price_view}")
        binding = authorization.bind(role)
        if binding.allowed_use == "not_allowed":
            return self._fail(request, generated_at, "PRICE_VIEW_NOT_AUTHORIZED", f"{role} price view is not allowed: {price_view}")
        return binding

    def _fail(self, request: RunDataRequest, generated_at: str, code: str, message: str) -> DataPreflightReport:
        return DataPreflightReport(
            resolved=False,
            run_id=request.run_id,
            dataset_id=request.dataset_id,
            fixture_kind=request.fixture_kind,
            generated_at_utc=generated_at,
            context_resolution_status="NOT_RESOLVED",
            physical_inspection_status="NOT_EXECUTED",
            preflight_status="PREFLIGHT_FAIL",
            failure=PreflightFailure(code=code, message=message),
            date_range={
                "date_start": request.date_start.isoformat(),
                "date_end": request.date_end.isoformat(),
            },
            session_policy=request.session_policy,
            timezone=request.timezone,
            calendar_id=request.calendar_id,
            missing_data_policy=request.missing_data_policy,
            corporate_action_policy=request.corporate_action_policy,
            missing_data_summary={
                "inspection_status": "not_implemented",
                "policy_id": request.missing_data_policy.policy_id,
            },
            corporate_action_screen={
                "inspection_status": "not_implemented",
                "policy_id": request.corporate_action_policy.policy_id,
            },
        )

    def _validate_run_id(self, request: RunDataRequest, generated_at: str) -> DataPreflightReport | None:
        if SAFE_RUN_ID_PATTERN.fullmatch(request.run_id) is None:
            return self._fail(
                request,
                generated_at,
                "INVALID_RUN_ID",
                "run_id must match ^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$",
            )
        if self._output_root is None:
            return None
        try:
            self._resolve_run_output_root(request)
        except ValueError:
            return self._fail(
                request,
                generated_at,
                "INVALID_RUN_ID",
                "resolved run output directory must remain inside output_root",
            )
        return None

    def _resolve_run_output_root(self, request: RunDataRequest) -> Path | None:
        if self._output_root is None:
            return None
        output_root = self._output_root.resolve(strict=False)
        run_output_root = (output_root / request.run_id).resolve(strict=False)
        try:
            run_output_root.relative_to(output_root)
        except ValueError as exc:
            raise ValueError("run output directory escapes output_root") from exc
        return run_output_root

    def _generated_at(self) -> str:
        if self._generated_at_utc is not None:
            return self._generated_at_utc
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _data_quality_state(dataset: DatasetDefinition) -> str:
        if dataset.is_candidate:
            return "validated_candidate_for_controlled_downstream_consumption"
        return "registered_non_candidate"


def _norm(path: Path) -> str:
    return str(path.resolve(strict=False)).lower()