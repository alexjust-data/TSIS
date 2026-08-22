# SEC PIT Implementation Readout v0_1

## Control

~~~
document_id = sec_pit_implementation_readout
document_version = v0_1
status = BNAI_V0_40_G7_PASS_G8_OS_RECONCILED_BLOCKED
updated_at = 2026-08-10
canonical_promotion = NOT_AUTHORIZED
full_scale_4821 = NOT_AUTHORIZED
~~~

## Current authoritative experimental run

~~~
D:/TSIS/fundamental_context/sec_pit_v0_1/runs/
sec_pit_bnai_g8_os_reconciliation_v0_40_20260810
~~~

The run completed with 496 daily O/S, float and tradability rows. G7 produced
82 non-null owner-exclusion estimates from 2025-11-07 onward. The 414 earlier
sessions remain NULL because no complete ownership baseline was available. The
two Forms 4 available on 2025-12-17 are resolved sequentially by transaction
date; only the latest direct-account balance of 15,727 shares is applied. G8
tradability remains NULL for all sessions.


## v0_40 audited registration/O/S reconciliation result

~~~
registration scope classifier v0_2 = PASS
registration/O/S capacity subgate = PASS_WITH_RESTRICTIONS
G7 = PASS_WITH_RESTRICTIONS
G8 = BLOCKED_BY_INPUT_GATES
~~~

The v0.2 clause classifier corrected four components previously misclassified
as issued. The corrected 28-row scope is:

~~~
18 = CONTINGENT_OR_FUTURE
6  = reported-current issued/held/transferred candidates
4  = non-component aggregate/threshold evidence
~~~

All six reported-current candidates were reconciled against the causal O/S
state on their first eligible trading session. All six are numerically
consistent with known O/S capacity; four use a reported anchor and two use a
stale anchor. This is a consistency check only:

~~~
OS capacity consistent = 6
OS conflicts = 0
OS unavailable = 0
OS inclusion confirmations = 0
tradable-supply confirmations = 0
non-null daily tradability estimates = 0
~~~

The ledger must not be interpreted as proving that each component was included
in a specific O/S anchor or entered freely tradable supply. G8 remains blocked
by lockup, restrictive-legend, resale-condition and methodology gates. Run
`v0_39` is retained as intermediate evidence for the classifier correction;
`v0_40` is the current authoritative experimental run.

## v0_38 audited G7/G8 condition result

~~~
G7 = PASS_WITH_RESTRICTIONS
G8 = BLOCKED_BY_INPUT_GATES
registration component condition subgate = PASS_WITH_RESTRICTIONS
~~~

The governed component-condition ledger contains 28 classified registration
components. Of these, 24 are applicable share components and all 24 link to a
causal EFFECT notice by SEC file number. Four aggregate/threshold rows are
explicitly non-components. The resolver preserves:

~~~
14 = ISSUANCE_OR_EXERCISE_UNCONFIRMED
10 = RESALE_REGISTRATION_EFFECTIVE_RESTRICTIONS_UNRESOLVED
4  = NOT_APPLICABLE_NON_COMPONENT
0  = tradable supply confirmations
0  = non-null tradability contributions
~~~

EFFECT proves registration effectiveness only. It does not prove exercise,
issuance, legend removal, lockup release, actual resale or entry into tradable
supply. G8 therefore remains blocked by O/S reconciliation, lockup/legend/resale
conditions and the absence of an authorized tradability methodology.

Run `v0_37` is non-authoritative diagnostic evidence: it used the default
100-document cap instead of the governed 300-document pilot scope and omitted
required EFFECT/424B3 evidence. The empty-input resolver was subsequently
hardened to return `BLOCKED_BY_INPUT_GATES` rather than a pass.

## v0_36 audited G7/G8 result

~~~
G6 row-level economic resolution = PASS
G6 temporal authority = DAILY_FLOAT_RESOLVER
post-baseline temporal updates = COMPLETE
G7 = PASS_WITH_RESTRICTIONS
G8 = BLOCKED_BY_INPUT_GATES
~~~

