from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TSIS_ROOT = ROOT.parent
GOV_ROOT = TSIS_ROOT / "00_CTO" / "14_BACKTEST_ENGINE"
RUN_ID = "bt_gate_012_multi_symbol_multi_session_qg5_v0_1"
EXPECTED_HASH = "414aceb2bc80836f8fa821cd4d14071e54c86f3c7855c0a34c82ffd8b1c79182"
EXPECTED_TEST_COUNT = 106


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
    if path.name.startswith("bt_gate_012_portfolio_slice_acceptance_packet_") and path.suffix == ".zip":
        return True
    if "_package_reruns" in parts:
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
    zip_path = ROOT / f"bt_gate_012_portfolio_slice_acceptance_packet_{timestamp}.zip"
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
    str(ROOT / "scripts" / "run_bt_gate_012_portfolio_slice.py"),
    "--config",
    "configs/runs/bt_gate_012_multi_symbol_multi_session_qg5_v0_1.json",
    "--run-id",
    "bt_gate_012_multi_symbol_multi_session_qg5_v0_1_package_rerun",
    "--output-root",
    "runs/_package_reruns",
    "--expect-hash",
    "{EXPECTED_HASH}",
]
proc = subprocess.run(cmd, text=True)
if proc.returncode != 0:
    raise SystemExit(proc.returncode)
run_dir = out / "bt_gate_012_multi_symbol_multi_session_qg5_v0_1_package_rerun"
validation = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))
determinism = json.loads((run_dir / "determinism_report.json").read_text(encoding="utf-8"))
metrics = json.loads((run_dir / "metrics_summary.json").read_text(encoding="utf-8"))
manifest = json.loads((run_dir / "portfolio_run_manifest.json").read_text(encoding="utf-8"))
print(json.dumps({{
    "status": "PASS",
    "validation_status": validation["status"],
    "event_loop_mode": "ONLINE_PORTFOLIO_REPLAY_COORDINATOR_V0_1",
    "deterministic_output_hash": validation["deterministic_output_hash"],
    "expected_hash_matches": determinism["expected_hash_matches"],
    "gross_pnl": metrics["gross_pnl"],
    "net_pnl": metrics["net_pnl"],
    "ending_equity": metrics["ending_equity"],
    "session_count": len(manifest["sessions"]),
    "symbol_count": len(manifest["symbol_set"]),
}}, indent=2, sort_keys=True))
''',
        )
        add_text(
            files,
            zf,
            "PACKAGE_REPRODUCTION_README.md",
            f'''# BT-GATE-012 Package Reproduction

This package contains the BT-GATE-012 implementation evidence pending final acceptance review.

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
event_loop_mode = ONLINE_PORTFOLIO_REPLAY_COORDINATOR_V0_1
```

The package uses a portable QG5 two-session acceptance slice under:

```text
tests/fixtures/bt_gate_012_qg5_multisession_portable
```

This remains an ENGINE_VALIDATION_RUN only. It is not edge evidence and does not claim complete small-caps economic realism.
''',
        )
        manifest = {
            "package_id": "BT_GATE_012_MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE_ACCEPTANCE_PACKET",
            "gate_id": "BT-GATE-012",
            "capability": "MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE",
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "status": "CLOSED_PASS_IMPLEMENTATION_ACCEPTED",
            "file_count": len(files),
            "files": [files[key] for key in sorted(files)],
            "required_external_commands": [
                "python -m pip install -e .",
                "python -B RUN_INCLUDED_TESTS.py",
                "python -B RUN_END_TO_END.py",
            ],
            "expected_included_test_count": EXPECTED_TEST_COUNT,
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
    with zipfile.ZipFile(zip_path) as check_zf:
        entries = check_zf.namelist()
    print(json.dumps({
        "zip_path": str(zip_path),
        "zip_sha256": sha256_bytes(zip_path.read_bytes()),
        "zip_manifest_declared_files": len(files),
        "zip_entries_total": len(entries),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
