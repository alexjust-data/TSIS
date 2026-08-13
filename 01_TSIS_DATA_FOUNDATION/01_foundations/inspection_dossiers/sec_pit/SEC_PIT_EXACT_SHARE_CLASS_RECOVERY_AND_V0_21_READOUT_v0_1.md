# SEC PIT exact share-class recovery and v0.21 readout v0.1

Status: `PASS_EXACT_SHARE_CLASS_GATE_V0_21_AUTHORITATIVE_4824_NOT_LAUNCHED`

Date: `2026-08-13`

## Decision

`sec_pit_100_case_resolution_v0_21_20260813T2135Z` is the authoritative
99-case result. It replaces v0.19 as current authority and explicitly
supersedes diagnostic v0.20.

v0.20 completed 99/99 O/S and ownership executions without runtime failures,
but its post-run delta audit exposed semantic regressions. It is therefore not
authoritative. The corrected v0.21 passed the complete SEC PIT test suite,
one production-equivalent probe on every governed shard, the 99-case result
audit, schema equivalence, formula checks, PIT checks and output-hash checks.

The 4,824-instrument run was not launched and remains unauthorized by this
readout.

## Authoritative evidence

| Artifact | Identity |
|---|---|
| four-shard certification | `sec_pit_share_class_shard_certification_v0_5_20260813T2130Z` |
| certification manifest SHA-256 | `4ee18be62077a9d92d2c98f1418c06870fbee47591250e5e5a2a2e1c1829fb4e` |
| immutable rerun | `sec_pit_100_case_resolution_v0_21_20260813T2135Z` |
| batch manifest SHA-256 | `a789f170f04632b58df4c08f93897fa6086af454487b8fce862fc8ee0d1a9261` |
| owner-result audit SHA-256 | `44330ce3ab90c667ec547267289f1580a74b48a9c00a17d0db8e9ed2d3008cbc` |
| coverage summary SHA-256 | `a7031126fcc31d86b1b62d79bd82fd1506d891026b5e71b9e38977c71d22ea8f` |

Runtime root:

`C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_21`

## Power-loss recovery checkpoint

This checkpoint was recorded after the terminal monitor state
`COMPLETE / FINAL`, with `wrapper_alive=False`, 99/99 O/S executions, 99/99
ownership executions and zero failures. v0.21 is finished: do not resume or
relaunch it. Any further semantic correction must use a new versioned run after
repeating the governed four-shard probe gate.

Exact recovery locations:

| Purpose | Path |
|---|---|
| immutable batch | `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_21/batches/sec_pit_100_case_resolution_v0_21_20260813T2135Z` |
| terminal manifest | `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_21/batches/sec_pit_100_case_resolution_v0_21_20260813T2135Z/final_manifest.json` |
| governed result audit | `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_21/owner_result_audit_v0_21.json` |
| governed coverage summary | `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_21/coverage_summary_v0_21/summary.json` |
| four-shard certification | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit/evidence_assets/sec_pit_share_class_shard_certification_v0_5_20260813T2130Z` |
| executed parser source | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/ownership_v2.py` |
| parser regression tests | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/test_sec_pit_ownership_v2.py` |

Executed source identity:

```text
ownership_v2.py SHA-256                 0dddddbaff560cd23241e56236ce56c3a765df371984ec9e2b78cfde5f8a9aa4
test_sec_pit_ownership_v2.py SHA-256   738a210db270fa9953c15785ae84adefd2dca461b347ddbac7b89d684eb60bbb
```

Git checkpoint captured before publication:

```text
branch        integrate/main-data-quality-dossiers-20260613
capture state v0.21 source, tests and evidence were captured in a dirty working
              tree shared with unrelated pre-existing changes before publication
```

When this readout is obtained from Git, the commit containing this file is the
published checkpoint authority. Resolve it with
`git log -1 -- <this-readout-path>`; the historical dirty-tree warning above no
longer describes the checkout after that commit is applied.

The next agent must preserve unrelated changes, verify the hashes above and
start from the residual blocker order in `Gate disposition`. The immediate
engineering loop is exact closure of the remaining 34
`SHARE_CLASS_ALLOCATION_UNRESOLVED` cases, followed by split-basis and causal
post-baseline work. The 4,824-instrument run remains explicitly unauthorized.

## Implemented semantics

The parser now admits only evidence-bound recovery paths:

- explicit current/acquirable columns, including explicit dash-as-zero;
- exact footnote component closure, including an all-acquirable current zero;
- exhaustive named lists of options/awards with exact individual and aggregate
  subtraction;
- exact Class A/Class B columns aligned through HTML colspans;
- integer share components only; missing class cells never imply zero;
- local table context for multi-class detection instead of unrelated
  document-wide class mentions;
- generic SEC beneficial-ownership definitions do not by themselves prove
  that a reported position contains options or warrants.

No ticker-specific production rule was introduced.

## v0.20 rejection and v0.21 correction

v0.20 measured 27/99 complete float cases and exposed five losses relative to
v0.19. The detector was narrowed and exact named-component recovery restored
PTE before v0.21. Regression probes covered AIFE, MPO, PTE, TAOX, VISL and
BNED; share-class production probes covered ACTT, CPTK, TIRX and HEPA.

v0.21 deliberately keeps four former v0.19 calculations fail-closed:

- `AIFE`: target-class allocation does not close across the Class A/B context;
- `MPO`: reported beneficial ownership includes options/RSUs without complete
  exact current-share closure for the selected baseline;
- `TAOX`: member and aggregate option components do not close completely;
- `VISL`: reported positions include options/RSUs and the aggregate cannot be
  reconstructed exactly from the disclosed components.

These are corrections to prior over-permissive results, not runtime
regressions. `BNED` is the new complete-float recovery. `PTE` is retained
through an exhaustive named acquirable-component list.

## Authoritative coverage

```text
eligible cases                 99
O/S executions                 99/99
ownership executions           99/99
failed executions              0
network requests               0
O/S complete                   71/99 = 71.72%
owner-exclusion float complete 28/99 = 28.28%
float non-NULL                 140/495 rows
share-class blocker            34 cases
```

The 28 complete-float cases are:

```text
AGL AIEV ALUR ATMC ATMV ATYR AUMN AYRO BGM BNED CYTO EJH ENFY INPX IOBT
MBI MTEM NHTC ONCO PGAC PLL PTE SHYF SNES STAF SYTA VIVE WINT
```

The larger share-class blocker count is intentional: v0.21 applies the
current-versus-acquirable and class-allocation contract consistently to all 99
cases and exposes positions that older runs accepted too permissively.

## Gate disposition

The exact share-class correction gate passes with measured residuals. v0.21 is
authoritative because it is more semantically correct than the numerically
higher v0.19 result. Coverage must not be maximized by treating option-inclusive
beneficial ownership as currently issued ownership.

Next priority order:

1. exact residual share-class/current-component closure;
2. ownership split-basis reconciliation;
3. causal post-baseline event identity/date application;
4. holder/economic overlap residuals;
5. no 4,824-instrument launch without a new explicit operator decision.
