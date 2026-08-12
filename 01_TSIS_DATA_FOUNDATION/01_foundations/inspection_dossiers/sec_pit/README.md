# SEC PIT ownership and float reconstruction — current handoff

Status: `ACTIVE_CORRECTION_LOOP_4824_DIAGNOSTIC_RUN_CONDITIONALLY_AUTHORIZED`

Last updated: `2026-08-13`

## Purpose

This is the mandatory entry point for an agent continuing the SEC PIT work. It
records the current authoritative state, what has been demonstrated, what is
still unresolved and the next governed action. Historical readouts remain
evidence; this file is the current navigation and handoff layer.

## Current authoritative result

```text
sample                         100 stratified cases
eligible common-equity cases   99
security-class halt             1 (CNOBP)
authoritative run              sec_pit_100_case_resolution_v0_13_20260812T2127Z
runtime root                   C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_13
network during resolution      0 requests
execution                      99/99 O/S + 99/99 ownership, 0 failures
daily rows                     495 (5 sessions per eligible case)
O/S complete                   56/99 = 56.57%
owner-exclusion float complete 15/99 = 15.15%
float non-NULL                 75/495 rows
physical Arrow schemas          1
duplicate keys                  0
formula/PIT violations          0
NULL float without blocker      0
```

The 15 complete-float cases are:

```text
AIEV ALUR ATMC ATMV ATYR BGM EJH ENFY IOBT ONCO PGAC PLL PTE SYTA WINT
```

Compared with v0.12, v0.13 recovered `ALUR`, `ATYR`, `ENFY`, `PTE` and
`WINT`, losing no v0.12 calculated case.

## What is already demonstrated

- selective SEC acquisition, content-addressed storage, hashes and provenance;
- no-network replay of acquired evidence;
- causal O/S and owner-exclusion state, with explicit availability dates;
- adaptive baseline-family traversal rather than latest-filing selection;
- issuer/instrument/share-class gates and explicit security-class halt;
- holder and aggregate deduplication in supported cases;
- separated fraction (`0-1`) and percentage (`0-100`) fields;
- fail-closed output: unresolved evidence produces `NULL + blocker`, never
  silent `float = O/S`;
- Company Facts is used only as exact O/S reconciliation evidence, not as float;
- one explicit physical Arrow schema across shards and NULL patterns;
- current shares are separated from options/acquirable-within-60-days shares
  when the filing makes that separation supportable.

## Why coverage remains low

This is not primarily a computation or orchestration failure. The SEC does not
publish a clean historical daily float series. The resolver must prove O/S,
availability, instrument interval, share class, current-versus-acquirable
shares, holder overlap, subsequent events and split basis simultaneously.

The 100-case sample is intentionally difficult: foreign issuers, amendments,
multiclass securities, SPAC/de-SPAC histories, ticker reuse, delistings,
pre-XBRL periods, special proxies, many Forms 4 and reverse splits. Therefore
`15.15%` must not be extrapolated directly to the full universe, but it is also
insufficient to claim broad float coverage.

## Residual blockers by measured impact

```text
SHARE_CLASS_ALLOCATION_UNRESOLVED                28 cases
INSTRUMENT_INTERVAL_CONFLICT                     25
HOLDER_OVERLAP_UNRESOLVED                        15
ECONOMIC_POSITION_OVERLAP_UNRESOLVED             14
OWNERSHIP_SPLIT_ADJUSTMENT_UNRESOLVED            10
SHARES_OUTSTANDING_UNAVAILABLE                   10
POST_BASELINE_EVENT_IDENTITY_OR_DATE_UNRESOLVED   7
BASELINE_DOCUMENT_PARTIAL                         3
OWNERSHIP_BASELINE_UNAVAILABLE                    1
AMENDMENT_FAMILY_UNRESOLVED                       1
EXISTING_BASELINE_HOLDER_ACCOUNT_SET_INCOMPLETE   1
```

