# 03_TABLES_feature_engineering Local Rules

Status: `local_rules_v0_1`
Date: `2026-07-30`
Parent authority: `C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/LOCAL_RULES.md`

Before changing this layer, read:

```text
STATE_PROVIDER_CONSUMER_RECOVERY.md
AGENT.md
99_ruta_de_trabajo.md
09_STATE_CONSUMPTION_BOUNDARY/README.md
```

## Active-State Precedence

```text
1. STATE_PROVIDER_CONSUMER_RECOVERY.md
2. first active block at the top of AGENT.md
3. first active block at the top of 99_ruta_de_trabajo.md
4. accepted contracts, manifests, matrices and readouts
5. older blocks as historical closure snapshots
```

Only the first handoff block in `AGENT.md` is current.

## Boundary Ownership

```text
03_TABLES_feature_engineering = State Provider and shared boundary
02_TSIS_BACKTEST_ENGINE = State consumer implementation and BT gates
```

Agents must not cross this boundary without explicit scope.

## Evidence Preservation

Accepted ZIPs, hashes, manifests, matrices, readouts and run evidence are
immutable historical authority. Never reuse a consumed authorization, rewrite
an accepted package, replace a historical hash or present a bounded probe as
general backtest authority.

## Six-Question Gate

Before defining or changing an attribute, answer:

```text
1. What phenomenon does it represent?
2. Which governed object or boundary concept owns it?
3. When is it legally available point-in-time?
4. Is it state, event, execution, outcome or audit metadata?
5. Which source, lineage, policy and schema govern it?
6. Which consumers may use it, under what restrictions?
```

## Physical Consumption Rule

Control-plane authority does not imply data-plane authority. Physical reads
require a distinct bounded authorization. Replay eligibility is governed by
`state_available_at_utc`, not `decision_timestamp_utc` alone.

Market State must remain separate from MarketData execution prices, Execution
State, future outcomes, strategy decisions, orders, fills and PnL.

## Recovery Rule

Every semantic gate must leave a scope, reproducible validation, matrix,
readout, evidence identity, living pointer, next owner and explicit
prohibitions. Update `STATE_PROVIDER_CONSUMER_RECOVERY.md` atomically when the
current state changes. Do not rely on conversation history.

Validate the recovery surface with:

```powershell
python scripts/validate_state_provider_consumer_recovery_v0_1.py
```
