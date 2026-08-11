from __future__ import annotations

import gzip
import hashlib
import json
import os
import tempfile
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_bytes(
        path, (json.dumps(value, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")
    )


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, sort_keys=True, default=str) + "\n")


class ContentAddressedStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def put(
        self,
        payload: bytes,
        suffix: str = ".bin",
        compress: bool = True,
        timings: dict[str, Any] | None = None,
    ) -> tuple[str, Path, int]:
        started = time.perf_counter()
        digest = sha256_bytes(payload)
        sha256_seconds = time.perf_counter() - started
        suffix = suffix if suffix.startswith(".") else f".{suffix}"
        extension = f"{suffix}.gz" if compress else suffix
        path = self.root / "sha256" / digest[:2] / digest[2:4] / f"{digest}{extension}"
        gzip_seconds = 0.0
        atomic_write_seconds = 0.0
        stored_bytes = path.stat().st_size if path.exists() else 0
        deduplicated = path.exists()
        if not path.exists():
            compression_started = time.perf_counter()
            stored = gzip.compress(payload, compresslevel=6, mtime=0) if compress else payload
            gzip_seconds = time.perf_counter() - compression_started if compress else 0.0
            write_started = time.perf_counter()
            atomic_write_bytes(path, stored)
            atomic_write_seconds = time.perf_counter() - write_started
            stored_bytes = len(stored)
        if timings is not None:
            timings.update(
                {
                    "sha256_seconds": sha256_seconds,
                    "gzip_seconds": gzip_seconds,
                    "atomic_write_seconds": atomic_write_seconds,
                    "stored_bytes": stored_bytes,
                    "deduplicated": deduplicated,
                }
            )
        return digest, path, len(payload)

    def read(self, path: Path) -> bytes:
        payload = path.read_bytes()
        return gzip.decompress(payload) if path.suffix == ".gz" else payload


def read_jsonl(paths: Iterable[Path]) -> Iterable[dict[str, Any]]:
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)
