from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parent
ROOT_TEST_RUNS_DIR = REPO_ROOT / "tests" / "test_runs"


class FixtureValidationError(ValueError):
    pass


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_utc(value: Any, field: str) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise FixtureValidationError(f"{field} must be an ISO UTC string or null")
    text = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise FixtureValidationError(f"{field} must be timezone-aware UTC")
    return parsed.astimezone(timezone.utc)


def resolve_path(path_value: str | Path, *, base: Path = REPO_ROOT) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    repo_relative = base / path
    if repo_relative.exists():
        return repo_relative
    module_relative = MODULE_ROOT / path
    if module_relative.exists():
        return module_relative
    return repo_relative


def ensure_test_run_output_dir(path: Path) -> Path:
    resolved = path.resolve()
    allowed_root = ROOT_TEST_RUNS_DIR.resolve()
    try:
        is_allowed = resolved.is_relative_to(allowed_root)
    except AttributeError:
        is_allowed = str(resolved).startswith(str(allowed_root) + "\\")
    if not is_allowed:
        raise FixtureValidationError(
            "deterministic fixture output must be written under "
            f"{ROOT_TEST_RUNS_DIR}"
        )
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def prohibited_prefixes(config: dict[str, Any]) -> list[str]:
    prefixes = config.get("prohibited_prefixes", [])
    if not isinstance(prefixes, list):
        raise FixtureValidationError("prohibited_prefixes must be a list")
    return [str(item).removesuffix("*") for item in prefixes]


def validate_common_config(config: dict[str, Any], dataset_id: str) -> None:
    if config.get("dataset_id") != dataset_id:
        raise FixtureValidationError(f"config dataset_id must be {dataset_id}")
    if config.get("mode") != "deterministic_fixture_only":
        raise FixtureValidationError("mode must be deterministic_fixture_only")
    if config.get("official_output_allowed") is not False:
        raise FixtureValidationError("official_output_allowed must be false")
    if not config.get("input_fixture"):
        raise FixtureValidationError("input_fixture is required")
    if not config.get("output_file"):
        raise FixtureValidationError("output_file is required")
    if not config.get("manifest_file"):
        raise FixtureValidationError("manifest_file is required")


def validate_no_prohibited_keys(row: dict[str, Any], prefixes: list[str]) -> None:
    for key in row:
        for prefix in prefixes:
            if key.startswith(prefix):
                raise FixtureValidationError(
                    f"prohibited state feature family detected: {key}"
                )


def validate_required_flags(row: dict[str, Any], required_flags: dict[str, Any]) -> None:
    for flag, expected in required_flags.items():
        if flag not in row:
            raise FixtureValidationError(f"missing required flag: {flag}")
        if row[flag] is not expected:
            raise FixtureValidationError(
                f"{flag} must be {expected!r}, got {row[flag]!r}"
            )


def build_deterministic_fixture_sample(
    *,
    dataset_id: str,
    config_path: Path,
    output_dir: Path,
    row_validator: Callable[[dict[str, Any], dict[str, Any]], None],
) -> dict[str, Any]:
    config = load_json(config_path)
    validate_common_config(config, dataset_id)

    fixture_path = resolve_path(config["input_fixture"])
    fixture = load_json(fixture_path)
    rows = fixture.get("rows")
    if not isinstance(rows, list) or not rows:
        raise FixtureValidationError("fixture must contain a non-empty rows list")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise FixtureValidationError(f"row {index} must be an object")
        row_validator(row, config)

    output_root = ensure_test_run_output_dir(output_dir)
    output_file = output_root / str(config["output_file"])
    manifest_file = output_root / str(config["manifest_file"])

    with output_file.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    manifest = {
        "dataset_id": dataset_id,
        "builder_version": config.get("builder_version"),
        "materialization_scope": config.get("materialization_scope"),
        "mode": config.get("mode"),
        "status": "deterministic_fixture_sample_only",
        "official_output_allowed": False,
        "official_output_materialized": False,
        "sample_output_written": True,
        "full_universe_claim": False,
        "rows": len(rows),
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "input_fixture": str(fixture_path),
        "input_fixture_sha256": sha256_file(fixture_path),
        "output_file": str(output_file),
        "manifest_file": str(manifest_file),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_file.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return manifest
