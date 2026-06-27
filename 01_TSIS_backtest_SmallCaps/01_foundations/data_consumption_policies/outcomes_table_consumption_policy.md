# Outcomes Table Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
outcomes_table_v0_1
```

## 2. Permitted Meaning

This table is a governed post-event outcome/label table.

Consumers may use it for:

- daily next-session outcome research;
- supervised label construction;
- strategy evaluation after signals are defined elsewhere;
- event-family outcome profiling;
- quality-aware exclusion and coverage accounting.

## 3. Feature/Label Separation

Every row contains post-event information.

Therefore:

```text
prohibited_as_pre_event_feature = true
contains_post_event_information = true
requires_feature_label_separation = true
```

No feature builder may consume `outcomes_table_v0_1` as an input feature source.

## 4. Required Gates

Primary labels require:

```text
valid_for_ml_label_candidate = true
```

Rows where `outcome_quality_state != good_daily_outcome` may be used only as:

- coverage diagnostics;
- missing-data masks;
- forensic evidence;
- flagged/non-primary research.

## 5. Price-View Discipline

Consumers must choose exactly one declared `price_view` unless the experiment is
explicitly comparing price views.

Allowed values:

- `daily_raw`
- `split_normalized`
- `adjusted`

Rules:

- Use `adjusted` for economic continuity research.
- Use `split_normalized` for split-comparable event studies.
- Use `daily_raw` for observed daily market context.
- Do not treat daily outcomes as raw intraday execution outcomes.

## 6. Prohibited Uses

This table must not be used as:

- pre-event feature source;
- quote/trade microstructure truth;
- fill/slippage table;
- RL reward table;
- live alert table;
- source for action decisions without a separate feature state.

## 7. Final Rule

`outcomes_table` exists so features and labels are not mixed.

It makes the post-event side explicit, governed and auditable. It does not make
the system trainable by itself.

