"""Long-running-operation telemetry for Massive SEC acquisition."""

from __future__ import annotations

import json
import os
import shutil
import threading
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil

from sec_pit.massive_sec_storage import append_jsonl_durable
from sec_pit.storage import atomic_write_json
from sec_pit.telemetry import process_tree_metrics


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class MassiveSecTelemetry:
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
        self._write_lock = threading.Lock()
        self._previous: tuple[float, dict[str, float | int]] | None = None
        self._last_sample: dict[str, Any] = {}
        self._peaks: dict[str, float] = {}
        psutil.cpu_percent(interval=None)

    @property
    def last_sample(self) -> dict[str, Any]:
        return dict(self._last_sample)

    @property
    def peaks(self) -> dict[str, float]:
        return dict(self._peaks)

    def log_event(self, event: str, **fields: Any) -> None:
        parts = [utc_now(), f"event={event}"]
        for key, value in sorted(fields.items()):
            text = str(value).replace("\r", " ").replace("\n", " ")
            parts.append(f"{key}={text}")
        path = self.run_root / "acquisition.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._write_lock:
            with path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(" ".join(parts) + "\n")
                handle.flush()
                os.fsync(handle.fileno())

    def start(self) -> None:
        self.sample()
        self._thread = threading.Thread(
            target=self._run, name="massive-sec-telemetry", daemon=True
        )
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
            except Exception as exc:  # telemetry may degrade but must not kill acquisition
                append_jsonl_durable(
                    self.run_root / "telemetry_errors.jsonl",
                    {"observed_at_utc": utc_now(), "error": f"{type(exc).__name__}: {exc}"},
                )

    def sample(self) -> dict[str, Any]:
        now = time.monotonic()
        tree = process_tree_metrics(os.getpid())
        interval = max(now - self._previous[0], 1e-9) if self._previous else None
        previous = self._previous[1] if self._previous else None
        read_bps = (
            max(0.0, float(tree["io_read_bytes"]) - float(previous["io_read_bytes"]))
            / interval
            if previous and interval
            else None
        )
        write_bps = (
            max(0.0, float(tree["io_write_bytes"]) - float(previous["io_write_bytes"]))
            / interval
            if previous and interval
            else None
        )
        process_cpu = (
            max(0.0, float(tree["cpu_seconds"]) - float(previous["cpu_seconds"]))
            / interval
            * 100.0
            if previous and interval
            else None
        )
        self._previous = (now, tree)
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        runtime = dict(self.state_snapshot())
        heartbeat = {
            "run_id": self.run_id,
            "observed_at_utc": utc_now(),
            "status": runtime.pop("status", "RUNNING"),
            "stage": runtime.pop("stage", "MASSIVE_SEC_ACQUISITION"),
            "elapsed_seconds": now - self.started,
            "wrapper_pid": os.getpid(),
            "active_pid": os.getpid(),
            "wrapper_pid_alive": True,
            "active_pid_alive": True,
            "process_tree_count": tree["process_tree_count"],
            "process_cpu_core_percent": process_cpu,
            "process_tree_rss_gib": float(tree["rss_bytes"]) / (1024**3),
            "system_cpu_percent": psutil.cpu_percent(interval=None),
            "available_memory_gib": virtual.available / (1024**3),
            "pagefile_used_gib": swap.used / (1024**3),
            "io_read_Bps": read_bps,
            "io_write_Bps": write_bps,
            "output_free_gib": shutil.disk_usage(self.output_root).free / (1024**3),
            "log_path": (self.run_root / "acquisition.log").as_posix(),
            **runtime,
        }
        for field in (
            "process_cpu_core_percent",
            "process_tree_rss_gib",
            "system_cpu_percent",
            "pagefile_used_gib",
            "io_read_Bps",
            "io_write_Bps",
        ):
            if heartbeat.get(field) is not None:
                self._peaks[field] = max(
                    self._peaks.get(field, 0.0), float(heartbeat[field])
                )
        with self._write_lock:
            atomic_write_json(self.run_root / "heartbeat_latest.json", heartbeat)
            append_jsonl_durable(self.run_root / "heartbeat.jsonl", heartbeat)
            self._last_sample = dict(heartbeat)
        return heartbeat


def write_pid_manifest(run_root: Path, *, run_id: str, expected_alive: bool, stage: str) -> None:
    process = psutil.Process(os.getpid())
    path = run_root / "pid_manifest.json"
    started_at_utc = utc_now()
    if path.is_file():
        try:
            prior = json.loads(path.read_text(encoding="utf-8-sig"))
            started_at_utc = str(prior.get("started_at_utc") or started_at_utc)
        except (OSError, ValueError):
            pass
    observed_at_utc = utc_now()
    atomic_write_json(
        path,
        {
            "run_id": run_id,
            "wrapper_pid": os.getpid(),
            "process_name": process.name(),
            "process_create_time": process.create_time(),
            "started_at_utc": started_at_utc,
            "observed_at_utc": observed_at_utc,
            "ended_at_utc": None if expected_alive else observed_at_utc,
            "stage": stage,
            "expected_alive": expected_alive,
        },
    )
