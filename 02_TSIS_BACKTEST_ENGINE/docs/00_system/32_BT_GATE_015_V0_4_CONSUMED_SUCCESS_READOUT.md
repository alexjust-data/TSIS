# BT-GATE-015 V0.4 Consumed Success Readout

```text
BT-GATE-015 = OPEN_PENDING_V0_4_POSTEXECUTION_EXTERNAL_REVIEW
V0.4 = CONSUMED_FINAL
SECOND_EXECUTION_V0.4 = PROHIBITED
BT-GATE-015_CLOSED_PASS = NOT_AUTHORIZED_PENDING_POSTEXECUTION_EXTERNAL_REVIEW
```

The externally approved V0.4 package had SHA-256
`ed26dd77908e87a84dddaac287798ca0073d9011e775ef72a5f4c1f1998d1bb5`.
The command executed exactly once at `2026-08-05T14:46:13.209293Z`.

```text
physical_data_files_opened = 1
physical_state_records_scanned = 8
physical_state_rows_selected = 1
market_state_dependency_events = 1
event_state_events_emitted = 1
event_state_store_inserts = 1
bounded_probe_observations = 1
typed_scientific_values = 17
delivery_before_available_at = 0
orders / fills / PnL = 0 / 0 / false
provider_modification = false
validation_phase_reached = EVENT_LOOP_COMPLETE
validation_status = PASS
```

```text
deterministic_output_hash =
35c8fbd98e3c167ffa8eebbc3b660e17f88952c0e189698e53fbaa0c2c5fc65a

scientific_manifest_hash =
2f5a438702dee9d87ebcc39df634d454df392b31eeaeb8ee726127cd40e0c45e
```

The delivered order was bounded to:

```text
ReplayBarEvent
-> BoundedMarketStateAvailable
-> BoundedEventStateAvailable
-> EventStateStore
-> bounded observation
```

V0.4 must never be executed again. BT-GATE-015 remains open until an
independent post-execution review accepts this evidence.
