# SEC PIT PGAC ownership and owner-exclusion probe readout v0_1

Date: `2026-08-11`

Status: `EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING`

Successful run ID: `sec_pit_pgac_owner_exclusion_v0_2_20260811T1530Z`

Superseded blocked run ID: `sec_pit_pgac_owner_exclusion_v0_1_20260811T1500Z`

## Decision

The no-network PGAC probe completed automated stages S6 through S8 using a
parameterized implementation with no ticker-specific arithmetic, holder-name
exceptions or accession-specific resolution rules. The result is evidence
ready for the S9 human audit. It is not a freely tradable-float result, does not
include global 13F ownership and does not authorize materialization over the
4,824-instrument parent universe.

```text
S5 O/S manual gate                         PASS_HUMAN_CONFIRMED_2026_08_11
S6 neutral ownership extraction            PASS_WITH_RESTRICTIONS
S7 holder and class reconciliation         PASS_WITH_RESTRICTIONS
S8 owner-exclusion float                    PASS_WITH_RESTRICTIONS
S9 float-change audit                       HUMAN_CONFIRMATION_PENDING
network requests                            0
```

## Automation contract

PGAC enters the runner only through governed configuration and locally acquired,
hashed source evidence. Production logic does not contain `PGAC`, its CIK,
accession numbers, ownership values or holder names. The same components accept
any instrument configuration with the same schemas and policies:

```text
selection plan + acquisition ledger + metadata inventory + daily O/S state
    -> document identity and issuer-name continuity
    -> neutral ownership source observations
    -> class-specific holder components
    -> holder/economic-position reconciliation
    -> methodology-scoped exclusions
    -> daily PIT owner-exclusion float or explicit NULL plus blockers
```

The implementation is fail closed. Unsupported class allocation, missing
identity continuity, unresolved methodology-relevant overlap or absent causal
baseline prevents calculation instead of substituting a ticker-specific guess.

## Preserved failed run and correction

The first run is retained as evidence. It processed the ownership corpus but
blocked all 140 float rows because the generic name-change extractor did not
recognize filing phrases such as `effected a name change from` and longer
`change ... Company's name from` constructions with typographic quotation
marks.

The correction broadened only the generic linguistic grammar and added
ticker-neutral regression cases. The second run then reconstructed the issuer
identity chain from primary evidence:

```text
Shepherd Ave Capital Acquisition Corporation
    -> Aifeex Nexus Acquisition Corporation
    -> Pantages Capital Acquisition Corporation
```

No historical run was overwritten.

## Source coverage

```text
ownership candidate documents              47
ownership acquired documents               47
documents processed                         47
documents producing normalized rows         43
identity continuity                         COMPLETE
target-class CUSIP                          G8089R100
opening proxy accession                     0001213900-25-064856
opening proxy measured at                    2025-07-15
opening proxy eligible session               2025-07-18
```

Two historical institutional Schedule 13G accessions did not yield broad
structured rows: `0001376474-24-000733` and `0001846718-24-000026`. They remain
explicit restrictions on broad ownership extraction. They do not block this
methodology because generic institutional 5/10/20 percent positions are not
authorized owner exclusions and all methodology-relevant source families were
resolved.

## Exact target-class reconciliation

The opening proxy reports combined Class A and Class B beneficial ownership.
It was not subtracted directly from Class A O/S. Exact components extracted
from Schedule 13D and Forms 3 reconcile the seven proxy rows:

```text
proxy insider/affiliate total             2,400,500
Class B sponsor component                 1,936,250
Class B officer/director components         220,000
Class A sponsor component                   244,250
                                         ---------
reconciled total                          2,400,500
```

The aggregate officer/director row is non-additive. Individual director and
officer positions are supported as Class B and therefore contribute zero to
the target Class A exclusion. The sponsor is supported as an explicit affiliate
and contributes one Class A economic position of 244,250 shares.

```text
proxy position rows                         7
class component rows                        8
aggregate non-additive rows                 1
methodology-relevant rows                   6
explicit-affiliate rows                     1
unresolved methodology-relevant rows        0
supported Class A exclusion shares          244,250
```

Schedule 13D/G joint reporting rows are normalized and deduplicated in the
broad ledger. Institutional Schedule 13G positions remain neutral and are not
subtracted.

## Daily PIT result

The daily series covers the governed PGAC observed interval and uses only the
ownership baseline available before each session.

```text
sessions                                    140
rows                                        140
duplicate instrument-session rows             0
future-baseline rows                           0
NULL float rows                                0
rows with blockers                             0
estimation state                         CALCULATED (140)
shares outstanding                         8,869,250
unique supported excluded shares             244,250
owner-exclusion float                       8,625,000
float fraction                           0.97246103
float percent                            97.24610311
```

The single emitted explanation is the initial state on `2025-08-15`, backed by
proxy accession `0001213900-25-064856`, eligible from `2025-07-18`. There is no
later supported methodology-relevant change within the observed interval.

`float_fraction_estimate_as_known` is a ratio on `[0, 1]` and
`float_percent_estimate_as_known` is a percentage on `[0, 100]` under schema
`sec_pit_resolved_daily_states_v0_2`.

## Reproducibility

The successful run persists a pre-manifest, final manifest, component/config/
input/output SHA-256 hashes, document dispositions, neutral observations,
class components, both holder ledgers, coverage and reconciliation readouts,
daily states, change explanations and a variable audit. It used
`NO_NETWORK_LOCAL_OBJECT_REPLAY` and made zero network requests.

Verification completed:

```text
focused ownership/holder/float tests         21 PASS
full test_sec_pit_*.py suite                126 PASS
daily grain and uniqueness                   PASS
PIT causality                                PASS
fraction and percent units                   PASS
source and output manifests                  PASS
```

Active heavy-data work resolves through `G:/TSIS/data`. Historical `E:` paths
remain provenance and are not silently rewritten.

## What this proves and what it does not

This proves that the selected PGAC evidence can be converted automatically
into neutral ownership observations, exact class allocations, a deduplicated
methodology-scoped holder state and a causal daily owner-exclusion float.

It does not yet prove universal parser coverage, freely tradable supply,
institutional ownership from global 13F information tables or operational
scalability over 4,824 instruments.

## Mandatory path to 4,824 instruments

The next governed gate must reuse these exact components, schemas and policies:

1. obtain S9 human confirmation for the one PGAC float state/change;
2. execute stratified difficult multi-ticker probes, including multi-class,
   renamed, delisted and sparse-evidence instruments;
3. remove generic parser gaps or preserve explicit blocker outcomes;
4. execute one bounded production-equivalent probe in every planned shard;
5. audit every variable, schema, grain, PIT rule, NULL/blocker state and shard
   equivalence;
6. publish a versioned certification readout;
7. only then authorize the long 4,824-instrument materialization.

Automation does not mean forcing a numeric value for every ticker. A reliable,
auditable `NULL` with precise blocker codes is the required result whenever the
SEC evidence cannot support the requested state.
