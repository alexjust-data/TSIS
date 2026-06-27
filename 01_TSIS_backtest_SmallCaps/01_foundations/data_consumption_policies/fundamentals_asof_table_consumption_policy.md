# Fundamentals As-Of Table Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
fundamentals_asof_table_v0_1
```

## 2. Permitted Meaning

This table is a filing-date-aware fundamental context component.

Permitted meaning:

```text
statement facts available from filing_date at date-level precision
```

Forbidden meaning:

```text
statement facts known at period_end
```

## 3. Required As-Of Join

Consumers must select rows using:

```text
as_of_date <= event/session decision cutoff
```

Then they must choose a deterministic rule, normally:

```text
latest eligible filing per ticker + statement_family + timeframe
```

No consumer may join by `period_end` as if it were availability.

## 4. Required Gates

Primary context candidates require:

```text
valid_for_event_context_candidate = true
fundamental_quality_state = good_statement_asof
```

Rows in `review_*` states may be used only for:

- coverage diagnostics;
- missing-identity analysis;
- robustness tests with explicit masks;
- forensic review.

## 5. ML/RL Boundary

`valid_for_ml_feature_candidate = true` means:

```text
this row may enter a feature set only after an external as-of builder selects it legally
```

It does not mean:

- direct `ml_primary` readiness;
- direct RL state/action/reward readiness;
- availability at intraday second precision.

`valid_for_rl_training_direct` is false for every v0.1 row.

## 6. Excluded Sources

Consumers must preserve these exclusions:

- `ratios_excluded_from_core_v0_1 = true`
- `standalone_financial_root_excluded_from_core_v0_1 = true`

Ratios and standalone `financial_v0_1` require separate promotion before they
can be joined into a training or event-state build.

## 7. Final Rule

`fundamentals_asof_table` is a component of state, not the state itself.

The future event/market-state builder must still compose:

```text
instrument + calendar + daily/intraday + microstructure + fundamentals + news + short + regime
```

under a single decision-time cutoff.

