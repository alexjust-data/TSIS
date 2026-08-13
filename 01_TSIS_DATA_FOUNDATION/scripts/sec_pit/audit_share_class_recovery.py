#!/usr/bin/env python
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from bs4 import BeautifulSoup


SHARE_CLASS_BLOCKER = "SHARE_CLASS_ALLOCATION_UNRESOLVED"
POLICY_ID = "sec_pit_share_class_recovery_audit_v0_1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_list(value: Iterable[str]) -> str:
    return json.dumps(sorted(set(value)), separators=(",", ":"))


def _attributes(frame: pd.DataFrame) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for value in frame.get("attributes_json", pd.Series(dtype="object")):
        result.append(json.loads(value) if isinstance(value, str) and value else {})
    return result


def _target_class_family(label: str) -> str:
    key = label.casefold()
    if label == "COMMON_STOCK_CLASS_CANDIDATE":
        return "COMMON_STOCK_CLASS_CANDIDATE"
    if "class a" in key and "ordinary" in key:
        return "CLASS_A_ORDINARY"
    if "class a" in key and "common" in key:
        return "CLASS_A_COMMON"
    if "class b" in key and "ordinary" in key:
        return "CLASS_B_ORDINARY"
    if "class b" in key and "common" in key:
        return "CLASS_B_COMMON"
    if "common" in key or "ordinary" in key:
        return "UNNUMBERED_COMMON_OR_ORDINARY"
    return "UNSUPPORTED_TARGET_CLASS_LABEL"


def _document_signals(text: str) -> dict[str, bool]:
    normalized = re.sub(r"\s+", " ", text)
    explicit_columns = bool(
        re.search(
            r"shares(?:\s+of\s+common\s+stock)?\s+beneficially\s+owned"
            r".{0,700}?shares\s+acquirable\s+upon\s+exercise",
            normalized,
            re.I,
        )
        or re.search(
            r"number\s+of\s+shares\s+beneficially\s+(?:held|owned)"
            r".{0,700}?number\s+of\s+shares\s+issuable\s+upon\s+exercise",
            normalized,
            re.I,
        )
    )
    component_decomposition = bool(
        re.search(
            r"(?:consists?\s+of|includes?)\s+[0-9][0-9,]*\s+shares?"
            r".{0,350}?(?:options?|warrants?|issuable|acquirable)",
            normalized,
            re.I,
        )
        or re.search(
            r"shares?\s+owned\s+include\s+[0-9][0-9,]*\s+shares?"
            r".{0,180}?(?:options?|warrants?)",
            normalized,
            re.I,
        )
    )
    option_or_acquirable = bool(
        re.search(
            r"(?:issuable|acquirable|exercisable).{0,120}?(?:options?|warrants?)|"
            r"(?:options?|warrants?).{0,120}?(?:issuable|acquirable|exercisable)",
            normalized,
            re.I,
        )
    )
    return {
        "explicit_current_acquirable_columns": explicit_columns,
        "numeric_component_decomposition": component_decomposition,
        "option_or_acquirable_language": option_or_acquirable,
        "document_mentions_class_a_and_b": bool(
            re.search(r"\bClass\s+A\b", normalized, re.I)
            and re.search(r"\bClass\s+B\b", normalized, re.I)
        ),
    }


