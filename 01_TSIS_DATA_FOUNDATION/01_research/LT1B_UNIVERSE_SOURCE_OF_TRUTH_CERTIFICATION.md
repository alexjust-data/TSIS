# LT1B Universe Source of Truth Certification

Fecha: 2026-06-20
Estado: certificado de consumo para `01_research`
Scope: Event Discovery, Event Definition, Feature Requirements, Event Engine,
research backtests y labels derivados dentro de `01_TSIS_DATA_FOUNDATION`.

## 1. Decision certificada

Para cualquier busqueda de eventos, preparacion de estrategias, backtest o
labeling sobre el universo smallcap `<1B`, la fuente de verdad institucional es:

```text
dataset_id: lt1b_universe_v0_1
dataset_type: derived_operational_universe
promotion_state: canonical_operational_cut
run_id: 20260320_market_cap_last_observed_cutoff
```

Artefacto fisico canonico:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet
```

Este documento no crea una nueva fuente de verdad. Certifica para `01_research`
la fuente ya gobernada por `01_foundations`.

La autoridad viva permanece en:

```text
01_foundations/dataset_registry/universes/lt1b_universe_registry_entry.yaml
01_foundations/contract_registry/dataset_contracts/lt1b_universe_dataset_contract_v0_1.md
01_foundations/canonical_schemas/universes/lt1b_universe_schema_contract.md
01_foundations/data_consumption_policies/lt1b_universe_consumption_policy.md
01_foundations/module_contracts/raw_data_authority_and_derivation_map.md
```

## 2. Que certifica este documento

Este certificado fija que `01_research` debe tratar `lt1b_universe_v0_1` como el
universo operativo canonico `<1B>` para:

- buscar candidatos de eventos;
- construir queries reproducibles de Event Discovery;
- seleccionar casos humanos revisables;
- preparar definiciones de eventos;
- construir requerimientos de features;
- construir futuras event tables;
- ejecutar backtests de research;
- construir labels y outcomes derivados.

El universo no debe reconstruirse ad hoc desde carpetas de datos, desde
`reference`, desde `financial`, desde `ratios`, desde un snapshot vivo ni desde
conteos de carpetas de OHLCV.

## 3. Conteo certificado

Verificacion fisica local del artefacto canonico en 2026-06-20:

```text
rows: 4824
unique_tickers: 4824
```

Clases incluidas:

```text
active_lt_1b_last_classifiable: 2476
inactive_died_lt_1b:            2348
```

Clases excluidas en el detalle de clasificacion:

```text
ge_1b_last_classifiable:    2837
unclassified_no_market_cap: 4807
```

Regla:

```text
Un ticker entra en lt1b_universe_v0_1 solo si classification_1b esta en:

- active_lt_1b_last_classifiable
- inactive_died_lt_1b
```

`unclassified_no_market_cap` no es una clase elegible y no debe mezclarse con
`<1B`.

## 4. Regla obligatoria de filtrado

El filtro institucional no es solo:

```text
ticker in lt1b_universe_v0_1
```

La regla correcta es:

```text
ticker normalizado + interseccion temporal con [first_seen_date, last_observed_date]
```

Para eventos puntuales:

```text
event_date >= first_seen_date
event_date <= last_observed_date
```

Para ventanas:

```text
window_end   >= first_seen_date
window_start <= last_observed_date
```

Todo script de Event Discovery o backtest que consuma este universo debe guardar
en su manifest:

```yaml
universe_dataset_id: lt1b_universe_v0_1
universe_run_id: 20260320_market_cap_last_observed_cutoff
universe_filter_policy: ticker_plus_pti_window
universe_rows: 4824
universe_physical_path: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet
```

## 5. Linaje del corte `<1B`

El corte `<1B>` no se deriva de un `market_cap` estatico de `reference`.

La cadena institucional es:

```text
universe_pti/tickers_panel_pti
  + D:\ohlcv_daily
  + D:\financial\income_statements
  + ASOF backward join por filing_date
  + TTL_DAYS = 180
  -> population_target_pti.parquet
  -> market_cap_last_observed_by_ticker_1b.parquet
  -> market_cap_cutoff_lt_1b_active_inactive.parquet
