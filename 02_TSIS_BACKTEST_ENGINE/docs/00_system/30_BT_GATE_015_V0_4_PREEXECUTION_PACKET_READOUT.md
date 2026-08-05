# BT-GATE-015 V0.4 Corrected R2 Pre-Execution Packet Readout

Status:

```text
BT_GATE_015_V0_4_PREEXECUTION_PACKET = CORRECTED_R2_READY_FOR_EXTERNAL_REVIEW
BT-GATE-015_V0.4 = AUTHORIZED_NOT_CONSUMED
PHYSICAL_COMMAND_EXECUTION = NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
EVENT_STATE_PHYSICAL_READ = NOT_EXECUTED
PHYSICAL_STATE_RECORDS_SCANNED / SELECTED = 0 / 0
BT-GATE-015_CLOSED_PASS = NOT_AUTHORIZED
```

The prior package `ed16c2bc...f9d4` failed external pre-execution review and
must not be executed. The corrected package uses the filename pattern:

```text
deliverables/bt_gate_015_single_use_physical_preexecution_packet_v0_4_corrected_r1_<UTC>.zip
```

Its exact SHA-256 is reported out of band after packaging so the canonical tree
is not mutated after the ZIP snapshot is created.

Validation required before transfer:

```text
missing / unexpected / hash / size errors = 0 / 0 / 0 / 0
provider Event State JSONL included = 0
provider Event State Parquet included = 0
V0.4 physical run directory = ABSENT
focused V0.4 suite = 24/24 PASS
full repository suite = 280/280 PASS
governance = PASS
canonical tree drift after packaging = 0
```

The specification freezes an exact 27-file executable binding set. Empty,
incomplete, extra and byte-mutated maps fail before authorization consumption.

## Next Required Action

Submit the corrected ZIP and its externally reported SHA-256 for independent
pre-execution review. Do not run `RUN_BT_GATE_015_PHYSICAL_V0_4.py` until the
review explicitly returns:

```text
BT_GATE_015_V0_4_PREEXECUTION_EXTERNAL_REVIEW = PASS
PHYSICAL_COMMAND_EXECUTION = APPROVED_SINGLE_USE_V0_4
```

A pre-execution PASS authorizes one execution only. It does not close
BT-GATE-015; post-execution evidence requires a separate review.