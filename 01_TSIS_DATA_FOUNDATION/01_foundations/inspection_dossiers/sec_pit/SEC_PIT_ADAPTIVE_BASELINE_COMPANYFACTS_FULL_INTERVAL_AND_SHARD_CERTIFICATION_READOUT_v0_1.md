# SEC PIT Adaptive Baseline, Company Facts, Full-Interval and Shard Certification Readout `v0_1`

Date: `2026-08-11`

Status: `SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING`

Promotion level: `evidence_ready`; this is not yet an institutional 4,824-instrument dataset.

## Executive conclusion

The bounded SEC PIT pipeline now resolves class-specific O/S, selects ownership baselines adaptively, applies causal ownership updates, deduplicates supported exclusions and produces a fail-closed daily owner-exclusion float with one implementation across all tested cases and shards.

The official SEC Company Facts API is integrated as a free O/S reconciliation lane. It is not a float source and does not replace filing-level class and ownership evidence.

The seven-case gate result is:

```text
ALUR   CALCULATED
BGM    CALCULATED after 20-F family fallback
BNAI   CALCULATED with causal Form 4 update
DOMH   CALCULATED after annual-proxy fallback
PGAC   CALCULATED with exact Class A reconciliation
BBBY   NULL: TICKER_REUSE_CONFLICT
CNOBP  HALT_SECURITY_CLASS
```

The per-shard system gate passes. Scaling to 4,824 instruments remains explicitly unauthorized until a human or governed scale gate approves a 30-50 case expansion.

## Problems corrected

### Adaptive ownership baseline resolution

The resolver no longer treats the newest form as automatically authoritative. It:

- distinguishes annual and special proxies;
- rejects partial or ownership-incomplete baselines;
- traverses a bounded causal candidate family;
- resolves `20-F` plus `20-F/A` as a family;
- inherits an earlier complete baseline when a later filing does not restate ownership;
- records every rejected candidate, fallback depth and selected accession.

This converts BGM and DOMH from unexplained `NULL` results to reproducible calculations without ticker-specific code.

### Exact blocker taxonomy

The pipeline now emits actionable blockers such as:

```text
NO_OWNERSHIP_BASELINE_FOUND
BASELINE_DOCUMENT_PARTIAL
AMENDMENT_FAMILY_UNRESOLVED
HOLDER_OVERLAP_UNRESOLVED
SHARE_CLASS_ALLOCATION_UNRESOLVED
INSTRUMENT_INTERVAL_CONFLICT
TICKER_REUSE_CONFLICT
NO_CAUSAL_OS_ANCHOR
```

BBBY is blocked only by `TICKER_REUSE_CONFLICT`; the pipeline does not fabricate O/S or float.

### O/S issued-versus-outstanding defect

The first Company Facts comparison exposed a real DOMH extraction defect. A filing sentence contained distinct issued and outstanding counts, and the former parser selected issued shares. The parser now recognizes `issued and N shares outstanding`, selects the outstanding count and records its numeric-selection state. Company Facts `v0_2` then reconciled with zero value conflicts.

## Authoritative five-session results

| Case | O/S | Excluded shares | Owner-exclusion float | Float percent | State |
|---|---:|---:|---:|---:|---|
| ALUR | 9,262,586 | 655,338 | 8,607,248 | 92.924892% | `CALCULATED` |
| BGM | 6,006,480 | 3,028,492 | 2,977,988 | 49.579587% | `CALCULATED` |
| BNAI | 44,880,795 | 11,578,292 | 33,302,503 | 74.202124% | `CALCULATED_AND_TEMPORAL_UPDATE` |
| DOMH | 16,012,435 | 4,787,068 | 11,225,367 | 70.104060% | `CALCULATED` |
| PGAC | 8,869,250 | 244,250 | 8,625,000 | 97.246103% | `CALCULATED` |
| BBBY | NULL | NULL | NULL | NULL | `TICKER_REUSE_CONFLICT` |
| CNOBP | n/a | n/a | n/a | n/a | `HALT_SECURITY_CLASS` |

Selected fallback evidence:

- BGM selected `0001410578-25-000636` at fallback depth 1 after rejecting the later partial `20-F/A`.
- DOMH selected annual proxy `0001213900-25-107877` at fallback depth 1 after rejecting a later special-meeting proxy.
- PGAC preserved Class A O/S and excluded only the supported Class A sponsor-affiliate position; founder Class B shares were not subtracted.

## Official Company Facts O/S reconciliation

Authoritative run:

`C:/TSIS_Data/runtime/sec_pit_companyfacts_os_v0_1/runs/sec_pit_companyfacts_7t_reconciliation_v0_2_20260812T0400Z`

Results:

- 7 official SEC JSON requests completed;
- 708 facts inspected;
- 0 request failures, retries or HTTP 429 responses;
- 0 same-accession, same-measurement O/S value conflicts after the parser correction;
- exact matches: ALUR 2, BNAI 2 and DOMH 2;
- BGM and PGAC multiclass facts were not promoted as class proof;
- PGAC had no usable Company Facts O/S observation;
- CNOBP remained halted by security class.

