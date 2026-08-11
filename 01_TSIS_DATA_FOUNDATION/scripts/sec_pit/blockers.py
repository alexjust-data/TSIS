from __future__ import annotations

from typing import Any, Iterable


BLOCKER_REGISTRY: dict[str, dict[str, Any]] = {
    "NO_OWNERSHIP_BASELINE_FOUND": {
        "category": "SOURCE_COVERAGE",
        "retry_action": "SEARCH_EARLIER_BASELINE_CANDIDATE",
    },
    "BASELINE_DOCUMENT_PARTIAL": {
        "category": "DOCUMENT_CONTENT",
        "retry_action": "FALLBACK_TO_PREVIOUS_CONTENT_COMPLETE_CANDIDATE",
    },
    "AMENDMENT_FAMILY_UNRESOLVED": {
        "category": "DOCUMENT_FAMILY",
        "retry_action": "ACQUIRE_ORIGINAL_AND_PRIOR_AMENDMENTS",
    },
    "HOLDER_OVERLAP_UNRESOLVED": {
        "category": "ECONOMIC_IDENTITY",
        "retry_action": "RESOLVE_CONTROL_AND_OVERLAP_GRAPH",
    },
    "SHARE_CLASS_ALLOCATION_UNRESOLVED": {
        "category": "SECURITY_CLASS",
        "retry_action": "ACQUIRE_CAUSAL_CLASS_COMPONENT_EVIDENCE",
    },
    "INSTRUMENT_INTERVAL_CONFLICT": {
        "category": "INSTRUMENT_IDENTITY",
        "retry_action": "RESOLVE_INSTRUMENT_INTERVAL",
    },
    "TICKER_REUSE_CONFLICT": {
        "category": "INSTRUMENT_IDENTITY",
        "retry_action": "RESOLVE_TICKER_REUSE_TO_DISTINCT_INSTRUMENT_IDS",
    },
    "NO_CAUSAL_OS_ANCHOR": {
        "category": "O_S_COVERAGE",
        "retry_action": "ACQUIRE_EARLIER_CAUSAL_OS_EVIDENCE",
    },
}


def blocker_details(codes: Iterable[str]) -> list[dict[str, Any]]:
    return [
        {"code": code, **BLOCKER_REGISTRY.get(code, {
            "category": "UNCLASSIFIED",
            "retry_action": "HUMAN_REVIEW_REQUIRED",
        })}
        for code in sorted(set(codes))
    ]
