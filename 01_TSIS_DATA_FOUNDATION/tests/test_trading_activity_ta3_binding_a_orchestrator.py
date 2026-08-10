from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_trading_activity_ta3_binding_a import (  # noqa: E402
    OFFICIAL_TRADE_ROOT,
    build_block_config,
    load_and_verify_sample,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sample(tmp_path: Path) -> Path:
    blocks = tmp_path / "blocks.parquet"
    targets = tmp_path / "targets.parquet"
    scope = tmp_path / "scope.parquet"
    pd.DataFrame({"block_id": ["ta3b:test"]}).to_parquet(blocks)
    pd.DataFrame({"block_id": ["ta3b:test"]}).to_parquet(targets)
    pd.DataFrame({"block_id": ["ta3b:test"]}).to_parquet(scope)
    manifest = {
        "schema_version": "trading_activity_ta3_sample_manifest_v0_2",
        "official_trade_source_root": OFFICIAL_TRADE_ROOT,
        "legacy_root_fallback": "PROHIBITED",
        "promotion_state": "FROZEN_EXPERIMENTAL_SAMPLE_NOT_CANONICAL",
        "outputs": {
            "selected_blocks": {"path": str(blocks), "sha256": _sha(blocks)},
            "selected_targets": {"path": str(targets), "sha256": _sha(targets)},
            "selected_scope_sessions": {"path": str(scope), "sha256": _sha(scope)},
        },
    }
    path = tmp_path / "sample.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_sample_gate_requires_hashes_and_g_only(tmp_path: Path) -> None:
    sample = _sample(tmp_path)
    manifest, paths = load_and_verify_sample(sample)
    assert manifest["legacy_root_fallback"] == "PROHIBITED"
    assert set(paths) == {"blocks", "targets", "scope"}

    payload = json.loads(sample.read_text(encoding="utf-8"))
    payload["official_trade_source_root"] = "D:/trades_ticks_prod_2005_2026"
    sample.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="governed G root"):
        load_and_verify_sample(sample)


def test_sample_gate_rejects_mutated_binding(tmp_path: Path) -> None:
    sample = _sample(tmp_path)
    payload = json.loads(sample.read_text(encoding="utf-8"))
    Path(payload["outputs"]["selected_blocks"]["path"]).write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        load_and_verify_sample(sample)


def test_block_config_preserves_exact_scope_and_target_range() -> None:
    base = {
        "config_id": "base",
        "scope": {},
        "sources": {"raw_trade_root": OFFICIAL_TRADE_ROOT},
        "outputs": {},
    }
    block = pd.Series(
        {
            "block_id": "ta3b:test",
            "ticker_as_of_session": "TST",
            "instrument_id": "figi:TST",
        }
    )
    scope = pd.DataFrame(
        {
            "session_date": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "scope_role": ["WARMUP", "TARGET", "TARGET"],
        }
    )
    config = build_block_config(base, block, scope)
    assert config["scope"]["session_start"] == "2024-01-02"
    assert config["scope"]["session_end"] == "2024-01-04"
    assert config["scope"]["expected_session_count"] == 3
    assert config["scope"]["evaluation_start"] == "2024-01-03"
    assert config["scope"]["evaluation_end"] == "2024-01-04"
    assert config["scope"]["expected_evaluation_session_count"] == 2
    assert config["sources"]["raw_trade_root"] == OFFICIAL_TRADE_ROOT

