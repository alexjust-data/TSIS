from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path("C:/TSIS_Data")
MODULE_ROOT = REPO_ROOT / "01_TSIS_backtest_SmallCaps"

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


def _load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def test_master_intraday_quote_guarded_candidate_config_blocks_promotion() -> None:
    cfg = _load_config()

    assert cfg["dataset_id"] == "master_intraday_bar_table_v0_2_candidate_quote_guarded"
    assert cfg["promotion_state"] == "candidate_contract_defined_not_materialized"
    assert cfg["materialization_scope"] == "quote_guarded_full_universe_candidate_pending_final_repair"
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
    assert bridge["repair_run_state"] == "running_or_not_final_validated"
    assert bridge["official_quote_guarded_root_state"] == "pending_final_manifest_and_validation"

    future = cfg["future_official_sources"]
    assert future["quote_guarded_output_root"] == "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded"
    assert future["repair_manifest"].endswith("repair_manifest_v0_2_or_later.parquet")
    assert "final_validation_report_passed" in cfg["promotion_blockers"]
    assert "builder_consumes_manifest_not_blind_recursive_scan" in cfg["promotion_blockers"]
    assert cfg["repair_row_count_interpretation"]["repair_rows"] == (
        "affected_manifest_rows_not_full_replacement_bars"
    )
    assert "replace_o_h_l_c_in_memory_only_for_affected_minutes" in cfg["loader_semantics"]


def test_master_intraday_quote_guarded_candidate_contract_surfaces_are_linked() -> None:
    cfg = _load_config()
    dataset_id = cfg["dataset_id"]

    for path in [CONTRACT_PATH, SCHEMA_PATH, VALIDATOR_PATH, REGISTRY_PATH]:
        assert path.exists(), path
        text = path.read_text(encoding="utf-8")
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