The owner-exclusion baseline is the DEF 14A available from 2025-11-07. Its
supported excluded issued-common total is 9,956,985 shares. Two filing conflicts
are preserved under explicit precedence rules: the transfer-agent-backed table
value for Paul Chang and the explicitly stated 46,686 common-share component for
Michael Zacharski. Neither conflict is erased.

~~~
414 sessions = OWNERSHIP_BASELINE_UNAVAILABLE
27 sessions = CALCULATED_WITH_SOURCE_CONFLICT
55 sessions = CALCULATED_WITH_SOURCE_CONFLICT_AND_TEMPORAL_UPDATE
~~~

The post-baseline events available on 2025-12-17 are resolved from transaction
dates 2025-12-12 and 2025-12-15; the latest account snapshot is selected and
the two balances are not added. This is an experimental partial PIT estimate,
not canonical float and not authorization for scanner or backtest consumption.

G8 has executed. The runner extracted 61/61 scoped 424B3 documents, linked all
four EFFECT file numbers to registration evidence, and preserved one source
conflict in registration family 333-278673. EFFECT and 424B3 establish
registration eligibility and mixed issued/contingent components; they do not
identify confirmed tradable supply or resolve selling-holder share lots and
conditions.

## Implemented evidence pipeline

~~~
SEC metadata-first acquisition
content-addressed compressed storage
conservative eligible-session policy
Company Facts and cover-page O/S candidates
strict O/S reconciliation and admitted anchors
daily PIT O/S resolution
Forms 3/4/5 structured ownership
DEF 14A ownership tables
legacy SC 13D/G cover sheets
modern SCHEDULE 13G XML
instrument-validity-scoped holder ledger
broad issuer holder ledger retained separately
G7 owner-exclusion methodology contract/config
restriction-document acquisition evidence
EFFECT XML eligibility events
daily blocked-state G7/G8 outputs
governed manifests, heartbeat, readouts and tests
~~~

## Ownership coverage G5

~~~
broad issuer ownership inventory = 80 accessions
BNAI instrument-scope inventory = 49
selected = 49
acquired = 49
structured extraction attempted = complete
expected position documents left empty = 0
structured extraction = complete
~~~

The operational holder ledger is restricted to:

~~~
instrument valid_from = 2024-03-15
instrument valid_to = 2026-03-09
~~~

Predecessor/SPAC evidence remains in holder_position_ledger_broad.parquet and is
not consumed by G6/G7 for the BNAI class.

## Holder ledger G6

~~~
broad source positions = 97
instrument-scope positions = 76
unique holder identities = 34
missing holder identities = 0
row-level methodology-relevant positions unresolved = 0
row-level economic position resolution = complete
temporal position update resolution = incomplete
~~~

Name-only identities are retained as candidate identities, never silently
merged. Aggregate groups, controlled entities, direct/indirect positions and
derivative-inclusive proxy values still require economic-position resolution.

## G7 owner-exclusion methodology

Methodology:

~~~
officer_director_explicit_affiliate_v0_1
experimental execution = AUTHORIZED
canonical promotion = NOT AUTHORIZED
~~~

The methodology excludes only supported current officers, directors, explicit
affiliates and control persons. It does not automatically exclude institutions
or every holder above a percentage threshold. Derivatives are not deducted
before issued-common status, aggregate group rows are non-additive and each
economic position may be deducted once.

Current result:

~~~
G7 = PASS_WITH_RESTRICTIONS
non-null float rows = 82
ownership baseline unavailable rows = 414
post-baseline temporal update rows = 55
post-baseline temporal update resolution = complete
historical ownership coverage = incomplete
~~~

Coverage, row-level economic resolution and experimental methodology
authorization passed. Canonical promotion remains unauthorized.

## G8 restrictions and tradability

~~~
instrument-scope restriction inventory = 122
selected = 122
acquired = 122

forms:
- 424B3 = 61
- 8-K = 47
- 8-K/A = 2
- S-1 = 5
- S-1/A = 3
- EFFECT = 4

