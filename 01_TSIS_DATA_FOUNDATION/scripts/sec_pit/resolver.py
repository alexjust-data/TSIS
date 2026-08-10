from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class DailyOsState:
    instrument_id: str
    session_date: str
    shares_outstanding_estimate_as_known: float | None
    os_state: str
    anchor_observation_id: str | None
    anchor_measurement_at: str | None
    anchor_eligible_from_session: str | None
    staleness_days: int | None
    source_conflict_state: str
    causality_state: str


def resolve_daily_os(
    *,
    instrument_id: str,
    sessions: Iterable[date],
    observations: Iterable[dict[str, Any]],
    stale_after_days: int = 180,
    require_admitted: bool = True,
) -> list[DailyOsState]:
    anchors = [
        item for item in observations
        if item.get("observation_type") == "SHARES_OUTSTANDING_ANCHOR_CANDIDATE"
        and item.get("value") is not None
        and item.get("eligible_from_session")
        and item.get("causality_state") in {"PIT_VALID", "AVAILABILITY_SESSION_RESOLVED"}
        and not str(item.get("quality_state", "")).startswith("REJECT_")
        and (not require_admitted or item.get("quality_state") == "ADMITTED_OS_ANCHOR")
    ]
    anchors.sort(key=lambda item: (item["eligible_from_session"], item.get("measurement_at") or "", item["observation_id"]))
    output: list[DailyOsState] = []
    for session in sorted(set(sessions)):
        eligible = [item for item in anchors if item["eligible_from_session"] <= session.isoformat()]
        if not eligible:
            output.append(DailyOsState(instrument_id, session.isoformat(), None, "OS_UNAVAILABLE", None, None, None, None, "NO_KNOWN_CONFLICT", "PIT_VALID"))
            continue
        latest_eligible_session = eligible[-1]["eligible_from_session"]
        latest = [item for item in eligible if item["eligible_from_session"] == latest_eligible_session]
        latest_acceptance = max(item.get("filing_accepted_at") or "" for item in latest)
        latest = [item for item in latest if (item.get("filing_accepted_at") or "") == latest_acceptance]
        latest_measurement = max(item.get("measurement_at") or "" for item in latest)
        latest = [item for item in latest if (item.get("measurement_at") or "") == latest_measurement]
        values = {float(item["value"]) for item in latest}
        chosen = sorted(latest, key=lambda item: item["observation_id"])[-1]
        measurement = date.fromisoformat(chosen["measurement_at"]) if chosen.get("measurement_at") else None
        staleness = (session - measurement).days if measurement else None
        conflict = "SOURCE_CONFLICT" if len(values) > 1 else "NO_KNOWN_CONFLICT"
        state = "OS_SOURCE_CONFLICT" if len(values) > 1 else ("OS_STALE_ANCHOR" if staleness is not None and staleness > stale_after_days else "OS_REPORTED_ANCHOR")
        output.append(DailyOsState(
            instrument_id=instrument_id,
            session_date=session.isoformat(),
            shares_outstanding_estimate_as_known=float(chosen["value"]),
            os_state=state,
            anchor_observation_id=chosen["observation_id"],
            anchor_measurement_at=chosen.get("measurement_at"),
            anchor_eligible_from_session=chosen["eligible_from_session"],
            staleness_days=staleness,
            source_conflict_state=conflict,
            causality_state="PIT_VALID",
        ))
    return output


def owner_exclusion_estimate(
    *,
    shares_outstanding: float | None,
    unique_supported_excluded_shares: float | None,
    ownership_coverage_state: str,
) -> dict[str, float | str | None]:
    if shares_outstanding is None:
        return {"float_owner_exclusion_estimate": None, "float_percent_estimate": None, "estimation_state": "OS_UNAVAILABLE"}
    if unique_supported_excluded_shares is None or ownership_coverage_state != "SUFFICIENT_FOR_METHODOLOGY":
        return {"float_owner_exclusion_estimate": None, "float_percent_estimate": None, "estimation_state": "OWNERSHIP_COVERAGE_INSUFFICIENT"}
    estimate = max(0.0, shares_outstanding - unique_supported_excluded_shares)
    return {"float_owner_exclusion_estimate": estimate, "float_percent_estimate": 100.0 * estimate / shares_outstanding if shares_outstanding else None, "estimation_state": "OWNER_EXCLUSION_ESTIMATE"}

