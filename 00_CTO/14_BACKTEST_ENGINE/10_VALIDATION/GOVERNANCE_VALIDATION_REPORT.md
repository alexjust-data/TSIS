# Governance Validation Report

status: PASS
validation_date: 2026-07-30

```text
BT-GATE-014 = OPEN_CONTRACT_CORRECTION_REQUIRED
V0.3 = CONSUMED_FAILED_FINAL
V0.4 = CONSUMED_FAILED_FINAL
V0.4 physical progress = 1 file / 2 rows
V0.4 error = FAIL_MARKET_STATE_RESTRICTION_PROPAGATION
V0.4 events / store / orders / fills / PnL = 0 / 0 / 0 / 0 / false
SECOND_EXECUTION_V0.4 = PROHIBITED
NEW_SINGLE_USE_AUTHORIZATION = NOT_AUTHORIZED
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
Governance controlled hashes = 50/50 PASS
```

The V0.4 diagnostic proves that physical-row design/provenance restrictions and sidecar bounded-consumption restrictions are distinct domains. Contract correction is required before another authorization.