EFFECT expected = 4
EFFECT extracted = 4
424B3 expected = 61
424B3 extracted = 61
EFFECT-to-registration file-number links = 4/4
unlinked EFFECT file numbers = 0
registration component source conflicts = 1
selling-holder share-lot rows = 62
selling-holder file-number families = 4
registration-to-selling-lot links = 4/4
exact registration/lot reconciliations = 3
registration/lot mismatches = 0
mixed issuer-issuance partial matches = 1
registration-scope component rows = 28
registration-scope families = 4
registration-scope unresolved rows = 0
registration-scope classification complete = true
~~~

Each EFFECT is represented as resale-registration eligibility evidence with its
file number, effective time and eligible session. Each 424B3 observation
preserves cover totals and issued/contingent component candidates without a
tradable-supply claim. Family 333-278673 contains an SEC-source disagreement of
2,119,016 versus 21,190,316 underlying warrant shares; TSIS preserves the two
reported values and emits REGISTRATION_COMPONENT_SOURCE_CONFLICT. Neither
EFFECT nor 424B3 confirms that affected shares entered tradable supply.

The neutral selling-holder ledger extracts holder name, beneficial shares before,
maximum common shares offered and the reported post-sale balance. Families
333-280366, 333-282130 and 333-282132 reconcile exactly to their cover totals.
Family 333-278673 reports 35,288,630 shares across the principal selling-holder
table against a 46,752,838-share cover total. Its narrative explicitly states
that the registration also covers issuance by the company, so the 11,464,208
difference is classified as PARTIAL_MATCH_MIXED_ISSUER_ISSUANCE rather than an
unexplained mismatch. Those future/derivative components remain unresolved and
are never added to current float or tradable supply.

Current result:

~~~
G8 = BLOCKED_BY_INPUT_GATES

blockers:
- OWNER_EXCLUSION_FLOAT_PARTIAL_COVERAGE
- OWNER_EXCLUSION_FLOAT_SOURCE_CONFLICT
- REGISTRATION_COMPONENT_SOURCE_CONFLICT
- RESTRICTION_STRUCTURED_EXTRACTION_INCOMPLETE
- RESTRICTION_CONDITIONS_UNRESOLVED
- TRADABILITY_METHODOLOGY_NOT_AUTHORIZED

non-null tradability rows = 0
~~~

## Current gate matrix

~~~
G0 identity/security class             = PASS
G1 EDGAR metadata completeness         = PASS
G2 availability policy                 = PASS_WITH_RESTRICTIONS
G3 O/S anchor extraction               = PASS_WITH_RESTRICTIONS
G4 O/S reconciliation/admission        = PASS_WITH_RESTRICTIONS
G5 ownership source coverage           = PASS_WITH_RESTRICTIONS
G6 holder deduplication                 = PASS_WITH_RESTRICTIONS
G7 owner-exclusion methodology         = PASS_WITH_RESTRICTIONS
G8 restrictions/tradability            = BLOCKED_BY_INPUT_GATES
G9 corporate-action alignment          = PASS_WITH_RESTRICTIONS
G10 presession market cap              = PASS_WITH_RESTRICTIONS
G11 historical CUSIP                   = PASS_WITH_RESTRICTIONS
G12 global 13F                         = BLOCKED_BY_SOURCE_NOT_ACQUIRED
G13 cash/debt/EV                       = PASS_WITH_RESTRICTIONS
G14 daily PIT O/S resolver             = PASS_WITH_RESTRICTIONS
G15 storage/reacquisition              = PASS
G16 manual change explanation          = PASS_WITH_RESTRICTIONS
~~~

BLOCKED_BY_INPUT_GATES means the gate executed and refused to invent an
estimate. It is not equivalent to NOT_EXECUTED.

## Next implementation sequence

~~~
1. Resolve exercise, issuance, lockup and resale conditions for classified components.
2. Resolve lockup, restriction and conditional effective events.
3. Freeze the G8 tradability-eligibility methodology.
4. Re-run G8; eligibility remains distinct from confirmed tradable supply.
5. Proceed to G9 corporate-action alignment and G10 presession market cap.
6. Extend historical ownership baselines before 2025-11-07 in a later coverage phase.
~~~

