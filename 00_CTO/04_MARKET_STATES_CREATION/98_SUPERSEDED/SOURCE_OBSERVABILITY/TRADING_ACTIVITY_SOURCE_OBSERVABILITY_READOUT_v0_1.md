# TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_1

> Acta de ejecución del contrato de auditoría de observabilidad física de
> `Trading Activity` para el perfil candidato `Wake-up`.

---

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_source_observability_readout` |
| `document_version` | `v0_1` |
| `document_role` | `SOURCE_OBSERVABILITY_AUDIT_READOUT` |
| `document_status` | `EXECUTION_IN_PROGRESS` |
| `audit_contract` | `TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2.md` |
| `base_matrix` | `TRADING_ACTIVITY_AUDIT_CONTRACT_v0_1.md` |
| `information_object_id` | `trading_activity` |
| `representation_model_candidate_id` | `absolute_and_pit_relative_multiscale_marked_activity_process` |
| `current_source_id` | `trades_ticks_prod_2005_2026_legacy_rth_reduced` |
| `current_source_root` | `G:/TSIS/data/trades_ticks_prod_2005_2026` |
| `target_source_contract` | `../_MASSIVE_TRADES_FULL_BACKFILL_REQUIREMENTS.md` |
| `execution_started_at` | `2026-08-06` |
| `current_legacy_source_gate` | `IN_PROGRESS` |
| `target_enriched_source_gate` | `DEFERRED_PENDING_MASSIVE_BACKFILL` |
| `live_temporal_capture_gate` | `DEFERRED_PENDING_LIVE_CAPTURE` |
| `canonical_feature_promotion` | `NOT_AUTHORIZED` |
| `downstream_consumption` | `NOT_AUTHORIZED` |
| `owner` | `TBD` |

```text
READOUT STATUS
==============

EXECUTION
= IN_PROGRESS

CURRENT LEGACY SOURCE
= AUDITED PARTIALLY WITH PHYSICAL EVIDENCE

TARGET ENRICHED SOURCE
= DEFERRED_PENDING_MASSIVE_BACKFILL

FINAL BINDING VERDICT
= NOT YET ISSUED
```

---

## 1. Pregunta auditada

```text
¿Qué partes del modelo candidato de Trading Activity
pueden construirse ahora con la fuente legacy,
qué restricciones deben declararse,
y qué observabilidad queda pendiente del backfill de Massive
o de captura prospectiva live/shadow?
```

Este Readout no evalúa todavía rendimiento predictivo, edge, estrategia,
ejecución ni selección final de variables.

---

## 2. Resumen ejecutivo provisional

Los resultados obtenidos hasta ahora no constituyen un fallo del Information
Object ni del Representation Model.

La fuente legacy conserva hechos suficientes para continuar auditando una
representación restringida de actividad transaccional:

```text
trade count
share volume
dollar volume
event-time arrival rate
intertrade duration with restrictions
temporal concentration with restrictions
raw price
integer size
exchange id
raw condition codes
```

No conserva observabilidad suficiente para afirmar todavía:

```text
full premarket/RTH/after-hours coverage
provider trade identity
provider sequence
separate participant/SIP/TRF timestamps
historical TSIS observed_at
historical TSIS available_at
as-of correction/cancellation replay
deterministic causal ordering of timestamp ties
```

Conclusión de trabajo:

```text
CURRENT LEGACY SOURCE
= potentially usable for a restricted,
   reconciled RTH event-time research profile

FULL WAKE-UP SOURCE PROFILE
= pending enriched Massive backfill
   and prospective temporal capture
