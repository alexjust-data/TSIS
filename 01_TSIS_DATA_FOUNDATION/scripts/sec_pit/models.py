from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class InstrumentScope:
    instrument_id: str
    ticker: str
    cik: str
    share_class_figi: str | None = None
    is_common_stock: bool | None = None
    valid_from: str | None = None
    valid_to: str | None = None


@dataclass(frozen=True)
class FilingRecord:
    cik: str
    accession_number: str
    form: str
    filing_date: str | None
    report_date: str | None
    acceptance_datetime: str | None
    primary_document: str | None
    primary_document_description: str | None
    items: str | None
    is_xbrl: bool | None
    is_inline_xbrl: bool | None
    filing_size_bytes: int | None
    metadata_source: str


@dataclass(frozen=True)
class SourceObservation:
    observation_id: str
    observation_type: str
    cik: str
    accession_number: str | None
    form: str | None
    instrument_id: str | None
    security_class_id: str | None
    value: float | None
    unit: str | None
    measurement_at: str | None
    effective_at: str | None
    filing_accepted_at: str | None
    eligible_from_session: str | None
    availability_policy_id: str
    source_url: str | None
    source_sha256: str | None
    source_excerpt: str | None
    extraction_method: str
    quality_state: str
    causality_state: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AcquisitionResult:
    url: str
    status: str
    http_status: int | None
    fetched_at_utc: str
    sha256: str | None
    bytes: int
    content_type: str | None
    object_path: str | None
    logical_path: str | None
    attempts: int
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

