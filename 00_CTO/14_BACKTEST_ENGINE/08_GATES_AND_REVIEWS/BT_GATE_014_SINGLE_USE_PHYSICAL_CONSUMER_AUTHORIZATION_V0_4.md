# BT-GATE-014 - Single-Use Physical Consumer Authorization V0.4

status: AUTHORIZED_NOT_CONSUMED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
physical_command_execution: NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW

## Purpose

V0.4 supersedes no evidence and never reuses V0.3. V0.3 is CONSUMED_FAILED_FINAL.
It corrects closed semantic restriction equivalence and durable physical progress telemetry.

## Frozen scope

- ACIU, 2021-03-15, exactly two governed rows.
- One physical file and one integration run maximum.
- No strategy, orders, fills, PnL, Event State, provider modification or scope expansion.

## Restriction contract

The physical row, sidecar and every component must contain exactly the governed restriction set. Order is not significant. Duplicates, omissions and extras fail closed. Raw restriction_codes_json remains fingerprinted and retained in lineage.

## Durable progress

The run records physical access start, opened-file count, loaded-row count and validation phase. Failure evidence uses that checkpoint and may not reset counters to zero.

## Executable binding

- `configs/fixtures/BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_4.json`: `03268886123d7b2361711385970c13048ba7d1ba9027e386a88ebeed7a35e8b2`
- `scripts/run_bt_gate_014_single_use_physical_market_state_consumer_v0_4.py`: `59dc173068438acc7c920769a1c3b5a7ad3865ec1525d2418dbf5a064f4f498f`
- `src/tsis_backtest/market_state/physical_authorization_v0_4.py`: `3ef8b4d2956bc1b92273b8b65a7083b7b9fe11067002d70a0a563752d25bb906`
- `src/tsis_backtest/market_state/physical_runner_v0_4.py`: `da1701ee4da1039f97d7f0585f53d8c21235f5511c1228b99d36b43b0206115f`
- `src/tsis_backtest/market_state/consumer.py`: `c5007095e6c0689e406c40340f7e1c58f385411e5c18f271ad47dbf2c1575fc5`
- `src/tsis_backtest/market_state/contracts.py`: `b3cf8d469e2c730c5341a37d7bbc3063a14decdb59d073a6b8ac3dd94f4b020b`
- `src/tsis_backtest/market_state/store.py`: `bc9f054657184bd2788c827145f3c5be945384f57d75b5f78c754e36ce3a1d4a`
- `src/tsis_backtest/replay/contracts.py`: `db8591453abb50e4e07125e7297e698c0690a14575fae66bca7795d97676fc29`
- `src/tsis_backtest/preflight/contracts.py`: `12da900f292c8ed4169c7674b125d688dd39712a3d475e3e0fe3cc63575cf238`

## Command (not approved until external PASS)

```text
python scripts/run_bt_gate_014_single_use_physical_market_state_consumer_v0_4.py --confirm-authorization-id BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-4
```

V0.4 must not execute before independent pre-execution approval.

## Verification target

Focused pre-execution suite: 18 tests. Full repository suite: 198 tests.

## R2 preconsumption review execution

The approved R2 command failed before authorization consumption and before physical access because PRODUCTION_SPEC retained the V0.3 barrier hash. V0.4 remained intact. R3 corrects that literal and adds a canonical PRODUCTION_SPEC/configuration regression. A new external PASS is required before execution.
