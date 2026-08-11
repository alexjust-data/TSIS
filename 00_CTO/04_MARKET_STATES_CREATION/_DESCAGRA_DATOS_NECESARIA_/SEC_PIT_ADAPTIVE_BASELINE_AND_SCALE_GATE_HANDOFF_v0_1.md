# SEC PIT Adaptive Baseline and Scale Gate Handoff `v0_1`

Date: `2026-08-11`

Status: `BOUNDED_SYSTEM_PASS_SCALE_NOT_AUTHORIZED`

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

## Required next execution

Run a 30-50 instrument stratified probe before any 4,824-instrument materialization. Use the same four-shard function, implementation hashes, config, schemas, sources and fail-closed policies. Any semantic or schema change invalidates all shard probes and requires rerunning every shard.

Required strata include domestic annual proxy, special proxy, foreign `20-F` amendment family, multiclass issuer, ticker reuse/lifecycle conflict, depositary preferred halt, SPAC/de-SPAC, amendment-heavy issuer and sparse historical ownership.

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

Scale remains `NOT_AUTHORIZED` until a human or governed gate reviews that evidence.

## Read first

The detailed result and runtime lineage are in:

`01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit/SEC_PIT_ADAPTIVE_BASELINE_COMPANYFACTS_FULL_INTERVAL_AND_SHARD_CERTIFICATION_READOUT_v0_1.md`.

