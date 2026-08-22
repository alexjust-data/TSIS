# MASSIVE_TRADES_FULL_HISTORY_CONTROLLED_BACKFILL_REQUIREMENTS_v0_2

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `massive_trades_full_history_controlled_backfill_requirements` |
| `document_version` | `v0_2` |
| `document_role` | `FULL_HISTORY_SOURCE_ACQUISITION_REQUIREMENTS` |
| `document_status` | `DRAFT_CANDIDATE` |
| `supersedes` | `_MASSIVE_TRADES_CONTROLLED_REDOWNLOAD_REQUIREMENTS_v0_1.md` |
| `supersession_reason` | `v0_1 incorrectly restricted final acquisition to selected ticker-days` |
| `provider` | `Massive, anteriormente Polygon.io` |
| `primary_source_family` | `Stocks tick-level trades` |
| `rest_endpoint` | `GET /v3/trades/{stockTicker}` |
| `flat_file_candidate` | `us_stocks_sip/trades_v1` |
| `physical_scope` | `FULL_UNIVERSE_FULL_HISTORY_ALL_SESSIONS` |
| `field_scope` | `FULL_PROVIDER_PAYLOAD_WITH_FORWARD_COMPATIBILITY` |
| `approximate_universe_size` | `4800 governed ticker entries, exact manifest pending` |
| `historical_scope` | `all provider-accessible history, approximately 20 years` |
| `execution_status` | `NOT_STARTED` |
| `canonical_source_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |
| `last_reviewed_at` | `2026-08-07` |

---

## 0.1 Límite de autoridad del artefacto

Este documento define los requisitos que deberán gobernar la futura
adquisición. No constituye evidencia de que el downloader exista, de que el
backfill haya sido ejecutado ni de que los datos resultantes sean íntegros,
completos, certificados o aptos para promoción canónica.

```text
REQUIREMENTS CONTRACT
!=
EXECUTION EVIDENCE
!=
DATA INTEGRITY CERTIFICATION
```

Antes de iniciar la descarga masiva todavía deberán:

```text
1. implementarse el downloader y sus manifests operativos;
2. ejecutarse y aprobarse el pilot técnico;
3. superarse los trece gates de admisión definidos en este contrato;
4. ejecutarse la reconciliación final de cobertura, inventario y hashes;
5. emitirse una decisión independiente de certificación y promoción.
```

La mera existencia o aprobación de este documento no autoriza a declarar el
dataset futuro como completo ni a sustituir silenciosamente el dataset legacy.

---
## 1. Decisión de alcance

La futura adquisición no queda limitada a casos Wake-up ni a ticker-días
seleccionados.

Debe descargar y conservar:

```text
TODO EL UNIVERSO FÍSICO GOBERNADO
aproximadamente 4.800 tickers

×

TODO EL HISTÓRICO ACCESIBLE
aproximadamente veinte años

×

TODAS LAS SESIONES
premarket + RTH + after-hours

×

TODO EL PAYLOAD DE TRADES OFRECIDO POR MASSIVE
campos conocidos + campos opcionales + campos futuros desconocidos
```

La motivación inicial es representar `Wake-up`, pero la adquisición física debe
ser reutilizable para futuros modelos de microestructura que todavía no están
definidos.

```text
RESEARCH QUESTION SCOPE
puede ser acotado

