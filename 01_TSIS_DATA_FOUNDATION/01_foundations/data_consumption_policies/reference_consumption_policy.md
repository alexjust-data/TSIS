# Reference Consumption Policy v0.1

## 1. Rol

Esta policy gobierna como puede consumirse `reference_v0_1`.

El contrato asociado es:

- `01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md`

La registry entry asociada es:

- `01_foundations/dataset_registry/reference/reference_registry_entry.yaml`

## 2. Principio rector

`reference` es infraestructura de identidad, eventos y corporate actions.

No es precio, no es tape, no es universo final y no es feature productiva por defecto.

Su consumo correcto exige declarar:

- subfamilia usada;
- disponibilidad temporal;
- unidad de evento o snapshot;
- si se usa como filtro, contexto, corporate action o variable;
- y que flags de review deben viajar downstream.

## 3. Mapa de subfamilias a usos

| Subfamilia | Uso permitido | Restriccion principal |
| --- | --- | --- |
| `all_tickers` | universo bruto, snapshots, presencia historica | no es universo final ni `<1B>` |
| `overview` | identidad, metadata, market cap observado | no es serie diaria PTI completa |
| `events` | ticker changes, overlays, lifecycle | no cierra continuidad economica |
| `splits` | split_normalized, adjusted, scale audit | no representa dividendos ni ticker remaps |
| `dividends` | adjusted, retorno economico | cola no `CD` requiere lectura |
| `exchanges` | venue metadata | no valida calidad del libro/tape |
| `ticker_types` | filtros de instrumento | no decide liquidez ni elegibilidad |
| `_run` | provenance y descarga | no es market data ni feature |

## 4. Consumidores permitidos

### `corporate_actions_service`

Permitido para:

- `splits`;
- `dividends`;
- `events` solo como continuity/remap input condicionado.

Condicion:

- la transformacion debe declarar si construye `split_normalized`, `adjusted` o solo `adjusted_proxy`.

### `price_view_builders`

Permitido para:

- `daily_adjusted`;
- `ohlcv_1m_split_normalized`;
- futuras vistas `split_normalized`.

Condicion:

- no invertir factores de split;
- no mezclar dividendos y splits sin declarar secuencia;
- no aplicar `ticker_change` como continuidad economica automatica.

### `universe_builder`

Permitido para:

- snapshots `all_tickers`;
- `overview`;
- `ticker_types`.

Condicion:

- no confundir presencia con elegibilidad final;
- mantener ventana temporal y PTI declaradas;
- usar `lt1b_universe` cuando el claim sea `<1B>`.

### `event_engine`

Permitido para:

- `events`;
- `splits`;
- `dividends`;
- `ticker_change` overlays;
- relaciones con `halts`, `quotes` y `trades`.

Condicion:

- separar `good` causal de `review`;
- no promover proximidad temporal a causalidad cerrada sin evidencia.

### `data_audit_overlay`

Permitido para:

- explicar casos de `quotes`, `trades`, `daily`, `1m` y `halts`;
- priorizar drilldowns;
- contextualizar scale mismatch, ticker changes y fragilidad de identidad.

Condicion:

- contexto externo puede explicar, pero no rehabilita automaticamente market data local.

## 5. Consumidores restringidos

### `backtest_core`

Permitido solo como infraestructura:

- filtros de instrumento;
- corporate actions para vistas de precio;
- universe support;
- exclusion o flag de eventos cuando exista contrato.

No permitido:

- usar `ticker_change_near_quotes_anomaly` como senal de trading sin contrato, lag y validacion.

### `backtest_extended`

Permitido para sensibilidad o research event-driven con flags.

Condicion:

- todo evento `review` debe viajar como metadata o mask.

### `ml_flagged`

Permitido solo si:

- se declara disponibilidad temporal;
- se evita leakage;
- la subfamilia se transforma en features con contrato posterior;
- los estados `review` quedan como flags, masks o sample weights.

### `execution_simulator`

No queda habilitado por defecto.

Puede usar `reference` como contexto auxiliar para:

- halts;
- venue metadata;
- corporate actions que afecten continuidad.

Pero la verdad de ejecucion vive en:

- `quotes_raw`;
- `trades_raw`;
- policies de ejecucion futuras.

### `rl_allowed` y `live_downstream_candidate`

Bloqueados hasta contrato especifico posterior.

## 6. Estados y consumo

| Estado | Consumo |
| --- | --- |
| `good_identity_snapshot` | universe/research/context |
| `good_split_event` | price view builders, audit overlays |
| `split_explains_trade_scale_mismatch` | forensic, audit overlay, review of trade scale |
| `ticker_change_near_halt` coherente | event_engine, causal overlay |
| `ticker_change_near_quotes_anomaly` | review detector, not clean good |
| `review_transient_symbol` | research/forensic only unless contracted |
| `review_instrument_type_ambiguity` | filtering review, not automatic exclusion |
| `bad_unresolved_identity` | forensic only |

## 7. Leakage y temporalidad

Reglas:

- `events.date`, `execution_date`, `ex_dividend_date`, `snapshot_date`, `request_date` y `_ingested_utc` no son intercambiables.
- Para ML o backtest, debe declararse que fecha esta disponible en decision time.
- `filing`, `event`, `request` y `ingestion` no tienen la misma semantica temporal.
- Un evento futuro no puede usarse para explicar una decision pasada salvo en auditoria forense.

## 8. Price views

`reference` puede alimentar price views, pero no es una price view.

Relaciones permitidas:

- `splits` -> `split_normalized`
- `splits + dividends` -> `adjusted`
- `splits/dividends/events` -> `adjusted_proxy` diagnostico

Relaciones no permitidas:

- `reference` como execution price;
- `overview.market_cap` como retorno;
- `events` como sustituto de price bars.

## 9. Flags obligatorias

Deben preservarse como metadata o flags:

- `reference_quality_state`;
- `reference_subfamily`;
- `event_type`;
- `event_date`;
- `event_temporal_relation`;
- `causal_overlay_state`;
- `instrument_type`;
- `identity_review_reason`;
- `corporate_action_source`;
- `price_view_affected`.

## 10. Usos no implicados

Esta policy no habilita:

- strategy alpha;
- RL;
- live trading;
- execution simulation final;
- full continuity remap service;
- final point-in-time daily universe membership.

## 11. Condiciones para promocion futura

Para abrir consumidores mas sensibles, hace falta:

- continuity/remap contract para `ticker_change`;
- event feature contract si `events` entra en ML/backtest;
- validators ejecutables o report reproducible;
- evidence dossier actualizado si cambia el estado;
- changelog cuando cambie allowed consumption.

## 12. Regla final

`reference` debe viajar como infraestructura semantica gobernada.

Si un pipeline usa sus eventos sin declarar temporalidad, estado y subfamilia, esta rompiendo el contrato.