No 50-ticker replay or 4,821-instrument scale-out is authorized yet.

## 2026-08-10 - G8 assignment/restriction event reconciliation v0_43

Authoritative run:

```text
D:/TSIS/fundamental_context/sec_pit_v0_1/runs/
sec_pit_bnai_g8_assignment_reconciled_v0_43_20260810
```

The specialized Assignment Agreement extractor now normalizes narrative dates to
ISO before reconciliation. A case-sensitive date defect discovered by the test
suite was corrected before materialization. Validation status:

```text
SEC PIT tests = 52/52 PASS
ruff = PASS
run status = COMPLETE
filings inventoried = 349
selected primary documents = 270
source observations = 757
```

Twenty-three source observations from the origin 8-K and corroborating 424B3
filings reconcile into five economic events:

```text
SPONSOR_SECURITIES_ASSIGNMENT_REPORTED = 1
LOCKUP_RELEASE_COMMITMENT_REPORTED = 1
SPONSOR_INITIAL_TRANSFER_SCHEDULED = 1
SPONSOR_ESCROW_CONDITIONAL_RELEASE = 1
SPONSOR_TRANSFER_VOLUME_RESTRICTION = 1
```

All five select accession `0001493152-24-033811` (8-K) under the frozen
authority rule `8-K > 8-K/A > 424B3 > other`. The escrow event preserves the
reported `11,350,000` value conflict and the implied `1,135,000` remainder as
separate evidence; TSIS does not silently repair the source.

```text
source observations = 23
economic events = 5
source numeric conflict events = 1
tradable-supply confirmations = 0
```

Daily outputs remain semantically guarded:

```text
daily O/S rows = 496; non-null O/S = 485
owner-exclusion float rows = 496; non-null estimate = 82
tradability rows = 496; non-null eligibility estimate = 0
```

Therefore:

```text
G7 = PASS_WITH_RESTRICTIONS
G8 = BLOCKED_BY_INPUT_GATES
```

The new evidence closes duplicate-observation reconciliation only. It does not
close share-lot linkage, conditional escrow releases, transfer completion,
restrictive-legend resolution or the tradability methodology gate.

Next: link the reconciled events to governed registration/share-lot candidates
only where identity and quantities support the relation. The 1,185,000-share
assignment is a candidate relation; the 1,252,500-share release commitment must
not be assumed to describe the same lot. No linkage may produce tradability by
itself.
## 2026-08-10 - Targeted exhibits and event-to-lot linkage v0_44/v0_45

Targeted exhibit acquisition downloaded only `ex10-1.htm` and `ex10-2.htm` from
accession `0001493152-24-033811`. Both are content-addressed, hashed and governed
by run `sec_pit_bnai_g8_targeted_exhibits_v0_44_20260810`.

The assignment schedule identifies seven Purchasers. All seven match by governed
name alias plus exact quantity to seven selling-holder lots in file-number family
`333-282130`:

```text
purchaser rows = 7
reported contractual total = 1,185,000
identity-and-quantity links = 7/7
tradable-supply confirmations = 0
```

The exhibit reports BEN Capital Fund I LLC as `2,000,000` while the contractual
total, funding amount and registration table support `200,000`. Both the raw and
resolved values are retained under `SOURCE_NUMERIC_CONFLICT_RESOLVED_BY_REPORTED_TOTAL`.
No source value is overwritten.

Authoritative linkage run:

```text
D:/TSIS/fundamental_context/sec_pit_v0_1/runs/
sec_pit_bnai_g8_assignment_lot_linkage_v0_45_20260810
```

This closes purchaser identity and quantity linkage for the 1,185,000-share
assignment. It does not establish funding completion, escrow release, legend
removal, unrestricted resale or actual entry into tradable supply. G8 therefore
remains `BLOCKED_BY_INPUT_GATES` and all daily tradability estimates remain NULL.
## 2026-08-10 - August funding evidence v0_49

The sentence-bounded extractor resolves the November 13, 2024 disclosure as:

