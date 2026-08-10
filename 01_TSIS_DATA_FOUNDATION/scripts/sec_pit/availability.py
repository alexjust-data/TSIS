from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")


@dataclass(frozen=True)
class AvailabilityDecision:
    eligible_from_session: date | None
    state: str
    policy_id: str
    reason: str


class EdgarAvailabilityPolicy:
    """Conservative session eligibility policy for historical EDGAR filings.

    EDGAR acceptance is preserved as evidence. This policy deliberately does
    not claim an exact public dissemination timestamp when one is unavailable.
    """

    policy_id = "edgar_availability_conservative_v0_1"
    same_day_extended_forms = frozenset({"3", "3/A", "4", "4/A", "5", "5/A"})

    def __init__(self, holidays: set[date] | None = None) -> None:
        self.holidays = holidays or set()

    def _next_business_day(self, value: date) -> date:
        current = value + timedelta(days=1)
        while current.weekday() >= 5 or current in self.holidays:
            current += timedelta(days=1)
        return current

    def _same_or_next_session(self, value: date) -> date:
        if value.weekday() < 5 and value not in self.holidays:
            return value
        previous = value - timedelta(days=1)
        return self._next_business_day(previous)

    def resolve(self, accepted_at: str | datetime | None, form: str | None) -> AvailabilityDecision:
        if accepted_at is None:
            return AvailabilityDecision(None, "AVAILABILITY_UNCERTAIN", self.policy_id, "missing_acceptance_datetime")
        dt = datetime.fromisoformat(accepted_at.replace("Z", "+00:00")) if isinstance(accepted_at, str) else accepted_at
        if dt.tzinfo is None:
            return AvailabilityDecision(None, "AVAILABILITY_UNCERTAIN", self.policy_id, "naive_acceptance_datetime")
        eastern = dt.astimezone(NEW_YORK)
        normalized_form = (form or "").upper().strip()

        # A filing accepted after the 04:00 research cutoff cannot enter that
        # session even if EDGAR disseminated it immediately.
        if eastern.time() < time(4, 0):
            session = self._same_or_next_session(eastern.date())
            reason = "accepted_before_presession_cutoff"
        else:
            session = self._next_business_day(eastern.date())
            reason = "accepted_at_or_after_presession_cutoff"

        if eastern.time() > time(17, 30) and normalized_form not in self.same_day_extended_forms:
            next_day = self._next_business_day(eastern.date())
            if next_day > session:
                session = next_day
            reason += ";after_standard_edgar_acceptance_window"

        return AvailabilityDecision(session, "AVAILABILITY_SESSION_RESOLVED", self.policy_id, reason)