```

El perfil restringido no se declara todavía `PASS_WITH_RESTRICTIONS` porque
faltan cerrar la política de condition codes, la cobertura intraventana y la
política de disponibilidad simulada.

---

## 3. Evidencia física ejecutada

### 3.1 Schema observado

Las muestras físicas contienen:

```text
ticker       string
date         string
timestamp    timestamp[us]
price        double
size         int64
exchange     int64
conditions   list
year         int64
month        int64
day          string
```

No contienen:

```text
provider_trade_id
provider_sequence_number
participant_timestamp
sip_timestamp as a separate field
trf_timestamp
trf_id
correction
tape
decimal_size
observed_at
available_at
```

### 3.2 Muestras físicas

| Ticker/fecha | Filas | Min timestamp | Max timestamp | SHA256 |
|---|---:|---|---|---|
| `SGN 2005-11-15` | 16 | `2005-11-15 15:03:15.773000` | `2005-11-15 20:01:45.464000` | `a6f7c961321b58814da500af9759cc9ba0a3cfe41278805eca02929f0954dd4a` |
| `SELF 2016-01-19` | 37 | `2016-01-19 14:40:01.693827` | `2016-01-19 19:47:32.823143` | `ad997c611bd9c593aaf3f86f103b68bb56d9d281e7f83029c6e47984b6ba84d2` |
| `LIDR 2021-08-18` | 2.211 | `2021-08-18 13:30:00.001660` | `2021-08-18 19:59:55.157833` | `71f792980e1f9aaba719485b37610d1f838a1fa0473d540241323c0e63924305` |
| `SGN 2026-03-06` | 8.581 | `2026-03-06 14:30:00.175578` | `2026-03-06 20:59:58.525570` | `19c8778aaabd4a3081dc9529ae1bf17ba00bfca6805b65193ec4138111061e92` |
| `AAGR 2025-02-03` | 1 | `2025-02-03 15:06:50.834344` | `2025-02-03 15:06:50.834344` | `NOT_COMPUTED_IN_THIS_RUN` |

Los timestamps son timezone-naive en el Parquet. Su alineación UTC es coherente
con la transformación del downloader, pero la columna no conserva timezone ni
el tipo de timestamp fuente por fila.

### 3.3 Schema drift observado

```text
2005 sample:
conditions = list<null>

2016+ samples:
conditions = list<int64>
```

La diferencia debe quedar en el registro de schema versions; no invalida por sí
sola precio, tamaño o counts.

### 3.4 Duplicados y empates temporales

| Caso | Filas | Exceso de duplicados exactos | Exceso same-timestamp |
|---|---:|---:|---:|
| `SGN 2005-11-15` | 16 | 0 | 0 |
| `SELF 2016-01-19` | 37 | 0 | 0 |
| `LIDR 2021-08-18` | 2.211 | 3 | 23 |
| `SGN 2026-03-06` | 8.581 | 48 | 446 |
| `AAGR 2025-02-03` | 1 | 0 | 0 |

Esto demuestra que timestamp y contenido económico no bastan siempre para una
identidad única o un orden causal total.

### 3.5 Downloader histórico

Evidencia Git:

```text
commit inspected
= 3121664a5948b93c1d212d5ffedd4f101ac3f8a9

historical path
= 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/
   cell_code/00_data_certification/
   201_agent1_download_trades_ticks_realtime.py

