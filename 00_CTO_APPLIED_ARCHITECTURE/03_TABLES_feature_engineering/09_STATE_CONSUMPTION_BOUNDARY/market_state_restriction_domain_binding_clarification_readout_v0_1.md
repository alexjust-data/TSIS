# Market State Restriction Domain Binding Clarification Readout v0.1

Gate: `market_state_restriction_domain_binding_clarification_v0_1`
Date: `2026-07-30`
Status: `CLOSED_PASS_RESTRICTION_DOMAINS_DISAMBIGUATED_FOR_BT_GATE_014_NO_PHYSICAL_READ_NO_CONSUMER_AUTHORIZATION`

```text
case_count = 19
failed_cases = 0
physical provenance restrictions observed per row = 26
bounded replay-consumption restrictions = 4
required core-four components per row = 4
parquet opened by this gate = false
physical rows read by this gate = 0
backtester files modified = 0
new consumer authorization issued = false
```

The V0.4 failure is accepted as a correct fail-closed result. The physical row
restriction field and the replay sidecar restriction field are not the same
semantic domain and must not be compared for equality.

Physical provenance restrictions remain fingerprinted physical lineage.
Replay-consumption restrictions govern bounded delivery. Component replay
restrictions must propagate into the row replay-consumption set.

V0.4 remains consumed and cannot be reused. This clarification does not
authorize V0.5. The BT-GATE-014 owner must adopt the labeled domains in its
consumer contract, event, store, lineage and regression suite, then submit a
new single-use authorization for independent pre-execution review.
