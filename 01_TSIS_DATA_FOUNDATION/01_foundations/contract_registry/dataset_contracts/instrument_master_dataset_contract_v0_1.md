# Instrument Master Dataset Contract `v0_1`

## 1. Rol

Este contrato institucionaliza `instrument_master_v0_1` como el primer output
materializable de CAPA 1 Data Foundation.

La tabla existe para que ningun evento, backtest o feature posterior dependa
solo de una etiqueta `ticker`.

Debe responder:

- que ticker pertenece al universo operativo `<1B>`;
- que ventana PTI gobierna ese ticker;
- que identificadores existen para mapear CIK/FIGI/ticker;
- que tipo de instrumento declara reference;
- que flags de identidad deben viajar downstream.

## 2. Identidad

- `dataset_id`: `instrument_master_v0_1`
- `domain`: `outputs`
- `contract_type`: `data_foundation_reference_output`
- `logical_version`: `v0_1`
- `promotion_state`: `initial_materialized_candidate`
- `active`: `true`

## 3. Raiz fisica objetivo

Raiz operativa:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master
```

Artefacto principal:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
```

Artefactos de control:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_summary_v0_1.csv
E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_manifest_v0_1.json
```

## 4. Fuentes upstream

Fuentes gobernadas:

```text
reference_v0_1
lt1b_universe_v0_1
```

Rutas:

```text
E:/TSIS/data/reference/all_tickers/
E:/TSIS/data/reference/overview/
E:/TSIS/data/reference/events/
E:/TSIS/data/reference/exchanges/exchanges.parquet
E:/TSIS/data/reference/ticker_types/ticker_types.parquet
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet
```

## 5. Alcance v0.1

Incluye:

- una fila por ticker incluido en `lt1b_universe_v0_1`;
- ventana `first_seen_date/last_observed_date` del universo operativo;
- ultima metadata reference seleccionada sin mirar mas alla del anchor cuando
  exista una observacion compatible;
- resumen de eventos `ticker_change`;
- flags de identidad y tipo de instrumento.

No incluye:

- reconstruccion diaria fully PTI de market cap;
- continuidad economica cerrada entre ticker changes;
- event table;
- OHLCV;
- news;
- halts;
- strategy features;
- labels o outcomes.

## 6. Semantica temporal

La ventana de validez v0.1 es:

```text
valid_from = lt1b_first_seen_date
valid_to   = lt1b_last_observed_date
```

Esta ventana limita consumo de datos bajo afirmaciones `<1B>`.

No implica que el instrumento haya sido smallcap cada dia dentro de la ventana.
Esa precision queda reservada para un futuro `population_target_pti`.

## 7. Reglas de identidad

`instrument_id` se construye por prioridad:

1. `share_class_figi`
2. `composite_figi`
3. `cik + ticker`
4. `ticker`

La columna `identity_resolution_level` debe preservar la ruta usada.

El fallback `ticker_only_fallback` es usable solo con flag de review.

## 8. Consumidores

Permitidos:

- `event_engine`
- `backtest_core`
- `backtest_extended`
- `dataset_materialization_scope`
- `data_quality_report`
- `research_only`
- `ml_flagged`

Restringidos:

- `execution_simulator`, solo como contexto de identidad;
- `ml_primary`, pendiente de controles de leakage y lifecycle mas fuertes;
- `live_downstream_candidate`, pendiente de validacion operacional.

Prohibidos:

- usar `overview_market_cap` como feature diaria PTI;
- usar ticker changes como alpha;
- resolver mergers/remaps sin lifecycle contract adicional;
- sustituir `reference_v0_1`.

## 9. Promotion barrier

Para declarar `instrument_master_v0_1` institucional completo hace falta:

- schema contract;
- registry entry;
- consumption policy;
- validator;
- materializer reproducible;
- manifest del run;
- resumen fisico;
- changelog;
- Graphify refresh queue;
- y, si se usa para decisiones de alto impacto, dossier visual o tabular de
  casos de identidad conflictiva.

## 10. Veredicto v0.1

`instrument_master_v0_1` queda definido como output inicial materializable y
consumible con flags.

No queda definido como lifecycle engine final.