Counts overlap because one case may carry multiple blockers.

## Current engineering assessment

This section is an explicit assessment, not an institutional coverage promise.

```text
automatic 4,824-case execution producing CALCULATED or NULL+blocker = viable
generalized O/S PIT with materially higher coverage                  = probable
owner-exclusion float for a broad majority                           = possible, not demonstrated
100% historical owner-exclusion float from issuer SEC filings alone = unlikely
4,824 diagnostic run after class+interval loop and four-shard PASS   = AUTHORIZED
automatic institutional promotion of the 4,824 output               = NOT GRANTED
```

The correct target is broad automatic coverage plus honest unresolved states,
not manufactured 100% coverage. A number is acceptable only when every causal
dependency is supported.

## Next governed loop

Work in this order:

1. classify all 28 share-class allocation cases into reusable document/layout
   families and true evidence gaps;
2. classify all 25 instrument-interval conflicts into false positives,
   recoverable identity bridges and genuine conflicts;
3. implement only generic rules supported by primary evidence—never
   ticker-specific production branches;
4. add unit/fixture regressions for every new semantic family;
5. execute one production-equivalent probe per each of the four governed
   shards with identical code, config, schema and policies;
6. audit formulas, PIT causality, NULL/blocker behavior, schema/type/order,
   hashes and human-readable samples;
7. only after a documented probe `PASS`, run a new immutable 99-case batch and
   publish deltas against v0.13;
8. after the share-class and interval correction loop passes all four shard
   probes, execute the human-authorized 4,824-instrument diagnostic scale run;
9. preserve `CALCULATED` and `NULL + blocker` outcomes and full denominator
   accounting; do not coerce unresolved cases into numbers;
10. treat execution authorization separately from institutional promotion—the
    resulting 4,824 output still requires its own coverage, false-positive,
    PIT, schema and reproducibility audit before downstream promotion.

Human authorization record (`2026-08-13`): after addressing the 28 measured
share-class conflicts and 25 measured instrument-interval conflicts, and only
after the mandatory four-shard production-equivalent probes pass, proceed with
the 4,824-instrument run. No additional conversational confirmation is required
for that diagnostic execution if those gates pass and the long-running
operation contract is satisfied.

## Mandatory reading for continuation

Read in this order after the repository-wide mandatory documents:

1. `SEC_PIT_100_CASE_OPTION_INCLUSIVE_AND_SCHEMA_V0_13_READOUT_v0_1.md` —
   authoritative coverage and blockers;
2. `SEC_PIT_OPTION_INCLUSIVE_CURRENT_SHARES_AND_PHYSICAL_SCHEMA_SHARD_CERTIFICATION_v0_1.md`
   — the probe gate that authorized v0.13;
3. `SEC_PIT_RESIDUAL_OWNERSHIP_LAYOUT_AND_EXPLICIT_ZERO_SHARD_CERTIFICATION_v0_1.md`
   — residual layouts and explicit-zero semantics;
4. `SEC_PIT_100_CASE_IDENTITY_DATE_AND_AGGREGATE_LOOP_READOUT_v0_1.md` — prior
   identity/date/aggregate correction loop;
5. `SEC_PIT_ADAPTIVE_BASELINE_COMPANYFACTS_FULL_INTERVAL_AND_SHARD_CERTIFICATION_READOUT_v0_1.md`
   — baseline families, Company Facts limits and earlier shard gate;
6. `C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/_DESCAGRA_DATOS_NECESARIA_/SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md`
   — governing acquisition/resolution contract.

## Git and Graphify state

All semantic changes must be committed in a focused SEC PIT commit; unrelated
Screener/CTO work must not be swept into it. A Graphify refresh is pending under
`GFQ-20260813-FOUNDATIONS-SEC-OWNER-V013-001` in the local
`GRAPHIFY_REFRESH_QUEUE.md`; it requires the coordinated Foundations SEC PIT
leaf refresh and governed root merge.
