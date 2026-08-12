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


POLICY_ID = "sec_pit_owner_exclusion_stratified_selection_v0_2"
DOWNLOAD_POLICY_ID = "sec_pit_predownload_control_v0_2"
DOMESTIC_BASELINE_DISCOVERY_LIMIT = 4
PERIODIC_FORMS = frozenset({"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "6-K"})
FOREIGN_BASELINE_FORMS = frozenset({"20-F", "20-F/A"})
DOMESTIC_BASELINE_FORMS = frozenset({"DEF 14A", "10-K", "10-K/A"})
BASELINE_FORMS = FOREIGN_BASELINE_FORMS | DOMESTIC_BASELINE_FORMS
FORM_3_FORMS = frozenset({"3", "3/A"})
SCHEDULE_13D_FORMS = frozenset({"SC 13D", "SC 13D/A", "SCHEDULE 13D", "SCHEDULE 13D/A"})


def load_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    if config.get("cases"):
        return list(config["cases"])
    cases = json.loads(Path(config["cases_path"]).read_text(encoding="utf-8"))
    overrides = config.get("expected_security_class_gate_overrides", {})
    default = config.get("default_expected_security_class_gate", "PASS")
    return [
        {
            **case,
            "target_class_label": case.get("target_class_label", "COMMON_STOCK_CLASS_CANDIDATE"),
            "stratum": case.get("temporal_cohort", "STRATIFIED_100_CASE_GATE"),
            "expected_security_class_gate": overrides.get(case["ticker"], default),
        }
        for case in cases
    ]


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    temporary.replace(path)


def write_parquet(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_parquet(temporary, index=False)
    temporary.replace(path)


def has_role(value: Any, role: str) -> bool:
    return role in list(value)


def load_reusable_rows(paths: list[Path]) -> dict[str, dict[str, Any]]:
    by_url: dict[str, dict[str, Any]] = {}
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("status") != "FETCHED" or not row.get("url"):
                continue
            object_path = Path(str(row.get("object_path") or ""))
            if not object_path.is_file():
                continue
            with gzip.open(object_path, "rb") as handle:
                payload = handle.read()
            if hashlib.sha256(payload).hexdigest() != row.get("sha256"):
                raise ValueError(f"reusable object hash mismatch: {object_path}")
            if len(payload) != int(row.get("bytes") or -1):
                raise ValueError(f"reusable object byte mismatch: {object_path}")
            by_url[str(row["url"])] = {
                **row,
                "reuse_source_ledger": path.as_posix(),
                "reuse_verification": "OBJECT_EXISTS_GZIP_READ_SHA256_AND_BYTES_PASS",
            }
    return by_url


def select_case(
    rows: pd.DataFrame,
    lifecycle: pd.DataFrame,
    *,
    ticker: str,
    probe_end: str,
    baseline_as_of: str | None = None,
    full_interval: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    baseline_as_of = baseline_as_of or probe_end
    scoped = rows[
        rows["ticker"].eq(ticker)
        & rows["filing_date"].astype(str).le(probe_end)
    ].copy()
    ownership = scoped[
        scoped["roles_v0_2"].map(
            lambda value: has_role(value, "OWNERSHIP_EVIDENCE_CANDIDATE")
        )
    ].copy()
    causal_baselines = scoped[
        scoped["form"].isin(BASELINE_FORMS)
        & scoped["filing_date"].astype(str).le(baseline_as_of)
    ].sort_values(["filing_date", "accession_number"])
    baseline = causal_baselines.tail(1)
    baseline_date = str(baseline.iloc[0]["filing_date"]) if len(baseline) else None

    baseline_chain = causal_baselines.iloc[0:0]
    if len(baseline):
        latest_form = str(baseline.iloc[0]["form"])
        if latest_form in FOREIGN_BASELINE_FORMS:
            foreign = causal_baselines[
                causal_baselines["form"].isin(FOREIGN_BASELINE_FORMS)
            ]
            originals = foreign[foreign["form"].eq("20-F")]
            if len(originals):
                family_start = str(originals.iloc[-1]["filing_date"])
                baseline_chain = foreign[
                    foreign["filing_date"].astype(str).ge(family_start)
                ]
            else:
                baseline_chain = foreign.tail(1)
        else:
            target_interval = causal_baselines[
                causal_baselines["temporal_scope_state"].eq("TARGET_INTERVAL")
            ]
            prehistory = causal_baselines[
                ~causal_baselines["temporal_scope_state"].eq("TARGET_INTERVAL")
            ]
            discovery_pool = target_interval if len(target_interval) else prehistory
            baseline_chain = discovery_pool.tail(
                DOMESTIC_BASELINE_DISCOVERY_LIMIT
            )

    baseline_chain_start = (
        str(baseline_chain["filing_date"].astype(str).min())
        if len(baseline_chain)
        else baseline_date
    )
    event_window_start = baseline_date
    periodic_candidates = scoped[
        scoped["roles_v0_2"].map(
            lambda value: has_role(value, "OS_EVIDENCE_CANDIDATE")
        )
        & scoped["form"].isin(PERIODIC_FORMS)
    ].sort_values(["filing_date", "accession_number"])
    if full_interval and baseline_as_of:
        interval_periodic = periodic_candidates[
            periodic_candidates["filing_date"].astype(str).ge(baseline_as_of)
        ]
        predecessor_periodic = periodic_candidates[
            periodic_candidates["filing_date"].astype(str).lt(baseline_as_of)
        ].tail(1)
        periodic = pd.concat(
            [predecessor_periodic, interval_periodic], ignore_index=True
        ).drop_duplicates("accession_number")
    else:
        periodic = periodic_candidates.tail(2)
    if event_window_start:
        post_baseline = ownership[
            ownership["filing_date"].astype(str).ge(event_window_start)
        ]
        pre_form_3 = ownership[
            ownership["form"].isin(FORM_3_FORMS)
            & ownership["filing_date"].astype(str).lt(event_window_start)
        ]
        pre_schedule_13d = ownership[
            ownership["form"].isin(SCHEDULE_13D_FORMS)
            & ownership["filing_date"].astype(str).lt(event_window_start)
        ]
    else:
        post_baseline = ownership
        pre_form_3 = ownership.iloc[0:0]
        pre_schedule_13d = ownership.iloc[0:0]
    lifecycle_accessions = set(
        lifecycle.loc[
            lifecycle["ticker"].eq(ticker)
            & lifecycle["filing_date"].astype(str).le(probe_end),
            "accession_number",
        ].astype(str)
    )
    lifecycle_rows = scoped[
        scoped["accession_number"].astype(str).isin(lifecycle_accessions)
    ]
    selections = {
        "OWNERSHIP_BASELINE_LATEST": baseline,
        "OWNERSHIP_BASELINE_CANDIDATE_CHAIN": baseline_chain,
        "OS_PERIODIC_LATEST_TWO": periodic,
        "OWNERSHIP_FROM_BASELINE_TO_PROBE_END": post_baseline,
        "PRE_BASELINE_FORM_3_CLASS_COMPONENT": pre_form_3,
        "PRE_BASELINE_SCHEDULE_13D_AFFILIATE_COMPONENT": pre_schedule_13d,
        "GOVERNED_LIFECYCLE_EVIDENCE": lifecycle_rows,
    }
    reasons: dict[str, set[str]] = {}
    for reason, frame in selections.items():
        for accession in frame["accession_number"].astype(str):
            reasons.setdefault(accession, set()).add(reason)
    chosen = pd.concat(selections.values(), ignore_index=True).drop_duplicates(
        "accession_number"
    )
    chosen["stratified_selection_reasons"] = chosen["accession_number"].astype(str).map(
        lambda accession: sorted(reasons[accession])
    )
    chosen["stratified_selection_policy_id"] = POLICY_ID
    summary = {
        "baseline_accession": (
            str(baseline.iloc[0]["accession_number"]) if len(baseline) else None
        ),
        "baseline_form": str(baseline.iloc[0]["form"]) if len(baseline) else None,
        "baseline_filing_date": baseline_date,
        "baseline_as_of": baseline_as_of,
        "baseline_candidate_documents": len(baseline_chain),
        "baseline_candidate_accessions": baseline_chain[
            "accession_number"
        ].astype(str).tolist(),
        "baseline_candidate_chain_start": baseline_chain_start,
        "event_window_start": event_window_start,
        "adaptive_supplement_required_if_fallback_selected": True,
        "session_scope_mode": (
            "FULL_GOVERNED_INTERVAL" if full_interval else "BOUNDED_TAIL_PROBE"
        ),
        "selected_documents": len(chosen),
        "os_periodic_documents": len(periodic),
        "ownership_from_baseline_documents": len(post_baseline),
        "pre_baseline_form_3_documents": len(pre_form_3),
        "pre_baseline_schedule_13d_documents": len(pre_schedule_13d),
        "lifecycle_documents": len(lifecycle_rows),
        "filing_size_ceiling_bytes": int(chosen["filing_size_bytes"].fillna(0).sum()),
    }
    return chosen, summary


def execute(config_path: Path, probe_root: Path, authorize_download: bool) -> Path:
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    probe_root = probe_root.resolve()
    if probe_root.exists():
        raise FileExistsError(f"refusing to overwrite probe root: {probe_root}")
    probe_root.mkdir(parents=True)

    selection_path = Path(config["full_selection_plan"]).resolve()
    identity_path = Path(config["identity_ledger"]).resolve()
    lifecycle_path = Path(config["lifecycle_selection_plan"]).resolve()
    calendar_path = Path(config["market_calendar"]).resolve()
    selection = pd.read_parquet(selection_path)
    identity = pd.read_parquet(identity_path)
    lifecycle = pd.read_parquet(lifecycle_path)
    calendar = pd.read_parquet(calendar_path, columns=["session_date"])
    reusable_paths = [Path(value).resolve() for value in config["reuse_acquisition_ledgers"]]
    reusable_by_url = load_reusable_rows(reusable_paths)

    case_by_ticker = {str(row["ticker"]): row for row in load_cases(config)}
    selected_frames: list[pd.DataFrame] = []
    case_matrix: list[dict[str, Any]] = []
    for identity_row in identity.to_dict("records"):
        ticker = str(identity_row["ticker"])
        case = case_by_ticker.get(ticker)
        if case is None:
            continue
        if str(identity_row["cik"]) != str(case["cik"]):
            raise ValueError(f"CIK mismatch for {ticker}")
        if identity_row["security_class_gate"] != case["expected_security_class_gate"]:
            raise ValueError(f"security-class expectation mismatch for {ticker}")
        if identity_row["security_class_gate"] != "PASS":
            case_matrix.append({
                **case,
                "instrument_id": identity_row["instrument_id"],
                "security_class_id": identity_row.get("security_class_id"),
                "security_class_gate": identity_row["security_class_gate"],
                "probe_gate": "HALT_SECURITY_CLASS",
                "selected_documents": 0,
                "local_documents": 0,
                "missing_documents": 0,
            })
            continue
        probe_end = min(
            str(identity_row["market_presence_last_session"]),
            str(config["probe_end_ceiling"]),
        )
        market_start = str(identity_row["market_presence_first_session"])
        eligible_sessions = calendar[
            calendar["session_date"].astype(str).between(
                market_start, probe_end, inclusive="both"
            )
        ]["session_date"].astype(str)
        full_interval = config.get("probe_mode") == "FULL_GOVERNED_INTERVAL"
        sessions = (
            eligible_sessions.tolist()
            if full_interval
            else eligible_sessions.tail(int(config["probe_session_count"])).tolist()
        )
        if not sessions or (
            not full_interval and len(sessions) != int(config["probe_session_count"])
        ):
            raise ValueError(f"insufficient market sessions for {ticker}")
        chosen, summary = select_case(
            selection,
            lifecycle,
            ticker=ticker,
            probe_end=probe_end,
            baseline_as_of=sessions[0],
            full_interval=full_interval,
        )
        chosen["probe_first_session"] = sessions[0]
        chosen["probe_last_session"] = sessions[-1]
        chosen["instrument_id"] = identity_row["instrument_id"]
        chosen["security_class_id"] = identity_row.get("security_class_id")
        selected_frames.append(chosen)
        local_count = int(chosen["primary_document_url"].isin(reusable_by_url).sum())
        case_matrix.append({
            **case,
            "instrument_id": identity_row["instrument_id"],
            "security_class_id": identity_row.get("security_class_id"),
            "security_name": identity_row["security_name"],
            "governed_interval_state": identity_row["governed_interval_state"],
            "identity_gate": identity_row["identity_gate"],
            "security_class_gate": identity_row["security_class_gate"],
            "probe_gate": "ELIGIBLE",
            "probe_first_session": sessions[0],
            "probe_last_session": sessions[-1],
            **summary,
            "local_documents": local_count,
            "missing_documents": len(chosen) - local_count,
        })

    full = pd.concat(selected_frames, ignore_index=True).sort_values(
        ["ticker", "filing_date", "accession_number"]
    )
    if full.duplicated(["ticker", "accession_number"]).any():
        raise ValueError("duplicate ticker/accession in stratified selection")
    full_path = probe_root / "document_selection_plan_v0_1.parquet"
    write_parquet(full_path, full)

    selected_urls = set(full["primary_document_url"].astype(str))
    reusable_rows = [
        reusable_by_url[url]
        for url in sorted(selected_urls & set(reusable_by_url))
    ]
    reusable_path = probe_root / "reusable_acquisition_ledger.jsonl"
    write_jsonl(reusable_path, reusable_rows)
    missing = full[~full["primary_document_url"].isin(reusable_by_url)].copy()
    missing_path = probe_root / "missing_document_selection.parquet"
    write_parquet(missing_path, missing)

    gate_frame = pd.DataFrame(case_matrix)
    gate_path = probe_root / "gate_matrix.parquet"
    write_parquet(gate_path, gate_frame)
    write_json(probe_root / "case_matrix.json", case_matrix)

    acquisition_root = probe_root / "acquisition_probe"
    acquisition_root.mkdir()
    acquisition_selection_path = acquisition_root / "document_selection_plan_v0_2.parquet"
    write_parquet(acquisition_selection_path, missing)
    acquisition_gates = gate_frame.copy()
    acquisition_gates["primary_document_acquisition_state"] = acquisition_gates.apply(
        lambda row: (
            "ELIGIBLE_FOR_GOVERNED_REVIEW"
            if row["probe_gate"] == "ELIGIBLE" and int(row["missing_documents"]) > 0
            else (
                "LOCAL_EVIDENCE_COMPLETE"
                if row["probe_gate"] == "ELIGIBLE"
                else "HALT_SECURITY_CLASS"
            )
        ),
        axis=1,
    )
    write_parquet(acquisition_root / "gate_matrix.parquet", acquisition_gates)
    acquisition_manifest = {
        "run_id": probe_root.name,
        "status": "COMPLETE",
        "probe_gate": "PASS",
        "policy_id": DOWNLOAD_POLICY_ID,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "selection_plan_sha256": file_sha256(acquisition_selection_path),
        "selected_missing_documents": len(missing),
        "eligible_tickers": sorted(
            acquisition_gates.loc[
                acquisition_gates["primary_document_acquisition_state"].eq(
                    "ELIGIBLE_FOR_GOVERNED_REVIEW"
                ),
                "ticker",
            ].astype(str)
        ),
        "security_class_halts": sorted(
            acquisition_gates.loc[
                acquisition_gates["primary_document_acquisition_state"].eq(
                    "HALT_SECURITY_CLASS"
                ),
                "ticker",
            ].astype(str)
        ),
    }
    acquisition_manifest_path = acquisition_root / "final_manifest.json"
    write_json(acquisition_manifest_path, acquisition_manifest)
    if authorize_download:
        if config.get("status") != "HUMAN_AUTHORIZED_BOUNDED_PROBE":
            raise ValueError("config does not persist human authorization")
        allowed = acquisition_manifest["eligible_tickers"]
        write_json(
            acquisition_root / "download_authorization.json",
            {
                "status": "AUTHORIZED",
                "policy_id": DOWNLOAD_POLICY_ID,
                "authorization_scope": "MISSING_ROWS_ONLY_STRATIFIED_OWNER_EXCLUSION_PROBE",
                "authorized_at_utc": datetime.now(UTC).isoformat(),
                "human_authorization_record": config["human_authorization_record"],
                "probe_manifest_sha256": file_sha256(acquisition_manifest_path),
                "selection_plan_sha256": file_sha256(acquisition_selection_path),
                "allowed_tickers": allowed,
            },
        )

    final = {
        "run_id": probe_root.name,
        "status": "COMPLETE",
        "probe_gate": "PASS",
        "policy_id": POLICY_ID,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "config_path": config_path.as_posix(),
        "config_sha256": file_sha256(config_path),
        "source_hashes": {
            "full_selection_plan": file_sha256(selection_path),
            "identity_ledger": file_sha256(identity_path),
            "lifecycle_selection_plan": file_sha256(lifecycle_path),
            "market_calendar": file_sha256(calendar_path),
            **{
                f"reuse_ledger_{index}": file_sha256(path)
                for index, path in enumerate(reusable_paths, start=1)
            },
        },
        "output_hashes": {
            path.name: file_sha256(path)
            for path in (full_path, reusable_path, missing_path, gate_path)
        },
        "selected_documents": len(full),
        "reusable_documents": len(reusable_rows),
        "missing_documents": len(missing),
        "missing_filing_size_ceiling_bytes": int(
            missing["filing_size_bytes"].fillna(0).sum()
        ),
        "eligible_case_count": sum(row["probe_gate"] == "ELIGIBLE" for row in case_matrix),
        "security_class_halt_count": sum(
            row["probe_gate"] == "HALT_SECURITY_CLASS" for row in case_matrix
        ),
        "network_requests": 0,
        "download_authorization_created": authorize_download,
    }
    write_json(probe_root / "final_manifest.json", final)
    return probe_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--probe-root", type=Path, required=True)
    parser.add_argument("--authorize-download", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(args.config, args.probe_root, args.authorize_download))