```text
gross proceeds = 550,000 USD
combined shares reported = 220,000
contract rule = one SPA share + one Sponsor share per 5 USD
SPA shares supported = 110,000
Sponsor shares supported = 110,000
failed required funding = 1,250,000 USD
tradable-supply confirmations = 0
```

Authoritative run: `sec_pit_bnai_g8_august_funding_evidence_v0_49_20260810`.
Runs v0_46, v0_47 and v0_48 are preserved as `QUARANTINED` because audit found
cross-transaction/cross-sentence matches to the May SPA. They are prohibited as
downstream evidence. The 110,000 Sponsor shares are aggregate condition-supported
releases as of the disclosure, but purchaser allocation and cancellation amounts
remain unavailable. G8 remains `BLOCKED_BY_INPUT_GATES`.
## 2026-08-10 - August funding multivintage resolver v0_53

The governed multivintage builder scanned the acquired primary-document set and
reconciled 24 source observations into seven PIT vintages. Authoritative run:
`sec_pit_bnai_g8_august_multivintage_v0_53_20260810`.

```text
2024-09-13 / eligible 2024-09-16: 50,000 escrow shares, lot unattributed
2024-11-13 / eligible 2024-11-15: 220,000 combined shares / $550,000, equation consistent
2025-02-14 / eligible 2025-02-17: 110,000 / rendered $550, source numeric conflict
2025-03-27 / eligible 2025-04-01: 110,000 / rendered $550, source numeric conflict
2025-03-31 / eligible 2025-06-05: partial termination, purchasers unidentified
2025-06-30 / eligible 2025-10-13: partial termination reiterated
2025-09-30 / eligible 2025-11-26: partial termination reiterated
```

v0_51 is `FAILED` due an unsupported numeric token. v0_52 is
`SUPERSEDED_INCOMPLETE_QUALITY_CLASSIFICATION`. Neither is authorized downstream.
The 2025 `$550` renderings are not silently changed to `$550,000`; they remain
`SOURCE_NUMERIC_CONFLICT`. Cancellation quantities and purchaser allocation stay
NULL. Tradable-supply confirmations remain zero and G8 stays
`BLOCKED_BY_INPUT_GATES`.
## 2026-08-10 - Lockup lifecycle, corporate actions and presession market cap v0_54-v0_58

G8 lockup evidence now resolves the six ex10-2 schedule rows totaling 1,252,500
shares. The contract reports a release of the prior lockup, subject to side-letter
execution and initiation of transfer to escrow, plus a 25% ADV transfer limit.
The later 10-Q supports the 1,185,000-share Sponsor transfer only from its own
public availability date. Neither legend-removal instruction nor registration
proves completed tradability.

```text
v0_54 lockup lots = 6; reported total = 1,252,500
v0_55 daily lifecycle rows = 2,976 (496 sessions x 6 lots)
tradability confirmations = 0
G8 = BLOCKED_BY_INPUT_GATES
```

G9 consumed only the primary `reference` split row from the governed corporate
actions table. The duplicate `additional` row was retained as corroboration but
not applied twice. BNAI's 10-for-1 reverse split effective 2025-12-12 transforms
58 stale pre-split O/S rows from that session onward.

```text
v0_56 daily O/S rows = 496
primary splits applied = 1
secondary duplicates ignored = 1
G9 = PASS_WITH_RESTRICTIONS
```

G10 proved from BNAI's physical downloader checkpoint that the source under
`G:/TSIS/data/ohlcv_daily` was requested with `adjusted=true`. It therefore must
not be multiplied directly by historical-basis O/S. The builder recovers the
historical price basis with future split factors and then aligns prior eligible
RTH close to the target session basis before multiplication.

Run v0_57 was rejected during mandatory first-output audit because pandas `NaN`
O/S was treated as available. A regression test was added and v0_58 supersedes
it. v0_57 is `NOT_AUTHORIZED` downstream.

```text
v0_58 daily rows = 496
market cap estimated = 485
market cap unavailable due O/S = 10
market cap unavailable due price = 1
duplicates = 0
non-finite resolved prices = 0
non-positive market caps = 0
provisional price-and-cap eligible sessions = 212
SEC PIT tests = 67/67 PASS
ruff = PASS
G10 = PASS_WITH_RESTRICTIONS
```

