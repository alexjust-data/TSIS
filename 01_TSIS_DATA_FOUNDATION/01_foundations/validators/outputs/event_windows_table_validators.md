# Event Windows Table Validators `v0_1`

## Scope

Validators for:

```text
event_windows_table_v0_1
```

Physical target:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/
```

## 1. Manifest And Source Checks

Must verify:

- manifest exists;
- summary exists;
- partitioned output exists;
- output tree hash matches manifest;
- source halts table exists and hash matches manifest;
- source instrument master exists and hash matches manifest;
- source market calendar exists and hash matches manifest;
- all contract paths in manifest exist.

Hard failure:

- missing output;
- missing source;
- hash drift;
- missing contract path.

## 2. Schema Checks

Must verify:

- required columns from schema contract exist;
- `event_window_id` is unique and non-empty;
- `source_event_id` is non-empty;
- `event_source_dataset_id = halts_table_v0_1`;
- `materialization_scope = halts_intraday_lt1b_calendar_covered`;
- `schema_version = event_windows_table_v0_1`;
- `quality_policy_version = event_windows_table_policy_v0_1`;
- `full_universe_claim = false`;
- `valid_for_rl_state_component_candidate = false`.

## 3. Window Semantics Checks

Must verify:

- `window_end_utc > window_start_utc`;
- allowed `window_role` vocabulary only;
- `pre_event_30m` ends at `event_time_utc`;
- `event_to_resume_or_30m` starts at `event_time_utc`;
- `prior_session_regular` and `pre_event_30m` are leakage-safe as pre-event
  features;
- no row with post-event information is marked as ML feature candidate.

## 4. Reconciliation Checks

Must verify:

- source event counts reconcile against `halts_table_v0_1`;
- temporal identity match counts reconcile against `instrument_master_v0_1`;
- calendar-covered counts reconcile against `market_calendar_v0_1`;
- excluded event counts are recorded in the manifest.

Expected v0.1 role vocabulary:

```text
prior_session_regular
pre_event_30m
event_to_resume_or_30m
same_session_regular
next_session_regular
```

## 5. Quality-State Checks

Must verify:

- allowed `event_window_quality_state` vocabulary only;
- fallback resume windows are counted;
- fallback resume windows are not hidden as fully observed response windows.

## 6. Non-Goals

These validators do not prove:

- live availability;
- execution feasibility;
- alpha;
- RL readiness;
- non-halt event coverage;
- correctness of future `outcomes_table`.