PHYSICAL SOURCE PRESERVATION
no debe quedar acotada a las features conocidas hoy
```

---

## 2. Qué significa descargar todo

En este contrato:

```text
DESCARGAR TODO
=
ser endpoint-complete para la familia de trades
```

Incluye:

```text
1. todos los trades devueltos para cada ticker y fecha;
2. todas las sesiones cubiertas por la fuente;
3. todos los campos presentes en cada objeto de trade;
4. todos los campos opcionales cuando aparezcan;
5. campos nuevos desconocidos sin descartarlos por whitelist;
6. metadata completa de petición, respuesta y paginación;
7. reference data necesaria para interpretar los códigos;
8. evidencia de empty, failure, retry y cobertura.
```

No significa descargar indiscriminadamente todos los productos de Massive. Este
contrato cubre:

```text
Stocks Trades
+
reference conditions
+
reference exchanges
```

Quotes, aggregates, news, fundamentals y otros productos necesitan contratos de
adquisición separados.

---

## 3. Por qué debe redescargarse también RTH

El histórico actual de RTH conserva únicamente:

```text
ticker
date
timestamp
price
size
exchange
conditions
year
month
day
```

El downloader anterior recibió objetos más ricos, pero `normalize_results()`
proyectó la respuesta a esas diez columnas antes de escribir Parquet.

Por tanto:

```text
DESCARGAR SOLO PREMARKET Y AFTER-HOURS
=
INCORRECTO PARA UN DATASET HOMOGÉNEO
```

Produciría:

```text
premarket       rich schema
RTH             reduced legacy schema
after-hours     rich schema
```

La adquisición correcta debe volver a obtener el día completo para recuperar
también durante RTH:

```text
provider trade id
sequence number
participant timestamp
SIP timestamp
TRF timestamp and id
correction indicator
tape
decimal size
full raw payload
```

El RTH existente no se sobrescribirá. Permanecerá como dataset legacy con su
lineage. La nueva adquisición tendrá identidad lógica y versión física propias.

---

## 4. Campos documentados por Massive

La documentación vigente de `GET /v3/trades/{stockTicker}` declara:

```text
conditions
correction                    optional
decimal_size
exchange
id
participant_timestamp
price
sequence_number
sip_timestamp
size
tape                          optional
trf_id                        optional
trf_timestamp                 optional
```

Todos deben conservarse cuando están presentes.

| Campo Massive | Campo normalizado candidato | Obligación |
|---|---|---|
| `id` | `provider_trade_id` | REQUIRED |
| `sequence_number` | `provider_sequence_number` | REQUIRED |
| `participant_timestamp` | `participant_timestamp_ns` | PRESERVE_WHEN_PRESENT |
| `sip_timestamp` | `sip_timestamp_ns` | REQUIRED |
| `trf_timestamp` | `trf_timestamp_ns` | PRESERVE_WHEN_PRESENT |
| `trf_id` | `trf_id` | PRESERVE_WHEN_PRESENT |
| `correction` | `provider_correction_indicator` | PRESERVE_WHEN_PRESENT |
| `conditions` | `provider_condition_codes` | REQUIRED |
| `exchange` | `provider_exchange_id` | REQUIRED |
| `tape` | `tape_id` | PRESERVE_WHEN_PRESENT |
| `price` | `trade_price_raw` | REQUIRED |
| `size` | `trade_size_raw` | REQUIRED |
| `decimal_size` | `trade_decimal_size_raw` | PRESERVE_WHEN_PRESENT |

Referencias oficiales:

- [Massive Stocks REST - Trades](https://massive.com/docs/rest/stocks/trades-quotes/trades)
- [Massive Stocks Flat Files - Trades](https://massive.com/docs/flat-files/stocks/trades)
- [Massive Stocks WebSocket - Trades](https://massive.com/docs/websocket/stocks/trades)
- [Massive - Condition Codes](https://massive.com/docs/rest/stocks/market-operations/condition-codes)
- [Massive - Exchanges](https://massive.com/docs/rest/stocks/market-operations/exchanges)

---

## 5. Forward compatibility

La materialización normalizada puede tener schema explícito, pero el raw no
puede usar una whitelist destructiva.

Regla:

```text
FOR EACH PROVIDER RESULT

persist complete raw object
before
field selection
normalization
sorting
deduplication
eligibility filtering
```

Si Massive añade un campo en el futuro:

```text
RAW LAYER
= preserva el campo automáticamente

NORMALIZED LAYER
= registra SCHEMA_DRIFT
   y requiere nueva versión para promocionarlo
```

No se descarta el campo por no tener utilidad conocida en 2026.

---

## 6. Cobertura temporal completa

Objetivo mínimo por trading date:

```text
PREMARKET
04:00:00 <= America/New_York < 09:30:00

REGULAR TRADING HOURS
09:30:00 <= America/New_York < 16:00:00

