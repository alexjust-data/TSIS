#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def execute(
    *,
    config_path: Path,
    probe_root: Path,
    acquisition_ledger: Path,
    os_output_root: Path,
    os_run_template: str,
    owner_output_root: Path,
    output_directory_name: str = "owner_case_configs",
) -> Path:
    config_path = config_path.resolve()
    probe_root = probe_root.resolve()
    acquisition_ledger = acquisition_ledger.resolve()
    os_output_root = os_output_root.resolve()
    owner_output_root = owner_output_root.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    cases = json.loads((probe_root / "case_matrix.json").read_text(encoding="utf-8"))
    selection_path = probe_root / "document_selection_plan_v0_1.parquet"
    selection_hash = file_sha256(selection_path)
    output = probe_root / output_directory_name
    if output.exists():
        raise FileExistsError(output)
    output.mkdir()
    index: list[dict[str, Any]] = []
    for case in cases:
        if case["probe_gate"] != "ELIGIBLE":
            index.append({
                "ticker": case["ticker"],
                "status": case["probe_gate"],
                "config_path": None,
            })
            continue
        ticker = str(case["ticker"])
        os_run_id = os_run_template.format(ticker_lower=ticker.lower(), ticker=ticker)
        os_run_root = os_output_root / "runs" / os_run_id
        os_manifest_path = os_run_root / "final_manifest.json"
        if not os_manifest_path.is_file():
            raise FileNotFoundError(os_manifest_path)
        os_manifest = json.loads(os_manifest_path.read_text(encoding="utf-8"))
        if os_manifest.get("status") != "COMPLETE":
            raise ValueError(f"O/S run is not complete for {ticker}")
        daily_os = os_run_root / "daily_os_state.parquet"
        case_config = {
            "config_version": "sec_pit_owner_exclusion_stratified_case_v0_1",
            "ticker": ticker,
            "cik": str(case["cik"]),
            "instrument_id": case["instrument_id"],
            "security_class_id": case.get("security_class_id"),
            "issuer_name": case["issuer_name"],
            "target_class_label": case["target_class_label"],
            "governed_interval_state": case.get("governed_interval_state"),
            "first_observed_session": case["probe_first_session"],
            "last_observed_session": case["probe_last_session"],
            "session_scope_mode": case.get(
                "session_scope_mode", "BOUNDED_TAIL_PROBE"
            ),
            "selection_plan": selection_path.as_posix(),
            "selection_plan_sha256": selection_hash,
            "acquisition_ledger": acquisition_ledger.as_posix(),
            "metadata_inventory": config["metadata_run_template"].format(
                ticker_lower=ticker.lower()
            ),
            "daily_os_state": daily_os.as_posix(),
            "daily_os_manifest": os_manifest_path.as_posix(),
            "daily_os_manifest_sha256": file_sha256(os_manifest_path),
            "output_root": owner_output_root.as_posix(),
            "methodology_id": config["methodology_id"],
            "methodology_authorized": bool(config["methodology_authorized"]),
            "network_requests_authorized": False,
        }
        case_path = output / f"{ticker.lower()}.json"
        write_json(case_path, case_config)
        index.append({
            "ticker": ticker,
            "status": "READY",
            "config_path": case_path.as_posix(),
            "config_sha256": file_sha256(case_path),
            "os_run_id": os_run_id,
            "os_result": os_manifest.get("result"),
        })
    write_json(output / "index.json", index)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--probe-root", type=Path, required=True)
    parser.add_argument("--acquisition-ledger", type=Path, required=True)
    parser.add_argument("--os-output-root", type=Path, required=True)
    parser.add_argument("--os-run-template", required=True)
    parser.add_argument("--owner-output-root", type=Path, required=True)
    parser.add_argument(
        "--output-directory-name", default="owner_case_configs"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(
        config_path=args.config,
        probe_root=args.probe_root,
        acquisition_ledger=args.acquisition_ledger,
        os_output_root=args.os_output_root,
        os_run_template=args.os_run_template,
        owner_output_root=args.owner_output_root,
        output_directory_name=args.output_directory_name,
    ))
