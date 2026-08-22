# SEC PIT Adaptive Baseline and Scale Gate Handoff `v0_1`

Date: `2026-08-11`

Status: `BOUNDED_SYSTEM_PASS_FULL_UNIVERSE_PREFLIGHT_PASS_METADATA_COHORT_01_AWAITING_HUMAN`

## Decision

The seven-case adaptive SEC PIT experiment has closed its original baseline-selection blockers. BGM and DOMH now calculate through generic document-family fallback; ALUR, BNAI and PGAC remain calculated; BBBY remains an explicit ticker-reuse NULL; CNOBP remains a class halt.

The official SEC Company Facts API has been added as a free O/S reconciliation channel only. It must never be used as owner-exclusion float authority or as proof of share class when a fact is issuer-wide or multiclass.

## Frozen workflow

```text
instrument identity and market-presence interval
-> bounded SEC metadata selection
-> content-addressed primary acquisition
-> class-specific O/S extraction
-> Company Facts O/S reconciliation
-> adaptive ownership document-family resolution
-> normalized holder/ownership events
-> class reconciliation and overlap deduplication
-> causal daily owner-exclusion state
-> NULL + exact blocker when evidence is insufficient
-> per-variable/per-shard certification
```

## Superseded probe requirement and current execution

The historical 30-50 case requirement was superseded by the completed
stratified 100-case gate and authoritative v0.21 four-shard result. The operator
has now authorized preparation of the full diagnostic as five sequential,
immutable ticker cohorts: `824/1000/1000/1000/1000`, prioritized by
`last_observed_date DESC, ticker ASC`.

The no-network 4,824-row preflight is `PASS`. Metadata-only cohort 01 awaits a
human-controlled launch. Primary documents, full resolution and institutional
promotion remain separately gated. See
`SEC_PIT_4824_DESCENDING_ACQUISITION_EXECUTION_PLAN_v0_1.md`.

## Gate criteria

Mandatory:

- zero known false positives;
- zero PIT leakage;
- formula and percentage invariants pass;
- schema, order, grain and component hashes equivalent across shards;
- every NULL has an exact blocker and retry action;
- every calculated transition has accession lineage;
- live telemetry records requests, bytes, latency, retries, HTTP status, CPU, memory, I/O and storage;
- pre-manifest, PID, heartbeat, log, monitor and final manifest exist.

Measured, not forced:

- O/S coverage;
- owner-exclusion float coverage;
- fallback-depth distribution;
- P50/P95/MAX storage and latency;
- blocker and retryability distribution.

Preparation and metadata-only cohort 01 are authorized under human launch.
Primary acquisition remains `NOT_AUTHORIZED` until the cohort metadata,
lifecycle/accession control, document plan, capacity readout and hash-bound
authorization pass.

## Read first

The detailed result and runtime lineage are in:

`01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit/SEC_PIT_ADAPTIVE_BASELINE_COMPANYFACTS_FULL_INTERVAL_AND_SHARD_CERTIFICATION_READOUT_v0_1.md`.
