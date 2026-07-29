from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tsis_backtest.preflight.contracts import (  # noqa: E402
    CandidateConsumptionPolicy,
    CorporateActionPolicy,
    DatasetDefinition,
    MissingDataPolicy,
    PriceViewAuthorization,
    RunDataRequest,
    TSIS_REAL_DATA_FIXTURE,
    UniverseDefinition,
)
from tsis_backtest.preflight.real_data_inspector import (  # noqa: E402
    FAIL,
    PASS_COMPLETE,
    PASS_WITH_GAPS,
    RealDataInspector,
    sha256_file,
)
from tsis_backtest.preflight.registries import DatasetRegistry, UniverseRegistry  # noqa: E402
from tsis_backtest.preflight.run_preflight import RunPreflight  # noqa: E402


class RealDataInspectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dataset_root = self.root / "qg"
        self.ca_path = self.root / "corporate_actions.parquet"
        self.ca_manifest = self.root / "corporate_actions_manifest.json"
        self.universe_path = self.root / "lt1b.parquet"
        self.validation_manifest = self.root / "validation_manifest.json"
        self.validation_manifest.write_text("{}\n", encoding="utf-8")
        self.ca_manifest.write_text("{}\n", encoding="utf-8")
        self.session_date = "2026-01-05"
        self.symbol = "AAA"
        self._write_universe()
        self._write_corporate_actions([])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_pass_complete_ignores_missing_vendor_vw(self) -> None:
        path = self._write_qg_file(self._rows([0, 1, 2]), include_vendor_vw=False)
        config = self._fixture_config(path)

        inspection = self._inspect(config)

        self.assertEqual(inspection.inspection_status, "PHYSICAL_INSPECTION_PASS")
        self.assertEqual(inspection.per_ticker_day_results[0].status, PASS_COMPLETE)
        self.assertNotIn("vw", config["dataset"]["minimum_required_columns"])
        self.assertIn("vw", config["dataset"]["non_consumable_vendor_fields"])

    def test_file_missing_fails(self) -> None:
        path = self._qg_path()
        config = self._fixture_config(path, expected_exists=False)

        inspection = self._inspect(config)

        self.assertEqual(inspection.inspection_status, "PHYSICAL_INSPECTION_FAIL")
        self.assertEqual(inspection.per_ticker_day_results[0].status, FAIL)
        self.assertIn("FILE_NOT_FOUND", inspection.per_ticker_day_results[0].failure_codes)

    def test_schema_invalid_missing_required_column_fails(self) -> None:
        path = self._write_qg_file(self._rows([0, 1, 2]), omit_columns=("o",))
        config = self._fixture_config(path)

        inspection = self._inspect(config)

        self.assertIn("SCHEMA_MISSING_REQUIRED_COLUMNS", inspection.per_ticker_day_results[0].failure_codes)

    def test_open_missing_fails_ticker_day(self) -> None:
        path = self._write_qg_file(self._rows([1, 2]))
        config = self._fixture_config(path)

        inspection = self._inspect(config)

        self.assertIn("REQUIRED_OPEN_BAR_MISSING", inspection.per_ticker_day_results[0].failure_codes)

    def test_close_missing_fails_ticker_day(self) -> None:
        path = self._write_qg_file(self._rows([0, 1]))
        config = self._fixture_config(path)

        inspection = self._inspect(config)

        self.assertIn("REQUIRED_CLOSE_BAR_MISSING", inspection.per_ticker_day_results[0].failure_codes)

    def test_interior_gap_is_pass_with_gaps_when_policy_allows_no_imputation(self) -> None:
        path = self._write_qg_file(self._rows([0, 2]))
        config = self._fixture_config(path)

        inspection = self._inspect(config)
        result = inspection.per_ticker_day_results[0]

        self.assertEqual(inspection.inspection_status, "PHYSICAL_INSPECTION_PASS")
        self.assertEqual(result.status, PASS_WITH_GAPS)
        self.assertIn("OBSERVED_MINUTE_GAP", result.warning_codes)
        self.assertEqual(result.missing_regular_minutes, 1)

    def test_duplicate_timestamp_fails(self) -> None:
        path = self._write_qg_file(self._rows([0, 1, 1, 2]))
        config = self._fixture_config(path)

        inspection = self._inspect(config)

        self.assertIn("DUPLICATE_TIMESTAMPS", inspection.per_ticker_day_results[0].failure_codes)

    def test_invalid_ohlcv_fails(self) -> None:
        rows = self._rows([0, 1, 2])
        rows[1]["h"] = 9.0
        rows[1]["c"] = 10.0
        path = self._write_qg_file(rows)
        config = self._fixture_config(path)

        inspection = self._inspect(config)

        self.assertIn("INVALID_CORE_ROWS", inspection.per_ticker_day_results[0].failure_codes)
        self.assertIn("high_below_open_low_or_close", inspection.per_ticker_day_results[0].invalid_core_issue_counts)

    def test_corporate_action_effective_on_session_fails(self) -> None:
        path = self._write_qg_file(self._rows([0, 1, 2]))
        self._write_corporate_actions([
            {"ticker": self.symbol, "action_type": "split", "action_date": datetime(2026, 1, 5, tzinfo=timezone.utc)}
        ])
        config = self._fixture_config(path)

        inspection = self._inspect(config)

        self.assertIn("CORPORATE_ACTION_EFFECTIVE_ON_SESSION", inspection.corporate_action_screen.failure_codes)
        self.assertEqual(inspection.corporate_action_screen.exact_session_rows, 1)

    def test_expected_discovery_drift_fails(self) -> None:
        path = self._write_qg_file(self._rows([0, 1, 2]))
        config = self._fixture_config(path)
        config["per_ticker_day"][0]["session_rows"] = 999

        inspection = self._inspect(config)

        self.assertIn("EXPECTED_DISCOVERY_EVIDENCE_DRIFT", inspection.per_ticker_day_results[0].failure_codes)
        self.assertIn("session_rows", inspection.per_ticker_day_results[0].expected_discovery_drift)

    def test_real_fixture_request_mismatch_fails(self) -> None:
        path = self._write_qg_file(self._rows([0, 1, 2]))
        config = self._fixture_config(path)

        inspection = self._inspect(config, request=self._request(date_start=date(2026, 1, 6), date_end=date(2026, 1, 6)))

        self.assertEqual(inspection.inspection_status, "PHYSICAL_INSPECTION_FAIL")
        self.assertIn("REAL_FIXTURE_REQUEST_MISMATCH", inspection.failure_codes)

    def test_validation_manifest_hash_mismatch_fails(self) -> None:
        path = self._write_qg_file(self._rows([0, 1, 2]))
        config = self._fixture_config(path)
        config["dataset"]["validation_manifest_sha256"] = "0" * 64

        inspection = self._inspect(config)

        self.assertEqual(inspection.inspection_status, "PHYSICAL_INSPECTION_FAIL")
        self.assertIn("VALIDATION_MANIFEST_HASH_MISMATCH", inspection.failure_codes)
        self.assertEqual(inspection.dataset_validation_manifest["sha256"], sha256_file(self.validation_manifest))

    def test_run_preflight_integrates_real_data_inspector_and_writes_hashes(self) -> None:
        path = self._write_qg_file(self._rows([0, 1, 2]))
        config = self._fixture_config(path)
        inspector = RealDataInspector(config)
        output_root = self.root / "out"
        dataset = self._dataset_definition()
        universe = UniverseDefinition(
            universe_id="lt1b_universe_v0_1",
            universe_run_id="synthetic_lt1b_run",
            selection_rule="ticker_plus_pti_window",
            symbols=(self.symbol,),
            source_hash=sha256_file(self.universe_path),
        )
        preflight = RunPreflight(
            DatasetRegistry({dataset.dataset_id: dataset}),
            UniverseRegistry({universe.universe_id: universe}),
            output_root=output_root,
            generated_at_utc="2026-07-28T00:00:00Z",
            real_data_inspector=inspector,
        )

        report = preflight.run(self._request(candidate_consumption_policy=self._candidate_policy()))

        run_root = output_root / "real_fixture_run"
        self.assertTrue(report.resolved)
        self.assertEqual(report.physical_inspection_status, "PHYSICAL_INSPECTION_PASS")
        self.assertTrue((run_root / "data_manifest.json").exists())
        manifest = json.loads((run_root / "data_manifest.json").read_text(encoding="utf-8"))
        self.assertIn(str(path), manifest["snapshot_or_content_hashes"])
        self.assertIn(str(self.validation_manifest), manifest["snapshot_or_content_hashes"])
        self.assertTrue(manifest["source_partitions_or_files_consumed"])

    def _inspect(self, config: dict, request: RunDataRequest | None = None) -> object:
        inspector = RealDataInspector(config)
        return inspector.inspect(request or self._request(), SimpleNamespace(selected_symbols=(self.symbol,), dataset_id="synthetic_qg_candidate", universe_dataset_id="lt1b_universe_v0_1"))

    def _request(self, **overrides) -> RunDataRequest:
        values = {
            "run_id": "real_fixture_run",
            "run_purpose": "ENGINE_MECHANICS_TEST",
            "dataset_id": "synthetic_qg_candidate",
            "signal_price_view": "quote_guarded_1m",
            "execution_price_view": "quote_guarded_1m",
            "valuation_price_view": "quote_guarded_1m",
            "universe_id": "lt1b_universe_v0_1",
            "date_start": date(2026, 1, 5),
            "date_end": date(2026, 1, 5),
            "session_policy": "REGULAR_ONLY",
            "timezone": "America/New_York",
            "calendar_id": "XNYS",
            "missing_data_policy": MissingDataPolicy(policy_id="missing_v0_1"),
            "corporate_action_policy": CorporateActionPolicy(policy_id="ca_v0_1"),
            "symbols_optional": (self.symbol,),
            "fixture_kind": TSIS_REAL_DATA_FIXTURE,
            "fixture_id": "synthetic_fixture",
        }
        values.update(overrides)
        return RunDataRequest(**values)

    def _dataset_definition(self) -> DatasetDefinition:
        auth = PriceViewAuthorization(
            price_view="quote_guarded_1m",
            physical_root=self.dataset_root,
            validation_manifest=self.validation_manifest,
        )
        return DatasetDefinition(
            dataset_id="synthetic_qg_candidate",
            dataset_version="v0_1",
            physical_root=self.dataset_root,
            schema_version="schema_v0_1",
            allowed_price_views={"quote_guarded_1m": auth},
            is_candidate=True,
            validation_manifest=self.validation_manifest,
            known_limitations=("synthetic_real_fixture",),
        )

    def _candidate_policy(self) -> CandidateConsumptionPolicy:
        return CandidateConsumptionPolicy(
            candidate_dataset_id="synthetic_qg_candidate",
            candidate_physical_root=self.dataset_root,
            authorization_basis="synthetic_validation",
            accepted_validation_manifest=self.validation_manifest,
            promotion_authorization=False,
            permitted_run_purposes=("ENGINE_MECHANICS_TEST",),
        )

    def _fixture_config(self, path: Path, expected_exists: bool = True) -> dict:
        per_ticker = {
            "ticker": self.symbol,
            "file": str(path),
            "sha256": sha256_file(path) if expected_exists and path.exists() else "missing",
            "session_rows": 0,
            "missing_regular_minutes": 0,
            "has_open_proxy_1430": False,
            "has_close_proxy_2059": False,
        }
        if expected_exists and path.exists():
            rows = pq.ParquetFile(path).read().to_pylist()
            session_rows = []
            expected_minutes = [datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc) + timedelta(minutes=i) for i in range(3)]
            observed = set()
            for row in rows:
                ts = datetime.fromisoformat(row["ts_utc"].replace("Z", "+00:00"))
                if expected_minutes[0] <= ts <= expected_minutes[-1]:
                    session_rows.append(row)
                    observed.add(ts)
            per_ticker.update(
                {
                    "session_rows": len(session_rows),
                    "missing_regular_minutes": sum(1 for ts in expected_minutes if ts not in observed),
                    "has_open_proxy_1430": expected_minutes[0] in observed,
                    "has_close_proxy_2059": expected_minutes[-1] in observed,
                }
            )
        return {
            "fixture_id": "synthetic_fixture",
            "fixture_kind": TSIS_REAL_DATA_FIXTURE,
            "fixture_id": "synthetic_fixture",
            "dataset": {
                "dataset_id": "synthetic_qg_candidate",
                "dataset_version": "v0_1",
                "physical_root": str(self.dataset_root),
                "validation_manifest": str(self.validation_manifest),
                "validation_manifest_sha256": sha256_file(self.validation_manifest),
                "minimum_required_columns": self._minimum_columns(),
                "optional_columns_observed_in_fixture": ["n", "vw"],
                "non_consumable_vendor_fields": {
                    "vw": {"classification": "PRESENT_BUT_NON_CONSUMABLE_VENDOR_DERIVED_FIELD"}
                },
                "allowed_row_dataset_ids": ["synthetic_row_dataset"],
                "expected_row_build_run_ids": ["synthetic_build"],
            },
            "universe": {
                "universe_id": "lt1b_universe_v0_1",
                "physical_path": str(self.universe_path),
                "sha256": sha256_file(self.universe_path),
                "classification_allowed": ["active_lt_1b_last_classifiable"],
            },
            "corporate_actions": {
                "dataset_id": "corporate_actions_table_v0_1",
                "physical_path": str(self.ca_path),
                "table_sha256": sha256_file(self.ca_path),
                "manifest_path": str(self.ca_manifest),
                "manifest_sha256": sha256_file(self.ca_manifest),
            },
            "session": {
                "session_date": self.session_date,
                "calendar_id": "XNYS",
                "session_policy": "REGULAR_ONLY",
                "timezone": "America/New_York",
                "regular_session_filter_utc_for_this_date": {
                    "start_inclusive": "2026-01-05T14:30:00Z",
                    "end_exclusive": "2026-01-05T14:33:00Z",
                },
                "open_proxy_ts_utc": "2026-01-05T14:30:00Z",
                "close_proxy_ts_utc": "2026-01-05T14:32:00Z",
            },
            "symbols": [self.symbol],
            "per_ticker_day": [per_ticker],
            "price_view_policy": {
                "signal": {"price_view": "quote_guarded_1m", "allowed_use": "allowed_controlled"},
                "execution": {
                    "price_view": "quote_guarded_1m",
                    "allowed_use": "proxy_allowed_for_engine_mechanics_only",
                    "execution_semantics_state": "pending_execution_semantics_review",
                },
                "valuation": {"price_view": "quote_guarded_1m", "allowed_use": "allowed_controlled"},
            },
            "limitations": ("synthetic_fixture",),
        }

    def _write_qg_file(self, rows: list[dict], include_vendor_vw: bool = False, omit_columns: tuple[str, ...] = ()) -> Path:
        path = self._qg_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        output = []
        for row in rows:
            clean = {key: value for key, value in row.items() if key not in omit_columns}
            if include_vendor_vw:
                clean["vw"] = 10.0
            output.append(clean)
        pq.write_table(pa.Table.from_pylist(output), path)
        return path

    def _qg_path(self) -> Path:
        return self.dataset_root / "year=2026" / f"ticker={self.symbol}" / "month=01" / "part-000.parquet"

    def _rows(self, minute_offsets: list[int]) -> list[dict]:
        rows = []
        for offset in minute_offsets:
            ts = datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc) + timedelta(minutes=offset)
            rows.append(
                {
                    "ticker": self.symbol,
                    "ts_utc": ts.isoformat().replace("+00:00", "Z"),
                    "date": "2026-01-05",
                    "year": 2026,
                    "month": 1,
                    "o": 10.0,
                    "h": 10.5,
                    "l": 9.8,
                    "c": 10.1,
                    "v": 1000.0,
                    "t": int(ts.timestamp() * 1000),
                    "o_raw": 10.0,
                    "h_raw": 10.5,
                    "l_raw": 9.8,
                    "c_raw": 10.1,
                    "quote_guarded_repair_applied": False,
                    "quote_guarded_view": "raw_1m_plus_quote_guarded_overlay",
                    "repair_lookup_state": "indexed_no_repair_rows",
                    "source_quote_guarded_repair_manifest": "indexed_no_repair_rows",
                    "dataset_id": "synthetic_row_dataset",
                    "build_run_id": "synthetic_build",
                    "created_utc": "2026-07-28T00:00:00Z",
                    "source_raw_path": "synthetic_raw.parquet",
                }
            )
        return rows

    @staticmethod
    def _minimum_columns() -> list[str]:
        return [
            "ticker",
            "ts_utc",
            "date",
            "year",
            "month",
            "o",
            "h",
            "l",
            "c",
            "v",
            "t",
            "o_raw",
            "h_raw",
            "l_raw",
            "c_raw",
            "quote_guarded_repair_applied",
            "quote_guarded_view",
            "repair_lookup_state",
            "source_quote_guarded_repair_manifest",
            "dataset_id",
            "build_run_id",
            "created_utc",
            "source_raw_path",
        ]

    def _write_universe(self) -> None:
        rows = [
            {
                "ticker": self.symbol,
                "first_seen_date": datetime(2020, 1, 1),
                "last_observed_date": datetime(2026, 3, 9),
                "classification_1b": "active_lt_1b_last_classifiable",
            }
        ]
        pq.write_table(pa.Table.from_pylist(rows), self.universe_path)

    def _write_corporate_actions(self, rows: list[dict]) -> None:
        schema = pa.schema(
            [
                ("ticker", pa.string()),
                ("action_type", pa.string()),
                ("action_date", pa.timestamp("us", tz="UTC")),
            ]
        )
        pq.write_table(pa.Table.from_pylist(rows, schema=schema), self.ca_path)


if __name__ == "__main__":
    unittest.main()