# Bounded StateBundle Read and Replay Authorization v0.1

Gate: `bounded_state_bundle_read_and_replay_authorization_v0_1`
Date: `2026-07-28`
Status: `CLOSED_BLOCKED_BEFORE_PHYSICAL_READ`

## Purpose

This gate attempted to authorize one bounded physical read-and-replay probe for a governed Market State `StateBundleManifest` reference.

The intended first slice remains:

```text
state_kind = market_state
profile_id = market_state_core_four_intraday_profile_v0_1
Event State requested = false
consumer_id = bounded_backtest_state_integration_probe_v0_1
strategy execution = false
orders = 0
fills = 0
PnL = false
```

## Decision

```text
physical read authorization = NOT_ISSUED
bounded read-and-replay execution = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
backtest consumption = false
production = false
downstream = false
```

The authorization is blocked because the provider control-plane reference is not yet a sufficient physical evidence authority.

## Blocking Findings

### 1. StateBundle dataset identity does not match the physical Market State candidate

The reuse-hit `StateBundleManifest` declares:

```text
dataset_id = market_state_candidate_scale_validation_reference_v0_1
candidate_dataset_fingerprint = 8563b1307af126bcf1cd4ec473bb710dbce9a38aa26f64aab2f080dfb31caea0
```

The physical Market State scale-validation candidate declares:

```text
dataset_id = market_state_candidate_dataset_scale_validation_v0_1_516a27d0f8f53762
candidate_dataset_fingerprint = 516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416
```

A reader cannot infer that these are the same scientific dataset.

### 2. StateBundle internal response hash does not match the response file

The `StateBundleManifest` references a runtime response hash:

```text
cdfd7d2acdb3c5e0885a0a96b1add49b49c990846fb02c9618869f9155baafd8
```

The observed `case_01_response.json` file hash is:

```text
0985e2b97a44e45eb4d05777406f0615f44fb1c80f463a7f2989bdcb9d06bab4
```

A physical authorization must fail closed when the response-to-bundle evidence chain is not reproducible.

### 3. StateBundle does not directly freeze the physical candidate output manifest and state-record artifact

The bundle references the scale `final_manifest`, whose file hash is valid:

```text
00b69f8445d8a8d1c8be1a5ab17648d0e7d6be289dccd70fc2c9c90524fdfd9c
```

But the physical authorization must also freeze the candidate output manifest and state-record artifact:

```text
candidate_output_manifest_sha256 = dd3037aa3a3226b7ac308dcc909575344de38202cbe59c25483259a4c07f0e78
candidate_parquet_sha256 = bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68
```

The current provider bundle does not expose that chain as a direct bounded-consumption authority.

### 4. Replay-safe timestamp evidence is not yet explicit in the physical schema contract

The reader/replay boundary requires:

```text
decision_timestamp_utc
state_as_of_utc
state_available_at_utc
```

The current Market State core-four physical schema contract exposes `decision_timestamp_utc`, but the preflight did not find `state_as_of_utc` or `state_available_at_utc` as explicit physical columns.

For read-and-replay, this must be resolved by either:

```text
1. adding governed availability fields to a new state output version;
```

or:

```text
2. providing a separate availability overlay/manifest with row-level identity and hashes.
```

Until then, decision-safe replay must remain blocked.

## Required Correction Before Reopening

Open a small corrective gate, not a backtest implementation:

```text
state_bundle_manifest_physical_evidence_alignment_v0_1
```

It must produce a corrected provider/boundary evidence chain that links:

```text
RuntimeInvocationResponse
-> StateBundleManifest
-> dataset registry entry
-> candidate_output_manifest
-> physical artifact hashes
-> schema contract
-> row-level temporal availability evidence
```

No rows may be read by that corrective gate.

## Counters

```text
state_bundle_rows_read = 0
physical_artifacts_opened = 0
StateReplayFeed_records_emitted = 0
EventLoop_ticks = 0
strategy_callbacks = 0
orders_emitted = 0
fills_emitted = 0
PnL_calculated = false
provider_registry_mutations = 0
production = false
downstream = false
official_dataset = false
```
