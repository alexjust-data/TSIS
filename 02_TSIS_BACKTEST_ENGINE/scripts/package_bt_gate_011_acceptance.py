
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TSIS_ROOT = ROOT.parent
GOV_ROOT = TSIS_ROOT / "00_CTO" / "14_BACKTEST_ENGINE"
RUN_ID = "bt_gate_011_open_short_close_qg5_v0_1"
EXPECTED_HASH = "f5bccea7d6f5f6eff0647a66d4827a011e5854af9644a8854b10135da883cc2b"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if "__pycache__" in parts or ".pytest_cache" in parts:
        return True
    if path.suffix in {".pyc", ".pyo"}:
        return True
    if "99_archive" in parts:
        return True
    if path.name.startswith("bt_gate_011_end_to_end_acceptance_packet_") and path.suffix == ".zip":
        return True
    if "_bt_gate_011_rerun_check" in parts or "_package_reruns" in parts:
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
    zip_path = ROOT / f"bt_gate_011_end_to_end_acceptance_packet_{timestamp}.zip"
    files: dict[str, dict[str, object]] = {}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in ["AGENTS.md", "CHANGELOG.md", "LOCAL_RULES.md", "README.md", "pyproject.toml"]:
            add_file(files, zf, ROOT / name, name)
        add_tree(files, zf, ROOT / "src", "src")
        add_tree(files, zf, ROOT / "tests", "tests")
        add_tree(files, zf, ROOT / "configs", "configs")
        add_tree(files, zf, ROOT / "docs", "docs")
        add_file(files, zf, ROOT / "scripts/run_bt_gate_011_end_to_end.py", "scripts/run_bt_gate_011_end_to_end.py")
        add_file(files, zf, ROOT / "scripts/package_bt_gate_011_acceptance.py", "scripts/package_bt_gate_011_acceptance.py")
        add_tree(files, zf, ROOT / "runs" / RUN_ID, f"runs/{RUN_ID}")
        for source, arcname in governance_files():
            add_file(files, zf, source, arcname)
        add_text(
            files,
            zf,
            "RUN_INCLUDED_TESTS.py",
            '''from __future__ import annotations

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
expected = 99
if count != expected:
    print(f"UNEXPECTED_INCLUDED_TEST_COUNT={count}; expected={expected}")
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
    str(ROOT / "scripts" / "run_bt_gate_011_end_to_end.py"),
    "--run-id",
    "bt_gate_011_open_short_close_qg5_v0_1_package_rerun",
    "--output-root",
    "runs/_package_reruns",
    "--expect-hash",
    "{EXPECTED_HASH}",
]
proc = subprocess.run(cmd, text=True)
if proc.returncode != 0:
    raise SystemExit(proc.returncode)
summary = json.loads((out / "bt_gate_011_open_short_close_qg5_v0_1_package_rerun" / "run_summary.json").read_text(encoding="utf-8"))
print(json.dumps({{
    "status": "PASS",
    "validation_status": summary["validation_status"],
    "event_loop_mode": summary["event_loop_mode"],
    "future_event_access_detected": summary["event_loop_future_event_access_detected"],
    "deterministic_output_hash": summary["deterministic_output_hash"],
}}, indent=2, sort_keys=True))
''',
        )
        add_text(
            files,
            zf,
            "PACKAGE_REPRODUCTION_README.md",
            f'''# BT-GATE-011 Package Reproduction

This package contains the corrected BT-GATE-011 acceptance evidence.

Run from the extracted package root:

```powershell
python -m pip install -e .
python -B RUN_INCLUDED_TESTS.py
python -B RUN_END_TO_END.py
```

Expected results:

```text
RUN_INCLUDED_TESTS.py -> Ran 99 tests OK
RUN_END_TO_END.py -> validation_status PASS
deterministic_output_hash = {EXPECTED_HASH}
event_loop_mode = ONLINE_REPLAY_COORDINATOR_V0_1
future_event_access_detected = false
```

The package uses a portable QG5 acceptance slice under:

```text
tests/fixtures/bt_gate_011_qg5_portable
```

This remains an ENGINE_VALIDATION_RUN only. It is not edge evidence and does not claim complete small-caps economic realism.
''',
        )
        manifest = {
            "package_id": "BT_GATE_011_SINGLE_STRATEGY_END_TO_END_ACCEPTANCE_PACKET",
            "gate_id": "BT-GATE-011",
            "capability": "SINGLE_STRATEGY_END_TO_END_BACKTEST",
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "status": "IMPLEMENTED_PENDING_FINAL_ACCEPTANCE_REVIEW",
            "file_count": len(files),
            "files": [files[key] for key in sorted(files)],
            "required_external_commands": [
                "python -m pip install -e .",
                "python -B RUN_INCLUDED_TESTS.py",
                "python -B RUN_END_TO_END.py",
            ],
            "expected_included_test_count": 99,
            "expected_deterministic_output_hash": EXPECTED_HASH,
            "state_provider_restrictions": {
                "StateReplayFeed": "NOT_AUTHORIZED",
                "state_bundle_physical_read": "NOT_AUTHORIZED",
                "Market State consumption": "NOT_AUTHORIZED",
                "Event State consumption": "NOT_AUTHORIZED",
                "provider modification": "NOT_AUTHORIZED",
            },
        }
        zf.writestr("ZIP_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8"))
    print(json.dumps({
        "zip_path": str(zip_path),
        "zip_sha256": sha256_bytes(zip_path.read_bytes()),
        "zip_manifest_declared_files": len(files),
        "zip_entries_total": len(zipfile.ZipFile(zip_path).namelist()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