AFTER-HOURS
16:00:00 <= America/New_York < 20:00:00
```

Unidad física objetivo:

```text
TICKER-DAY FULL EXTENDED SESSION
04:00-20:00 America/New_York
WITH COMPLETE PROVIDER PAYLOAD
```

Los límites deben ser configurables y calendar-aware. La descarga debe tratar
correctamente:

```text
DST
half days
exchange holidays
exceptional sessions
halts
symbol changes
delistings
days with no returned trades
```

Si Massive devuelve trades fuera de `04:00-20:00`, el raw deberá preservarlos y
el manifest deberá registrarlos. La política de sesión decidirá después cómo
clasificarlos; la ingesta no debe borrarlos silenciosamente.

---

## 7. Universo histórico

El número aproximado de 4.800 tickers debe transformarse antes de ejecutar en un
manifest exacto y versionado.

El manifest deberá resolver:

```text
current ticker
historical ticker aliases
listing and delisting dates
security identity
corporate-action identity transitions
provider ticker syntax
first requested date
last requested date
expected trading dates
```

Regla:

```text
CURRENT TICKER LIST ONLY
!=
FULL HISTORICAL UNIVERSE
```

No se excluirá un ticker-día porque posteriormente no produjo Wake-up, no entró
en un scanner o no resultó rentable.

---

## 8. Timestamps del proveedor y de TSIS

Massive proporciona timestamps del recorrido de mercado:

```text
participant_timestamp
= trade generado en exchange o participante

trf_timestamp
= trade recibido por TRF, cuando aplica

sip_timestamp
= trade recibido por el SIP
```

No son equivalentes a:

```text
observed_at_utc
= TSIS recibió físicamente el mensaje

available_at_utc
= TSIS permitió consumir el dato procesado
```

Para descarga REST histórica:

```text
observed_historical_available_at_utc
= NOT_PROVIDED

source_causal_anchor
= sip_timestamp

simulated_available_at_utc
= sip_timestamp + latency_policy_versioned
```

Para adquisición futura live/shadow, TSIS deberá capturar por mensaje:

```text
local_socket_received_at_utc
raw_persisted_at_utc
normalized_at_utc
available_at_utc
```

Una disponibilidad simulada nunca se etiquetará como observada.

---

## 9. Metadata de adquisición generada por TSIS

Debe conservarse:

```text
run_id
request_id
request_started_at_utc
response_received_at_utc
raw_payload_persisted_at_utc
endpoint and endpoint version
query parameters without secrets
page ordinal
provider response ordinal
next_url traversal state
HTTP status
retry ordinal
raw payload SHA256
code commit
schema version
```

La posición original dentro de `results` debe conservarse antes de cualquier
sort. La API key queda prohibida en manifests, logs y payload sidecars.

---

## 10. Semántica todavía no confirmada

La documentación revisada no declara campos independientes para:

```text
cancellation_action
original_event_reference
late_indicator
out_of_sequence_indicator
provider_available_at
```

Tratamiento:

| Necesidad | Decisión candidata |
|---|---|
| Cancelación | Validar si `correction` codifica cancelación y sus valores. |
| Original reference | Consultar si Massive expone linkage con el trade original. |
| Late | Derivar solo si timestamps, secuencia y condiciones lo permiten. |
| Out of sequence | Derivar conservando response order y sequence number. |
| Provider available_at | No inventar; no está documentado por trade en REST. |

La ausencia de confirmación no autoriza a descartar el resto del payload.

---

## 11. REST frente a Flat Files

La decisión de transporte no cambia el alcance de datos.

```text
REST /v3/trades
= flexible por ticker y rango

S3 us_stocks_sip/trades_v1
= archivo diario de mercado completo
```

Para veinte años y miles de tickers, los Flat Files diarios pueden ser
operativamente más adecuados que millones de peticiones REST. Sin embargo, no
se usarán hasta demostrar mediante pilot:

```text
field parity with REST
timestamp parity
correction parity
condition parity
session coverage
row-count reconciliation
```

Resultado permitido:

```text
IF FLAT_FILE_PARITY = PASS
THEN bulk backfill may use Flat Files

ELSE
REST remains authoritative for missing fields
or a hybrid acquisition is required
```

El método elegido deberá conservar siempre el raw completo disponible en ese
canal.

---

## 12. El pilot no acota la descarga final

Antes del backfill masivo se ejecutará un pilot pequeño para validar el
downloader y evitar una operación multiterabyte incorrecta.

El pilot debe incluir:

```text
premarket trades
RTH trades
after-hours trades
corrections
same-timestamp trades
TRF trades
fractional-size trades
sequence gaps
empty ticker-days
failed requests
```

Pero:

```text
PILOT SCOPE
= technical validation sample

