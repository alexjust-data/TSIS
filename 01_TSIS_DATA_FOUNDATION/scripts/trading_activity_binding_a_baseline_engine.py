"""Explicit Stage-8 engine registry with reproducible source/binary fingerprints."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from trading_activity_binding_a_baseline_cpp import (
    materialize_baseline_and_surprise_cpp,
    native_module_path,
)
from trading_activity_binding_a_multisession_engine import (
    materialize_baseline_and_surprise,
)

ENGINE_CONTRACT_VERSION = "trading_activity_stage8_engine_binding_v0_1"
PYTHON_ENGINE_ID = "trading_activity_stage8_python_reference_v0_2"
CPP_ENGINE_ID = "trading_activity_stage8_cpp_native_candidate_v0_1"

Materializer = Callable[..., pd.DataFrame]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _component(role: str, path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Stage-8 engine component missing: {resolved}")
    return {
        "role": role,
        "path": str(resolved),
        "sha256": _sha256_file(resolved),
        "bytes": resolved.stat().st_size,
    }


@dataclass(frozen=True)
class Stage8EngineBinding:
    engine_name: str
    engine_id: str
    materialize: Materializer
    manifest: dict[str, Any]


def _manifest(engine_name: str, engine_id: str, components: list[dict[str, Any]]) -> dict[str, Any]:
    fingerprint_material = {
        "contract_version": ENGINE_CONTRACT_VERSION,
        "engine_name": engine_name,
        "engine_id": engine_id,
        "semantic_oracle_engine_id": PYTHON_ENGINE_ID,
        "components": [
            {"role": item["role"], "sha256": item["sha256"]}
            for item in components
        ],
    }
    serialized = json.dumps(
        fingerprint_material, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        **fingerprint_material,
        "components": components,
        "engine_fingerprint_sha256": hashlib.sha256(serialized).hexdigest(),
    }


def resolve_stage8_engine(engine_name: str) -> Stage8EngineBinding:
    normalized = engine_name.strip().lower()
    scripts = Path(__file__).resolve().parent
    registry = scripts / "trading_activity_binding_a_baseline_engine.py"
    if normalized == "python":
        components = [
            _component("engine_registry", registry),
            _component(
                "stage8_runner",
                scripts / "run_trading_activity_binding_a_multisession_pilot.py",
            ),
            _component(
                "python_semantic_oracle",
                scripts / "trading_activity_binding_a_multisession_engine.py",
            ),
        ]
        return Stage8EngineBinding(
            engine_name=normalized,
            engine_id=PYTHON_ENGINE_ID,
            materialize=materialize_baseline_and_surprise,
            manifest=_manifest(normalized, PYTHON_ENGINE_ID, components),
        )
    if normalized == "cpp":
        components = [
            _component("engine_registry", registry),
            _component(
                "stage8_runner",
                scripts / "run_trading_activity_binding_a_multisession_pilot.py",
            ),
            _component(
                "python_cpp_adapter",
                scripts / "trading_activity_binding_a_baseline_cpp.py",
            ),
            _component(
                "cpp_source",
                scripts.parent
                / "native"
                / "trading_activity"
                / "tsis_baseline_native_cpp.cpp",
            ),
            _component("native_binary", native_module_path()),
        ]
        return Stage8EngineBinding(
            engine_name=normalized,
            engine_id=CPP_ENGINE_ID,
            materialize=materialize_baseline_and_surprise_cpp,
            manifest=_manifest(normalized, CPP_ENGINE_ID, components),
        )
    raise ValueError(f"Unsupported Stage-8 engine: {engine_name!r}")
