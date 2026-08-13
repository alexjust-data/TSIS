# SEC PIT instrument-interval recovery and v0.18 readout v0.1

Status: `PASS_INSTRUMENT_INTERVAL_GATE_4824_DIAGNOSTIC_NOT_LAUNCHED`

Date: `2026-08-13`

## Decision

The bounded `INSTRUMENT_INTERVAL_CONFLICT` correction loop is complete. The
blocker falls from 25/99 eligible cases in authoritative v0.16 to 0/99 in
authoritative v0.18. The implementation is generic, evidence-bound, tested,
equivalent across all four governed shards and fail-closed.

The 4,824-instrument diagnostic run was not launched. Although the earlier
human authorization conditions have now been technically satisfied, the
operator explicitly instructed that the scale run must remain unlaunched while
this closeout is completed and reviewed. Institutional promotion remains
separately unauthorized in all cases.

## Authoritative evidence

| Artifact | Identity |
|---|---|
| classification audit | `sec_pit_instrument_interval_recovery_audit_v0_2_20260813T1040Z` |
| classification manifest SHA-256 | `ba72702ce10bd0c094e85cead07f457c201b244c2dfd278253aaf83e691b9867` |
| four-shard certification | `sec_pit_instrument_interval_shard_certification_v0_2_20260813T1610Z` |
| certification manifest SHA-256 | `e9d5bfc07eb71a974fcecd2067a752d9b9da496c2a08eef4795133981eefe61d` |
| immutable authoritative rerun | `sec_pit_100_case_resolution_v0_18_20260813T1400Z` |
| final manifest SHA-256 | `70492ab9603fec8c8f232fd015b6397c6a58d5313ed4c781c86198f72a306953` |
| owner-result audit | `owner_result_audit_v0_18.json` |
| owner-result audit SHA-256 | `3258cf2db478e58eef28461b2a6b05364daeb7339a9faed1e9d9c74bbdeb2611` |
| coverage summary SHA-256 | `8b0ddd2a468e0fcc0988163f032c4eb4fc87d6c2e86a265f98a05e19be6cf66b` |

Runtime roots:

- `C:/TSIS_Data/runtime/sec_pit_instrument_interval_shard_probes_v0_2`
- `C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_18`

The frozen Company Facts input remained present with SHA-256
`6647ae0b44c6e05d38e5fb4f099895afeca8d8591ea653f090013d3dc1f69e24`.
Resolution used zero network requests.

## Classification and implemented semantics

The no-network audit classified all 25 originally blocked cases and 355
document candidates. It found:

- 264 target-CIK common-equity continuity candidates;
- 27 issuer-filed baseline metadata continuity candidates;
- 7 documents from an explicit non-target issuer;
- 28 documents for an explicit non-target security;
- 29 initially unsupported identity/class gaps across six mixed cases.

The resolver now admits continuity only through governed issuer CIK, trusted
issuer-name continuity, common-equity evidence or an exact target-class CUSIP.
It rejects explicit other-issuer CIKs, names linked to those CIKs, non-common
security rows and explicit non-target class CUSIPs. Schedule cover-page parsing
handles values before labels and plain-text colon layouts. Issuer comparison is
restricted to the extracted issuer field, never the whole filing body. A
limited long-token singular/plural normalization resolves forms such as
`Tanker`/`Tankers` without admitting unrelated issuers.

No ticker-specific production branch was added. A ticker-reuse conflict still
cannot be bridged by these rules, and unsupported evidence remains NULL with an
explicit blocker.

## Probe and regression gates

The final production-equivalent certification repeated the full variable audit
with identical code, config semantics, sources, policies and ordered schemas:

- shard 0: `BBBY`;
- shard 1: `MCAC`;
- shard 2: `SNMP`;
- shard 3: `OSG`.

All four shards passed grain, uniqueness, formula, PIT causality, explicit
NULL/blocker behavior, readable-value sampling, schema equivalence and
component-hash equivalence. The complete SEC PIT test suite passed at 100%
(258 test functions across 60 files).

Diagnostic v0.17 was not accepted as authority because it introduced four
interval regressions (`CYTO`, `NAT`, `SENEB`, `SINT`). Dedicated microprobes
then demonstrated `unresolved=0` and no interval blocker for all four. The full
v0.18 rerun also removes the two older v0.17 residuals in `AULT` and `IDR`.

## Authoritative v0.18 result