Company Facts is deliberately constrained to `O/S_RECONCILIATION_ONLY_NOT_FLOAT_SOURCE`. The taxonomy fact `EntityPublicFloat` is a monetary disclosure and is not the share-count owner-exclusion float modeled here. Yahoo or free convenience libraries are not accepted as PIT authority because their history, as-of semantics, corrections and class identity are not governed sufficiently; they may only be optional external comparison sources.

## Full-interval production-equivalent probes

| Case | Sessions | O/S non-NULL | Float non-NULL | Float coverage |
|---|---:|---:|---:|---:|
| ALUR | 649 | 592 | 92 | 14.1757% |
| BNAI | 495 | 484 | 81 | 16.3636% |
| PGAC | 140 | 140 | 140 | 100.0000% |

State distribution:

```text
ALUR
  OWNERSHIP_BASELINE_OVERLAP_UNRESOLVED       286
  OWNERSHIP_BASELINE_UNAVAILABLE              187
  CALCULATED                                   92
  POST_BASELINE_OWNERSHIP_EVENT_UNRESOLVED     84

BNAI
  OWNERSHIP_BASELINE_UNAVAILABLE              414
  CALCULATED_AND_TEMPORAL_UPDATE               54
  CALCULATED                                   27

PGAC
  CALCULATED                                  140
```

The non-homogeneous coverage is evidence-driven, not ticker-specific implementation drift. The same resolver fails closed when a causal baseline, overlap reconciliation or later ownership event cannot be resolved. A later clean baseline can restore calculation without backfilling knowledge into earlier sessions.

## Per-shard certification

Certification root:

`C:/TSIS_Data/runtime/sec_pit_stratified_owner_exclusion_v0_1/certifications/sec_pit_7t_variable_shard_certification_v0_1_20260812T0800Z`

Stable shard function: `sha256(instrument_id) mod 4`.

```text
s0: BBBY, CNOBP
s1: ALUR, BNAI
s2: BGM, PGAC
s3: DOMH
```

All four shards contain at least one eligible case. The gate verified equivalent O/S and float schemas, equivalent component hashes, stable column order, grain and uniqueness, causal O/S and ownership baselines, the float formula, fraction/percent semantics, readable values and explicit NULL/blocker behavior.

Result: `SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING`.

Scale authorization: `NOT_GRANTED_REQUIRES_HUMAN_OR_GOVERNED_GATE`.

## Acquisition and performance evidence

The adaptive seven-case probe reused 247 previously acquired documents and fetched only 10 additional documents. The full-interval three-case extension selected and fetched 87 additional documents. Both acquisitions completed without errors, retries or HTTP 429 responses.

The Company Facts lane measured network/rate limiting as its bottleneck, not CPU or memory. This supports Python orchestration and parsing; C++ is not currently justified for this I/O-bound stage.

## Verification

The complete focused suite passed on `2026-08-11`:

```text
python -m pytest -q tests -k sec_pit
PASS
```

The certification also validates samples, not only process completion, as required by the TSIS per-variable/per-shard gate.

## Next governed gate

Do not launch 4,824 instruments yet. The next authorized design target is a 30-50 case stratified probe using the frozen implementation, schemas, policies and four-shard function.

It must report:

- no false positives and zero PIT leakage;
- exact blocker distribution and automatic retryability;
- O/S and float coverage by issuer/form/lifecycle stratum;
- storage, requests, latency and rate-limit telemetry at P50/P95/MAX;
- baseline fallback depth and document-family behavior;
- explainability of every calculated state transition;
- identical component hashes and schema across shards.

The desired result is not 100% numeric coverage. It is maximum defensible coverage with `NULL + exact blocker` everywhere evidence is insufficient.

## Authoritative runtime lineage

- adaptive case matrix: `C:/TSIS_Data/runtime/sec_pit_stratified_owner_exclusion_v0_1/probes/sec_pit_owner_exclusion_7t_adaptive_v0_4_20260812T0030Z`
- five-session O/S: `sec_pit_<ticker>_os_stratified_v0_6_20260812T0330Z`
- five-session ownership/float: `sec_pit_<ticker>_owner_adaptive_v0_14_20260812T0730Z`
- full-interval probe: `C:/TSIS_Data/runtime/sec_pit_stratified_owner_exclusion_v0_1/probes/sec_pit_owner_exclusion_3t_full_interval_v0_1_20260812T0530Z`
- full-interval O/S: `sec_pit_<ticker>_os_full_interval_v0_1_20260812T0600Z`
- full-interval ownership/float: `sec_pit_<ticker>_owner_full_interval_v0_2_20260812T0700Z`
- Company Facts: `C:/TSIS_Data/runtime/sec_pit_companyfacts_os_v0_1/runs/sec_pit_companyfacts_7t_reconciliation_v0_2_20260812T0400Z`
- shard certification: `C:/TSIS_Data/runtime/sec_pit_stratified_owner_exclusion_v0_1/certifications/sec_pit_7t_variable_shard_certification_v0_1_20260812T0800Z`

