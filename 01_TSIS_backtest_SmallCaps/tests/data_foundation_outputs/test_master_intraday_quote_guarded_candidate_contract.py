from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path("C:/TSIS_Data")
MODULE_ROOT = REPO_ROOT / "01_TSIS_backtest_SmallCaps"
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import preflight_master_intraday_quote_guarded_candidate as preflight  # noqa: E402

CONFIG_PATH = (
    MODULE_ROOT
    / "configs"
    / "data_foundation_outputs"
    / "master_intraday_bar_table_quote_guarded_candidate_v0_2.json"
)
CONTRACT_PATH = (
    MODULE_ROOT
    / "01_foundations"
    / "module_contracts"
    / "outputs"
    / "master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md"
)
SCHEMA_PATH = (
    MODULE_ROOT
    / "01_foundations"
    / "canonical_schemas"
    / "outputs"
    / "master_intraday_bar_table_schema_contract.md"
)
VALIDATOR_PATH = (
    MODULE_ROOT
    / "01_foundations"
    / "validators"
    / "outputs"
    / "master_intraday_bar_table_validators.md"
)
REGISTRY_PATH = (
    MODULE_ROOT
    / "01_foundations"
    / "dataset_registry"
    / "outputs"
    / "master_intraday_bar_table_registry_entry.yaml"
)
LINEAGE_PATH = (
    MODULE_ROOT
    / "01_foundations"
    / "module_contracts"
    / "outputs"
    / "state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md"
)


def _load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def test_master_intraday_quote_guarded_candidate_config_blocks_promotion() -> None:
    cfg = _load_config()

    assert cfg["dataset_id"] == "master_intraday_bar_table_v0_2_candidate_quote_guarded"
    assert cfg["promotion_state"] == "scoped_candidate_materialized_not_official"
    assert cfg["materialization_scope"] == "quote_guarded_lt1b_candidate_pending_builder_materialization"
    assert cfg["full_universe_claim"] is False
    assert cfg["official_dataset_created"] is False
    assert cfg["safe_to_launch_full_materialization"] is False
    assert cfg["storage_model"] == "raw_ohlcv_1m_plus_repair_manifest_overlay"
    assert cfg["creates_full_corrected_tree"] is False
    assert cfg["raw_ohlcv_1m_mutation_allowed"] is False
    assert cfg["primary_promoted_artifact_type"] == "repair_manifest_overlay"

    target = cfg["target_dataset_path"].replace("\\", "/")
    forbidden = [path.replace("\\", "/") for path in cfg["must_not_write_paths"]]
    assert target.endswith("/master_intraday_bar_table_v0_2_candidate_quote_guarded")
    assert all(not target.startswith(path) for path in forbidden)

    bridge = cfg["current_bridge_sources"]
    assert bridge["minute_root"] == "E:/TSIS/data/ohlcv_1m"
    assert bridge["quotes_root"] == "D:/quotes"
    assert bridge["active_repair_shards_dir"].endswith("/repair_shards")
    assert bridge["active_consolidated_repair_manifest"].endswith("/repair_manifest.parquet")
    assert bridge["quotes_root_state"] == "provisional_d_legacy_recovery_root_pending_e_parity"
    assert bridge["repair_run_state"] == "PASS_promoted_lt1b_manifest"
    assert bridge["official_quote_guarded_root_state"] == "promoted_manifest_available"
    assert bridge["official_quote_guarded_manifest"].endswith("repair_manifest_lt1b_v0_1.parquet")
    assert bridge["official_quote_guarded_manifest_rows"] == 301278342
    assert bridge["lt1b_completed_tickers"] == 4824
    assert bridge["lt1b_missing_tickers"] == 0

    official = cfg["official_quote_guarded_sources"]
    assert official["quote_guarded_output_root"] == "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded"
    assert official["repair_manifest"].endswith("repair_manifest_lt1b_v0_1.parquet")
    assert official["repair_summary"].endswith("repair_manifest_lt1b_v0_1_summary.json")
    assert official["repair_sample"].endswith("repair_manifest_lt1b_v0_1_sample.csv")
    assert official["manifest_state"] == "PASS_promoted_lt1b_manifest"
    assert official["manifest_rows"] == 301278342
    assert "builder_consumes_manifest_not_blind_recursive_scan" in cfg["promotion_blockers"]
    assert cfg["repair_row_count_interpretation"]["repair_rows"] == (
        "affected_manifest_rows_not_full_replacement_bars"
    )
    assert "replace_o_h_l_c_in_memory_only_for_affected_minutes" in cfg["loader_semantics"]


