# Trading Activity validation and final OOS selection and seal contract v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_validation_and_final_oos_selection_and_seal_contract` |
| `document_version` | `v0_1` |
| `document_role` | `LOCKBOX_MEMBERSHIP_AND_CUSTODY_CONTRACT_DRAFT` |
| `document_status` | `DRAFT_FOR_SCIENTIFIC_OWNER_APPROVAL_NOT_EXECUTABLE` |
| `temporal_validation_opening_gate` | `B-17_A_B_COMPARISON_ONLY` |
| `final_oos_opening_gate` | `B-18_SELECTED_CANDIDATE_ONLY` |
| `identity_generation_authorized` | `false` |
| `labels_or_metrics_exposed` | `false` |
| `created_at` | `2026-08-15` |

## 1. Frozen split boundaries

```text
DEVELOPMENT
= 2011-01-03 through 2022-12-30

TEMPORAL VALIDATION
= 2023-01-03 through 2024-12-31

ENGINEERING-EXPOSED EMBARGO
= 2025-01-02 through 2025-03-14

FINAL TEMPORAL OOS
= 2025-03-17 through 2026-03-09
```

The embargo is excluded from both lockboxes. A date range is a boundary, not a
membership manifest.

## 2. Frozen upstream selection sources

The selection procedure may read identity, calendar, PIT population, prior
activity and source-quality fields only from these hash-bound authorities:

```text
population candidate parquet
G:/TSIS/data/data_foundation_outputs/
population_target_presession_4824_candidate/
population_target_presession_4824_candidate_v0_1_experimental_20260807T170430Z/
population_target_presession_4824_candidate_v0_1.parquet
SHA-256 = a777b3338d1ff2f2304e768113a5a14728d16372553081b144c943a93fa0702c

population manifest
SHA-256 = 26a131b7c01e8b598fe0bd2dbeac8b768ddcd4103fdb1d66746508f4aca398da

market calendar parquet
SHA-256 = cbf1879261866d980c5a8542fadf683dbc91f96b80b7865055417a16d1e6e87c

master daily manifest
SHA-256 = b965f766a809e8b99c968204dd5b6c6bfdc47aa92986cf628dd3960222e9340a

instrument master parquet
SHA-256 = 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2
```

The population source is explicitly an experimental proxy and asserts neither
exact point shares nor a full historical US `<$100M` population. It may define
the restricted A/B experiment only if the scientific owner accepts that scope
restriction. It must never be promoted silently to canonical population truth.

## 3. Read-only coverage preflight

Aggregate inspection of identity/population fields produced:

| Split | Candidate rows | Distinct instruments | `ELIGIBLE_UNDER_DECLARED_PROXY` rows | Eligible instruments |
|---|---:|---:|---:|---:|
| Development | 4,614,183 | 4,007 | 798,761 | 1,841 |
| Temporal validation | 1,425,981 | 3,482 | 367,644 | 1,691 |
| Engineering embargo | 129,029 | 2,688 | 36,946 | 930 |
| Final OOS | 632,769 | 2,738 | 213,965 | 1,494 |

This preflight did not read A/B variables, labels, detector scores, outcomes or
PnL. It establishes only that candidate identity supply exists.

## 4. Selection population

For either lockbox, a target context is feasible only when:

```text
instrument listed and observable as-of session
+ common-stock eligibility known as-of session
+ population_membership_state = ELIGIBLE_UNDER_DECLARED_PROXY
+ 0.50 <= prior_close_eligible <= 20.00 USD
+ identity and XNYS calendar resolvable
+ 120 strictly prior governed sessions available for baseline accounting
```

Source-unavailable contexts remain in requested accounting as blocked; they are
not silently rewritten as ineligible.

## 5. Selection algorithm inherited from development

The candidate design preserves the development selector's structure:

```text
sampling unit
= instrument x block of 10 consecutive PIT-eligible target contexts

maximum blocks per instrument = 2
minimum reuse separation       = 252 governed sessions
target blocks do not overlap
every target uses complete governed RTH decision grid
```

Strata are assigned from only pre-target information:

```text
price bands P1..P5
market-cap proxy bands M1..M4
strictly-prior activity A0..A3/AU
prior zero-activity prevalence Z1..Z3/ZU
source-quality metadata
```

Selection inputs explicitly prohibited:

```text
target-session trade activity
Binding A or Binding B values/scores
known Wake-up/In-Play labels
scanner 500k appearance
gap or future return
frontside or strategy outcome
chart review or human winner lists
PnL, fills, MFE or MAE
```

## 6. Blocking membership decisions

The following proposal is deliberately not frozen:

```text
temporal validation = 60 blocks x 10 sessions = 600 targets
final OOS           = 60 blocks x 10 sessions = 600 targets

validation selection salt = "20260815|TEMPORAL_VALIDATION"
final OOS selection salt  = "20260815|FINAL_OOS"
```

For each feasible block:

```text
selection_hash
= SHA256(
    selection_salt |
    split_id |
    instrument_id |
    block_start_session
  )
```

The scientific owner must approve or replace the block counts and salts before
identity generation. They cannot be chosen after inspecting labels or A/B
results. A full-population lockbox is a materially different cost/scientific
design and requires a versioned amendment, not an implementation shortcut.

## 7. Required identity artifacts

For each split the independent custodian emits:

```text
target identities
= one row per exact instrument_id x session_date target

denominator identities
= one row per exact governed symbol-second with typed eligibility state
```

Target fields include at least:

```text
target_identity_id
split_id
block_id
block_ordinal
instrument_id
ticker_as_of_session
session_date
session_open_utc
session_close_utc
is_early_close
population_context_id
population_membership_state
price_band
market_cap_band
prior_activity_stratum
zero_prevalence_stratum
source_quality_state
selection_hash
selection_contract_id
selection_contract_sha256
```

## 8. Custody and access rules

Identity selection and sealing must be performed by a custodian independent of
the Binding B implementation agent. The custodian may inspect only fields allowed
by this contract.

Before the authorized opening gate, ordinary agents may receive only:

```text
manifest path
manifest SHA-256
target identity count
denominator identity count
access_count = 0
metrics_exposed = false
labels_exposed = false
```

Temporal validation may open once at B-17 for the frozen A/B comparison. Final
OOS may open once at B-18 for the already selected candidate. Opening increments
`access_count` atomically and records actor, gate, timestamp and reason.

## 9. Manifest requirements

Both manifests must validate against
`TRADING_ACTIVITY_LOCKBOX_MANIFEST_SCHEMA_v0_1.json` and bind:

```text
selection contract and SHA
exact source/policy/calendar hashes
target and denominator artifacts/hashes/counts
Wake-up label contract and label artifact hash/count
split dates and identity schema
sealed timestamp and custodian
access ledger state
allowed opening gate
```

Label prevalence, outcome distributions and detector metrics are prohibited
from the externally visible seal readout.

## 10. D12 closure rule

```text
B02-D12 = CLOSED
only when:
  final selection contract is human-frozen
  + exact identities are generated by the custodian
  + label authority/hash is bound
  + manifest validates
  + access_count = 0
  + metrics_exposed = false
  + labels_exposed = false
```

## 11. Current gate

```text
date boundaries                = FROZEN
source hashes                  = BOUND
aggregate coverage preflight   = PASS
selection algorithm structure  = PREPARED
block counts / salts           = OPEN_HUMAN_DECISION
label contract                 = NOT_FROZEN
custodian assignment           = OPEN
identity generation            = NOT_AUTHORIZED
temporal validation manifest   = NOT_CREATED
final OOS manifest             = NOT_CREATED
B02-D12                         = OPEN
```

