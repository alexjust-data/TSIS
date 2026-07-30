from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE")
TSIS_ROOT = ROOT.parent
GOV_ROOT = TSIS_ROOT / "00_CTO" / "14_BACKTEST_ENGINE"
RUN_ID = "bt_gate_013_physical_historical_replay_slice_v0_1"
EXPECTED_HASH = "ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019"
EXPECTED_TEST_COUNT = 119


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if "__pycache__" in parts or ".pytest_cache" in parts:
        return True
    if any(part.endswith(".egg-info") for part in parts):
        return True
    if path.suffix in {".pyc", ".pyo"}:
        return True
    if "99_archive" in parts:
        return True
    if "_package_reruns" in parts:
        return True
    if path.name.startswith("bt_gate_013_physical_replay_acceptance_packet_") and path.suffix == ".zip":
        return True
    return False


def add_file(files: dict[str, dict[str, object]], zf: zipfile.ZipFile, source: Path, arcname: str) -> None:
    data = source.read_bytes()
    arc = arcname.replace("\\", "/")
    zf.writestr(arc, data)
    files[arc] = {"path": arc, "sha256": sha256_bytes(data), "size": len(data)}


def add_tree(files: dict[str, dict[str, object]], zf: zipfile.ZipFile, source_root: Path, arc_prefix: str) -> None:
    if not source_root.exists():
        return
    for path in sorted(source_root.rglob("*")):
        if path.is_file() and not should_skip(path):
            add_file(files, zf, path, f"{arc_prefix}/{path.relative_to(source_root).as_posix()}")


def add_text(files: dict[str, dict[str, object]], zf: zipfile.ZipFile, arcname: str, text: str) -> None:
    data = text.encode("utf-8")
    arc = arcname.replace("\\", "/")
    zf.writestr(arc, data)
    files[arc] = {"path": arc, "sha256": sha256_bytes(data), "size": len(data)}