def test_master_intraday_quote_guarded_candidate_contract_surfaces_are_linked() -> None:
    cfg = _load_config()
    dataset_id = cfg["dataset_id"]

    for path in [CONTRACT_PATH, SCHEMA_PATH, VALIDATOR_PATH, REGISTRY_PATH, LINEAGE_PATH]:
        assert path.exists(), path
        text = path.read_text(encoding="utf-8")
        if path == LINEAGE_PATH:
            assert "repair_manifest_lt1b_v0_1.parquet" in text
        else:
            assert dataset_id in text

    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    assert "does not materialize a parquet dataset" in contract
    assert "does not modify `master_intraday_bar_table_v0_1`" in contract
    assert "full_universe_claim: false" in contract
    assert "D:/quotes" in contract
    assert "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded" in contract
    assert "raw ohlcv_1m + repair_manifest = ohlcv_1m_quote_guarded view" in contract
    assert "does not create a complete corrected tree" in contract
    assert "repair_rows != full replacement bars" in contract


def test_master_intraday_quote_guarded_preflight_fixture(tmp_path: Path) -> None:
    raw_root = tmp_path / "ohlcv_1m"
    quotes_root = tmp_path / "quotes"
    qg_root = tmp_path / "ohlcv_1m_quote_guarded"
    raw_root.mkdir()
    quotes_root.mkdir()
    qg_root.mkdir()

    repair_manifest = qg_root / "repair_manifest_lt1b_v0_1.parquet"
    repair_manifest.write_bytes(b"not-a-real-parquet-for-preflight-path-check")
    repair_summary = qg_root / "repair_manifest_lt1b_v0_1_summary.json"
    repair_sample = qg_root / "repair_manifest_lt1b_v0_1_sample.csv"
    consolidation_summary = tmp_path / "consolidation_summary.json"

    summary = {
        "status": "PASS",
        "manifest_path": repair_manifest.as_posix(),
        "manifest_rows": 301278342,
        "universe_tickers": 4824,
        "completed_tickers": 4824,
        "missing_tickers": 0,
        "selected_repair_shards": 421533,
        "skipped_out_scope_shards": 19510,
    }
    repair_summary.write_text(json.dumps(summary), encoding="utf-8")
    consolidation_summary.write_text(json.dumps(summary), encoding="utf-8")
    repair_sample.write_text(
        ",".join(sorted(preflight.REQUIRED_SAMPLE_COLUMNS)) + "\n",
        encoding="utf-8",
    )

    cfg = _load_config()
    cfg["current_bridge_sources"]["minute_root"] = raw_root.as_posix()
    cfg["current_bridge_sources"]["quotes_root"] = quotes_root.as_posix()
    cfg["current_bridge_sources"]["output_root"] = qg_root.as_posix()
    cfg["current_bridge_sources"]["official_quote_guarded_manifest"] = repair_manifest.as_posix()
    cfg["current_bridge_sources"]["official_quote_guarded_summary"] = repair_summary.as_posix()
    cfg["current_bridge_sources"]["official_quote_guarded_sample"] = repair_sample.as_posix()
    cfg["official_quote_guarded_sources"]["quote_guarded_output_root"] = qg_root.as_posix()
    cfg["official_quote_guarded_sources"]["repair_manifest"] = repair_manifest.as_posix()
    cfg["official_quote_guarded_sources"]["repair_summary"] = repair_summary.as_posix()
    cfg["official_quote_guarded_sources"]["repair_sample"] = repair_sample.as_posix()
    cfg["official_quote_guarded_sources"]["consolidation_summary"] = consolidation_summary.as_posix()
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(cfg), encoding="utf-8")

    report = preflight.run_preflight(
        config_path,
        tmp_path / "out",
        created_at_utc="2026-07-05T00:00:00Z",
    )

    assert report["dataset_id"] == "master_intraday_bar_table_v0_2_candidate_quote_guarded"
    assert report["validations"]["validator_status"] == "passed"
    assert report["validations"]["validator_hard_fail_count"] == 0
    assert report["manifest_rows"] == 301278342
    assert report["completed_tickers"] == 4824
    assert report["not_allowed_actions"] == [
        "overwrite_raw_ohlcv_1m",
        "write_into_master_intraday_bar_table_v0_1",
        "claim_full_universe_state_table",
        "enable_ml_rl_alphaevolve",
    ]
    assert (tmp_path / "out" / "master_intraday_quote_guarded_candidate_preflight_v0_1.json").exists()
