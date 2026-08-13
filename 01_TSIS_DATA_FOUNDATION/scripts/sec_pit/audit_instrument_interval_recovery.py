#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from sec_pit.ownership_identity import is_common_equity_title


BLOCKER = "INSTRUMENT_INTERVAL_CONFLICT"
ADMITTED_STATE = "ADMITTED_BY_NAME_CHANGE_CONTINUITY_OR_CLASS_CUSIP"
POLICY_ID = "sec_pit_instrument_interval_recovery_audit_v0_2"
BASELINE_FORMS = frozenset({"DEF 14A", "10-K", "10-K/A", "20-F", "20-F/A"})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_cik(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(10) if digits else None


def sec_archive_cik(source_url: Any) -> str | None:
    match = re.search(r"/Archives/edgar/data/(\d+)/", str(source_url or ""), re.I)
    return normalize_cik(match.group(1)) if match else None


def is_common_equity_observation(attributes: dict[str, Any]) -> bool:
    return is_common_equity_title(attributes.get("security_title"))


def classify_unresolved_document(
    *,
    target_cik: Any,
    issuer_cik: Any,
    form: Any,
    source_url: Any,
    common_equity_rows: int,
) -> str:
    target = normalize_cik(target_cik)
    issuer = normalize_cik(issuer_cik)
    if issuer and issuer != target:
        return "NON_TARGET_ISSUER_DOCUMENT_MUST_BE_REJECTED"
    if common_equity_rows == 0:
        return "NON_TARGET_SECURITY_DOCUMENT_MUST_BE_REJECTED"
    if issuer == target:
        return "TARGET_CIK_COMMON_EQUITY_CONTINUITY_CANDIDATE"
    if (
        issuer is None
        and str(form or "").upper() in BASELINE_FORMS
        and sec_archive_cik(source_url) == target
        and common_equity_rows > 0
    ):
        return "ISSUER_FILED_BASELINE_METADATA_CONTINUITY_CANDIDATE"
    return "TRUE_IDENTITY_EVIDENCE_GAP_OR_UNSUPPORTED_CLASS"


def classify_case(families: set[str]) -> str:
    gap = "TRUE_IDENTITY_EVIDENCE_GAP_OR_UNSUPPORTED_CLASS"
    if gap in families:
        return "MIXED_WITH_TRUE_IDENTITY_EVIDENCE_GAP" if len(families) > 1 else gap
    if families == {"NON_TARGET_ISSUER_DOCUMENT_MUST_BE_REJECTED"}:
        return "GENERIC_NON_TARGET_ISSUER_REJECTION"
    if families == {"NON_TARGET_SECURITY_DOCUMENT_MUST_BE_REJECTED"}:
        return "GENERIC_NON_TARGET_SECURITY_REJECTION"
    if families == {"TARGET_CIK_COMMON_EQUITY_CONTINUITY_CANDIDATE"}:
        return "GENERIC_TARGET_CIK_COMMON_EQUITY_CONTINUITY"
    if families == {"ISSUER_FILED_BASELINE_METADATA_CONTINUITY_CANDIDATE"}:
        return "GENERIC_ISSUER_FILED_BASELINE_METADATA_CONTINUITY"
    return "MIXED_RECOVERABLE_INTERVAL_FAMILIES"


def _attributes_by_accession(observations: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for accession, frame in observations.groupby("accession_number", dropna=False):
        result[str(accession)] = [
            json.loads(value) if isinstance(value, str) and value else {}
            for value in frame["attributes_json"]
        ]
    return result


def audit_case(run_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = run_root / "final_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config_path = Path(manifest["config_path"])
    config = json.loads(config_path.read_text(encoding="utf-8"))
    dispositions = pd.read_parquet(run_root / "ownership_document_disposition.parquet")
    observations = pd.read_parquet(run_root / "ownership_source_observations.parquet")
    attrs = _attributes_by_accession(observations)
    unresolved = dispositions[
        dispositions["temporal_scope_state"].eq("TARGET_INTERVAL")
        & dispositions["structured_position_rows"].gt(0)
        & ~dispositions["identity_admission_state"].eq(ADMITTED_STATE)
    ].copy()
    candidates: list[dict[str, Any]] = []
    families: Counter[str] = Counter()
    for row in unresolved.to_dict("records"):
        accession = str(row["accession_number"])
        common_rows = sum(
            is_common_equity_observation(item) for item in attrs.get(accession, [])
        )
        family = classify_unresolved_document(
            target_cik=config["cik"],
            issuer_cik=row.get("issuer_cik"),
            form=row.get("form"),
            source_url=row.get("source_url"),
            common_equity_rows=common_rows,
        )
        families[family] += 1
        candidates.append(
            {
                "ticker": config["ticker"],
                "accession_number": accession,
                "form": row.get("form"),
                "filing_date": row.get("filing_date"),
                "target_cik": normalize_cik(config["cik"]),
                "document_issuer_cik": normalize_cik(row.get("issuer_cik")),
                "document_issuer_name": row.get("issuer_name"),
                "archive_cik": sec_archive_cik(row.get("source_url")),
                "structured_position_rows": int(row["structured_position_rows"]),
                "common_equity_rows": int(common_rows),
                "interval_family": family,
                "source_url": row.get("source_url"),
                "source_sha256": row.get("source_sha256"),
            }
        )
    blockers = manifest["counts"]["ownership_coverage"]["methodology_blocker_codes"]
    other = sorted(set(blockers) - {BLOCKER})
    case = {
        "ticker": config["ticker"],
        "run_id": manifest["run_id"],
        "instrument_id": config["instrument_id"],
        "security_class_id": config.get("security_class_id"),
        "target_cik": normalize_cik(config["cik"]),
        "configured_issuer_name": config["issuer_name"],
        "first_observed_session": config["first_observed_session"],
        "last_observed_session": config["last_observed_session"],
        "governed_interval_state": config.get("governed_interval_state"),
        "unresolved_document_count": len(unresolved),
        "interval_families_json": json.dumps(families, sort_keys=True),
        "gate_classification": classify_case(set(families)),
        "other_blockers_json": json.dumps(other, sort_keys=True),
        "source_manifest_path": manifest_path.as_posix(),
        "source_manifest_sha256": sha256_file(manifest_path),
        "config_path": config_path.as_posix(),
        "config_sha256": sha256_file(config_path),
    }
    return case, candidates


def build_audit(runs_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for run_root in sorted(runs_root.glob("*__owner__*")):
        manifest_path = run_root / "final_manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        blockers = manifest["counts"]["ownership_coverage"]["methodology_blocker_codes"]
        if BLOCKER not in blockers:
            continue
        case, rows = audit_case(run_root)
        cases.append(case)
        candidates.extend(rows)
    case_frame = pd.DataFrame(cases).sort_values("ticker").reset_index(drop=True)
    candidate_frame = pd.DataFrame(candidates).sort_values(
        ["ticker", "filing_date", "accession_number"]
    ).reset_index(drop=True)
    checks = {
        "instrument_interval_case_count_is_25": len(case_frame) == 25,
        "all_cases_have_unresolved_documents": bool(case_frame["unresolved_document_count"].gt(0).all()),
        "all_cases_have_explicit_classification": bool(case_frame["gate_classification"].notna().all()),
        "all_source_manifests_hash_verified": bool(
            case_frame.apply(
                lambda row: sha256_file(Path(row["source_manifest_path"]))
                == row["source_manifest_sha256"], axis=1
            ).all()
        ),
        "all_configs_hash_verified": bool(
            case_frame.apply(
                lambda row: sha256_file(Path(row["config_path"])) == row["config_sha256"],
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
        "case_count": len(case_frame),
        "candidate_count": len(candidate_frame),
        "classification_counts": case_frame["gate_classification"].value_counts().sort_index().to_dict(),
        "document_family_counts": candidate_frame["interval_family"].value_counts().sort_index().to_dict(),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    return case_frame, candidate_frame, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)
    cases, candidates, manifest = build_audit(Path(args.runs_root))
    case_path = output / "instrument_interval_recovery_case_matrix.csv"
    candidate_path = output / "instrument_interval_recovery_candidate_matrix.csv"
    cases.to_csv(case_path, index=False)
    candidates.to_csv(candidate_path, index=False)
    manifest["output_files"] = {
        case_path.name: {"sha256": sha256_file(case_path), "rows": len(cases)},
        candidate_path.name: {"sha256": sha256_file(candidate_path), "rows": len(candidates)},
    }
    manifest_path = output / "final_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(manifest_path)
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
