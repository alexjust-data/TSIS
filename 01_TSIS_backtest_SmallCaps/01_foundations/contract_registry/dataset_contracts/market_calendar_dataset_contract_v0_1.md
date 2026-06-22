# Market Calendar Dataset Contract `v0_1`

## 1. Rol

Este contrato institucionaliza `market_calendar_v0_1` como output gobernado de
CAPA 1 Data Foundation.

Su funcion es fijar una tabla de sesiones oficiales para:

- expected coverage;
- event windows;
- joins diarios/intradia;
- early closes;
- timezone operacional.

## 2. Identidad

- `dataset_id`: `market_calendar_v0_1`
- `domain`: `outputs`
- `contract_type`: `data_foundation_reference_output`
- `logical_version`: `v0_1`
- `promotion_state`: `initial_materialized_candidate`
- `active`: `true`

## 3. Raiz fisica objetivo

```text
E:/TSIS/data/data_foundation_outputs/market_calendar
```

Artefacto principal:

```text
E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
```

## 4. Fuente upstream

Fuente local:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20251231.parquet
```

Metadata local:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20251231.meta.json
```

Generador historico:

```text
scripts/agent05_build_market_calendar_official.py
exchange_calendars 4.13.1
calendar = XNYS
timezone = America/New_York
```

Fuentes externas de contraste documentadas:

```text
exchange_calendars project source
NYSE Holidays & Trading Hours
Nasdaq Stock Market Holiday Schedule
```

## 5. Alcance v0.1

```text
calendar: XNYS
timezone: America/New_York
start: 2005-01-01
end: 2025-12-31
sessions: 5283
first_session: 2005-01-03
last_session: 2025-12-31
early_close_sessions: 45
```

## 6. Consumidores

Permitidos:

- `event_engine`
- `backtest_core`
- `backtest_extended`
- `dataset_materialization_scope`
- `data_quality_report`
- `master_daily_table`
- `master_intraday_bar_table`
- `expected_data_calendar`
- `research_only`

Restringidos:

- `live_downstream_candidate`, requiere extension a calendario futuro/actual;
- `execution_simulator`, solo como calendario de sesiones, no microestructura.

Prohibidos:

- inferir halts;
- inferir liquidez;
- inferir venue-specific trading availability;
- usar para exchanges no-XNYS sin nuevo contrato.

## 7. Promotion barrier

Para promocion institucional completa:

- schema;
- registry;
- policy;
- validator;
- materializer;
- manifest;
- summary;
- changelog;
- Graphify queue;
- evidencia de reproducibilidad o source contrast documentado.

## 8. Veredicto v0.1

`market_calendar_v0_1` queda definido como output materializable inicial.

No reemplaza futuros calendarios por venue, ni calendario live extendido mas
alla de `2025-12-31`.