def governance_files() -> list[tuple[Path, str]]:
    manifest = json.loads((GOV_ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    out = []
    for rel in sorted(manifest["files"]):
        source = TSIS_ROOT / rel
        if source.exists():
            out.append((source, rel.replace("\\", "/")))
    out.append((GOV_ROOT / "PACKAGE_MANIFEST.json", "00_CTO/14_BACKTEST_ENGINE/PACKAGE_MANIFEST.json"))
    return out


def main() -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    zip_path = ROOT / f"bt_gate_013_physical_replay_acceptance_packet_{timestamp}.zip"
    files: dict[str, dict[str, object]] = {}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in ["AGENTS.md", "CHANGELOG.md", "LOCAL_RULES.md", "README.md", "pyproject.toml"]:
            add_file(files, zf, ROOT / name, name)
        add_tree(files, zf, ROOT / "src", "src")
        add_tree(files, zf, ROOT / "tests", "tests")
        add_tree(files, zf, ROOT / "configs", "configs")
        add_tree(files, zf, ROOT / "docs", "docs")
        add_tree(files, zf, ROOT / "scripts", "scripts")
        add_tree(files, zf, ROOT / "runs" / RUN_ID, f"runs/{RUN_ID}")
        for source, arcname in governance_files():
            add_file(files, zf, source, arcname)
        add_text(
            files,
            zf,
            "RUN_INCLUDED_TESTS.py",
            f'''from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
os.chdir(ROOT)
suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
count = suite.countTestCases()
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)
expected = {EXPECTED_TEST_COUNT}
if count != expected:
    print(f"UNEXPECTED_INCLUDED_TEST_COUNT={{count}}; expected={{expected}}")
    raise SystemExit(2)
raise SystemExit(0 if result.wasSuccessful() else 1)
''',
        )
        add_text(
            files,
            zf,
            "RUN_END_TO_END.py",
            f'''from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
out = ROOT / "runs" / "_package_reruns"
if out.exists():
    shutil.rmtree(out)
cmd = [
    sys.executable,
    "-B",
    str(ROOT / "scripts" / "run_bt_gate_013_physical_replay_slice.py"),
    "--config",
    "configs/runs/bt_gate_013_physical_historical_replay_slice_v0_1.json",
    "--run-id",
    "bt_gate_013_physical_historical_replay_slice_v0_1_package_rerun",
    "--output-root",
    "runs/_package_reruns",
    "--expect-hash",
    "{EXPECTED_HASH}",
]
proc = subprocess.run(cmd, text=True)
if proc.returncode != 0:
    raise SystemExit(proc.returncode)
run_dir = out / "bt_gate_013_physical_historical_replay_slice_v0_1_package_rerun"
validation = json.loads((run_dir / "physical_replay_validation_report.json").read_text(encoding="utf-8"))
determinism = json.loads((run_dir / "determinism_report.json").read_text(encoding="utf-8"))
metrics = json.loads((run_dir / "metrics_summary.json").read_text(encoding="utf-8"))
manifest = json.loads((run_dir / "final_manifest.json").read_text(encoding="utf-8"))
print(json.dumps({{
    "status": "PASS",
    "validation_status": validation["status"],
    "deterministic_output_hash": validation["deterministic_output_hash"],
    "expected_hash_matches": determinism["expected_hash_matches"],
    "gross_pnl": metrics["gross_pnl"],
    "net_pnl": metrics["net_pnl"],
    "ending_equity": metrics["ending_equity"],
    "source_file_inventory_hash": manifest["source_file_inventory_hash"],
    "row_to_event_lineage_hash": manifest["row_to_event_lineage_hash"],
}}, indent=2, sort_keys=True))
''',
        )
        add_text(
            files,
            zf,
            "PACKAGE_REPRODUCTION_README.md",
            f'''# BT-GATE-013 Package Reproduction

This package contains BT-GATE-013 implementation evidence pending final external acceptance review.

Run from the extracted package root:

```powershell
python -m pip install -e .
python -B RUN_INCLUDED_TESTS.py
python -B RUN_END_TO_END.py
```

Expected results:

```text
RUN_INCLUDED_TESTS.py -> Ran {EXPECTED_TEST_COUNT} tests OK
RUN_END_TO_END.py -> validation_status PASS
deterministic_output_hash = {EXPECTED_HASH}
```

The package includes the frozen portable physical acceptance slice under:

```text
tests/fixtures/bt_gate_013_physical_qg5_slice
```

This remains an ENGINE_VALIDATION_RUN only. It is not edge evidence, not a full 2005-2026 backtest, and does not claim complete small-caps economic realism.
''',
        )
        package_manifest = {
            "package_id": "BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_ACCEPTANCE_PACKET",
            "gate_id": "BT-GATE-013",
            "capability": "PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1",
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "status": "IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW",
            "file_count": len(files),
            "files": [files[key] for key in sorted(files)],
            "required_external_commands": [
                "python -m pip install -e .",
                "python -B RUN_INCLUDED_TESTS.py",
                "python -B RUN_END_TO_END.py",
            ],
            "expected_included_test_count": EXPECTED_TEST_COUNT,
            "expected_deterministic_output_hash": EXPECTED_HASH,
            "physical_run_authorization": "AUTHORIZED_ONLY_FOR_THE_FROZEN_ACCEPTANCE_SLICE_EXECUTED",
            "implementation_acceptance": "PENDING_FINAL_EXTERNAL_REVIEW",
            "state_provider_restrictions": {
                "StateReplayFeed": "NOT_AUTHORIZED",
                "state_bundle_physical_read": "NOT_AUTHORIZED",
                "Market State consumption": "NOT_AUTHORIZED",
                "Event State consumption": "NOT_AUTHORIZED",
                "provider modification": "NOT_AUTHORIZED",
            },
        }
        add_text(files, zf, "ZIP_MANIFEST.json", json.dumps(package_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    data = zip_path.read_bytes()
    print(json.dumps({
        "zip_path": str(zip_path),
        "zip_sha256": sha256_bytes(data),
        "manifest_declared_files": len(files) - 1,
        "zip_entries": len(files),
        "expected_test_count": EXPECTED_TEST_COUNT,
        "expected_deterministic_output_hash": EXPECTED_HASH,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
