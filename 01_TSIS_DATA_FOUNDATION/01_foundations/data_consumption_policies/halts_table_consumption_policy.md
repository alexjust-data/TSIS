# Halts Table Consumption Policy `v0_1`

## 1. Role

This policy governs `halts_table_v0_1`.

It does not replace:

```text
01_foundations/data_consumption_policies/halts_consumption_policy.md
```

The source policy governs the `halts_v0_1` family. This policy governs the CAPA
1 output table derived from that family.

## 2. Principle

`halts_table_v0_1` is event context and market-state interruption context.

It is not:

- price;
- liquidity;
- tape;
- execution truth;
- alpha;
- proof that non-halt windows are clean.

## 3. Required Consumer Behavior

Every consumer must preserve:

- `halt_event_state`;
- `event_granularity`;
- `quality_state`;
- `intraday_consumption_state`;
- `valid_for_intraday_mask`;
- `valid_for_backtest_event_mask_candidate`;
- `requires_decision_time_availability_contract`;
- source lineage.

## 4. Allowed Uses

Allowed:

- Event Engine context;
- daily event context;
- data quality overlays;
- forensic inspection;
- research filtering;
- backtest masks only with availability contract.

## 5. Restricted Uses

`backtest_event_mask_candidate`:

- allowed only when `valid_for_backtest_event_mask_candidate = true`;
- must declare when the halt was knowable to the simulated decision process;
- must not use review rows as exact intraday truth.

`ml_flagged`:

- requires lag/availability control;
- must not use future halt knowledge as pre-event feature.

`execution_simulator`:

- may use as no-trade/suspension context;
- may not use as fill or liquidity truth.

## 6. Prohibited Uses

Blocked:

- `strategy_alpha`;
- `ml_primary`;
- `rl_allowed`;
- `live_downstream_candidate`;
- treating `regulatory_context_only` as intraday window;
- treating `review_partial_identity` as good;
- treating absence of halt as proof of normal market conditions.

## 7. Final Rule

If a downstream consumer cannot explain how it uses each halt state, it is not
allowed to consume this table.

