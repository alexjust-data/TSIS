# Intraday Scanner Candidates Table Validators v0.1

Dataset:

```text
intraday_scanner_candidates_table_v0_1
```

## Required Validator Checks

Schema:

```text
required columns present
prohibited columns absent
date/timestamp columns parseable
boolean flags boolean
numeric movement/volume fields numeric
```

Key integrity:

```text
no duplicate scanner_run_id + ticker + session_date
intraday_scanner_candidate_id unique
```

Selection semantics:

```text
selected implies motion_threshold_passed
selected implies tradability_threshold_passed
selected implies price_filter_passed_at_first_cross
selected implies base_eligible_smallcap_denominator_passed
motion_threshold_passed implies first_cross_50_ts_utc not null
motion_threshold_passed implies first_cross_move_vs_prev_close_pct >= 50
```

Segment semantics:

```text
first_cross_50_segment in {premarket, regular, afterhours, null}
premarket means 04:00-09:30 America/New_York
regular means 09:30-16:00 America/New_York
afterhours means 16:00-20:00 America/New_York
```

Governance:

```text
full_universe_claim=false for controlled replays
float_shares null until float_context_table exists
labels/rewards/fills/PnL/action columns absent
source roots and manifest paths recorded
```

## Current Executable Evidence

```text
python -m pytest C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_intraday_scanner_candidates_table_builder_v0_1.py -q
```

Result:

```text
1 passed
```
