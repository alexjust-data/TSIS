from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_ROOT = REPO_ROOT / "01_TSIS_DATA_FOUNDATION"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_parquet_tree(root: Path) -> dict[str, int | str]:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*.parquet") if path.is_file())
    total_bytes = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        file_hash = sha256_file(path)
        size = path.stat().st_size
        total_bytes += size
        digest.update(rel.encode("utf-8"))
        digest.update(str(size).encode("ascii"))
        digest.update(file_hash.encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def assert_relative_contract_paths_exist(manifest: dict[str, Any]) -> None:
    for name, relative_path in manifest.get("contracts", {}).items():
        path = MODULE_ROOT / relative_path
        assert path.exists(), f"Missing contract path for {name}: {path}"


def non_empty_string_mask(series):
    return series.notna() & series.astype(str).str.strip().ne("")


def write_json_artifact(directory: Path, name: str, payload: dict[str, Any]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path
