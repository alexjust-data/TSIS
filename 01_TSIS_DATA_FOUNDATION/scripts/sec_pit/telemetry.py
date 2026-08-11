from __future__ import annotations

import os
import shutil
import threading
import time
from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil

from sec_pit.storage import append_jsonl, atomic_write_json


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def percentile(values: Iterable[float], quantile: float) -> float | None:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def process_tree_metrics(root_pid: int) -> dict[str, float | int]:
    processes: dict[int, psutil.Process] = {}
    try:
        root = psutil.Process(root_pid)
        processes[root.pid] = root
        for child in root.children(recursive=True):
            processes[child.pid] = child
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    rss = private = read_bytes = write_bytes = cpu_seconds = 0.0
    for process in processes.values():
        try:
            memory = process.memory_info()
            rss += float(memory.rss)
            private += float(getattr(memory, "private", memory.rss))
            io = process.io_counters()
            read_bytes += float(io.read_bytes)
            write_bytes += float(io.write_bytes)
            cpu = process.cpu_times()
            cpu_seconds += float(cpu.user + cpu.system)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {
        "process_tree_count": len(processes),
        "rss_bytes": rss,
        "private_bytes": private,
        "io_read_bytes": read_bytes,
        "io_write_bytes": write_bytes,
        "cpu_seconds": cpu_seconds,
    }