content git hash-object
= 7ca8f21c9a8252bb7186d6c1e2a89a6cd0129139
```

La función histórica:

```text
1. recibió payload.get("results");
2. eligió timestamp = sip OR participant OR TRF;
3. proyectó solo diez columnas;
4. convirtió timestamp a microsegundos timezone-naive;
5. ordenó establemente solo por timestamp;
6. permitió session choices market o premarket.
```

### 3.6 Manifests de adquisición

Diez runs gobernados bajo:

```text
01_TSIS_DATA_FOUNDATION/runs/backtest/trades_lt_1b_download
```

producen:

```text
runs          = 10
tasks_total   = 10,394,196
done_ok       = 10,393,745
done_bad      = 451
pending       = 0
session       = market
```

Los manifests distinguen estados terminales como `DOWNLOADED_EMPTY`,
`DOWNLOADED_OK` y `DOWNLOAD_FAIL` a nivel ticker-día. No demuestran por sí solos
cobertura continua dentro de cada ventana intradía.

### 3.7 Capacidad documentada del proveedor

Massive documenta en `GET /v3/trades/{stockTicker}` campos adicionales como
`id`, `sequence_number`, `participant_timestamp`, `sip_timestamp`, `correction`,
`tape`, `trf_id`, `trf_timestamp` y `decimal_size`.

Referencias:

- [Massive Stocks REST - Trades](https://massive.com/docs/rest/stocks/trades-quotes/trades)
- [Massive Stocks Flat Files - Trades](https://massive.com/docs/flat-files/stocks/trades)
- [Massive - Condition Codes](https://massive.com/docs/rest/stocks/market-operations/condition-codes)
- [Massive - Exchanges](https://massive.com/docs/rest/stocks/market-operations/exchanges)

La documentación del proveedor demuestra capacidad potencial. No demuestra que
el futuro backfill haya sido ejecutado ni que su output físico haya superado los
gates TSIS.

---

## 4. Source Observability Matrix: ejecución actual

| ID | Requisito | Evidencia actual | Veredicto actual | Restricción o siguiente evidencia |
|---|---|---|---|---|
| `TA-SO-001` | Identidad canónica del instrumento | `ticker` físico; identity resolver externo requerido | `OBSERVABLE_WITH_RESTRICTIONS` | Resolver aliases y ticker reuse PIT. |
| `TA-SO-002` | Identidad única del trade/mensaje | No existe ID en legacy; Massive documenta `id` | `DEFERRED_PENDING_MASSIVE_BACKFILL` | Validar clave compuesta e identidad entre revisiones. |
| `TA-SO-003` | `event_time` | `timestamp[us]`; downloader usa SIP, fallback participant/TRF | `OBSERVABLE_WITH_RESTRICTIONS` | Tipo fuente por fila y nanosegundos se perdieron. |
| `TA-SO-004` | `available_at` | No existe histórico TSIS | `REPRODUCIBLE_SIMULATION_ONLY` | Congelar `sip/legacy timestamp + latency_policy`. |
| `TA-SO-005` | `observed_at` | No existe histórico TSIS | `DEFERRED_PENDING_LIVE_CAPTURE` | Capturar en WebSocket live/shadow. |
| `TA-SO-006` | Orden determinista | Orden físico tras stable sort por timestamp | `OBSERVABLE_WITH_RESTRICTIONS` | No equivale a secuencia causal en empates. |
| `TA-SO-007` | Resolución temporal | Microsegundos almacenados; empates observados | `OBSERVABLE_WITH_RESTRICTIONS` | Nanosegundos pendientes; posible bloqueo C1/C2. |
| `TA-SO-008` | Timezone/calendario | Conversión UTC conocida en código; timezone no almacenada | `OBSERVABLE_WITH_RESTRICTIONS` | Aplicar calendario gobernado y documentar DST. |
| `TA-SO-009` | Session phase as-of | Runs `session=market` | `OBSERVABLE_WITH_RESTRICTIONS` | Solo RTH; sesiones extendidas pendientes. |
| `TA-SO-010` | Precio | `price: double`, raw trade | `OBSERVABLE` | Sujeto a política de calidad ya gobernada. |
| `TA-SO-011` | Tamaño | `size: int64` | `OBSERVABLE_WITH_RESTRICTIONS` | `decimal_size` no preservado. |
| `TA-SO-012` | Valor nocional | `price × size` reconstruible | `OBSERVABLE` | Solo cuando ambos campos sean válidos. |
| `TA-SO-013` | Condiciones | Códigos raw preservados parcialmente | `REQUIRES_EVIDENCE` | Materializar snapshot oficial y política de elegibilidad. |
| `TA-SO-014` | Venue/exchange/TRF/tape | Solo `exchange` preservado | `OBSERVABLE_WITH_RESTRICTIONS` | TRF/tape pendientes del backfill. |
| `TA-SO-015` | Corrección/cancelación | No preservadas en legacy; `correction` documentado por Massive | `DEFERRED_PENDING_MASSIVE_BACKFILL` | Cancelación requiere pilot y semántica oficial. |
| `TA-SO-016` | Referencia al original | No existe; no documentada inequívocamente | `REQUIRES_PROVIDER_CONFIRMATION` | Confirmar linkage de revisiones. |
| `TA-SO-017` | Late/out-of-sequence | Sin sequence ni arrival order original | `DEFERRED_PENDING_MASSIVE_BACKFILL` | Derivar solo tras conservar payload y orden raw. |
| `TA-SO-018` | Cobertura temporal | Manifests distinguen OK/EMPTY/FAIL por ticker-día | `OBSERVABLE_WITH_RESTRICTIONS` | No demuestra cobertura intraventana. |
| `TA-SO-019` | Inicio/fin de cobertura | Bounds solicitados conocidos; sin heartbeat intradía | `REQUIRES_EVIDENCE` | Diseñar coverage sidecar por intervalo. |
| `TA-SO-020` | Gaps/outages | Fallos de adquisición registrados por tarea | `OBSERVABLE_WITH_RESTRICTIONS` | Gaps internos no observables con manifests actuales. |
| `TA-SO-021` | Completitud de partición | Expected manifests, estado terminal, archivo y filas | `OBSERVABLE_WITH_RESTRICTIONS` | Formalizar reconciliación por partición. |
| `TA-SO-022` | Duplicados | Duplicados exactos detectables; no existe provider ID | `OBSERVABLE_WITH_RESTRICTIONS` | No eliminar prints idénticos sin identidad. |
| `TA-SO-023` | Mensajes fuera de orden | No se conserva sequence ni raw response order | `DEFERRED_PENDING_MASSIVE_BACKFILL` | Requiere payload enriquecido. |
| `TA-SO-024` | Historial de revisiones | Legacy parece snapshot reconciliado sin revision history | `DEFERRED_PENDING_MASSIVE_BACKFILL` | Su suficiencia depende de semántica Massive confirmada. |
| `TA-SO-025` | Versionado del dataset | Dataset contracts y roots gobernados | `OBSERVABLE_WITH_RESTRICTIONS` | Añadir fingerprint del input exacto por run experimental. |
| `TA-SO-026` | Versionado de schema | Contrato v0_1; drift físico en `conditions` | `OBSERVABLE_WITH_RESTRICTIONS` | Registrar effective periods/fingerprints. |
| `TA-SO-027` | Lineage y hashes | Manifests, Git y hashes físicos disponibles | `OBSERVABLE_WITH_RESTRICTIONS` | Empaquetar evidence manifest del experimento. |
| `TA-SO-028` | Raw/adjusted | Contrato identifica raw trade tape | `OBSERVABLE` | No aplicar ajustes retrospectivos silenciosos. |

---

## 5. Mandatory Tests: estado de ejecución

| Test | Estado | Resultado actual |
|---|---|---|
| `TA-ST-001` | `EXECUTED_PARTIAL` | `DOWNLOADED_EMPTY` existe a nivel ticker-día; `OBSERVED_ZERO` intraventana aún no demostrado. |
| `TA-ST-002` | `EXECUTED_PARTIAL` | `DOWNLOAD_FAIL` se distingue de empty; gaps intraventana pendientes. |
| `TA-ST-003` | `PASS_WITH_RESTRICTIONS` | Caso AAGR con un trade: counts/volume calculables; duraciones `INSUFFICIENT_SAMPLE`. Elegibilidad final pendiente. |
| `TA-ST-004` | `PASS_WITH_RESTRICTIONS` | Existen timestamp ties; row order reproducible, orden causal no demostrado. |
| `TA-ST-005` | `DEFERRED_PENDING_MASSIVE_BACKFILL` | Late arrival no reconstruible con legacy. |
| `TA-ST-006` | `DEFERRED_PENDING_MASSIVE_BACKFILL` | Corrección as-of no reconstruible con legacy. |
| `TA-ST-007` | `REQUIRES_PROVIDER_CONFIRMATION` | Cancelación y vínculo al original no resueltos. |
| `TA-ST-008` | `IN_PROGRESS` | Duplicados exactos observados; prueba cross-partition y dedupe con lineage pendiente. |
| `TA-ST-009` | `IN_PROGRESS` | Falta snapshot versionado y caso de condition code desconocido. |
| `TA-ST-010` | `EXECUTED_PARTIAL` | Partición/tarea fallida no se trata como empty; completitud intrapartición pendiente. |
| `TA-ST-011` | `DEFERRED_PENDING_MASSIVE_BACKFILL` | Fuente actual no permite cruce premarket-RTH. |
| `TA-ST-012` | `IN_PROGRESS` | Código usa `America/New_York` y UTC; falta fixture DST gobernado. |
| `TA-ST-013` | `IN_PROGRESS` | Requiere especificar `simulated_available_at` y tie-break. |
| `TA-ST-014` | `PASS_NEGATIVE_CONTROL` | Legacy sin revision history se clasifica no observable para replay as-of de revisiones. |
| `TA-ST-015` | `PASS_WITH_RESTRICTIONS` | `timestamp[us]` y colisiones observadas; C1/C2 no autorizados todavía. |

---

## 6. Restrictions Register

| Restricción | Efecto | Resolución prevista |
|---|---|---|
| `R-001 RTH_ONLY` | No representa Wake-up premarket ni continuidad after-hours. | Full-history Massive backfill. |
| `R-002 REDUCED_SCHEMA` | Faltan ID, sequence, timestamps separados y revision metadata. | Full payload backfill. |
| `R-003 COLLAPSED_TIMESTAMP` | No puede conocerse por fila si operó fallback. | Conservar participant/SIP/TRF separados. |
| `R-004 HISTORICAL_AVAILABILITY_UNOBSERVED` | No puede afirmarse latencia histórica real TSIS. | Simulación versionada + captura live futura. |
| `R-005 CONDITION_POLICY_OPEN` | `eligible_trade` no está congelado. | Snapshot Massive + policy versionada. |
| `R-006 WINDOW_COVERAGE_OPEN` | Silencio intraventana no equivale aún a cero demostrado. | Coverage sidecar y tests. |
| `R-007 NO_PROVIDER_ID` | Dedupe y ties no tienen identidad fuente. | Backfill enriquecido. |
| `R-008 CONDITIONS_SCHEMA_DRIFT` | Tipos físicos difieren por periodo. | Schema registry por effective period. |

---

## 7. Deferred Evidence Register

### 7.1 Massive historical backfill

```text
provider_trade_id
provider_sequence_number
participant_timestamp_ns
sip_timestamp_ns
trf_timestamp_ns
trf_id
correction
tape
decimal_size
premarket coverage
RTH rich-schema replacement dataset
after-hours coverage
full raw provider payload
```

### 7.2 Provider confirmation

```text
cancellation semantics
correction value mapping
original-event linkage
revision-history behavior in REST and Flat Files
```

### 7.3 Prospective live/shadow capture

```text
observed_at_utc
available_at_utc
socket arrival order
TSIS processing latency
```

---

## 8. Binding verdicts provisionales

| Binding | Estado actual | Razón |
|---|---|---|
| `A Minimal Multiscale Activity` | `IN_PROGRESS_PROVISIONAL_RESEARCH_FEASIBILITY` | Counts, volume, notional e intensidad event-time son físicamente calculables; faltan eligibility, coverage intraventana y latency policy. |
| `B Marked Duration and Concentration` | `IN_PROGRESS_WITH_MATERIAL_RESTRICTIONS` | Sizes y duraciones existen, pero IDs, ties y resolución limitan semántica. |
| `C1 Conditional Duration / ACD` | `DEFERRED_PENDING_ENRICHED_SOURCE_AND_SPEC` | Requiere secuencia/resolución y cardinalidad validadas. |
| `C2 Hawkes` | `DEFERRED_PENDING_ENRICHED_SOURCE_AND_SPEC` | Requiere timestamps finos, orden y source integrity superiores. |

Ningún binding queda admitido ni congelado por este estado provisional.

---

## 9. Hard Gates provisionales

| Gate | Estado |
|---|---|
| `Semantic Coverage` | `PARTIAL_PASS` |
| `Semantic Boundary` | `PASS` |
| `Causal Legality` | `REPRODUCIBLE_SIMULATION_ONLY__POLICY_PENDING` |
| `Source Observability` | `PARTIAL_PASS` |
| `Profile Compatibility` | `RTH_RESEARCH_ONLY` |
| `Missingness Semantics` | `PARTIAL_PASS` |
| `Reproducibility` | `PARTIAL_PASS` |

```text
OVERALL CURRENT LEGACY SOURCE GATE
= IN_PROGRESS

