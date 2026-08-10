from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sec_pit.models import FilingRecord

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"

OS_FORMS = frozenset({
    "10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A",
    "8-K", "8-K/A", "6-K", "6-K/A", "S-1", "S-1/A", "S-3", "S-3/A",
    "F-1", "F-1/A", "F-3", "F-3/A", "424B1", "424B2", "424B3", "424B4",
    "424B5", "POS AM", "EFFECT",
})
OWNERSHIP_FORMS = frozenset({
    "DEF 14A", "DEFA14A", "10-K", "10-K/A", "SC 13D", "SC 13D/A", "SC 13G",
    "SC 13G/A", "SCHEDULE 13D", "SCHEDULE 13D/A", "SCHEDULE 13G",
    "SCHEDULE 13G/A", "3", "3/A", "4", "4/A", "5", "5/A",
})
LIFECYCLE_REGISTRATION_FORMS = frozenset({
    "8-A", "8-A/A", "8-A12B", "8-A12B/A", "8-A12G", "8-A12G/A",
})
LIFECYCLE_DELISTING_FORMS = frozenset({"25", "25-NSE"})


def has_item(items: str | None, target: str) -> bool:
    return target in {item.strip() for item in str(items or "").split(",")}

RESTRICTION_FORMS = frozenset({
    "S-1", "S-1/A", "S-3", "S-3/A", "F-1", "F-1/A", "F-3", "F-3/A",
    "424B1", "424B2", "424B3", "424B4", "424B5", "EFFECT", "8-K", "8-K/A", "6-K", "6-K/A",
})


def normalize_cik(value: str | int) -> str:
    digits = "".join(character for character in str(value) if character.isdigit())
    if not digits:
        raise ValueError(f"Invalid CIK: {value!r}")
    return digits.zfill(10)


def _records_from_columns(cik: str, source: str, columns: dict[str, list[Any]]) -> Iterable[FilingRecord]:
    count = max((len(values) for values in columns.values()), default=0)
    for index in range(count):
        def value(name: str, row_index: int = index) -> Any:
            values = columns.get(name, [])
            return values[row_index] if row_index < len(values) else None

        size = value("size")
        yield FilingRecord(
            cik=cik,
            accession_number=str(value("accessionNumber") or ""),
            form=str(value("form") or ""),
            filing_date=value("filingDate"),
            report_date=value("reportDate"),
            acceptance_datetime=value("acceptanceDateTime"),
            primary_document=value("primaryDocument"),
            primary_document_description=value("primaryDocDescription"),
            items=value("items"),
            is_xbrl=_optional_bool(value("isXBRL")),
            is_inline_xbrl=_optional_bool(value("isInlineXBRL")),
            filing_size_bytes=int(size) if str(size or "").isdigit() else None,
            metadata_source=source,
        )


def _optional_bool(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    return bool(int(value)) if str(value).isdigit() else bool(value)


def parse_submissions_root(payload: dict[str, Any], source: str) -> tuple[list[FilingRecord], list[str]]:
    cik = normalize_cik(payload.get("cik", ""))
    filings = payload.get("filings", {})
    records = list(_records_from_columns(cik, source, filings.get("recent", {})))
    supplements = [str(item["name"]) for item in filings.get("files", []) if item.get("name")]
    return records, supplements


def parse_submissions_supplement(cik: str, payload: dict[str, Any], source: str) -> list[FilingRecord]:
    return list(_records_from_columns(normalize_cik(cik), source, payload))


def accession_compact(accession: str) -> str:
    return accession.replace("-", "")


def primary_document_url(record: FilingRecord) -> str | None:
    if not record.primary_document or not record.accession_number:
        return None
    document = record.primary_document
    parts = document.split("/", 1)
    if len(parts) == 2 and parts[0].lower().startswith("xsl"):
        document = parts[1]
    return f"{ARCHIVES_BASE}/{int(record.cik)}/{accession_compact(record.accession_number)}/{document}"


def complete_submission_url(record: FilingRecord) -> str | None:
    if not record.accession_number:
        return None
    return f"{ARCHIVES_BASE}/{int(record.cik)}/{accession_compact(record.accession_number)}/{record.accession_number}.txt"


def stratified_primary_selection(rows: list[dict[str, Any]], max_total: int | None) -> list[dict[str, Any]]:
    eligible = [row for row in rows if row.get("roles") and row.get("primary_document_url")]
    eligible.sort(key=lambda row: (row.get("acceptance_datetime") or "", row["accession_number"]), reverse=True)
    if max_total is None or len(eligible) <= max_total:
        return eligible
    role_order = [
        "LIFECYCLE_EVIDENCE_CANDIDATE",
        "OS_EVIDENCE_CANDIDATE",
        "OWNERSHIP_EVIDENCE_CANDIDATE",
        "RESTRICTION_EVIDENCE_CANDIDATE",
        "INSTITUTIONAL_CONTEXT_CANDIDATE",
    ]
    buckets = {role: [row for row in eligible if role in row["roles"]] for role in role_order}
    selected: list[dict[str, Any]] = []
    selected_accessions: set[str] = set()
    cursor = 0
    while len(selected) < max_total and any(buckets.values()):
        role = role_order[cursor % len(role_order)]
        cursor += 1
        bucket = buckets[role]
        while bucket:
            row = bucket.pop(0)
            if row["accession_number"] not in selected_accessions:
                selected.append(row)
                selected_accessions.add(row["accession_number"])
                break
        if cursor > max_total * len(role_order) * 2:
            break
    if len(selected) < max_total:
        for row in eligible:
            if row["accession_number"] not in selected_accessions:
                selected.append(row)
                selected_accessions.add(row["accession_number"])
                if len(selected) == max_total:
                    break
    return selected


def filing_roles(record: FilingRecord) -> list[str]:
    form = record.form.upper()
    roles: list[str] = []
    if (
        form in LIFECYCLE_REGISTRATION_FORMS
        or form in LIFECYCLE_DELISTING_FORMS
        or (form in {"8-K", "8-K/A"} and has_item(record.items, "3.01"))
    ):
        roles.append("LIFECYCLE_EVIDENCE_CANDIDATE")
    if form in OS_FORMS:
        roles.append("OS_EVIDENCE_CANDIDATE")
    if form in OWNERSHIP_FORMS:
        roles.append("OWNERSHIP_EVIDENCE_CANDIDATE")
    if form in RESTRICTION_FORMS:
        roles.append("RESTRICTION_EVIDENCE_CANDIDATE")
    if form.startswith("13F"):
        roles.append("INSTITUTIONAL_CONTEXT_CANDIDATE")
    return roles

