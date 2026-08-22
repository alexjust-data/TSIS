"""Frozen models and endpoint allowlist for the Massive SEC acquisition.

The endpoint paths and page limits reflect the official Massive Stocks REST
documentation reviewed on 2026-08-22.  A live bounded probe must still confirm
the response schemas before any full-universe authorization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


EndpointGate = Literal["DIRECT", "CONDITIONAL"]
QueryStrategy = Literal["PER_ISSUER_CIK", "SINGLETON", "GLOBAL_CUSIP_FILTER"]


@dataclass(frozen=True)
class EndpointSpec:
    endpoint_id: str
    path: str
    gate: EndpointGate
    query_strategy: QueryStrategy
    target_parameter: str | None
    page_limit: int
    default_sort: str | None
    dataset_directory: str
    documented_result_fields: tuple[str, ...]
    identity_fields: tuple[str, ...]

    def initial_parameters(self, *, cik: str | None = None) -> dict[str, Any]:
        values: dict[str, Any] = {"limit": self.page_limit}
        if self.default_sort:
            values["sort"] = self.default_sort
        if self.query_strategy == "PER_ISSUER_CIK":
            if not cik or not self.target_parameter:
                raise ValueError(f"{self.endpoint_id} requires a target CIK")
            values[self.target_parameter] = normalize_cik(cik)
        elif self.query_strategy == "GLOBAL_CUSIP_FILTER":
            raise ValueError(
                "13F requires a separately authorized quarter-window/CUSIP query plan"
            )
        return values


ENDPOINT_SPECS: dict[str, EndpointSpec] = {
    "edgar_index": EndpointSpec(
        endpoint_id="edgar_index",
        path="/stocks/filings/vX/index",
        gate="DIRECT",
        query_strategy="PER_ISSUER_CIK",
        target_parameter="cik",
        page_limit=10_000,
        default_sort="filing_date.asc",
        dataset_directory="edgar_index",
        documented_result_fields=(
            "accession_number",
            "cik",
            "filing_date",
            "filing_url",
            "form_type",
            "issuer_name",
            "ticker",
        ),
        identity_fields=("accession_number", "cik", "form_type"),
    ),
    "form_3": EndpointSpec(
        endpoint_id="form_3",
        path="/stocks/filings/vX/form-3",
        gate="DIRECT",
        query_strategy="PER_ISSUER_CIK",
        target_parameter="issuer_cik",
        page_limit=10_000,
        default_sort="filing_date.asc",
        dataset_directory="form_3",
        documented_result_fields=(
            "accession_number",
            "date_of_original_submission",
            "filing_date",
            "filing_url",
            "form_type",
            "issuer_cik",
            "issuer_name",
            "owner_cik",
            "owner_name",
            "period_of_report",
            "security_title",
            "security_type",
            "shares_owned",
            "tickers",
        ),
        identity_fields=("accession_number", "issuer_cik", "form_type"),
    ),
    "form_4": EndpointSpec(
        endpoint_id="form_4",
        path="/stocks/filings/vX/form-4",
        gate="DIRECT",
        query_strategy="PER_ISSUER_CIK",
        target_parameter="issuer_cik",
        page_limit=10_000,
        default_sort="filing_date.asc",
        dataset_directory="form_4",
        documented_result_fields=(
            "accession_number",
            "date_of_original_submission",
            "filing_date",
            "filing_url",
            "form_type",
            "issuer_cik",
            "issuer_name",
            "owner_cik",
            "owner_name",
            "period_of_report",
            "record_type",
            "security_title",
            "security_type",
            "transaction_code",
            "transaction_date",
            "transaction_price_per_share",
            "transaction_shares",
            "shares_owned_following_transaction",
            "tickers",
        ),
        identity_fields=("accession_number", "issuer_cik", "form_type"),
    ),
    "eight_k_disclosures": EndpointSpec(
        endpoint_id="eight_k_disclosures",
        path="/stocks/filings/8-K/vX/disclosures",
        gate="DIRECT",
        query_strategy="PER_ISSUER_CIK",
        target_parameter="cik",
        page_limit=1_000,
        default_sort="filing_date.asc",
        dataset_directory="eight_k_disclosures",
        documented_result_fields=(
            "accession_number",
            "cik",
            "filing_date",
            "filing_url",
            "primary_category",
            "secondary_category",
            "supporting_text",
            "tertiary_category",
            "tickers",
        ),
        identity_fields=("accession_number", "cik"),
    ),
    "disclosure_taxonomy": EndpointSpec(
        endpoint_id="disclosure_taxonomy",
        path="/stocks/taxonomies/vX/disclosures",
        gate="DIRECT",
        query_strategy="SINGLETON",
        target_parameter=None,
        page_limit=1_000,
        default_sort="taxonomy.asc",
        dataset_directory="disclosure_taxonomy",
        documented_result_fields=(
            "description",
            "primary_category",
            "secondary_category",
            "taxonomy",
            "tertiary_category",
        ),
        identity_fields=("taxonomy", "primary_category"),
    ),
    "eight_k_text": EndpointSpec(
        endpoint_id="eight_k_text",
        path="/stocks/filings/8-K/vX/text",
        gate="CONDITIONAL",
        query_strategy="PER_ISSUER_CIK",
        target_parameter="cik",
        page_limit=100,
        default_sort="filing_date.asc",
        dataset_directory="eight_k_text",
        documented_result_fields=(
            "accession_number",
            "cik",
            "filing_date",
            "filing_url",
            "form_type",
            "items_text",
            "ticker",
        ),
        identity_fields=("accession_number", "cik", "form_type"),
    ),
    "form_13f": EndpointSpec(
        endpoint_id="form_13f",
        path="/stocks/filings/vX/13-F",
        gate="CONDITIONAL",
        query_strategy="GLOBAL_CUSIP_FILTER",
        target_parameter="filer_cik",
        page_limit=1_000,
        default_sort="filing_date.asc",
        dataset_directory="form_13f",
        documented_result_fields=(
            "accession_number",
            "cusip",
            "filer_cik",
            "filing_date",
            "filing_url",
            "form_type",
            "issuer_name",
            "market_value",
            "period",
            "shares_or_principal_amount",
            "shares_or_principal_type",
            "title_of_class",
        ),
        identity_fields=("accession_number", "cusip", "filer_cik"),
    ),
}

DIRECT_ENDPOINT_IDS = tuple(
    endpoint_id for endpoint_id, spec in ENDPOINT_SPECS.items() if spec.gate == "DIRECT"
)
CONDITIONAL_ENDPOINT_IDS = tuple(
    endpoint_id
    for endpoint_id, spec in ENDPOINT_SPECS.items()
    if spec.gate == "CONDITIONAL"
)


def normalize_cik(value: Any) -> str:
    digits = "".join(character for character in str(value or "") if character.isdigit())
    if not digits or len(digits) > 10:
        raise ValueError(f"invalid SEC CIK: {value!r}")
    return digits.zfill(10)


def sanitize_url(url: str) -> str:
    """Remove credentials and stabilize query ordering for identity/logging."""
    parts = urlsplit(url)
    query = sorted(
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.casefold() != "apikey"
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def canonical_request_key(endpoint_id: str, url: str) -> str:
    payload = f"{endpoint_id}|{sanitize_url(url)}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class TargetGroup:
    cik: str
    tickers: tuple[str, ...]
    instrument_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PageCommit:
    endpoint_id: str
    work_id: str
    target_cik: str | None
    sanitized_url: str
    request_id: str
    retrieved_at_utc: str
    raw_sha256: str
    raw_object_path: str
    raw_bytes: int
    normalized_sha256: str
    normalized_path: str
    result_count: int
    next_url: str | None
    http_status: int
    attempts: int
    retry_count: int
    http_429_count: int
    elapsed_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def stable_json_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