```text
eligible cases                    99
O/S executions                    99/99
ownership executions              99/99
failed executions                 0
network requests                  0
owner-result audit                PASS (99/99)
O/S complete                      56/99 = 56.57%
owner-exclusion float complete    16/99 = 16.16%
float non-NULL                    80/495 rows
INSTRUMENT_INTERVAL_CONFLICT      0 cases (was 25)
```

The 16 calculated cases are unchanged from v0.16:

```text
AIEV ALUR ATMC ATMV ATYR BGM EJH ENFY IOBT ONCO PGAC PLL PTE SYTA TAOX WINT
```

Therefore this loop removes a false upstream barrier but does not itself add a
new calculated case. This is a correct fail-closed outcome: every recovered
case still lacks at least one different causal dependency.

## What “downstream blockers were exposed” means

`INSTRUMENT_INTERVAL_CONFLICT` was an upstream identity gate. While it was
present, the resolver could not safely decide whether ownership documents
belonged to the target instrument interval, so it stopped before relying on
later evidence. Once target and non-target documents were separated correctly,
the resolver was able to evaluate the next dependency for each case. It then
reported the actual remaining reason a number cannot yet be calculated.

Counts overlap because one case can have more than one blocker:

| Remaining blocker | Cases | Meaning | Required work |
|---|---:|---|---|
| `SHARE_CLASS_ALLOCATION_UNRESOLVED` | 26 | Ownership evidence cannot be allocated exactly to the target common-share class. | Continue only with exact class/component evidence; retain measured residuals otherwise. |
| `HOLDER_OVERLAP_UNRESOLVED` | 21 | Holder rows may describe the same account/person/group more than once. Summing them could double count excluded shares. | Reconcile reporting groups, members, direct/indirect accounts and repeated snapshots with evidence-backed precedence. |
| `ECONOMIC_POSITION_OVERLAP_UNRESOLVED` | 20 | Reported totals, current shares, options and acquirable-within-60-days positions overlap economically. | Separate current ownership from derivative/future rights and prove exact component closure before subtraction. |
| `SHARES_OUTSTANDING_UNAVAILABLE` | 17 | No admitted causal O/S anchor exists for all target sessions. Ownership alone cannot yield float. | Recover exact class-level historical O/S from primary filings or governed Company Facts reconciliation without crossing class/interval boundaries. |
| `OWNERSHIP_SPLIT_ADJUSTMENT_UNRESOLVED` | 12 | Ownership and O/S observations may be expressed on different pre/post-split bases. | Link the causal split event, effective session, factor and target class, then adjust both sides consistently. |
| `POST_BASELINE_EVENT_IDENTITY_OR_DATE_UNRESOLVED` | 7 | A later Form 3/4/5 or ownership event exists, but its holder/account, transaction date, class or application order cannot be proven. | Build a causal post-baseline update ledger and apply only events with resolved identity, date, class and precedence. |
| `BASELINE_DOCUMENT_PARTIAL` | 3 | The selected opening ownership document is incomplete for the methodology. | Traverse to a content-complete causal baseline or retain NULL. |
| other one-case residual families | 3 | Baseline absence, unresolved amendment family, or incomplete existing holder-account set. | Resolve each generic evidence family; no manual numeric imputation. |

The main coverage implication is that removing an upstream blocker does not
guarantee a calculated result. Float requires all of the following at once:
causal O/S, target instrument/class continuity, complete ownership baseline,
non-overlapping current economic positions, correct split basis and all
material post-baseline updates. Any unresolved dependency keeps the output
NULL.

## Gate disposition and next work

The instrument-interval gate is `PASS_WITH_MEASURED_DOWNSTREAM_RESIDUALS`.
Authoritative v0.18 supersedes v0.16 only for the interval-correction state;
v0.17 remains diagnostic and non-authoritative.

The next bounded recovery work should prioritize:

1. `SHARES_OUTSTANDING_UNAVAILABLE`, because it directly constrains both O/S
   and float coverage;
2. the paired holder/economic overlap families, because they block the largest
   ownership cohort after share-class residuals;
3. split-basis reconciliation;
4. causal post-baseline event application.

No 4,824-instrument diagnostic execution was started as part of this closeout.
Before any future launch, the operator must deliberately re-open that action
and the long-running operation contract must still be satisfied. Any scale
output must preserve full denominator accounting and `CALCULATED` versus
`NULL + blocker`; it cannot be promoted automatically.