def summarize_document_performance(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    timing_names = (
        "total_seconds",
        "throttle_seconds",
        "request_seconds",
        "retry_wait_seconds",
        "storage_seconds",
        "sha256_seconds",
        "gzip_seconds",
        "atomic_write_seconds",
    )
    totals = {name: sum(float(row.get(name) or 0.0) for row in rows) for name in timing_names}
    latencies = [
        float(row["total_seconds"]) for row in rows if row.get("total_seconds") is not None
    ]
    request_latencies = [
        float(value) for row in rows for value in (row.get("request_attempt_seconds") or [])
    ]
    fetched = sum(row.get("status") == "FETCHED" for row in rows)
    failed = len(rows) - fetched
    byte_count = sum(int(row.get("bytes") or 0) for row in rows)
    retries = sum(int(row.get("retry_count") or 0) for row in rows)
    http_429 = sum(int(row.get("http_429_count") or 0) for row in rows)
    measured = max(totals["total_seconds"], 1e-9)
    shares = {
        "throttle_and_retry": (totals["throttle_seconds"] + totals["retry_wait_seconds"])
        / measured,
        "http_request": totals["request_seconds"] / measured,
        "storage": totals["storage_seconds"] / measured,
        "hash_and_compression": (totals["sha256_seconds"] + totals["gzip_seconds"]) / measured,
        "atomic_write": totals["atomic_write_seconds"] / measured,
    }
    dominant = max(shares, key=shares.get) if rows else "insufficient_sample"
    if not rows:
        bottleneck = "INSUFFICIENT_SAMPLE"
    elif dominant in {"throttle_and_retry", "http_request"}:
        bottleneck = "SEC_RATE_LIMIT_OR_NETWORK"
    elif dominant in {"storage", "atomic_write"}:
        bottleneck = "STORAGE_IO"
    elif dominant == "hash_and_compression":
        bottleneck = "HASH_OR_COMPRESSION_CPU"
    else:
        bottleneck = "MIXED_OR_INSUFFICIENT_SAMPLE"
    return {
        "status": "RUNTIME_DIAGNOSTIC_NOT_INSTITUTIONAL_EVIDENCE",
        "document_count": len(rows),
        "fetched": fetched,
        "failed": failed,
        "bytes": byte_count,
        "retry_count": retries,
        "http_429_count": http_429,
        "timing_totals_seconds": {key: round(value, 9) for key, value in totals.items()},
        "timing_shares": {key: round(value, 6) for key, value in shares.items()},
        "document_latency_seconds": {
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
            "p99": percentile(latencies, 0.99),
        },
        "http_attempt_latency_seconds": {
            "p50": percentile(request_latencies, 0.50),
            "p95": percentile(request_latencies, 0.95),
            "p99": percentile(request_latencies, 0.99),
        },
        "provisional_bottleneck_candidate": bottleneck,
        "bottleneck_is_inference": True,
        "downstream_stage_telemetry": {
            "parse": "NOT_APPLICABLE_IN_PRIMARY_ACQUISITION_RUNNER",
            "extract": "NOT_APPLICABLE_IN_PRIMARY_ACQUISITION_RUNNER",
            "reconcile": "NOT_APPLICABLE_IN_PRIMARY_ACQUISITION_RUNNER",
            "parquet_write": "NOT_APPLICABLE_IN_PRIMARY_ACQUISITION_RUNNER",
        },
    }


class LiveResourceTelemetry:
    def __init__(
        self,
        *,
        run_root: Path,
        output_root: Path,
        run_id: str,
        interval_seconds: float,
        state_snapshot: Callable[[], Mapping[str, Any]],
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("telemetry interval must be positive")
        self.run_root = run_root
        self.output_root = output_root
        self.run_id = run_id
        self.interval_seconds = interval_seconds
        self.state_snapshot = state_snapshot
        self.started = time.monotonic()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._previous: tuple[float, dict[str, float | int]] | None = None
        self._peaks: dict[str, float] = {}
        self._last_sample: dict[str, Any] = {}
        self._write_lock = threading.Lock()
        psutil.cpu_percent(interval=None)

    @property
    def peaks(self) -> dict[str, float]:
        return dict(self._peaks)

    @property
    def last_sample(self) -> dict[str, Any]:
        return dict(self._last_sample)

    def start(self) -> None:
        self.sample()
        self._thread = threading.Thread(target=self._run, name="sec-pit-telemetry", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=max(2.0, self.interval_seconds + 1.0))
        self.sample()

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            try:
                self.sample()
            except Exception as exc:  # telemetry must not terminate acquisition
                append_jsonl(
                    self.run_root / "telemetry_errors.jsonl",
                    {
                        "observed_at_utc": utc_now(),
                        "error": f"{type(exc).__name__}: {exc}",
                    },
                )

    def sample(self) -> dict[str, Any]:
        now = time.monotonic()
        tree = process_tree_metrics(os.getpid())
        interval = max(now - self._previous[0], 1e-9) if self._previous else None
        previous = self._previous[1] if self._previous else None
        io_read_bps = (
            max(0.0, float(tree["io_read_bytes"]) - float(previous["io_read_bytes"])) / interval
            if previous and interval
            else None
        )
        io_write_bps = (
            max(0.0, float(tree["io_write_bytes"]) - float(previous["io_write_bytes"])) / interval
            if previous and interval
            else None
        )
        process_cpu = (
            max(0.0, float(tree["cpu_seconds"]) - float(previous["cpu_seconds"])) / interval * 100.0
            if previous and interval
            else None
        )
        self._previous = (now, tree)
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        output_free = shutil.disk_usage(self.output_root).free / (1024**3)
        runtime = dict(self.state_snapshot())
        heartbeat = {
            "run_id": self.run_id,
            "status": runtime.pop("status", "RUNNING"),
            "stage": runtime.pop("stage", "PRIMARY_ACQUISITION"),
            "observed_at_utc": utc_now(),
            "elapsed_seconds": now - self.started,
            "wrapper_pid": os.getpid(),
            "active_pid": os.getpid(),
            "wrapper_pid_alive": psutil.pid_exists(os.getpid()),
            "active_pid_alive": psutil.pid_exists(os.getpid()),
            "process_tree_count": tree["process_tree_count"],
            "active_worker_count": tree["process_tree_count"],
            "process_tree_rss_gib": float(tree["rss_bytes"]) / (1024**3),
            "process_tree_private_gib": float(tree["private_bytes"]) / (1024**3),
            "system_cpu_percent": psutil.cpu_percent(interval=None),
            "process_cpu_core_percent": process_cpu,
            "process_cpu_pct": process_cpu,
            "available_memory_gib": virtual.available / (1024**3),
            "memory_percent": virtual.percent,
            "pagefile_used_gib": swap.used / (1024**3),
            "io_read_Bps": io_read_bps,
            "io_write_Bps": io_write_bps,
            "io_read_bytes_per_sec": io_read_bps,
            "io_write_bytes_per_sec": io_write_bps,
            "output_root": self.output_root.as_posix(),
            "output_free_gib": output_free,
            "output_drive_free_gb": output_free,
            "log_path": (self.run_root / "run.log").as_posix(),
            **runtime,
        }
        for name in (
            "process_tree_rss_gib",
            "process_tree_private_gib",
            "system_cpu_percent",
            "process_cpu_core_percent",
            "pagefile_used_gib",
            "io_read_Bps",
            "io_write_Bps",
        ):
            value = heartbeat.get(name)
            if value is not None:
                self._peaks[name] = max(self._peaks.get(name, 0.0), float(value))
        with self._write_lock:
            atomic_write_json(self.run_root / "heartbeat_latest.json", heartbeat)
            append_jsonl(self.run_root / "heartbeat.jsonl", heartbeat)
            append_jsonl(
                self.run_root / "run.log",
                {
                    key: heartbeat.get(key)
                    for key in (
                        "observed_at_utc",
                        "status",
                        "stage",
                        "elapsed_seconds",
                        "current_index",
                        "total_count",
                        "current_item",
                        "documents_per_minute",
                        "mib_per_minute",
                        "http_p95_ms",
                        "retry_count",
                        "http_429_count",
                        "process_cpu_core_percent",
                        "process_tree_rss_gib",
                        "available_memory_gib",
                        "pagefile_used_gib",
                        "io_read_Bps",
                        "io_write_Bps",
                        "output_free_gib",
                    )
                },
            )
            self._last_sample = dict(heartbeat)
        return heartbeat
