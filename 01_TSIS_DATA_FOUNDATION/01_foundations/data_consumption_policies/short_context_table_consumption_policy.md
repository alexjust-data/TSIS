# Short Context Table Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
short_context_table_v0_1
```

## 2. Permitted Meaning

This table is source-scoped short-side context.

Permitted meaning:

```text
short interest / short sale volume context from a declared source scope
```

Forbidden meaning:

```text
complete consolidated shorting truth
```

## 3. Required As-Of / Lag Join

Consumers must select rows using:

```text
as_of_date <= event/session decision cutoff
```

Then they must apply a downstream lag rule appropriate to the family:

- `short_interest`: slow biweekly settlement/reporting context.
- `short_volume`: daily source-scope reported short-sale volume.

No consumer may use same-day intraday short context as causal evidence without a
separate lag/availability contract.

## 4. Required Gates

Primary context candidates require:

```text
valid_for_event_context_candidate = true
source_duplicate_key_flag = false
instrument_identity_temporal_match = true
```

For ML feature candidates:

```text
valid_for_ml_feature_candidate = true
```

Rows in these states require review or explicit masks:

- `review_finra_pre_2021_short_interest_semantics`
- `review_local_certification_status`
- `review_no_temporal_identity`
- `review_source_duplicate_key`

## 5. Source-Specific Rules

### FINRA

FINRA rows must preserve:

- `finra_official_free_baseline = true`
- `source_scope`
- duplicate-key flags;
- pre-2021 short-interest semantics flag where applicable.

FINRA short volume must not be read as consolidated market-wide shorting
pressure.

### Local / Polygon

Local rows must preserve:

- `local_certification_status`
- `local_certified_date_start`
- `local_certified_date_end`
- `local_observation_inside_certified_window`

Rows with `REVIEW_*` certification are not primary feature candidates.

## 6. ML/RL Boundary

`valid_for_ml_feature_candidate = true` means:

```text
this row may enter a feature set only after an external as-of/lag builder selects it legally
```

It does not mean:

- direct `ml_primary` readiness;
- direct RL state/action/reward readiness;
- complete market-wide shorting pressure;
- borrow or SSR coverage.

`valid_for_rl_training_direct` is false for every v0.1 row.

## 7. Missing Families

The target concept mentions SSR and borrow availability when available.

In v0.1:

```text
borrow_data_present = false
ssr_data_present = false
```

No downstream consumer may infer borrow or SSR state from this table.

## 8. Final Rule

`short_context_table` is a component of state, not the state itself.

The future event/market-state builder must still compose:

```text
instrument + calendar + daily/intraday + microstructure + fundamentals + news + short + regime
```

under a single decision-time cutoff and declared lag model.
