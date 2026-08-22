# Daily Eligible Universe selector and Binding consumption contract v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `daily_eligible_universe_selector_and_binding_consumption_contract` |
| `document_version` | `v0_1` |
| `document_role` | `UPSTREAM_POPULATION_OWNERSHIP_AND_CONSUMPTION_CONTRACT` |
| `document_status` | `HUMAN_POLICY_CONFIRMED_OPERATIONAL_SELECTOR_PROMOTION_PENDING` |
| `human_directive` | `HUMAN_SCIENTIFIC_DIRECTIVE_DAILY_ELIGIBLE_UNIVERSE_v0_1.md` |
| `created_at` | `2026-08-15` |
| `binding_a_or_b_feature_authority` | `false` |
| `wake_up_label_authority` | `false` |

## 1. Non-negotiable ownership

```text
Daily Eligible Universe Selector
= owns daily membership
= owns price and market-cap thresholds
= runs before Trading Activity

Binding A / Binding B
= consume exact membership identities
= never calculate or redefine selector thresholds

Wake-up Detector
= evaluates all eligible symbol-seconds
= does not choose the eligible parent population

In-Play / strategy
= downstream layers
= cannot redefine eligibility or Wake-up truth
```

Eligibility means only that the instrument must be watched. It is not an
In-Play classification, alert or trading decision.

## 1.1 General Screener authority versus the A/B bridge

The project-wide conceptual authority for the general Screener Engine lives in:

```text
C:/TSIS_Data/00_CTO/15_SCREENER_ENGINE
```

Its future executable runtime must be an independently governed module. The
proposed `C:/TSIS_Data/07_TSIS_SCREENER_ENGINE` name remains uncreated and
unauthorized pending an explicit human gate.

The executed restricted consumption gate used by Trading Activity is not that
general Screener Engine:

```text
daily_eligible_universe_restricted_consumption_gate_v0_1_20260815
= controlled experimental bridge
= admits the existing presession candidate for A/B development
= prevents A and B from reimplementing membership

it does not equal
= canonical Daily Eligible Universe runtime
= Backtest integration
= live or RL authorization
= exact historical market-cap authority
```

When the general Screener Engine produces a promoted, sealed daily-universe
artifact, Trading Activity, Wake-up, Backtest, research, live and Offline RL
must consume it through separate authorized adapters or policies. The bridge
cannot be silently relabelled or promoted as the general artifact.

## 2. Human-confirmed TA-3 candidate policy

The current experimental candidate uses one presession decision per
instrument-session:

```text
cutoff
= 04:00:00 America/New_York

availability
= strictly before cutoff
= date-only fundamental source requires as_of_date < session_date

reference price
= prior eligible RTH close

price membership
= 0.50 <= reference price <= 20.00 USD

market-cap proxy
= reference price * selected weighted-average shares proxy

market-cap membership
= proxy < 100,000,000 USD

instrument requirement
= valid common-stock instrument/session identity
```

The inclusive price boundary belongs only to this selector policy. No Binding
formula may contain `0.50`, `20.00` or `100,000,000` as a membership rule.

## 3. Candidate implementation evidence

```text
config
= C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/
  population_target_presession_4824_audit_v0_1.json
SHA-256
= f15f49ee4cf081937eb1df59763250509c8aad4f07c917c96b1ca6da6a03b716

builder SHA-256
= ec4b1459feed30d0bbdd18eb9ad7653b84aaf84d5f3a251f03d84ea13bbdfcd9

validator SHA-256
= 62368cb6ae45fd7b13a86ff6e4bd6ddfdc6314b2ace943b5f993d6a5f3b486d5

candidate parquet SHA-256
= a777b3338d1ff2f2304e768113a5a14728d16372553081b144c943a93fa0702c

candidate manifest SHA-256
= 26a131b7c01e8b598fe0bd2dbeac8b768ddcd4103fdb1d66746508f4aca398da
```

The candidate contains:

