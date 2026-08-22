"""Power-loss-safe storage primitives for Massive SEC response pages."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import socket
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import psutil

from sec_pit.massive_sec_models import PageCommit
from sec_pit.storage import ContentAddressedStore, atomic_write_bytes, atomic_write_json


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bytes_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def append_jsonl_durable(path: Path, value: Any) -> None:
    """Append one complete record and force it to stable storage."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def _process_matches(pid: int, expected_create_time: float | None) -> bool:
    try:
        process = psutil.Process(pid)
        if not process.is_running():
            return False
        if expected_create_time is None:
            return True
        return abs(process.create_time() - float(expected_create_time)) < 2.0
    except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
        return False


class DuplicateWriterError(RuntimeError):
    """Raised when a live or unverifiable writer already owns the output root."""


class OutputWriterLock:
    """Exclusive output-root writer lock with evidence-preserving stale takeover."""

    def __init__(self, output_root: Path, run_id: str) -> None:
        self.output_root = output_root.resolve()
        self.run_id = run_id
        self.path = self.output_root / "locks" / "massive_sec_acquisition.lock"
        self.host = socket.gethostname()
        self.pid = os.getpid()
        self.process_create_time = psutil.Process(self.pid).create_time()
        self.token = hashlib.sha256(
            f"{self.host}|{self.pid}|{self.process_create_time}|{run_id}".encode("utf-8")
        ).hexdigest()
        self.acquired = False

    def _payload(self) -> dict[str, Any]:
        return {
            "lock_version": "massive_sec_writer_lock_v0_1",
            "run_id": self.run_id,
            "host": self.host,
            "pid": self.pid,
            "process_create_time": self.process_create_time,
            "token": self.token,
            "acquired_at_utc": utc_now(),
        }

    def acquire(self, *, allow_stale_takeover: bool) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for _attempt in range(2):
            try:
                descriptor = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0),
                )
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(
                        (
                            json.dumps(self._payload(), indent=2, sort_keys=True) + "\n"
                        ).encode("utf-8")
                    )
                    handle.flush()
                    os.fsync(handle.fileno())
                self.acquired = True
                return
            except FileExistsError:
                try:
                    existing = json.loads(self.path.read_text(encoding="utf-8-sig"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise DuplicateWriterError(
                        f"writer lock exists but cannot be verified: {self.path}: {exc}"
                    ) from exc
                same_host = str(existing.get("host")) == self.host
                alive = same_host and _process_matches(
                    int(existing.get("pid") or -1), existing.get("process_create_time")
                )
                if alive:
                    raise DuplicateWriterError(
                        "live Massive SEC writer already owns output root: "
                        f"run_id={existing.get('run_id')} pid={existing.get('pid')}"
                    )
                if not allow_stale_takeover:
                    raise DuplicateWriterError(
                        "stale or foreign-host writer lock exists; only --resume may archive "
                        f"a same-host stale lock: {self.path}"
                    )
                if not same_host:
                    raise DuplicateWriterError(
                        "foreign-host lock cannot be taken over automatically"
                    )
                timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
                stale = self.path.with_name(
                    f"{self.path.name}.stale.{timestamp}.{existing.get('token', 'unknown')}.json"
                )
                os.replace(self.path, stale)
        raise DuplicateWriterError(f"could not acquire writer lock: {self.path}")

    def release(self) -> None:
        if not self.acquired:
            return
        try:
            existing = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            self.acquired = False
            return
        if existing.get("token") == self.token:
            self.path.unlink(missing_ok=True)
        self.acquired = False

    def __enter__(self) -> "OutputWriterLock":
        self.acquire(allow_stale_takeover=False)
        return self

    def __exit__(self, _exc_type: Any, _exc: Any, _traceback: Any) -> None:
        self.release()


class MassiveSecStorage:
    """Commit raw, normalized and receipt artifacts in a strict durable order."""

    def __init__(self, output_root: Path, run_id: str) -> None:
        self.output_root = output_root.resolve()
        self.run_id = run_id
        self.run_root = self.output_root / "runs" / run_id
        self.objects = ContentAddressedStore(self.output_root / "objects")
        self.ledger_path = self.run_root / "request_ledger.jsonl"
        self._ledger_lock = threading.Lock()

    def prepare_topology(self, dataset_directories: Iterable[str]) -> None:
        (self.output_root / "objects").mkdir(parents=True, exist_ok=True)
        (self.output_root / "locks").mkdir(parents=True, exist_ok=True)
        self.run_root.mkdir(parents=True, exist_ok=True)
        (self.run_root / "receipts").mkdir(parents=True, exist_ok=True)
        for directory in dataset_directories:
            (self.output_root / "datasets" / directory / "pages").mkdir(
                parents=True, exist_ok=True
            )

    def receipt_path(self, endpoint_id: str, work_id: str) -> Path:
        return self.run_root / "receipts" / endpoint_id / f"{work_id}.json"

    def normalized_path(self, dataset_directory: str, work_id: str) -> Path:
        return (
            self.output_root
            / "datasets"
            / dataset_directory
            / "pages"
            / work_id[:2]
            / f"{work_id}.jsonl.gz"
        )

    def load_receipt(self, endpoint_id: str, work_id: str) -> dict[str, Any] | None:
        path = self.receipt_path(endpoint_id, work_id)
        if not path.is_file():
            return None
        receipt = json.loads(path.read_text(encoding="utf-8-sig"))
        if receipt.get("status") != "COMMITTED" or receipt.get("work_id") != work_id:
            raise RuntimeError(f"invalid committed receipt: {path}")
        raw_path = Path(str(receipt["raw_object_path"]))
        normalized_path = Path(str(receipt["normalized_path"]))
        if not raw_path.is_file() or not normalized_path.is_file():
            raise RuntimeError(f"receipt references missing artifact: {path}")
        raw = self.objects.read(raw_path)
        if bytes_sha256(raw) != receipt.get("raw_sha256"):
            raise RuntimeError(f"raw CAS hash mismatch for receipt: {path}")
        normalized = gzip.decompress(normalized_path.read_bytes())
        if bytes_sha256(normalized) != receipt.get("normalized_sha256"):
            raise RuntimeError(f"normalized shard hash mismatch for receipt: {path}")
        return receipt

    def commit_page(
        self,
        *,
        endpoint_id: str,
        dataset_directory: str,
        work_id: str,
        target_cik: str | None,
        sanitized_url: str,
        request_id: str,
        retrieved_at_utc: str,
        response_bytes: bytes,
        results: list[dict[str, Any]],
        next_url: str | None,
        http_status: int,
        attempts: int,
        retry_count: int,
        http_429_count: int,
        elapsed_seconds: float,
    ) -> PageCommit:
        existing = self.load_receipt(endpoint_id, work_id)
        if existing is not None:
            return PageCommit(**{
                key: existing[key]
                for key in PageCommit.__dataclass_fields__
            })

        raw_digest, raw_path, raw_bytes = self.objects.put(
            response_bytes, suffix=".json", compress=True
        )
        normalized_rows = []
        for row_index, row in enumerate(results):
            normalized_rows.append(
                json.dumps(
                    {
                        **row,
                        "_massive_endpoint_id": endpoint_id,
                        "_massive_request_id": request_id,
                        "_massive_retrieved_at_utc": retrieved_at_utc,
                        "_massive_raw_sha256": raw_digest,
                        "_massive_target_cik": target_cik,
                        "_massive_row_index": row_index,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                    default=str,
                )
            )
        normalized_bytes = (
            ("\n".join(normalized_rows) + ("\n" if normalized_rows else "")).encode("utf-8")
        )
        normalized_digest = bytes_sha256(normalized_bytes)
        normalized_path = self.normalized_path(dataset_directory, work_id)
        compressed = gzip.compress(normalized_bytes, compresslevel=6, mtime=0)
        if normalized_path.exists():
            current = gzip.decompress(normalized_path.read_bytes())
            if bytes_sha256(current) != normalized_digest:
                raise FileExistsError(
                    f"normalized path collision with different content: {normalized_path}"
                )
        else:
            atomic_write_bytes(normalized_path, compressed)

        commit = PageCommit(
            endpoint_id=endpoint_id,
            work_id=work_id,
            target_cik=target_cik,
            sanitized_url=sanitized_url,
            request_id=request_id,
            retrieved_at_utc=retrieved_at_utc,
            raw_sha256=raw_digest,
            raw_object_path=raw_path.as_posix(),
            raw_bytes=raw_bytes,
            normalized_sha256=normalized_digest,
            normalized_path=normalized_path.as_posix(),
            result_count=len(results),
            next_url=next_url,
            http_status=http_status,
            attempts=attempts,
            retry_count=retry_count,
            http_429_count=http_429_count,
            elapsed_seconds=elapsed_seconds,
        )
        receipt = {"status": "COMMITTED", **commit.to_dict()}
        receipt_path = self.receipt_path(endpoint_id, work_id)
        atomic_write_json(receipt_path, receipt)
        with self._ledger_lock:
            append_jsonl_durable(self.ledger_path, receipt)
        return commit

    def iter_receipts(self) -> Iterable[dict[str, Any]]:
        for path in sorted((self.run_root / "receipts").glob("*/*.json")):
            yield json.loads(path.read_text(encoding="utf-8-sig"))

    def rebuild_request_ledgers(self) -> dict[str, Any]:
        receipts = sorted(
            self.iter_receipts(), key=lambda row: (row["endpoint_id"], row["work_id"])
        )
        jsonl_payload = b"".join(
            (
                json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) + "\n"
            ).encode("utf-8")
            for row in receipts
        )
        atomic_write_bytes(self.ledger_path, jsonl_payload)
        parquet_path = self.run_root / "request_ledger.parquet"
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{parquet_path.name}.", suffix=".tmp", dir=parquet_path.parent
        )
        os.close(descriptor)
        try:
            pd.DataFrame(receipts).to_parquet(temp_name, index=False)
            with open(temp_name, "rb") as handle:
                os.fsync(handle.fileno())
            os.replace(temp_name, parquet_path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        return {
            "receipt_count": len(receipts),
            "request_ledger_jsonl": self.ledger_path.as_posix(),
            "request_ledger_parquet": parquet_path.as_posix(),
            "request_ledger_parquet_sha256": file_sha256(parquet_path),
        }
