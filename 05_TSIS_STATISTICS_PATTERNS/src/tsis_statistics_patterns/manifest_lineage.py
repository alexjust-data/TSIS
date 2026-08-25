from __future__ import annotations

import hashlib
from pathlib import Path

import pyarrow.parquet as pq


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parquet_artifact(path: Path) -> dict:
    parquet = pq.ParquetFile(path)
    schema_text = parquet.schema_arrow.to_string(show_field_metadata=True)
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "rows": parquet.metadata.num_rows,
        "sha256": sha256_file(path),
        "schema_sha256": hashlib.sha256(schema_text.encode("utf-8")).hexdigest(),
        "schema": schema_text,
    }


def verify_artifacts(records: dict[str, dict]) -> dict:
    violations: dict[str, str] = {}
    for name, expected in records.items():
        path = Path(expected["path"])
        if not path.exists():
            violations[name] = "missing"
            continue
        observed = parquet_artifact(path)
        for field in ("bytes", "rows", "sha256", "schema_sha256"):
            if observed[field] != expected[field]:
                violations[name] = f"{field}_mismatch"
                break
    return {
        "status": "pass" if records and not violations else "fail",
        "violations": violations,
        "artifacts_checked": len(records),
    }
