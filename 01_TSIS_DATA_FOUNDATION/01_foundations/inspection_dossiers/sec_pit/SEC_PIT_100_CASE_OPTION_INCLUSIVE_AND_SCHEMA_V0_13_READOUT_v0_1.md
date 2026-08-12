# SEC PIT 100-case option-inclusive and schema v0.13 readout v0.1

Status: `PASS_SYSTEM_GATE_FLOAT_COVERAGE_INSUFFICIENT_FOR_4824_SCALE`

Date: `2026-08-13`

## Scope

This readout closes the immutable 99-eligible-case no-network rerun authorized
by
`SEC_PIT_OPTION_INCLUSIVE_CURRENT_SHARES_AND_PHYSICAL_SCHEMA_SHARD_CERTIFICATION_v0_1.md`.
The frozen 100-case sample contains 99 eligible common-equity cases; CNOBP
remains outside this batch under the governed security-class halt.

Authoritative runtime identity:

```text
output root = C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_13
run id      = sec_pit_100_case_resolution_v0_13_20260812T2127Z
mode        = NO_NETWORK_LOCAL_RESOLUTION_BATCH
```

## Execution and integrity

```text
batch status                  COMPLETE
O/S resolution               99 / 99
ownership resolution         99 / 99
execution failures           0
network requests             0
daily rows                    495
duplicate instrument-session 0
component-hash variants      1
Arrow-schema variants        1
formula violations           0
fraction/percent violations  0
range violations             0
causal violations            0
NULL float without blocker   0
```

All 99 cases use the same code identity and the same physical
`daily_float_state.parquet` schema, including columns that are entirely NULL in
a blocked case.

## Coverage

```text
O/S complete cases        56 / 99 = 56.57%
float complete cases      15 / 99 = 15.15%
float non-NULL rows       75 / 495
v0.12 float complete      10 / 99
net gain over v0.12        5 cases
regressions vs v0.12       0 cases
```

The 15 complete-float cases are:

```text
AIEV ALUR ATMC ATMV ATYR BGM EJH ENFY IOBT ONCO PGAC PLL PTE SYTA WINT
```

The five cases recovered relative to v0.12 are:

```text
ALUR ATYR ENFY PTE WINT
```

## Required semantic controls

- ATYR is `5/5 CALCULATED`; the resolver subtracts `1,400,094` currently
  owned shares and does not treat the separately disclosed `2,172,129`
  acquirable shares as current issued supply.
- BASI is `5/5 BLOCKED_BY_INPUT_GATES`; holder footnotes make the reported
  beneficial ownership option-inclusive and no supported current-share
  component is invented.
- OSG is `5/5 BLOCKED_BY_INPUT_GATES`; its table-level 60-day issuable-share
  note is detected and the aggregate is not subtracted from current O/S.
- ASPN, BNED, DOMH, MULN and TAOX remain intentionally fail-closed after
  discovering options or other issuable securities inside their reported
  aggregates. This is a scientific correction, not a coverage regression.

## Residual blockers

| Blocker | Cases | Rows |
|---|---:|---:|
| `SHARE_CLASS_ALLOCATION_UNRESOLVED` | 28 | 140 |
| `INSTRUMENT_INTERVAL_CONFLICT` | 25 | 125 |
| `HOLDER_OVERLAP_UNRESOLVED` | 15 | 75 |
| `ECONOMIC_POSITION_OVERLAP_UNRESOLVED` | 14 | 70 |
| `OWNERSHIP_SPLIT_ADJUSTMENT_UNRESOLVED` | 10 | 50 |
| `SHARES_OUTSTANDING_UNAVAILABLE` | 10 | 50 |
| `POST_BASELINE_EVENT_IDENTITY_OR_DATE_UNRESOLVED` | 7 | 35 |
| `BASELINE_DOCUMENT_PARTIAL` | 3 | 15 |
| `OWNERSHIP_BASELINE_UNAVAILABLE` | 1 | 5 |
| `AMENDMENT_FAMILY_UNRESOLVED` | 1 | 5 |
| `EXISTING_BASELINE_HOLDER_ACCOUNT_SET_INCOMPLETE` | 1 | 5 |

## Decision

The parser, PIT resolver, fail-closed behavior and cross-shard physical schema
pass the bounded system gate. The resulting `15.15%` complete-float coverage is
not sufficient to authorize a 4,824-instrument materialization.

The next correction loop must attack the residual blockers in measured impact
order, beginning with share-class allocation and instrument-interval conflicts.
Every semantic change requires production-equivalent probes in all four shards.
The human authorized a 4,824-instrument diagnostic execution on `2026-08-13`
after this correction loop and a four-shard `PASS`. That authorization does not
promote the resulting dataset: full-denominator coverage, false-positive, PIT,
schema and reproducibility audits remain mandatory. No downstream component may
reinterpret a blocked row as zero ownership or `float = O/S`.
