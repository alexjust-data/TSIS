# BT-GATE-014 — autorización física single-use V0.3

## Autoridad vigente

```text
authorization_id =
BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-3

consumer_id =
BT_GATE_014_BOUNDED_MARKET_STATE_CONSUMER

status =
AUTHORIZED_NOT_CONSUMED

PHYSICAL_CONSUMER_READ = NOT_EXECUTED
PHYSICAL_STATE_ROWS_READ = 0
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
```

V0.1 y V0.2 están
`SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL`. No conceden autoridad
vigente.

V0.3 autoriza como máximo una lectura física y un único run de integración de
las dos identidades gobernadas ACIU de `2021-03-15`, únicamente después de una
revisión externa pre-ejecución favorable. La emisión de este documento no
ejecuta ni consume la autorización.

## Binding cerrado

```text
authorization_document_sha256 =
98c558a75d27027142a9398fb673a21c9cead8ff957c27db9ca2c20196654109

configuration_sha256 =
11c3b5af6015f5ee3eebe39dcfb6828ef0d51f80e5e4d617357627a64ef3989b

state_machine_sha256 =
1f9f1b1964f78e66bf5a27cf8e3e4834bc35bbb064e4d9c494574b7064bbfc03
```

La configuración y el estado machine-readable congelan nueve inputs provider,
dos handoffs adoptados, dos `source_candidate_record_id`, schema exacto de 40
columnas, join sidecar 1:1, payload tipado de 17 valores, orden causal
`BAR → STATE`, dos inserciones en `MarketStateStore`, dos observaciones y
evidencia completa de éxito o fallo.

## Barrera de consumo

Antes de la transición atómica se crea y sincroniza en disco un
`failure_manifest.json` armado. Después de la transición, cualquier fallo,
incluido el de escritura o validación del recibo, reconcilia ese manifiesto como
evidencia durable. Un segundo uso falla cerrado sin alterar la evidencia del run
anterior.

## Límites

```text
strategy = NONE
orders = 0
fills = 0
PnL = false
provider modification = false
```

Permanecen prohibidos las otras 102 filas, otros símbolos o sesiones, Event
State, `StateReplayFeed` general, Market State como precio y cualquier ruta de
estrategia, ejecución, valoración o contabilidad.

El documento canónico completo es:

```text
docs/00_system/18_BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_3.md
```