def derive_workstreams(
    *,
    target_class_label: str,
    ownership_states: Counter[str],
    supported_single_rows: int,
    baseline_states: set[str],
    document_signals: dict[str, bool],
) -> list[str]:
    streams: list[str] = []
    family = _target_class_family(target_class_label)
    if document_signals.get("explicit_current_acquirable_columns"):
        streams.append("EXPLICIT_CURRENT_ACQUIRABLE_COLUMN_PARSER")
    if (
        family in {"CLASS_A_COMMON", "CLASS_B_COMMON"}
        and supported_single_rows > 0
        and ownership_states.get("MULTI_CLASS_ALLOCATION_REQUIRED", 0) == 0
        and not document_signals.get("document_mentions_class_a_and_b")
    ):
        streams.append("SINGLE_TABLE_TO_NUMBERED_TARGET_CLASS_BRIDGE")
    if (
        ownership_states.get("CURRENTLY_ISSUED_COMPONENT_UNRESOLVED", 0) > 0
        and document_signals.get("numeric_component_decomposition")
    ):
        streams.append("NUMERIC_FOOTNOTE_COMPONENT_DECOMPOSITION")
    if (
        ownership_states.get("MULTI_CLASS_ALLOCATION_REQUIRED", 0) > 0
        or (
            family in {"CLASS_A_COMMON", "CLASS_B_COMMON"}
            and document_signals.get("document_mentions_class_a_and_b")
        )
    ):
        streams.append("EXPLICIT_MULTI_CLASS_COMPONENT_EVIDENCE")
    if any("MEASUREMENT_DATE_UNRESOLVED" in value for value in baseline_states):
        streams.append("OWNERSHIP_MEASUREMENT_DATE_RECOVERY")
    if "OWNERSHIP_TABLE_NO_MANAGEMENT_BASELINE" in baseline_states:
        streams.append("MANAGEMENT_BASELINE_EXTRACTION")
    if not streams:
        streams.append("TRUE_EVIDENCE_GAP_OR_CORRECT_FAIL_CLOSED_REVIEW")
    return sorted(set(streams))


def _read_object_text(object_path: str) -> str:
    path = Path(object_path)
    payload = gzip.open(path, "rb").read() if path.suffix == ".gz" else path.read_bytes()
    return " ".join(BeautifulSoup(payload, "html.parser").stripped_strings)


