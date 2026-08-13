# SEC PIT share-class recovery and v0.16 readout v0.1

Status: `PASS_SHARE_CLASS_CORRECTION_GATE_INTERVAL_GATE_REMAINS_OPEN`

Date: `2026-08-13`

## Decision

The bounded `SHARE_CLASS_ALLOCATION_UNRESOLVED` correction loop is complete.
The generic parser and reconciliation changes passed the versioned
classification audit, one production-equivalent probe on each governed shard,
the complete SEC PIT test suite and an immutable 99-case rerun.

This result does **not** authorize the 4,824-instrument diagnostic run yet.
The separately governed `INSTRUMENT_INTERVAL_CONFLICT` gate remains open with
25 affected cases.

## Authoritative evidence

| Artifact | Identity |
|---|---|
| classification audit | `sec_pit_share_class_recovery_audit_v0_2_20260813T0945Z` |
| classification manifest SHA-256 | `db29ee7a81ccad8e0b1430288bd869d5a248733b253faaf0bfab3d1e4da4fd1b` |
| four-shard certification | `sec_pit_share_class_shard_certification_v0_3_20260813T0940Z` |
| certification manifest SHA-256 | `cd7d8d60c8b3f65d958b364da8a2f3bf55ee50d4f492b62a5bcde82402ab02e5` |
| immutable rerun | `sec_pit_100_case_resolution_v0_16_20260813T0941Z` |
| final manifest SHA-256 | `116923d8d08d9b9f4f4aa1b5d717f58c0cad77f49bb2a5a29b3da3d5a3352ae5` |
| owner-result audit | `owner_result_audit_v0_16.json` |
| owner-result audit SHA-256 | `0c35f61ee1ff3758e84e9be5cf4bc876a7140234ff5c9cad53ff59a4fdfa746b` |
| coverage summary SHA-256 | `7e04ae7c4f8023d8aa32e6cf51df92b5a1e09e561d0fb0114f4b59cfc94c291b` |

Runtime roots:

- `C:/TSIS_Data/runtime/sec_pit_share_class_recovery_v0_2`
- `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_16`

## Classification and implemented semantics

The audit examined the 28 originally blocked cases and 97 candidates:

- 10 true multi-class cases requiring evidence;
- 8 cases with mixed blockers;
- 7 recoverable generic footnote-component layouts;
- 2 true evidence gaps that correctly remain fail-closed;
- 1 explicit-column layout.

The implementation remains generic and evidence-bound. It adds explicit and
positional current/acquirable/total table handling, accepts a dash as an
explicit current zero, permits exact same-footnote component decomposition only
when the values close exactly, preserves reported beneficial totals separately,
and reconciles management aggregates only through exact arithmetic closure.
No ticker-specific production rule or unsafe identity bridge was added.

## Four-shard production-equivalent gate

The final certification used identical code, config semantics, schema, sources
and policies on every shard:

- shard 0: `SMIT`, expected fail-closed;
- shard 1: `ASPN`, expected fail-closed;
- shard 2: `ATMV`, calculated;
- shard 3: `CLRB` and `TAOX`; `TAOX` calculated and `CLRB` retained only
  the independent interval conflict.

All four shards had equivalent ordered schemas and component hashes. Formula,
grain, uniqueness, PIT causality, NULL/blocker behavior and readable samples
passed. The complete focused SEC PIT suite passed: `243 passed` across 58
test files.

## Authoritative v0.16 result

`v0.14` is invalid and non-authoritative because its launch omitted the frozen
Company Facts input. `v0.15` restored that input and exposed a regression that
was corrected before the final run. Only `v0.16` is authoritative.

The v0.16 batch completed:

```text
eligible cases                 99
O/S executions                 99/99
ownership executions           99/99
failed executions              0
network requests               0
O/S complete                   56/99 = 56.57%
owner-exclusion float complete 16/99 = 16.16%
float non-NULL                 80/495 rows
share-class blocker            26 cases
instrument-interval blocker    25 cases
```

There were no O/S regressions and no losses among the previous 15 calculated
float cases. `TAOX` is the newly recovered complete case:

```text
O/S                     7,128,912
excluded current shares   166,989
owner-exclusion float   6,961,923
float percent           97.657581
```

The 16 calculated cases are:

```text
AIEV ALUR ATMC ATMV ATYR BGM EJH ENFY IOBT ONCO PGAC PLL PTE SYTA TAOX WINT
```

Exact material deltas versus authoritative v0.13:

- `TAOX` becomes calculated;
- `MBI` and `SNES` lose the share-class blocker but retain independent
  blockers;
- `SMIT` gains the correct share-class blocker because its aggregate does not
  close exactly; the older result was too permissive;
- `CLRB` has no net regression and retains only its interval blocker;
- `ATMV` remains calculated through exact affiliate closure.

The 26 residual share-class cases are:

```text
ACTT AEN ASPN AULT AXAC BASI BLNG BNED BWAQ CDAQ CORR CPTK DOMH FORL GPUS
HEPA IDR IPXX MULN NIVF OMCC OSG SCON SMIT SOFO TIRX
```

## Gate disposition

The share-class gate passes with measured residuals because the correction is
generic, tested, shard-equivalent, causally auditable and fail-closed. Its
measured coverage gain is modest: `15/99 -> 16/99`, while the class blocker
count falls from 28 to 26.

The next governed loop is the 25-case instrument-interval classification and
correction gate. It must repeat the mandatory sequence: classification,
generic implementation, tests, one production-equivalent probe per shard,
versioned certification and a new immutable 99-case rerun. The 4,824 run
remains blocked until that second gate passes.
