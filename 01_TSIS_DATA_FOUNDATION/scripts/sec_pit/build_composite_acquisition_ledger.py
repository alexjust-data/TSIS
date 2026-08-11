#!/usr/bin/env python
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def verify_row(row: dict[str, Any]) -> None:
    object_path = Path(str(row.get("object_path") or ""))
    if not object_path.is_file():
        raise FileNotFoundError(object_path)
    with gzip.open(object_path, "rb") as handle:
        payload = handle.read()
    if hashlib.sha256(payload).hexdigest() != row.get("sha256"):
        raise ValueError(f"object hash mismatch: {object_path}")
    if len(payload) != int(row.get("bytes") or -1):
        raise ValueError(f"object byte mismatch: {object_path}")


def execute(
    *,
    selection_path: Path,
    source_ledgers: list[Path],
    output_path: Path,
) -> Path:
    selection_path = selection_path.resolve()
    source_ledgers = [path.resolve() for path in source_ledgers]
    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(output_path)
    selection = pd.read_parquet(selection_path)
    required_urls = set(selection["primary_document_url"].astype(str))
    by_url: dict[str, dict[str, Any]] = {}
    for source in source_ledgers:
        for row in read_jsonl(source):
            if row.get("status") not in {"FETCHED", "FETCHED_REUSED"}:
                continue
            url = str(row.get("url") or "")
            if url not in required_urls:
                continue
            verify_row(row)
            candidate = {
                **row,
                "status": "FETCHED_REUSED",
                "composite_source_ledger": source.as_posix(),
                "composite_verification": "GZIP_READ_SHA256_AND_BYTES_PASS",
            }
            previous = by_url.get(url)
            if previous and previous.get("sha256") != candidate.get("sha256"):
                raise ValueError(f"conflicting source hashes for {url}")
            by_url[url] = candidate
    missing = sorted(required_urls - set(by_url))
    if missing:
        raise ValueError(f"composite ledger missing {len(missing)} selected URLs")
    rows = [by_url[url] for url in sorted(required_urls)]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    temporary.replace(output_path)
    counts = selection.groupby("ticker").size().to_dict()
    manifest = {
        "status": "COMPLETE",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "selection_path": selection_path.as_posix(),
        "selection_sha256": file_sha256(selection_path),
        "source_ledgers": [
            {"path": path.as_posix(), "sha256": file_sha256(path)}
            for path in source_ledgers
        ],
        "output_path": output_path.as_posix(),
        "output_sha256": file_sha256(output_path),
        "selected_urls": len(required_urls),
        "composite_rows": len(rows),
        "duplicate_urls": len(rows) - len(set(row["url"] for row in rows)),
        "missing_urls": 0,
        "rows_by_ticker": counts,
        "object_verification": "PASS_ALL_ROWS",
    }
    write_json(output_path.with_suffix(".manifest.json"), manifest)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--source-ledger", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(
        selection_path=args.selection,
        source_ledgers=args.source_ledger,
        output_path=args.output,
    ))
