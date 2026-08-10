from __future__ import annotations

import importlib.util
import json
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = MODULE_ROOT / "scripts/snapshot_massive_market_operations_reference.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("massive_reference_snapshot", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reference_snapshot_materializes_sanitized_versioned_artifacts(tmp_path: Path) -> None:
    module = _load_module()
    conditions = {
        "endpoint": "/v3/reference/conditions",
        "query": {"asset_class": "stocks", "data_type": "trade"},
        "page_count": 1,
        "request_ids": ["condition-request"],
        "terminal_status": "OK",
        "results": [
            {
                "id": 2,
                "name": "Average Price Trade",
                "asset_class": "stocks",
                "data_types": ["trade"],
                "sip_mapping": {"CTA": "B", "UTP": "W"},
                "update_rules": {
                    "consolidated": {
                        "updates_high_low": False,
                        "updates_open_close": False,
                        "updates_volume": True,
                    }
                },
            }
        ],
    }
    exchanges = {
        "endpoint": "/v3/reference/exchanges",
        "query": {"asset_class": "stocks", "locale": "us"},
        "page_count": 1,
        "request_ids": ["exchange-request"],
        "terminal_status": "OK",
        "results": [
            {
                "id": 11,
                "type": "exchange",
                "asset_class": "stocks",
                "locale": "us",
                "name": "NYSE Arca, Inc.",
                "mic": "ARCX",
                "operating_mic": "XNYS",
                "participant_id": "P",
            }
        ],
    }

    result = module.materialize_snapshot(
        condition_response=conditions,
        exchange_response=exchanges,
        output_dir=tmp_path,
        captured_at_utc="2026-08-06T00:00:00+00:00",
        overwrite=False,
    )
    manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
    assert manifest["condition_count"] == 1
    assert manifest["exchange_count"] == 1
    assert manifest["api_key_persisted"] is False
    assert manifest["canonical_promotion"] == "NOT_AUTHORIZED"
    assert manifest["provider_effective_history"] == "NOT_AVAILABLE_FROM_REFERENCE_ENDPOINT"

    combined = "\n".join(path.read_text(encoding="utf-8") for path in tmp_path.iterdir())
    assert "apiKey" not in combined
    assert "secret-provider-key" not in combined


def test_reference_snapshot_flattens_update_rules_without_losing_raw_json(tmp_path: Path) -> None:
    module = _load_module()
    item = {
        "id": 2,
        "name": "Average Price Trade",
        "asset_class": "stocks",
        "data_types": ["trade"],
        "sip_mapping": {"CTA": "B"},
        "update_rules": {"consolidated": {"updates_volume": True}},
    }
    row = module.normalize_conditions([item])[0]
    assert row["consolidated_updates_volume"] is True
    assert json.loads(row["sip_mapping_json"]) == {"CTA": "B"}
    assert json.loads(row["update_rules_json"])["consolidated"]["updates_volume"] is True

