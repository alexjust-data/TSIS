#!/usr/bin/env python
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    temporary.replace(path)


def merge_ledgers(inputs: list[Path], output: Path) -> Path:
    inputs = [path.resolve() for path in inputs]
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    by_url: dict[str, dict[str, Any]] = {}
    duplicate_rows = 0
    for ledger in inputs:
        for line_number, line in enumerate(
            ledger.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("status") not in {"FETCHED", "FETCHED_REUSED"}:
                continue
            url = str(row.get("url") or "")
            if not url:
                raise ValueError(f"missing URL in {ledger}:{line_number}")
            object_path = Path(str(row.get("object_path") or ""))
            if not object_path.is_file():
                raise FileNotFoundError(object_path)
            with gzip.open(object_path, "rb") as handle:
                payload = handle.read()
            digest = hashlib.sha256(payload).hexdigest()
            if digest != row.get("sha256") or len(payload) != int(row.get("bytes") or -1):
                raise ValueError(f"object verification failed: {object_path}")
            prior = by_url.get(url)
            if prior:
                duplicate_rows += 1
                if (
                    prior.get("sha256") != row.get("sha256")
                    or int(prior.get("bytes") or -1) != int(row.get("bytes") or -1)
                ):
                    raise ValueError(f"conflicting immutable objects for URL: {url}")
                continue
            by_url[url] = {
                **row,
                "merged_from_ledger": ledger.as_posix(),
                "merge_verification": "GZIP_READ_SHA256_AND_BYTES_PASS",
            }
    rows = [by_url[url] for url in sorted(by_url)]
    _write_jsonl(output, rows)
    manifest = {
        "status": "COMPLETE",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "policy_id": "sec_pit_acquisition_ledger_merge_v0_1",
        "input_ledgers": [
            {"path": path.as_posix(), "sha256": sha256_file(path)}
            for path in inputs
        ],
        "admitted_rows": len(rows),
        "duplicate_equivalent_rows": duplicate_rows,
        "conflicting_rows": 0,
        "object_verification": "ALL_GZIP_READ_SHA256_AND_BYTES_PASS",
        "output_path": output.as_posix(),
        "output_sha256": sha256_file(output),
    }
    _write_json(output.with_suffix(".manifest.json"), manifest)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(merge_ledgers(args.input, args.output))
