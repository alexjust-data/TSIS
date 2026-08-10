# POPULATION_TARGET_PRESESSION_4824_SELECTOR_CONTRACT_v0_2

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `population_target_presession_4824_selector_contract` |
| `document_version` | `v0_2` |
| `document_role` | `EXPERIMENTAL_PRESESSION_SELECTOR_CONTRACT` |
| `document_status` | `DRAFT_G0` |
| `g0_contract_status` | `SPECIFIED_PENDING_EXECUTABLE_VERIFICATION` |
| `g1_daily_spine_audit` | `NOT_EXECUTED` |
| `g2_shares_source_temporal_audit` | `NOT_EXECUTED` |
| `g3_measure_ttl_reconciliation` | `NOT_EXECUTED` |
| `selector_gate` | `NOT_EVALUATED` |
| `controlled_fixture_execution` | `NOT_AUTHORIZED_UNTIL_G0_PASS` |
| `broad_materialization` | `NOT_AUTHORIZED` |
| `ta3_sample_freeze` | `NOT_AUTHORIZED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `owner_layer` | `00_CTO` |
| `implementation_owner_layer` | `01_TSIS_DATA_FOUNDATION` |
| `consumer_workstream` | `wake_up_trading_activity_ta_3` |
| `created_at` | `2026-08-07` |
| `supersedes` | `POPULATION_TARGET_PIT_SESSION_START_CANDIDATE_SPEC_v0_1.md` |

## 1. Decision scope

This contract governs the experimental daily selector required to freeze the
TA-3 sample. It does not redefine the `Trading Activity` Information Object or
its representation model.

```text
Universe Resolver + Fundamental Context
-> selects eligible instrument-sessions

Trading Activity
-> represents activity within selected instrument-sessions
```

The parent research frame is intentionally fixed to the governed operational
universe of 4,824 instruments:

```text
parent_universe_id
= lt1b_universe_v0_1
```

This work does not claim that the parent frame is a complete historical census
of every US common stock that was below $1B at every historical date.

## 2. Scientific construct

At the start of premarket for session `d`, determine whether an instrument in
the fixed parent universe can be classified using only information available
before the cutoff as:

```text
0.50 <= presession reference price <= 20.00
AND
presession reference market-cap proxy < 100,000,000
```

The construct is a presession reference classification. It is not session-open
market cap, dynamic intraday market cap, float, scanner output or Wake-up.

## 3. Grain and identity

```text
candidate_dataset_id
= population_target_presession_4824_candidate_v0_1

grain
= instrument_id x ticker_as_of_session x session_date

primary_key
= population_context_id
```

Ticker alone is not an admissible identity key. Instrument ID alone is also not
admissible because the current master can assign one instrument ID to multiple
contemporaneous tickers. The composite key plus governed identity lineage is
required until temporal identity is rehabilitated.

## 4. Presession cutoff

```text
presession_cutoff_local
= 04:00:00 America/New_York on session_date
```

The UTC cutoff must be derived through the governed exchange calendar and DST
rules. A fixed UTC offset is prohibited.

Exact temporal legality is:

```text
source_available_at < presession_cutoff_utc
```

When a legacy source provides only a calendar availability date, the only
authorized conservative proxy is:

```text
source_as_of_date < session_date
```

That proxy must be labeled `DATE_ONLY_CONSERVATIVE_AVAILABILITY`. It must never
be presented as an observed historical publication timestamp.

## 5. Governed input candidates

```text
master_daily_table_v0_1 / price_view=daily_raw
  parent session spine, prior close and price-quality context

instrument_master_v0_1
  parent-universe membership and stable identity context

market_calendar_v0_1
  session calendar and DST-safe derivation of the 04:00 ET cutoff

fundamentals_asof_table_v0_1
  dated basic and diluted weighted-average share measures

corporate_actions_table_v0_1
  split, ticker-change and instrument-transition context

