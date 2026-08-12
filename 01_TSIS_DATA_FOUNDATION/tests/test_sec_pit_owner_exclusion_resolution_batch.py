# ruff: noqa: E402
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.run_owner_exclusion_resolution_batch import configs_complete, manifest_complete


def test_manifest_complete_is_fail_closed(tmp_path: Path) -> None:
    manifest = tmp_path / "final_manifest.json"
    assert not manifest_complete(manifest, {"COMPLETE"})
    manifest.write_text('{"status":"FAILED"}', encoding="utf-8")
    assert not manifest_complete(manifest, {"COMPLETE"})
    manifest.write_text('{"status":"COMPLETE"}', encoding="utf-8")
    assert manifest_complete(manifest, {"COMPLETE"})


def test_configs_complete_requires_exact_tickers_files_and_hashes(tmp_path: Path) -> None:
    config = tmp_path / "aaa.json"
    config.write_text('{"ticker":"AAA"}\n', encoding="utf-8")
    digest = hashlib.sha256(config.read_bytes()).hexdigest()
    (tmp_path / "index.json").write_text(
        json.dumps([
            {
                "ticker": "AAA",
                "status": "READY",
                "config_path": config.as_posix(),
                "config_sha256": digest,
            }
        ]),
        encoding="utf-8",
    )

    assert configs_complete(tmp_path, {"AAA"})
    assert not configs_complete(tmp_path, {"AAA", "BBB"})
    config.write_text('{"ticker":"CHANGED"}\n', encoding="utf-8")
    assert not configs_complete(tmp_path, {"AAA"})