def _load_ledger(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {str(row["url"]): row for row in rows}


def audit_case(
    run_root: Path,
    *,
    acquisition_by_url: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = run_root / "final_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    coverage = manifest["counts"]["ownership_coverage"]
    blockers = list(coverage["methodology_blocker_codes"])
    baseline = pd.read_parquet(run_root / "ownership_baseline_resolution.parquet")
    observations = pd.read_parquet(run_root / "ownership_source_observations.parquet")
    disposition = pd.read_parquet(run_root / "ownership_document_disposition.parquet")
    disposition_by_accession = {
        str(row["accession_number"]): row for row in disposition.to_dict("records")
    }
    attrs_by_accession: dict[str, list[dict[str, Any]]] = {}
    for accession, frame in observations.groupby("accession_number", dropna=False):
        attrs_by_accession[str(accession)] = _attributes(frame)

    candidate_rows: list[dict[str, Any]] = []
    aggregate_states: Counter[str] = Counter()
    supported_single_rows = 0
    all_signals: Counter[str] = Counter()
    for row in baseline.to_dict("records"):
        accession = str(row["accession_number"])
        attrs = attrs_by_accession.get(accession, [])
        states = Counter(str(item.get("ownership_component_state")) for item in attrs)
        bases = Counter(str(item.get("table_class_basis")) for item in attrs)
        aggregate_states.update(states)
        supported = sum(
            item.get("supported_issued_common_shares") is not None
            and item.get("table_class_basis") == "SINGLE_OR_UNSPECIFIED"
            for item in attrs
        )
        supported_single_rows += supported
        source = disposition_by_accession.get(accession, {})
        signals = {
            "explicit_current_acquirable_columns": False,
            "numeric_component_decomposition": False,
            "option_or_acquirable_language": False,
            "document_mentions_class_a_and_b": False,
        }
        ledger_row = acquisition_by_url.get(str(source.get("source_url") or ""))
        if ledger_row and ledger_row.get("object_path"):
            signals = _document_signals(_read_object_text(str(ledger_row["object_path"])))
        all_signals.update(key for key, value in signals.items() if value)
        candidate_rows.append(
            {
                "ticker": manifest["ticker"],
                "run_id": manifest["run_id"],
                "accession_number": accession,
                "form": row["form"],
                "filing_date": row["filing_date"],
                "identity_admitted": bool(row["identity_admitted"]),
                "ownership_table_state": row["ownership_table_state"],
                "structured_position_rows": int(row["structured_position_rows"]),
                "class_allocation_complete": bool(row["class_allocation_complete"]),
                "selected_as_opening_baseline": bool(row["selected_as_opening_baseline"]),
                "supported_single_rows": int(supported),
                "ownership_component_states_json": json.dumps(states, sort_keys=True),
                "table_class_bases_json": json.dumps(bases, sort_keys=True),
                "document_signals_json": json.dumps(signals, sort_keys=True),
                "source_url": source.get("source_url"),
                "source_sha256": source.get("source_sha256"),
            }
        )

    baseline_states = set(baseline["ownership_table_state"].astype(str))
    document_signals = {
        key: all_signals[key] > 0
        for key in (
            "explicit_current_acquirable_columns",
            "numeric_component_decomposition",
            "option_or_acquirable_language",
            "document_mentions_class_a_and_b",
        )
    }
    streams = derive_workstreams(
        target_class_label=str(manifest["target_class_label"]),
        ownership_states=aggregate_states,
        supported_single_rows=supported_single_rows,
        baseline_states=baseline_states,
        document_signals=document_signals,
    )
    other_blockers = sorted(set(blockers) - {SHARE_CLASS_BLOCKER})
    os_daily = pd.read_parquet(Path(manifest["daily_os_state_path"]))
    float_daily = pd.read_parquet(run_root / "daily_float_state.parquet")
    direct = not other_blockers
    if not direct:
        classification = "MIXED_BLOCKERS"
    elif "EXPLICIT_CURRENT_ACQUIRABLE_COLUMN_PARSER" in streams:
        classification = "GENERIC_EXPLICIT_COLUMN_RECOVERY_CANDIDATE"
    elif (
        "SINGLE_TABLE_TO_NUMBERED_TARGET_CLASS_BRIDGE" in streams
        and "EXPLICIT_MULTI_CLASS_COMPONENT_EVIDENCE" not in streams
    ):
        classification = "GENERIC_SINGLE_TABLE_CLASS_BRIDGE_CANDIDATE"
    elif "NUMERIC_FOOTNOTE_COMPONENT_DECOMPOSITION" in streams:
        classification = "GENERIC_FOOTNOTE_COMPONENT_RECOVERY_CANDIDATE"
    elif "EXPLICIT_MULTI_CLASS_COMPONENT_EVIDENCE" in streams:
        classification = "TRUE_MULTI_CLASS_EVIDENCE_REQUIRED"
    else:
        classification = "TRUE_EVIDENCE_GAP_OR_CORRECT_FAIL_CLOSED_REVIEW"
    case = {
        "ticker": manifest["ticker"],
        "run_id": manifest["run_id"],
        "instrument_id": manifest["instrument_id"],
        "security_class_id": manifest.get("security_class_id"),
        "target_class_label": manifest["target_class_label"],
        "target_class_family": _target_class_family(str(manifest["target_class_label"])),
        "blockers_json": _json_list(blockers),
        "other_blockers_json": _json_list(other_blockers),
        "direct_recovery_candidate": direct,
        "os_rows": len(os_daily),
        "os_nonnull_rows": int(os_daily["shares_outstanding_estimate_as_known"].notna().sum()),
        "os_complete": bool(os_daily["shares_outstanding_estimate_as_known"].notna().all()),
        "float_rows": len(float_daily),
        "float_nonnull_rows": int(float_daily["float_owner_exclusion_estimate_as_known"].notna().sum()),
        "float_complete": bool(float_daily["float_owner_exclusion_estimate_as_known"].notna().all()),
        "baseline_candidates": len(baseline),
        "content_complete_candidates": int(baseline["baseline_content_complete_candidate"].sum()),
        "class_incomplete_candidates": int((~baseline["class_allocation_complete"]).sum()),
        "selected_causal_baseline_count": int(coverage["selected_causal_baseline_count"]),
        "supported_single_rows": int(supported_single_rows),
        "ownership_component_states_json": json.dumps(aggregate_states, sort_keys=True),
        "document_signals_json": json.dumps(document_signals, sort_keys=True),
        "recovery_workstreams_json": _json_list(streams),
        "gate_classification": classification,
        "source_manifest_path": manifest_path.as_posix(),
        "source_manifest_sha256": sha256_file(manifest_path),
        "config_path": manifest["config_path"],
        "config_sha256": manifest["config_sha256"],
    }
    return case, candidate_rows


def build_audit(
    runs_root: Path,
    *,
    acquisition_ledger: Path | None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    acquisition_by_url = _load_ledger(acquisition_ledger)
    cases: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for run_root in sorted(runs_root.glob("*__owner__*")):
        manifest_path = run_root / "final_manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        blockers = manifest["counts"]["ownership_coverage"]["methodology_blocker_codes"]
        if SHARE_CLASS_BLOCKER not in blockers:
            continue
        case, rows = audit_case(run_root, acquisition_by_url=acquisition_by_url)
        cases.append(case)
        candidates.extend(rows)
    case_frame = pd.DataFrame(cases).sort_values("ticker").reset_index(drop=True)
    candidate_frame = pd.DataFrame(candidates).sort_values(
        ["ticker", "filing_date", "accession_number"], ascending=[True, False, False]
    ).reset_index(drop=True)
    checks = {
        "share_class_case_count_is_28": len(case_frame) == 28,
        "all_cases_have_zero_selected_baselines": bool(
            case_frame["selected_causal_baseline_count"].eq(0).all()
        ),
        "all_cases_have_explicit_classification": bool(
            case_frame["gate_classification"].notna().all()
        ),
        "all_source_manifests_hash_verified": bool(
            case_frame.apply(
                lambda row: sha256_file(Path(row["source_manifest_path"]))
                == row["source_manifest_sha256"],
                axis=1,
            ).all()
        ),
    }
    manifest = {
        "policy_id": POLICY_ID,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "mode": "NO_NETWORK_IMMUTABLE_RUN_AUDIT",
        "network_requests": 0,
        "runs_root": runs_root.as_posix(),
        "acquisition_ledger_path": acquisition_ledger.as_posix() if acquisition_ledger else None,
        "acquisition_ledger_sha256": sha256_file(acquisition_ledger) if acquisition_ledger else None,
        "case_count": len(case_frame),
        "candidate_count": len(candidate_frame),
        "direct_recovery_candidate_count": int(case_frame["direct_recovery_candidate"].sum()),
        "os_complete_case_count": int(case_frame["os_complete"].sum()),
        "classification_counts": case_frame["gate_classification"].value_counts().sort_index().to_dict(),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    return case_frame, candidate_frame, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", required=True)
    parser.add_argument("--acquisition-ledger")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cases, candidates, manifest = build_audit(
        Path(args.runs_root),
        acquisition_ledger=Path(args.acquisition_ledger) if args.acquisition_ledger else None,
    )
    case_path = output_dir / "share_class_recovery_case_matrix.csv"
    candidate_path = output_dir / "share_class_recovery_candidate_matrix.csv"
    cases.to_csv(case_path, index=False)
    candidates.to_csv(candidate_path, index=False)
    manifest["output_files"] = {
        case_path.name: {"sha256": sha256_file(case_path), "rows": len(cases)},
        candidate_path.name: {"sha256": sha256_file(candidate_path), "rows": len(candidates)},
    }
    manifest_path = output_dir / "final_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(manifest_path)
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