population_target_pti_legacy_run_01
  recovery, reconciliation and proxy sensitivity evidence only
```

No current source is assumed to contain exact historical point-in-time legal
common shares outstanding. G2 must determine the fitness and restrictions of
each available proxy before any selector verdict is issued.

## 6. G1 - daily spine contract

The selector must begin with every governed parent-universe ticker-session row
represented by `master_daily_table_v0_1`. The executable grain is the composite
`instrument_id x ticker_as_of_session x session_date`.
Rows may be classified, unavailable or under review; they may not disappear
because a downstream source is missing.

G1 must verify at least:

```text
parent instrument count
composite instrument-ticker-session grain uniqueness
session-date range
expected-session semantics
prior-close availability
identity coverage
corporate-action flags
requested = resolved + unavailable + review accounting
```

Possible G1 verdicts:

```text
PASS_WITH_RESTRICTIONS
FAIL
```

## 7. Presession reference price

The initial candidate is named according to its physical meaning:

```text
PRESESSION_REFERENCE_PRICE
= prior eligible RTH close
```

It must not be named `PRESESSION_PRICE`, because it is not necessarily the
latest tradable price at 04:00 ET.

Required price states:

```text
REFERENCE_PRICE_AVAILABLE
REFERENCE_PRICE_UNAVAILABLE
REFERENCE_PRICE_NONPOSITIVE
REFERENCE_PRICE_OUTSIDE_PROFILE
CORPORATE_ACTION_REVIEW
```

A future enriched-data candidate may use the latest eligible price available
before 04:00 ET. That would be a new versioned physical binding, not a silent
replacement of this candidate.

## 8. G2 - shares source and temporal audit

Available legacy measures must be audited as proxies, not renamed as exact
shares outstanding:

```text
BASIC_WEIGHTED_AVERAGE_SHARES_PROXY
DILUTED_WEIGHTED_AVERAGE_SHARES_PROXY
LEGACY_SELECTED_WEIGHTED_AVERAGE_SHARES_PROXY
```

G2 must measure for every candidate source:

```text
physical row and instrument coverage
historical date coverage
availability semantics
same-date observations excluded by the conservative cutoff
positive and finite value coverage
duplicate and deterministic tie-break behavior
source and lineage completeness
identity join coverage
corporate-action exposure
```

G2 must not choose a source solely because it produces more classified rows.
Semantic fitness, temporal legality and reproducibility are hard gates.

Possible G2 verdicts:

```text
PASS_WITH_RESTRICTIONS
FAIL
```

## 9. G3 - measure and TTL reconciliation

The following share-selection candidates must be compared without assuming a
winner:

```text
S1_DILUTED_FIRST
  diluted weighted-average shares when available
  else basic weighted-average shares

S2_BASIC_FIRST
  basic weighted-average shares when available
  else diluted weighted-average shares
```

The following staleness policies are experimental sensitivity candidates:

```text
SHARES_TTL_90D
SHARES_TTL_180D
SHARES_TTL_365D
```

No TTL is canonical in this contract. G3 must report:

```text
coverage by year and TTL
basic-versus-diluted value ratios
market-cap proxy differences
classification disagreements around $100M
rows gained by longer TTL
staleness distribution
source conflicts and ambiguous threshold cases
```

Possible G3 verdicts:

```text
PASS_WITH_RESTRICTIONS
FAIL
```

## 10. Market-cap proxy

For each share and TTL candidate:

```text
PRESESSION_REFERENCE_MARKET_CAP_PROXY
= PRESESSION_REFERENCE_PRICE
  x SELECTED_WEIGHTED_AVERAGE_SHARES_PROXY