```text
instrument-session rows                       = 7,369,699
ELIGIBLE_UNDER_DECLARED_PROXY                 = 1,417,316
full historical US <100M population claim    = false
exact point shares outstanding claim          = false
session-open exact market-cap claim            = false
promotion state                                = EXPERIMENTAL_CANDIDATE_NOT_CANONICAL
```

The asset is sufficient as restricted experimental evidence. It is not yet the
canonical operational screener.

## 4. Required selector output

The operational selector must emit a versioned daily membership artifact with
at least:

```text
population_context_id
instrument_id
ticker_as_of_session
session_date
presession_cutoff_utc
daily_universe_status
daily_universe_reason
reference_price
reference_price_source/state
shares_proxy and as-of lineage
market_cap_proxy
selector_policy_id
selector_policy_sha256
source_snapshot IDs/hashes
availability state
```

Typed states must distinguish at least:

```text
ELIGIBLE
INELIGIBLE_PRICE
INELIGIBLE_MARKET_CAP
PRICE_UNAVAILABLE
SHARES_UNAVAILABLE
STALE_SHARES_PROXY
IDENTITY_REVIEW
CORPORATE_ACTION_REVIEW
OUTSIDE_PARENT_FRAME
```

Unknown, stale or review rows cannot be silently converted to ineligible or
eligible.

## 5. Mandatory consumption order

```text
master instrument/session frame
-> Daily Eligible Universe Selector
-> exact daily eligible membership manifest
-> Wake-up observation population
-> Binding A and Binding B over identical eligible identities
-> common Wake-up detector protocol
-> Active Symbol Set
-> In-Play / heavier microstructure / strategy
```

The selector evaluates the broad parent frame once per day. The heavy Trading
Activity representation is not calculated for every master-universe
instrument; it is calculated only for the eligible membership supplied by the
selector.

## 6. A/B parity

A and B must consume exactly the same:

```text
population_context_id
instrument_id
session_date
eligible symbol-seconds
selector policy ID/SHA
membership artifact SHA
quality/unavailable states
```

Changing the selector for B alone invalidates the A/B comparison. If the parent
population changes materially, both bindings require a new versioned experiment
or a restriction explicitly limiting the claim.

## 7. Relationship to the 2,400 TARGET sessions

The executed read-only reconciliation in
`TRADING_ACTIVITY_AB_DENOMINATOR_DAILY_ELIGIBLE_UNIVERSE_RECONCILIATION_READOUT_v0_1.md`
establishes:

```text
2,400 / 2,400 TARGET sessions
= exact matches to the candidate population
= ELIGIBLE_UNDER_DECLARED_PROXY
```

Therefore Binding A does not require rematerialization merely to repair daily
eligibility, and Binding B may use the same frozen 2,400-session development
denominator after B-02/B-03 gates.

This does not turn the stratified 2,400-session sample into the full operational
daily denominator. Operational false-alert load and final Wake-up claims require
governed eligible-symbol-second manifests for development, temporal validation
and final OOS.

## 8. Gate ordering

```text
mathematical B-02 work that does not alter population
= may continue

D07 label/negative materialization
= blocked until selector consumption and eligible-second denominator are frozen

D12 validation/final-OOS membership
= blocked until the same selector policy is bound to both lockboxes

B-03 implementation
= remains blocked by unfinished B-02

long B materialization / A-B comparison
= blocked until identical membership artifacts are hash-bound
```

## 9. Next required institutional work

```text
1. Review the existing candidate as the implementation seed.
2. Freeze the selector's operational contract and output schema.
3. Decide whether proxy shares/TTL restrictions are acceptable for the stated claim.
4. Produce versioned daily membership manifests per experimental split.
5. Produce eligible-symbol-second denominator manifests.
6. Bind D07 labels and D12 lockboxes to those exact hashes.
7. Only then complete B-02 and request its human freeze.
```

The Screener Engine architecture and its Backtest consumer gate evolve in
`C:/TSIS_Data/00_CTO/15_SCREENER_ENGINE`; they are not implemented inside this
Market States workstream.
