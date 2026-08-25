from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


EXPECTED_KEYS = {
    "session_observables": ["ticker", "date"],
    "activation_labels": ["ticker", "date", "activation_label"],
    "episodes": ["episode_id"],
    "episode_trajectories": ["episode_id", "offset_session"],
    "episode_events": ["episode_id", "event_label"],
}


def certify_shard(shard_root: Path) -> dict:
    manifest = json.loads((shard_root / "shard_manifest.json").read_text(encoding="utf-8"))
    checks: dict[str, dict] = {}
    overall = manifest["status"] == "pass"
    for table_name, keys in EXPECTED_KEYS.items():
        files = sorted((shard_root / table_name).glob("*.parquet"))
        row_count = sum(pq.ParquetFile(path).metadata.num_rows for path in files)
        duplicate_count = 0
        null_key_count = 0
        if files:
            frames = [pd.read_parquet(path, columns=keys) for path in files]
            keys_frame = pd.concat(frames, ignore_index=True)
            duplicate_count = int(keys_frame.duplicated(keys).sum())
            null_key_count = int(keys_frame[keys].isna().any(axis=1).sum())
        expected_count = int(manifest["counts"].get(table_name, 0))
        passed = row_count == expected_count and duplicate_count == 0 and null_key_count == 0
        overall = overall and passed
        checks[table_name] = {
            "files": len(files),
            "rows": row_count,
            "expected_rows": expected_count,
            "duplicate_keys": duplicate_count,
            "null_keys": null_key_count,
            "status": "pass" if passed else "fail",
        }

    result = {
        "status": "pass" if overall else "fail",
        "shard_root": str(shard_root.resolve()),
        "source_manifest_status": manifest["status"],
        "checks": checks,
    }
    (shard_root / "certification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-root", type=Path, required=True)
    args = parser.parse_args()
    result = certify_shard(args.shard_root)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