```

The `PROXY` suffix is mandatory until an exact historical point-shares source
with auditable availability is admitted.

Calculation states must include:

```text
CALCULATED_PROXY
REFERENCE_PRICE_UNAVAILABLE
SHARES_PROXY_UNAVAILABLE
SHARES_PROXY_STALE
IDENTITY_REVIEW
CORPORATE_ACTION_REVIEW
SOURCE_SEMANTICS_REVIEW
SOURCE_CONFLICT
AMBIGUOUS_THRESHOLD
```

## 11. Candidate membership

Numeric boundaries are frozen for all compared candidates:

```text
0.50 <= PRESESSION_REFERENCE_PRICE <= 20.00
PRESESSION_REFERENCE_MARKET_CAP_PROXY < 100,000,000
```

Therefore:

```text
price = 0.50       included
price = 20.00      included
market cap = 100M excluded
```

The state for a numeric pass must be named:

```text
ELIGIBLE_UNDER_DECLARED_PROXY
```

It is not evidence that exact legal market cap was known.

## 12. Float boundary

```text
float != shares outstanding
float != market cap
```

Float is supporting or conditional PIT context in this stage. It is not a
membership predicate and its historical unavailability does not block TA-3.
Historical float must remain `UNAVAILABLE` or `PROXY_RESEARCH_ONLY` until a
separate source gate admits it. Prospective float capture belongs to a separate
versioned contract.

## 13. Missingness and denominator

The selector must conserve:

```text
requested parent instrument-sessions
= numerically eligible
  + numerically ineligible
  + unavailable
  + stale
  + identity review
  + corporate-action review
  + source conflict
  + ambiguous threshold
```

The following conversions are prohibited:

```text
missing shares -> zero shares
missing reference price -> zero price
unavailable market cap -> market cap above threshold
review label -> silent row removal
current market cap or float -> historical value
target-session close -> presession reference price
```

Foundation quality labels are evidence and routing metadata. They do not cause
automatic exclusion unless a selector-relevant local audit demonstrates that
the affected field is unfit. Causal leakage and unresolved identity collisions
remain hard blockers for the affected rows.

## 14. Selector gate

The contract does not predeclare a successful result.

```text
POSSIBLE_SELECTOR_GATE_VERDICTS
= PASS_WITH_RESTRICTIONS
  | FAIL
```

`PASS_WITH_RESTRICTIONS` requires all of the following:

```text
G0 contract executable and internally consistent
G1 daily spine accountable and deterministic
G2 at least one proxy source temporally admissible under declared restrictions
G3 measure and TTL sensitivity quantified
fixtures pass
probe accounting closes
all claims retain proxy semantics
```

`FAIL` prohibits broad materialization and TA-3 sample freeze until the failed
gate is repaired or the scientific scope is changed through a new decision.

## 15. Execution sequence and authorization

```text
G0 contract
-> executable contract tests
-> G1 daily spine audit
-> G2 source and temporal audit
-> G3 measure and TTL reconciliation
-> selector gate readout
-> controlled fixtures
-> controlled stratified probe
-> broad materialization under long-running-operations contract
-> independent validation
-> deterministic TA-3 sample manifest
-> Trading Activity A/B comparison
```

No broad materialization or TA-3 sample freeze is authorized by this document
alone.

## 16. Required lineage

Every materialized row must preserve or reference:

```text
population_context_id
instrument_id
ticker_as_of_session
session_date
presession_cutoff_utc
parent_universe_id
reference_price_value
reference_price_source_row_id
reference_price_available_at_rule
shares_proxy_value
shares_measure_type
shares_source_row_id
shares_as_of_date
shares_period_end
shares_available_at_rule
shares_age_days
shares_ttl_policy_id
share_selection_policy_id
market_cap_proxy_value
calculation_state
membership_state
reason_codes
foundation_quality_labels
local_audit_disposition
schema_version
build_run_id
lineage_manifest_id
```

## 17. Explicit non-claims

This contract and any output governed by it do not establish:

```text
complete historical US <$100M population coverage
exact legal point shares outstanding
historical float
session-open market cap
dynamic intraday market cap
Wake-up detection
In-Play status
Trading Activity model admission
canonical feature promotion
```
