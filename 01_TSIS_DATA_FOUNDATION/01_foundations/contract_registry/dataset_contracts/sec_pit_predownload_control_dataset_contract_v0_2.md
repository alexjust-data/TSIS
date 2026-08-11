# SEC PIT Predownload Control Dataset Contract `v0_2`

Status: `PROBE_VALIDATED_NOT_DOWNLOAD_AUTHORIZED`

## Role

This contract governs the control plane that must pass before SEC primary
documents can be acquired. It separates five questions that v0.1 mixed:

1. Is the ticker in the governed universe?
2. Which instrument and security class is the target?
3. Which issuer filings are candidates for that instrument?
4. Which time interval does each filing support?
5. Is the exact selection explicitly authorized for network acquisition?

## Authority chain

```text
lt1b_universe_v0_1
-> defines the 4,824-ticker parent scope and its PTI windows

instrument_master_v0_1
-> projects identity for each ticker; it is not the universe list

all_tickers snapshots + lifecycle reconciliation
-> supply identity history, vendor dates, market presence and SEC candidates

SEC submissions metadata
-> supplies issuer-level accession candidates; CIK alone never proves class
```

## Outputs

- `instrument_identity_interval_ledger.parquet`
- `accession_instrument_link_candidates.parquet`
- `document_selection_plan_v0_2.parquet`
- `gate_matrix.parquet`
- pre/PID/heartbeat/final manifests

The interval ledger preserves separate source fields. Vendor, SEC and market
dates must never overwrite each other. `sec_exchange_end_candidate` is not a
legal delisting date.

The accession ledger may emit zero, one or multiple instrument candidates.
Even one candidate is `NOT_PROVEN_BY_METADATA` until document/class evidence
supports admission.

## Selection semantics

- 8-K is selected by Item metadata; Item 2.02 alone is not O/S or restriction evidence.
- 6-K uses a separate content-probe lane.
- periodic, registration, lifecycle and ownership roles remain explicit.
- 13F belongs to the separate global manager information-table lane.
- issuer prehistory is labeled `OPENING_STATE_PREHISTORY_CANDIDATE`.
- post-window evidence is labeled `POST_INTERVAL_CONFIRMATION_CANDIDATE`.
- a capacity below the required evidence count is `FAIL`, never silent truncation.

## Acquisition authorization

Technical `PASS` does not authorize a download. Execution additionally requires
an external authorization whose SHA-256 values match the exact final manifest
and selection parquet and whose ticker scope is a subset of technically eligible
classes. CNOBP is a mandatory halt in the seven-case probe.

## Recovery

Acquisition is sequential and content-addressed. Every successful URL is
persisted immediately with `FETCHED + sha256`; `--resume` skips those URLs.
After power loss, completed objects are preserved and only incomplete URLs are
retried.

## Runtime telemetry

An authorized acquisition must emit a fresh heartbeat independently of document
completion plus append-only resource and document-performance histories. The
runtime fields cover process-tree CPU/RSS/private memory, system RAM/pagefile,
process I/O rates, output free space, progress, documents/MiB per minute, HTTP
attempt latency, retries and 429 responses. Each document also separates
throttle, HTTP, retry wait, SHA-256, gzip and atomic-write time.

`performance_summary.json` may name a provisional bottleneck candidate. That
classification is diagnostic inference, not institutional evidence and not an
authorization to replace Python with C++. Parse, extraction, reconciliation and
Parquet timings remain explicitly not applicable until those later runners are
instrumented. The PowerShell SEC monitor uses shared read/delete access so it
cannot block atomic heartbeat replacement on Windows.

## Promotion boundary

The seven-case probe validates the control implementation only. It does not
authorize the six eligible downloads and does not authorize parent-universe
scale-out.
