"""Create a runnable FULL replay plan only after an exact four-shard probe PASS."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: Any) -> None:
    if path.exists():
        raise FileExistsError(f"Authorization output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-preparation", required=True, type=Path)
    parser.add_argument("--probe-final", required=True, type=Path)
    parser.add_argument("--human-authorization", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.human_authorization.startswith("AUTHORIZED_BY_"):
        raise ValueError("Human authorization must start with AUTHORIZED_BY_")
    preparation = read_json(args.full_preparation.resolve())
    if preparation.get("mode") != "FULL" or preparation.get("artifact_status") != "FULL_SCOPE_PREPARED_NOT_AUTHORIZED":
        raise ValueError("Input is not a non-runnable FULL preparation")
    probe_final_path = args.probe_final.resolve()
    probe = read_json(probe_final_path)
    required_probe = {
        "status": "PASS", "mode": "PROBE", "blocks_completed": 4,
        "sessions_completed": 8, "mismatch_count": 0, "exact_match": True,
        "null_mask_exact": True,
    }
    for key, expected in required_probe.items():
        if probe.get(key) != expected:
            raise ValueError(f"Probe gate mismatch: {key}={probe.get(key)!r} expected {expected!r}")
    probe_pre_path = probe_final_path.parent / "pre_manifest.json"
    probe_pre = read_json(probe_pre_path)
    probe_plan_path = Path(probe_pre["plan_path"])
    if sha256_file(probe_plan_path) != probe["plan_sha256"]:
        raise ValueError("Probe plan hash mismatch")
    probe_plan = read_json(probe_plan_path)
    if probe_plan.get("source_reference_manifest_sha256") != preparation.get("source_reference_manifest_sha256"):
        raise ValueError("Probe and FULL preparation do not bind the same source reference manifest")
    for key in ("runner_sha256", "oracle_sha256", "specification_sha256"):
        if probe_plan.get(key) != preparation.get(key):
            raise ValueError(f"Probe and FULL preparation differ on {key}")
    if probe_plan.get("scope", {}).get("shard_block_counts") != {"0": 1, "1": 1, "2": 1, "3": 1}:
        raise ValueError("Probe did not cover exactly one block in every shard")
    authorized = {
        **preparation,
        "artifact_status": "PREREGISTERED_FULL_HUMAN_AUTHORIZED_AFTER_PROBE_PASS",
        "authorized_at_utc": datetime.now(UTC).isoformat(),
        "human_authorization": args.human_authorization,
        "probe_final_manifest": str(probe_final_path),
        "probe_final_manifest_sha256": sha256_file(probe_final_path),
        "probe_plan": str(probe_plan_path.resolve()),
        "probe_plan_sha256": sha256_file(probe_plan_path),
        "authorization_script": str(SCRIPT_PATH),
        "authorization_script_sha256": sha256_file(SCRIPT_PATH),
    }
    atomic_json(args.output.resolve(), authorized)
    print(json.dumps({
        "status": "FULL_AUTHORIZED_PLAN_CREATED",
        "output": str(args.output.resolve()),
        "output_sha256": sha256_file(args.output.resolve()),
        "human_authorization": args.human_authorization,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