```

`population_target_pti.parquet` reconstruye:

```text
market_cap_t = close_t * shares_outstanding_t
```

con:

```text
close_t              -> D:\ohlcv_daily
shares_outstanding_t -> D:\financial\income_statements
anti_lookahead_violations: 0
```

Verificacion fisica local de `population_target_pti`:

```text
rows_total: 29735570
tickers_total: 13066
date_min: 2005-01-01
date_max: 2026-03-09
rows_classifiable: 10278625
```

El detalle de clasificacion `market_cap_last_observed_by_ticker_1b.parquet`
contiene:

```text
rows: 12468
unique_tickers: 12468
market_cap_t_notna: 7661
```

De esos 12468 tickers, el corte operativo `<1B>` conserva solo los 4824
tickers defendibles como `<1B` en su ultimo punto clasificable.

## 6. Relacion con `E:\TSIS\data`

Para Event Discovery y backtesting operativo, la data de mercado nueva puede
vivir en:

```text
E:\TSIS\data
```

Pero esa ruta no define el universo `<1B>`.

Regla:

```text
market data root operativo -> E:\TSIS\data
universe source of truth   -> lt1b_universe_v0_1
```

Ejemplo para busquedas intradia:

```text
leer datos desde E:\TSIS\data\ohlcv_1m
filtrar candidatos con lt1b_universe_v0_1
aplicar ventana [first_seen_date, last_observed_date]
guardar en manifest el dataset_id del universo
```

Si la investigacion usa `ohlcv_1m` raw para senales intradia puras, debe seguir
la regla vigente de `01_research/README.md` sobre split risk. Si cruza sesiones,
usa gaps, retornos multi-dia, `prev_close`, rangos previos o medias, el consumo
de raw `1m` no es promocionable como limpio sin control split-aware.

## 7. Lo que este universo no es

`lt1b_universe_v0_1` no es:

- una tabla RAW vendor;
- una membership diaria fully point-in-time por market cap;
- una lista live actual;
- una tabla de identidad completa;
- una correccion de todas las ventanas historicas de market cap;
- una autorizacion para ignorar calidad de la data consumida.

Es:

```text
derived_operational_universe
canonical_operational_cut
corte operacional <1B con ticker + ventana PTI
```

Si en el futuro se necesita membership diaria estricta por market cap, debe
crearse y promoverse otro dataset. No debe redefinirse silenciosamente
`lt1b_universe_v0_1`.

## 8. Uso aprobado en Event Discovery

El uso aprobado para la fase actual es:

```text
candidate_event_search_lt1b
human_case_review_lt1b
event_definition_support_lt1b
feature_requirement_support_lt1b
research_backtest_universe_filter_lt1b
```

El uso no aprobado es:

```text
live_trading_current_membership
daily_market_cap_membership_truth
raw_data_quality_certificate
split_adjusted_price_truth
identity_master_replacement
```

## 9. Prohibiciones operativas

Queda prohibido para `01_research`:

- reconstruir el universo `<1B>` con filtros locales sobre `financial` o
  `reference` sin nueva identidad logica;
- tratar `unclassified_no_market_cap` como `<1B`;
- usar solo tickers activos actuales y eliminar inactivos historicos;
- usar conteos de carpetas de `ohlcv_1m`, `quotes`, `trades` o
  `ohlcv_1m_split_normalized` como definicion del universo;
- mezclar `>=1B` o no clasificables en resultados etiquetados como `<1B`;
- ocultar en notebooks o prompts que el filtro real fue diferente;
- publicar backtests o eventos como `lt1b` sin manifest de universo.

## 10. Evidencia Graphify

El leaf oficial:

```text
01_foundations/graphify-out/leaf_slices/foundations_authority_20260619/graph.json
```

reconoce `lt1b_universe_v0_1` como nodo de alta conectividad y lo relaciona con:

- `ohlcv_1m_raw_v0_1`;
- `ohlcv_1m_split_normalized`;
- `quotes_core_v0_1`;
- `trades_raw`;
- `halts_v0_1`;
- `reference_v0_1`;
- `daily_return_labels_v0_1`;
- `Short Data Context`;
- `PTI Window Filter`.

Graphify se usa aqui como mapa de relaciones. La autoridad final sigue siendo
el registry, contrato, schema, policy y parquet canonico.

## 11. Deuda y matices conocidos

Existen referencias historicas a rutas antiguas como:

```text
C:\TSIS_Data\02_backtest_SmallCaps\...
C:\TSIS_Data\v1\backtest_SmallCaps\...
```

La ubicacion fisica vigente verificada para consumo actual dentro del modulo es:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\...
```

Esta deuda de paths no cambia la identidad logica del dataset, pero debe
tenerse en cuenta al leer notebooks o documentacion historica.

## 12. Change control

Cualquier cambio futuro que altere cualquiera de estos puntos debe tratarse como
cambio de alta severidad:

- dataset_id del universo;
- regla de inclusion/exclusion;
- corte de market cap;
- definicion de `classification_1b`;
- ventana temporal PTI;
- ruta fisica canonica;
- uso aprobado por research o backtests.

Ese cambio debe actualizar como minimo:

```text
01_foundations/dataset_registry/universes/
01_foundations/contract_registry/dataset_contracts/
01_foundations/canonical_schemas/universes/
01_foundations/data_consumption_policies/
01_research/LT1B_UNIVERSE_SOURCE_OF_TRUTH_CERTIFICATION.md
01_research/README.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
```

## 13. Decision final

Para la fase actual de busqueda de eventos y preparacion de estrategias:

```text
Usar lt1b_universe_v0_1.
Consumir el parquet canonico market_cap_cutoff_lt_1b_active_inactive.parquet.
Filtrar por ticker + ventana PTI.
No inferir <1B desde carpetas de data ni desde market_cap estatico.
Registrar el universo en cada manifest de research.
```

Esta es la lectura institucional vigente para `01_research`.