TARGET ENRICHED SOURCE GATE
= DEFERRED_PENDING_MASSIVE_BACKFILL

DECISION-SAFE PROMOTION GATE
= CLOSED
```

---

## 10. Trabajo inmediato que no depende del backfill

```text
1. materializar snapshots versionados de condition codes y exchanges;

2. congelar la Trade Eligibility Policy legacy;

3. definir y testear el coverage sidecar intraventana;

4. materializar fixtures TA-ST-001, 002, 008, 009, 010, 012 y 013;

5. congelar una latency policy para simulated_available_at;

6. registrar schema fingerprints por periodo;

7. cerrar el veredicto legacy de Binding A;

8. mantener por separado el diseño y ejecución futura del backfill Massive.
```

Este trabajo puede continuar sin esperar la descarga masiva.

---

## 11. Siguiente paso autorizado

```text
AUTHORIZED NOW
= continue source audit
   and produce missing evidence fixtures

CONDITIONALLY AUTHORIZABLE AFTER LEGACY GATE CLOSE
= PIT baseline policy candidate
   and Binding A exact experimental specification

NOT AUTHORIZED
= canonical variables
   output tables
   predictive consumption
   strategy
   orders
   execution
```

---

## 12. Estado de cierre

```text
READOUT_STATUS                   = EXECUTION_IN_PROGRESS
TA_SO_REQUIREMENTS_CLASSIFIED    = 28_OF_28
TA_ST_TESTS_CLASSIFIED           = 15_OF_15
TA_ST_TESTS_FULLY_CLOSED         = NOT_YET
CURRENT_LEGACY_SOURCE_GATE       = IN_PROGRESS
TARGET_ENRICHED_SOURCE_GATE      = DEFERRED_PENDING_MASSIVE_BACKFILL
LIVE_TEMPORAL_CAPTURE            = DEFERRED_PENDING_LIVE_CAPTURE
FINAL_BINDING_A_VERDICT          = NOT_YET_ISSUED
CANONICAL_PROMOTION              = NOT_AUTHORIZED
```

---

## 13. Change Log

| Versión | Fecha | Cambio |
|---|---|---|
| `v0_1` | `2026-08-06` | Inicio formal de ejecución; evidencia física legacy; clasificación 28/28 requisitos y 15/15 tests; registros de restricciones y deferrals. |
