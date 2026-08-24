# SEC PIT Massive provisional schemas

Status: **PROVISIONAL_LIVE_PROBE_PENDING**

These files describe vendor evidence and acquisition lineage. They are not
canonical TSIS feature/state schemas.

Common normalized lineage fields:

| Field | Type | Rule |
|---|---|---|
| _massive_endpoint_id | string | required |
| _massive_request_id | string | required, non-empty |
| _massive_retrieved_at_utc | UTC timestamp string | required |
| _massive_raw_sha256 | 64-char hex | required |
| _massive_target_cik | nullable 10-digit string | target query CIK |
| _massive_row_index | integer >= 0 | page-local stable order |

Unknown vendor fields are preserved. Required identity fields are fail-closed.
Types and field presence remain provisional until versioned sample audit from
the 250-case live probe.

Files:

- runtime artifact contract;
- direct endpoint contracts for EDGAR index, Forms 3/4, 8-K disclosures and
  disclosure taxonomy;
- conditional contracts for 8-K text and 13F, both currently unauthorized.
