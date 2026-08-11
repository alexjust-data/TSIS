# SEC PIT seven-ticker owner-exclusion stratified probe plan v0_1

Date: `2026-08-11`

Status: `EXECUTED_PARTIAL_PASS_SCALE_BLOCKED_ADAPTIVE_BASELINE_BACKFILL_REQUIRED`

## Purpose

Test whether the same SEC PIT O/S, ownership, holder reconciliation and
owner-exclusion implementation used for PGAC generalizes across the frozen
seven-case sample before any authorization for the 4,824-instrument parent
universe.

No ticker-specific parser, arithmetic, accession rule, holder exception or
manually supplied output is permitted. A causal `NULL + blocker_codes` is an
accepted probe outcome when evidence is insufficient.

## Frozen strata

| Ticker | Stratum | Expected behavior |
|---|---|---|
| `BNAI` | modern XBRL benchmark | eligible probe |
| `DOMH` | pre-XBRL and identity stress | eligible, restrictions expected |
| `BBBY` | lifecycle/ticker-reuse stress | fail closed while identity conflict remains |
| `BGM` | foreign issuer | eligible parser-coverage probe |
| `CNOBP` | preferred/depositary negative control | halt before acquisition |
| `ALUR` | OTC/security-type review | eligible, restrictions expected |
| `PGAC` | SPAC/foreign identity | completed positive control |

CNOBP must not enter common-equity O/S or float calculation. Its correct probe
result is `HALT_SECURITY_CLASS` with zero acquired documents.

## Bounded temporal scope

For every eligible instrument, the output probe covers the last five canonical
market sessions ending no later than `2026-03-06`. Supporting evidence must be
available before each session under the existing Edgar availability policy.

The bounded window reduces runtime only. It does not change source families,
schema, class gates, PIT rules, extraction code, reconciliation policies or
blocker semantics.

## Deterministic source selection

For each eligible instrument the selection builder must include, without
ticker-specific accessions:

1. the latest proxy ownership anchor (`DEF 14A`) available by the probe end;
2. for a foreign issuer without a proxy, the latest `20-F`/`20-F/A` candidate;
3. the two latest periodic O/S candidates available by the probe end;
4. every ownership event from the selected baseline through the probe end;
5. every pre-baseline Form 3/3-A needed to identify opening insider class;
6. every pre-baseline Schedule 13D/13D-A needed to identify explicit affiliate
   positions and class components;
7. lifecycle documents already selected under the governed lifecycle policy.

Pre-baseline institutional Schedule 13G evidence is not required to calculate
`officer_director_explicit_affiliate_v0_1`; post-baseline 13G rows remain
neutral observations and are never automatically excluded.

## Current capacity estimate

```text
eligible instruments                         6
security-class negative controls              1
selected primary documents                  343
already available local documents            96
missing documents requiring acquisition     247
missing SEC filing-size ceiling        205.76 MiB
concurrent tickers                             1
network requests per second                  5.0
```

The SEC filing-size sum is a conservative planning ceiling, not an expected
response-byte total.

## Mandatory execution sequence

```text
freeze selection + hashes
-> parameterize common O/S runner
-> unit/regression tests
-> build local-evidence reuse ledger
-> hash-bound acquisition authorization for missing rows only
-> sequential acquisition with PID/heartbeat/log/telemetry/final manifest
-> one no-network O/S probe per eligible instrument
-> one no-network owner-exclusion probe per eligible instrument
-> CNOBP negative-control audit
-> variable-by-variable cross-stratum audit
-> versioned certification readout
-> human scale decision
```

## Fail-closed gates

The following must block calculation rather than be guessed:

- unresolved ticker reuse or instrument continuity;
- wrong or unproven security class;
- missing causal O/S anchor;
- unsupported proxy/20-F ownership structure;
- unresolved target-class allocation;
- unresolved methodology-relevant holder overlap;
- missing acceptance timestamp;
- incomplete methodology-relevant source coverage.

Broad institutional parser coverage, 13F institutional ownership and freely
tradable supply remain separate outputs and cannot be silently represented by
this owner-exclusion estimate.

## Recovery and hardware policy

Acquisition is sequential and content-addressed. Existing verified objects are
reused by URL and hash. A power loss may interrupt only the active request; a
resume skips completed URLs. The run must persist pre-manifest, PID, heartbeat,
live telemetry, acquisition log and final manifest.

The workload is network/HTML parsing and small-table I/O bound. It runs on CPU,
not GPU, and uses one acquisition stream to respect SEC rate limits. Active
runtime/manifests use the NVMe; heavy governed SEC objects remain in the
existing `D:/TSIS/fundamental_context/sec_pit_v0_1` content store.

## Scale decision

This probe cannot authorize 4,824 instruments by itself. A favorable result
must still be followed by one production-equivalent probe per planned shard and
the variable-by-variable certification required by `AGENTS.md`.

## Execution outcome

The probe was executed on `2026-08-11`. `ALUR`, `BNAI` and `PGAC` produced five causal non-NULL owner-exclusion rows; `BBBY`, `BGM` and `DOMH` produced explicit NULLs; `CNOBP` halted before acquisition. The scale gate remains closed pending adaptive annual-baseline family traversal and the required per-shard probes.

Authoritative readout:

`C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit/SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_READOUT_v0_1.md`
