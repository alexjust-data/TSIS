# Observable RAW Parquet Content Inventory v0.1

Status: `external_agent_handoff_package`
Date: `2026-07-20`

Este paquete contiene copias planas de los documentos que describen las columnas observadas en muestras parquet por familia RAW dentro de:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\04_DATA_Raw_audit
```

## Rol

Este paquete sirve para entregar a un agente externo una fotografia limpia de la informacion observable RAW documentada.

No certifica datasets.
No promociona fuentes.
No sustituye schemas, contracts, registries, manifests ni validators.

La autoridad operativa permanece en:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations
```

## Contenido Incluido

| Fuente / familia RAW | Documento incluido | Origen |
|---|---|---|
| Trades | `PARQUET_CONTENT_TRADES.md` | `000_TRADES` |
| Quotes | `PARQUET_CONTENT_QUOTES.md` | `001_QUOTES` |
| OHLCV Daily | `PARQUET_CONTENT_OHLCV_DAILY.md` | `002_DAILY` |
| OHLCV Daily Adjusted | `PARQUET_CONTENT_OHLCV_DAILY_ADJUSTED.md` | `003_DAILY_ADJUSTED` |
| OHLCV 1m | `PARQUET_CONTENT_OHLCV_1M.md` | `004_1_MINUTE` |
| OHLCV 1m Split Normalized | `PARQUET_CONTENT_OHLCV_1M_SPLIT_NORMALIZED.md` | `005_1_MINUTE_SPLIT_NORMALIZED` |
| Additionals | `PARQUET_CONTENT_ADDITIONALS.md` | `006_ADDITIONALS` |
| Reference | `PARQUET_CONTENT_REFERENCE.md` | `007_REFERENCE` |
| Halts | `PARQUET_CONTENT_HALTS.md` | `008_HALTS` |
| Short | `PARQUET_CONTENT_SHORT.md` | `009_SHORT` |
| Short Review | `PARQUET_CONTENT_SHORT_REVIEW.md` | `010_SHORT_REVIEW` |

## Exclusion

`011_DAS_API_DATA_MIRROR` no se incluye porque actualmente no contiene un documento `PARQUET_CONTENT*.md`; solo contiene `README.md`.

## Uso Correcto

Leer estos documentos como:

```text
OBSERVABLE INFORMATION
RAW content samples
column inventory evidence
```

No leerlos como:

```text
schema oficial
contrato de consumo
evidencia de cobertura completa
promocion institucional
```
