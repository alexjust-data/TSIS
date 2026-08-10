# Massive Market Operations Reference Snapshot Readout v0.1

## 0. Control

| Campo | Valor |
|---|---|
| `document_id` | `massive_market_operations_reference_snapshot_readout` |
| `document_version` | `v0_1` |
| `document_role` | `THIRD_PARTY_REFERENCE_EVIDENCE_READOUT` |
| `document_status` | `EXECUTED_SNAPSHOT` |
| `snapshot_id` | `massive_stock_market_operations_reference_snapshot_v0_1` |
| `captured_at_utc` | `2026-08-06T22:05:31.281301+00:00` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `owner` | `TBD` |

---

## 1. Fuente

Endpoints oficiales:

```text
GET /v3/reference/conditions
asset_class = stocks
data_type = trade

GET /v3/reference/exchanges
asset_class = stocks
locale = us
```

Documentacion:

- https://massive.com/docs/rest/stocks/market-operations/condition-codes
- https://massive.com/docs/rest/stocks/market-operations/exchanges

La credencial se consumio desde `POLYGON_API_KEY` y no se persistio.

---

## 2. Artefactos

Root:

```text
C:/TSIS_Data/tests/third_party_evidence/massive/market_operations/
snapshot_20260806T220504Z
```

| Artefacto | SHA-256 |
|---|---|
| Conditions raw JSON | `596ad0f2335a0dcafa64f1a47515778ecb47c9680da458a111cf9354208f3038` |
| Conditions normalized CSV | `6325f5e61f783d20703a6ed188b6bf693d9d77c12c8e1050422195d8e8237398` |
| Exchanges raw JSON | `382988cce66ff7c1b648633b5c8f3346d655183f69281d832533551fd7360190` |
| Exchanges normalized CSV | `fc0e4785bcff1e78b7541272714b019c69e062b099533779a7cf5be9a9897cbf` |

---

## 3. Resultado de adquisicion

```text
trade condition codes = 55
condition pages        = 1
condition status       = OK

stock exchanges        = 27
exchange pages         = 1
exchange status        = OK

api key persisted      = false
```

El snapshot de conditions conserva:

```text
id
name and description
data types
legacy flag
exchange dependency
SIP mapping
consolidated update rules
market-center update rules
```

---

## 4. Comparacion con el snapshot local de exchanges

Snapshot local:

```text
G:/TSIS/data/reference/exchanges/exchanges.parquet
rows = 26
```

Snapshot actual Massive:

```text
rows = 27
```

Nuevo ID:

```text
23 | exchange | Texas Stock Exchange LLC | TXSE | participant F
```

Cambios de nombre observados con ID y MIC estables:

```text
id 2
Nasdaq OMX BX, Inc.
-> Nasdaq Texas, Inc.
MIC = XBOS

id 9
NYSE Chicago, Inc.
-> NYSE Texas, Inc.
MIC = XCHI
```

No hay IDs presentes en el snapshot local que falten en el snapshot actual.

---

## 5. Cobertura del pilot fisico RTH

Sobre los 83 parquets `DOWNLOADED_OK` del pilot:

```text
observed exchange IDs = 18
unknown versus current exchange snapshot = 0

observed condition IDs = 14
unknown versus current condition snapshot = 0
```

Condition IDs observados:

```text
2, 7, 9, 10, 12, 14, 16, 17, 31, 32, 37, 41, 52, 53
```

Exchange IDs observados:

```text
1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 14, 15, 17, 18, 19, 20, 21, 62
```

---

## 6. Limite temporal decisivo

El endpoint de referencia esta marcado por el proveedor como actualizado cuando
sea necesario y no ofrece historial PIT de sus mappings.

Por tanto, este snapshot demuestra:

```text
current provider mapping observed at captured_at_utc
```

No demuestra:

```text
condition mapping effective on every historical trade date
exchange name effective on every historical trade date
historical publication timestamp of each mapping change
```

Los IDs y raw condition lists permanecen observables. La interpretacion
historica queda `WITH_RESTRICTIONS` hasta disponer de evidencia temporal
adicional o una politica conservadora preregistrada.

---

## 7. Implicacion para Trade Eligibility

Las reglas oficiales permiten construir por codigo:

```text
consolidated_updates_volume
consolidated_updates_high_low
consolidated_updates_open_close
market_center equivalents
```

No permiten identificar automaticamente:

```text
activity_eligible for the Wake-up construct
causal contemporaneity under legacy collapsed timestamps
historical effective interval of the mapping
```

En particular:

```text
updates_volume = true
does not by itself prove
unrestricted causal activity eligibility
```

Conditions como `Form T/Extended Hours`, `Sold (Out Of Sequence)`, average-price
o contingent trades requieren tratamiento explicito en la policy experimental.

---

## 8. Veredicto

```text
CONDITION SNAPSHOT MATERIALIZATION = PASS
EXCHANGE SNAPSHOT MATERIALIZATION  = PASS
PILOT OBSERVED-ID COVERAGE         = PASS
CURRENT REFERENCE COMPLETENESS     = PASS_FOR_CAPTURED_SNAPSHOT
HISTORICAL PIT SEMANTICS           = NOT_PROVEN
TRADE ELIGIBILITY MAPPING          = READY_FOR_EXPERIMENTAL_POLICY_REVIEW
LEGACY SOURCE GATE                 = IN_PROGRESS
MASSIVE FULL BACKFILL              = DEFERRED_PENDING_MASSIVE_BACKFILL
CANONICAL PROMOTION                = NOT_AUTHORIZED
```

---

## 9. Siguiente paso

Construir una matriz versionada por condition code que separe:

```text
activity eligibility
volume eligibility
notional eligibility
price-forming eligibility
causal restriction state
historical-temporality confidence
reason codes
```

La matriz debe testear `empty`, `known`, `conflicting` y `unknown conditions`
antes de cerrar `TA-ST-009`.

