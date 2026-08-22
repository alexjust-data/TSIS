# Wake-up label and denominator materialization contract v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `wake_up_label_and_denominator_materialization_contract` |
| `document_version` | `v0_1` |
| `document_role` | `DATA_FOUNDATION_OUTPUT_AND_CUSTODY_CONTRACT_DRAFT` |
| `document_status` | `PREPARED_NON_EXECUTABLE_LABEL_CONTRACT_NOT_FROZEN` |
| `builder_authorized` | `false` |
| `materialization_authorized` | `false` |
| `lockbox_opening_authorized` | `false` |
| `created_at` | `2026-08-15` |

## 1. Purpose

This contract defines the future Data Foundation outputs required to evaluate
Binding A and Binding B against the same independent Wake-up truth. It does not
define Binding features and does not authorize a builder.

```text
eligible symbol-seconds
+ independent episode labels
+ typed abstention/quality states
= shared A/B evaluation authority
```

The label semantic authority is
`WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md`. Until that contract is
human-frozen, every output below remains prohibited from materialization.

## 2. Split-specific output families

### 2.1 Development

```text
WAKE_UP_DEVELOPMENT_LABEL_MANIFEST_v0_1.parquet
WAKE_UP_DEVELOPMENT_ELIGIBLE_SYMBOL_SECONDS_MANIFEST_v0_1.parquet
```

Development may be opened after its separate label-materialization gate. Its
exact parent targets remain the frozen 2,400 development contexts:

```text
selected_target_contexts_v0_1.parquet
SHA-256
= 55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220
```

### 2.2 Temporal validation

```text
TRADING_ACTIVITY_TEMPORAL_VALIDATION_TARGET_IDENTITIES_v0_1.parquet
TRADING_ACTIVITY_TEMPORAL_VALIDATION_DENOMINATOR_IDENTITIES_v0_1.parquet
WAKE_UP_TEMPORAL_VALIDATION_LABEL_MANIFEST_v0_1.parquet
TRADING_ACTIVITY_TEMPORAL_VALIDATION_MANIFEST_v0_1.json
```

These artifacts remain sealed until B-17. Aggregate identity counts, paths,
hashes and `access_count=0` may be exposed; labels and metrics may not.

### 2.3 Final OOS

```text
TRADING_ACTIVITY_FINAL_OOS_TARGET_IDENTITIES_v0_1.parquet
TRADING_ACTIVITY_FINAL_OOS_DENOMINATOR_IDENTITIES_v0_1.parquet
WAKE_UP_FINAL_OOS_LABEL_MANIFEST_v0_1.parquet
TRADING_ACTIVITY_FINAL_OOS_LOCKBOX_MANIFEST_v0_1.json
```

These artifacts remain sealed until B-18 and only the already selected
candidate may consume them.

## 3. Episode-label grain and required fields

One row per adjudicated candidate episode:

```text
label_id                         string non-null
instrument_id                    string non-null
ticker_as_of_session             string nullable
session_date                     date32 non-null
episode_id                       string non-null
reference_onset_timestamp_utc    timestamp[us, UTC] nullable
confirmation_window_end_utc      timestamp[us, UTC] nullable
label_available_at_utc           timestamp[us, UTC] nullable
label_class                      categorical non-null
label_quality                     categorical non-null
label_reason_code                string non-null
later_episode_outcome            categorical nullable
label_contract_id                string non-null
label_contract_sha256            fixed string non-null
source_snapshot_ids              list<string> non-null
source_snapshot_hashes           list<string> non-null
future_window_used               bool = true
consumption_legality             string = OUTCOME_ONLY
adjudication_status              categorical non-null
reviewer_or_oracle_version       string non-null
build_run_id                     string non-null
schema_version                   string non-null
created_at_utc                   timestamp[us, UTC] non-null
```

Primary key:

```text
label_contract_id + instrument_id + session_date + episode_id
```

## 4. Eligible symbol-second grain and required fields

One row per governed decision second for every selected target session:

