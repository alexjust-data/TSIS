from __future__ import annotations

import re
from typing import Any, Iterable

from sec_pit.extract import stable_id
from sec_pit.holders_v3 import build_holder_position_ledger_v0_9


_UNRESOLVED_STATES = {
    "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED",
    "RELEVANT_ISSUED_COMMON_COMPONENT_UNRESOLVED",
}
_ACCOUNT_RELATION = re.compile(
    r"(?:\bheld(?:\s+(?:beneficially|indirectly|of\s+record))?\s+by\b"
    r"|\bheld\s+in\s+the\s+name\s+of\b"
    r"|\bowned(?:\s+(?:directly|indirectly|beneficially))?\s+by\b"
    r"|\bbeneficially\s+owned\s+by\b"
    r"|\bindirectly\s+beneficially\s+owns?\b.+?\bthrough\b"
    r"|\brecord\s+holders?\b|\bdirect\s+beneficial\s+owner\b"
    r"|\bis\s+the\s+holder\s+of\b|\bpurchased\s+by\b"
    r"|\bwhich\s+hold\s+shares\b"
    r"|\bas\s+a\s+result\s+of\s+(?:his|her|its)\s+"
    r"(?:equity\s+interest|status\s+as\s+trustee)\b)",
    re.I | re.S,
)
_NAMED_ACCOUNT = re.compile(
    r"(?:\b(?:LLC|L\.L\.C\.|LP|L\.P\.|Ltd\.?|Limited|Inc\.?|Corp\.?"
    r"|Corporation)\b|\bLimited\s+Partnership\b"
    r"|\b(?:Family|Revocable|Irrevocable)\s+Trust\b"
    r"|\bTrust(?:\s+[IVX]+)?\b"
    r"|\b(?:Fund|Funds|Group|Partnership|Capital|Productions)\b)",
    re.I,
)
def _source_described_account_key(row: dict[str, Any]) -> str | None:
    """Key explicit source-described accounts, never inferred entity identity."""
    evidence: list[str] = []
    for raw in row.get("footnote_texts") or []:
        text = " ".join(str(raw).split())
        sentences = re.split(r"(?<=[.!?])\s+", text)
        candidates = sentences + ([text] if not text.lower().startswith("of which") else [])
        for sentence in candidates:
            sentence = sentence.strip()
            if not sentence or sentence.lower().startswith("of which"):
                continue
            if not _ACCOUNT_RELATION.search(sentence):
                continue
            if not _NAMED_ACCOUNT.search(sentence):
                continue
            normalized = re.sub(r"\b\d[\d,.]*\b", " number ", sentence.lower())
            normalized = re.sub(r"[^a-z]+", " ", normalized).strip()
            if normalized:
                evidence.append(normalized)
    return "|".join(sorted(set(evidence))) or None


def build_holder_position_ledger_v0_10(
    observations: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Resolve explicit indirect accounts and fail closed on ambiguous notes."""
    rows, readout = build_holder_position_ledger_v0_9(observations)
    resolved = 0
    for row in rows:
        if (
            not row.get("methodology_relevant")
            or row.get("deduplication_state")
            != "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED"
        ):
            continue
        account_key = _source_described_account_key(row)
        if not account_key:
            continue
        group_id = stable_id(
            "source_described_indirect_account_v0_1",
            row.get("instrument_id"),
            row.get("security_class_id"),
            account_key,
        )
        row["canonical_holder_group_id"] = f"source_described_account:{group_id[:24]}"
        row["economic_position_id"] = stable_id(
            "source_described_indirect_position_v0_1",
            row.get("instrument_id"),
            row.get("security_class_id"),
            group_id,
            row.get("eligible_from_session"),
            row.get("supported_issued_common_shares"),
        )
        row["deduplication_state"] = "INDIRECT_SOURCE_DESCRIBED_ACCOUNT_RESOLVED"
        resolved += 1

    unresolved = sum(
        row.get("methodology_relevant")
        and row.get("deduplication_state") in _UNRESOLVED_STATES
        for row in rows
    )
    positions = {
        row.get("economic_position_id")
        for row in rows
        if row.get("methodology_relevant") and row.get("economic_position_id")
    }
    readout.update(
        {
            "policy_id": "holder_methodology_scoped_economic_position_resolution_v0_10",
            "source_described_indirect_account_rows_resolved": resolved,
            "methodology_relevant_economic_positions": len(positions),
            "unresolved_methodology_relevant_rows": unresolved,
            "row_level_economic_position_resolution_complete": unresolved == 0,
            "economic_position_resolution_complete": False,
            "owner_exclusion_authorized": False,
            "status": "PASS_WITH_RESTRICTIONS" if rows and unresolved == 0 else "FAIL",
        }
    )
    return rows, readout
