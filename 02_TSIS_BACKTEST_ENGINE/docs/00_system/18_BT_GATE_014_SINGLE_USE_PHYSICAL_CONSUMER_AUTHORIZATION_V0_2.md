# BT-GATE-014 — autorización física single-use V0.2 (registro histórico)

## Estado canónico

```text
authorization_id =
BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-2

status =
SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL

PHYSICAL_CONSUMER_READ = NOT_EXECUTED
PHYSICAL_STATE_ROWS_READ = 0
```

V0.2 fue emitida inicialmente, pero la revisión externa pre-ejecución detectó:

- orden causal efectivo `STATE → BAR`;
- una ventana posterior al consumo sin evidencia durable de fallo;
- contradicciones documentales y de governance.

No fue consumida y no autoriza ninguna lectura. La autoridad vigente para una
posible ejecución futura es exclusivamente V0.3, sujeta a revisión externa y a
su estado machine-readable.

## Evidencia histórica inmutable

El documento original y todos sus bindings se conservan sin modificación en:

```text
bt_gate_014_single_use_physical_preexecution_packet_v0_2_20260730T181505Z.zip
SHA-256 =
189c911ee5ca83ebf279ddf28be86d320e1f26aebab8967637a08259b6259562
```

Este registro no concede autorización, no consume una autorización y no modifica
al provider.
