# SEC PIT ownership and float reconstruction — current handoff

Status: `V0_21_AUTHORITATIVE_4824_PREFLIGHT_PASS_METADATA_COHORT_01_AWAITING_HUMAN_LAUNCH`

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
authoritative run              sec_pit_100_case_resolution_v0_21_20260813T2135Z
runtime root                   C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_21
network during resolution      0 requests
execution                      99/99 O/S + 99/99 ownership, 0 failures
daily rows                     495 (5 sessions per eligible case)
O/S complete                   71/99 = 71.72%
owner-exclusion float complete 28/99 = 28.28%
float non-NULL                 140/495 rows
physical Arrow schemas          1
duplicate keys                  0
formula/PIT violations          0
NULL float without blocker      0
```

The 28 complete-float cases are:

```text
AGL AIEV ALUR ATMC ATMV ATYR AUMN AYRO BGM BNED CYTO EJH ENFY INPX IOBT
MBI MTEM NHTC ONCO PGAC PLL PTE SHYF SNES STAF SYTA VIVE WINT
```

v0.21 preserves v0.19 O/S at 71/99 and corrects four over-permissive historical
float calculations (`AIFE`, `MPO`, `TAOX`, `VISL`) while recovering `BNED`.
Diagnostic v0.20 is non-authoritative because its delta audit found semantic
regressions before the corrected four-shard v0.21 certification.

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
`28.28%` must not be extrapolated directly to the full universe, but it is also
insufficient to claim broad float coverage.

## Residual blockers by measured impact

```text
SHARE_CLASS_ALLOCATION_UNRESOLVED                34 cases
OWNERSHIP_SPLIT_ADJUSTMENT_UNRESOLVED            12
POST_BASELINE_EVENT_IDENTITY_OR_DATE_UNRESOLVED  10
SHARES_OUTSTANDING_UNAVAILABLE                    7
HOLDER_OVERLAP_UNRESOLVED                         7
ECONOMIC_POSITION_OVERLAP_UNRESOLVED              4
BASELINE_DOCUMENT_PARTIAL                         2
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
instrument-interval correction gate                                 = PASS
4,824 descending no-network preflight                               = PASS
metadata cohort 01 (824 ticker rows)                                = AWAITING HUMAN LAUNCH
primary-document acquisition                                        = NOT AUTHORIZED
automatic institutional promotion of the 4,824 output               = NOT GRANTED
```

The interval, O/S-unavailable and paired-overlap bounded correction gates have
passed with measured residuals. O/S is now 71/99 and safe float is 28/99. Removing
overlap exposed additional genuine split and post-baseline dependencies; those
later blockers remain fail-closed. The correct target is broad automatic
coverage plus honest unresolved states, not manufactured 100% coverage.

## Next governed loop

Work in this order:

1. treat v0.21 as current authority and v0.20 as a rejected diagnostic;
2. prioritize exact share-class allocation, split-basis reconciliation and
   causal post-baseline event application;
3. keep every residual fail-closed and repeat tests, four-shard probes,
   certification and immutable 99-case deltas for each semantic change;
4. use the frozen `824/1000/1000/1000/1000` descending cohorts and launch only
   metadata cohort 01 under the human-controlled long-run contract;
5. review metadata, identity/lifecycle conflicts, selection volume and capacity
   before any separately authorized primary-document acquisition;
6. preserve `CALCULATED` and `NULL + blocker` outcomes and treat execution
   separately from institutional promotion.

Operator direction (`2026-08-13`): the previous leave-unlaunched instruction is
reopened only for governed preparation and sequential execution. The parent
universe is frozen as `824/1000/1000/1000/1000`, starting with 2026 rows and
moving backwards. The no-network preflight is complete; metadata cohort 01 is
the next human-controlled run. Primary documents and promotion remain closed.
Read `SEC_PIT_4824_DESCENDING_PREFLIGHT_READOUT_v0_1.md` and the CTO execution
plan before launch.

## Mandatory reading for continuation

Read in this order after the repository-wide mandatory documents:

Start with `SEC_PIT_EXACT_SHARE_CLASS_RECOVERY_AND_V0_21_READOUT_v0_1.md`,
which is the current authority for coverage, residuals and operating direction.
Then read the v0.19 O/S/overlap and v0.18 interval readouts for the preceding
gates.

1. `SEC_PIT_100_CASE_OPTION_INCLUSIVE_AND_SCHEMA_V0_13_READOUT_v0_1.md` —
   historical v0.13 coverage and blockers; it is not current authority;
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
Screener/CTO work must not be swept into it. The descending acquisition plan is
queued once under `GFQ-20260813-CTO-SEC-4824-DESCENDING-001` in
`00_CTO/GRAPHIFY_REFRESH_QUEUE.md` for a coordinated CTO/Foundation leaf refresh.

## Power-loss restart pointer

The exact terminal paths, artifact hashes, executed source/test hashes, branch
and dirty-working-tree warning are recorded in the current v0.21 readout under
`Power-loss recovery checkpoint`. At this checkpoint no long SEC PIT run is
active. Do not resume v0.21: it is complete. The new full-universe preparation
authority is the immutable preflight root
`runtime/sec_pit_4824_descending_acquisition_v0_1/preflight_20260813T215254Z`.
If metadata cohort 01 is interrupted, resume only that run with its frozen input
hash and `--resume`; do not start a duplicate writer or advance to cohort 02.