Authoritative run:
`sec_pit_bnai_g10_presession_market_cap_v0_58_20260810`.

This is a one-instrument pipeline pilot, not authorization to scale blindly.
The next scale gate requires a stratified filing/issuer sample and an explicit
parent-universe manifest resolution (4824 vs later references to 4821).
## 2026-08-10 - Historical CUSIP, 13F source gate, core EV and change explanations v0_59-v0_62

G11 extracted CUSIP observations only from SEC objects already acquired. Checksum
validation rejects narrative false positives. The issuer-number gate excludes the
pre-combination SPAC CUSIP `G2758T109` from the BNAI share class.

```text
source observations = 16
admitted BNAI observations = 3
104932108 = 2024-07-29 through 2025-12-11
104932207 = 2025-12-12 through 2026-03-09
pre-first-supported interval = CUSIP_UNAVAILABLE
G11 = PASS_WITH_RESTRICTIONS
```

G12 audited the official local data roots and found no acquired global 13F
information-table source. Institutional ownership remains `UNAVAILABLE`, never
zero. Run `sec_pit_bnai_g12_13f_source_audit_v0_60_20260810` records:

```text
G12 = BLOCKED_BY_SOURCE_NOT_ACQUIRED
required source = GLOBAL_SEC_13F_INFORMATION_TABLE_ACQUISITION
```

G13 resolves only same-measurement-date, causally eligible Company Facts for
cash, ConvertibleNotesPayable and ShortTermBorrowings. Facts measured before the
BNAI instrument valid interval are excluded. The output is deliberately named
`CORE_EV_ESTIMATE`; it is not represented as complete enterprise value.

```text
daily rows = 496
core EV calculated = 391
incomplete/unavailable = 105
lookahead rows = 0
non-finite core EV rows = 0
G13 = PASS_WITH_RESTRICTIONS
```

G16 emits one explanation row per daily state. The split session 2025-12-12 is
explained by corporate-action basis change, prior-close update and CUSIP interval
change. Counts are:

```text
prior-close updates = 495
O/S anchor vintage changes = 2
balance-sheet vintage changes = 6
CUSIP interval changes = 2
corporate-action basis changes = 1
G16 = PASS_WITH_RESTRICTIONS
```

Authoritative runs are v0_59 through v0_62 under
`D:/TSIS/fundamental_context/sec_pit_v0_1/runs`. This closes the executable BNAI
pilot except G8 tradability and G12 institutional ownership. Scale-out is not
authorized until the optimized stratified replay and parent-universe identity
scope are frozen.

## 2026-08-11 - Recovery clarification for approximate G8 outputs

The governing contract permits evidence-based outputs when an exact or admitted
tradability point estimate is unavailable:

```text
FLOAT_EVIDENCE_UPPER_BOUND
= O/S estimate - shares provably excluded

scenario outputs
= CONSERVATIVE / BASE / PERMISSIVE under separately versioned names
```

This is a permitted design boundary, not a completed implementation. The active
resolver still emits NULL while G8 blockers remain and deliberately has no
tradability arithmetic after the gates. BNAI owner-exclusion float may inform an
upper-bound input for its 82 covered sessions, but it must not be relabeled as
tradability float. A future implementation must create separate bound/scenario
schemas, methodology IDs, tests and certification; it may never substitute one
of them for `FLOAT_TRADABILITY_ELIGIBILITY_ESTIMATE_AS_KNOWN`.

## 2026-08-11 - G12 global 13F continuation registered

The pending all-instrument G12 work is now governed by:

```text
SEC_PIT_GLOBAL_13F_INSTITUTIONAL_OWNERSHIP_ACQUISITION_PLAN_v0_1.md
```

The plan requires one global acquisition per 13F vintage followed by historical
CUSIP/share-class mapping and aggregation across all governed ticker identities.
It explicitly prohibits a redundant ticker-by-ticker download and preserves
`UNAVAILABLE` as distinct from zero. Execution remains parked until Trading
Activity closes and a separate human authorization is recorded.