```text
denominator_identity_id          string non-null
split_id                         categorical non-null
target_identity_id               string non-null
instrument_id                    string non-null
ticker_as_of_session             string nullable
session_date                     date32 non-null
decision_timestamp_utc           timestamp[us, UTC] non-null
calendar_id                      string non-null
session_open_utc                 timestamp[us, UTC] non-null
session_close_utc                timestamp[us, UTC] non-null
is_early_close                   bool non-null
eligibility_state                categorical non-null
eligibility_reason_code          string non-null
source_observation_state         categorical non-null
trade_quality_state              categorical non-null
latency_policy_id                string non-null
trade_eligibility_policy_id      string non-null
population_policy_id             string non-null
source_snapshot_ids              list<string> non-null
source_snapshot_hashes           list<string> non-null
schema_version                   string non-null
build_run_id                     string non-null
created_at_utc                   timestamp[us, UTC] non-null
```

Allowed `eligibility_state` values:

```text
ELIGIBLE
DEGRADED
UNAVAILABLE
OUT_OF_SCOPE
```

Zero observed activity remains `ELIGIBLE` with an observed-zero source state.
No row may be removed because it is dormant, difficult, degraded or has no
candidate episode.

## 5. Source and policy bindings

```text
Wake-up semantic definition SHA
= 1ff56c25744d069cbdac997af628c174a61215209dbd82ac8c7275bc67a9aa46

development sample plan SHA
= 61aa1ef8a17f9bffc4c7c8dd6f9ca4146d65a35cdebf50e2a6b5a9043bee86ec

trade eligibility policy SHA
= f2dca73ac1ac95c37b6417e5edfd7cbeb3b82c1fe25c8d16f79e551fc9f232bd

latency registry SHA
= 839c376b8804baa8c0fd763df4b1d8a931c42d0926985a6e573c23d4567605f7

temporal/missingness contract SHA
= c4922374f3f99c3d19d1955ef76c41c5198f7cac494de757f462ec93bdfdd1a4

source-quality label consumption policy SHA
= f66a6f0e15b69d5d26d040058deb3b92c41a672443439942379a179d253e3acf
```

Physical source roots must use `G:/TSIS/data`; stale `E:` paths in old schema
documents are historical and not operational authority.

## 6. Construction phases

```text
Phase A: independent high-recall candidate reduction
-> no A/B imports and no final label claim

Phase B: frozen deterministic oracle
-> emits primary class or typed abstention

Phase C: blind stratified audit/adjudication
-> reviewers cannot see A/B scores or economic outcomes

Phase D: terminal manifest and independent validation
-> exact row accounting, hashes, class counts and leakage checks
```

Candidate reduction must also sample candidate-free eligible intervals so the
negative and dormant denominator is not defined by the candidate generator.

## 7. Mandatory accounting

For every split:

```text
requested decision seconds
= ELIGIBLE + DEGRADED + UNAVAILABLE + OUT_OF_SCOPE

candidate episodes
= positive + economic negatives + ambiguous + unavailable
```

Every target identity must map to its exact calendar row and complete governed
decision grid. Aggregate class counts may be exposed for development; validation
and final-OOS class counts remain sealed because they leak label prevalence.

## 8. Separation from existing outcomes_table v0.1

The current governed `outcomes_table_v0_1` has grain
`event_window_id + outcome_horizon + price_view` and scope
`halt_next_session_daily_outcomes_v0_1`. It is not a Wake-up intraday label
authority. Wake-up labels require a new versioned dataset contract, schema,
registry entry, validators and consumption policy before promotion.

## 9. Long-operation boundary

Any future label or denominator build is a long operation and must comply with
`LONG_RUNNING_OPERATIONS_CONTRACT.md`. Before execution it needs a pre-manifest,
PID, heartbeat, live log, monitor, atomic outputs, resume identity validation,
terminal manifest and an independent validator. Resume cannot mix label contract,
schema, source, policy or code hashes.

## 10. Current gate

```text
output families and grains       = PREPARED
label contract numeric decisions = OPEN
Data Foundation schema promotion = NOT_STARTED
builder/code                      = NOT_AUTHORIZED
development labels               = NOT_AUTHORIZED
validation labels                = SEALED_NOT_CREATED
final OOS labels                 = SEALED_NOT_CREATED
B02-D07                           = OPEN
B02-D12                           = OPEN
```