FINAL ACQUISITION SCOPE
= full universe × full history × all sessions
```

Superar el pilot autoriza preparar la operación completa; no convierte la
muestra en el universo final.

---

## 13. Capas físicas requeridas

### 13.1 Immutable raw

```text
complete provider payload
+ request metadata
+ pagination metadata
+ response order
+ cryptographic hash
```

### 13.2 Rich normalized trades

Schema tipado con todos los campos conocidos, sin colapsar timestamps y sin
eliminar el raw.

### 13.3 Coverage sidecar

```text
DOWNLOADED_NONEMPTY
DOWNLOADED_EMPTY
DOWNLOAD_FAILED
PARTIAL_PAGINATION
RETRY_EXHAUSTED
SCHEMA_DRIFT
UNAUTHORIZED_OR_PLAN_LIMIT
```

### 13.4 Reference snapshots

```text
GET /v3/reference/conditions
GET /v3/reference/exchanges
```

### 13.5 Governed manifests

```text
pre-manifest
live manifest and heartbeat
final manifest
inventory reconciliation
hash inventory
failure and retry inventory
```

---

## 14. Operación larga obligatoria

El backfill es una operación multiterabyte y deberá obedecer
`LONG_RUNNING_OPERATIONS_CONTRACT.md`.

No podrá empezar sin:

```text
exact universe manifest
expected ticker-date or date-file manifest
storage capacity estimate
network transfer estimate
API or S3 entitlement confirmation
rate-limit policy
checkpoint and resume design
PID
heartbeat
live log
independent monitor
failure quarantine
final reconciliation manifest
```

No se sobrescribirá el dataset RTH legacy ni se mezclarán silenciosamente raws de
schemas distintos.

---

## 15. Gates de admisión del downloader

```text
GATE 1  FULL FIELD PRESERVATION
GATE 2  UNKNOWN FIELD PRESERVATION
GATE 3  NANOS TIMESTAMP PRESERVATION
GATE 4  RESPONSE ORDER PRESERVATION
GATE 5  PAGINATION COMPLETENESS
GATE 6  PREMARKET/RTH/AFTER-HOURS COVERAGE
GATE 7  EMPTY VS FAILURE SEMANTICS
GATE 8  ID AND DUPLICATE AUDIT
GATE 9  CORRECTION SEMANTICS
GATE 10 REFERENCE CODE SNAPSHOTS
GATE 11 REST/FLAT-FILE PARITY, IF APPLICABLE
GATE 12 DETERMINISTIC REPRODUCIBILITY
GATE 13 LEGACY DATASET NON-DESTRUCTION
```

Fallado cualquier gate, no se inicia el backfill masivo.

---

## 16. Relación con Wake-up

El nuevo dataset permitirá reejecutar
`TRADING_ACTIVITY_AUDIT_CONTRACT_v0_1.md` con una fuente más rica.

No promueve automáticamente:

```text
Trading Activity Representation Model
experimental variables
Wake-up detector
Wake-up Event Type
predictive consumption
strategy
execution
```

La adquisición preserva observabilidad. La admisión científica sigue siendo una
decisión posterior.

---

## 17. Veredicto

```text
FINAL PHYSICAL ACQUISITION SCOPE
= FULL UNIVERSE
× FULL PROVIDER-ACCESSIBLE HISTORY
× PREMARKET + RTH + AFTER-HOURS

FIELD ACQUISITION SCOPE
= COMPLETE PROVIDER TRADE PAYLOAD
× FORWARD-COMPATIBLE RAW PRESERVATION

RTH REDOWNLOAD
= REQUIRED TO RECOVER FIELDS LOST
BY THE LEGACY REDUCED PROJECTION

PILOT
= REQUIRED TECHNICAL GATE
!= FINAL DATA SCOPE

AVAILABLE_AT / OBSERVED_AT
= TSIS TEMPORAL METADATA,
NOT HISTORICAL REST FIELDS

LEGACY RTH DATASET
= PRESERVED, NOT OVERWRITTEN

MASS BACKFILL EXECUTION
= NOT STARTED
```
