# Crosswalk Multidataset

## Objetivo

Este documento fija una capa transversal de interpretación entre los bloques auditados de mercado y soporte:

- `daily`
- `ohlcv_1m`
- `quotes`
- `trades`
- `halts`
- `reference`
- `short`
- `additional`

No reaudita ningún bloque. Su función es dejar reglas explícitas de:

- `problema observado -> fuente primaria`
- `fuente secundaria de contraste`
- `regla de resolución de conflictos`
- `artefactos canónicos`
- `qué aporta cada bloque al resto`

Todo lo que se afirma aquí está anclado a cierres de bloque y a artefactos concretos ya materializados en `cache_v2` o equivalentes.

## Documentos de base

### Contrato global y cobertura principal

- [01_auditoria_1B_general.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\01_auditoria_1B_general.md)
- [04_daily_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\daily\04_daily_closeout.md)
- [04_ohlcv_1m_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\ohlcv_1m\04_ohlcv_1m_closeout.md)
- [04_quotes_full_C_D_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\04_quotes_full_C_D_closeout.md)

### Bloques de soporte auditados después

- [04_halts_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\04_halts_closeout.md)
- [04_halts_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\04_halts_causal_overlay_closeout.md)
- [04_reference_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_closeout.md)
- [04_reference_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_causal_overlay_closeout.md)
- [04_short_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\04_short_closeout.md)
- [04_short_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\04_short_causal_overlay_closeout.md)
- [04_additional_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_closeout.md)
- [04_additional_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_causal_overlay_closeout.md)

## 1. Jerarquía de verdad por tipo de problema

### 1.1 Halt formal, interrupción regulatoria o reopen

**Fuente primaria**

- `halts`

**Fuentes secundarias**

- `quotes`
- `trades`

**Evidencia**

- [04_halts_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\04_halts_closeout.md)
- [04_halts_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\04_halts_causal_overlay_closeout.md)
- artefacto canónico:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cache_v2\halts_quotes_trades_visual_cases.parquet`

**Regla**

- si `halts` confirma el evento y `quotes/trades` muestran reacción o reapertura problemática, creer primero a `halts` para la existencia del evento
- usar `quotes` y `trades` para medir:
  - calidad microestructural
  - severidad del crossed
  - perfil del reopen

### 1.2 Identidad del ticker, listing state, ticker reuse, remap

**Fuente primaria**

- `reference`

**Fuentes secundarias**

- `additional.ipos`
- `halts` en casos de `ticker_change_near_halt`

**Evidencia**

- [04_reference_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_closeout.md)
- [04_reference_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_causal_overlay_closeout.md)
- artefactos canónicos:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_identity_snapshot_summary.parquet`
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_remap_review_index.parquet`
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_event_halt_link_candidates.parquet`

**Regla**

- ante conflicto entre `reference` y otra capa sobre qué instrumento es el ticker, creer primero a `reference`
- `ipos` solo eleva contexto de listing reciente; no sustituye a `reference` como verdad de identidad

### 1.3 Corporate actions: split, dividend, ticker change

**Fuente primaria**

- `reference`

**Fuentes secundarias**

- `additional corporate_actions`

**Evidencia**

- [04_reference_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_causal_overlay_closeout.md)
- [04_additional_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_causal_overlay_closeout.md)
- artefactos:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_split_market_link_candidates.parquet`
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_corp_actions_reference_overlap_summary.parquet`

**Regla**

- si `reference` explica un `split_explains_trade_scale_mismatch`, priorizar esa lectura frente a hipótesis de raw corruption
- si `additional corporate_actions` contradice o no solapa exactamente con `reference`, mantener `reference` como fuente primaria y `additional` como contraste secundario

### 1.4 Microestructura intradía

**Fuentes primarias**

- `quotes`
- `trades`

**Fuentes secundarias**

- `halts`
- `reference`
- `additional.news`
- `short`

**Evidencia**

- [04_quotes_full_C_D_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\04_quotes_full_C_D_closeout.md)
- [04_halts_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\04_halts_causal_overlay_closeout.md)
- [04_reference_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_causal_overlay_closeout.md)
- [04_additional_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_causal_overlay_closeout.md)

**Regla**

- `quotes/trades` describen el comportamiento observado
- `halts/reference/news/short` solo deben entrar para explicar o contextualizar ese comportamiento, no para sustituir la lectura primaria de microestructura

### 1.5 Presión short, crowding o squeeze context

**Fuente primaria**

- `short` con baseline oficial FINRA

**Fuentes secundarias**

- `halts`
- `quotes`
- `trades`
- `additional.news`

**Evidencia**

- [04_short_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\04_short_closeout.md)
- [04_short_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\04_short_causal_overlay_closeout.md)
- artefactos:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2\short_volume_market_link_candidates.parquet`
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2\short_interest_market_context_candidates.parquet`

**Regla**

- ante contradicción `Polygon short` vs `FINRA short`, creer primero a `FINRA`
- `short` aporta sobre todo contexto:
  - `short_flow_near_halt`
  - `days_to_cover_spike_near_halt`
- no debe tratarse como verdad primaria de microestructura

### 1.6 Contexto informacional

**Fuente primaria**

- `additional.news`

**Fuentes secundarias**

- `halts`
- `quotes`
- `trades`
- `short`

**Evidencia**

- [04_additional_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_causal_overlay_closeout.md)
- artefactos:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_news_market_link_candidates.parquet`
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_news_link_summary.parquet`

**Regla**

- `news` nunca es verdad del evento
- sí puede subir a explicación `good` cuando:
  - es mono-ticker
  - `published_ny` cae antes de la reacción
  - la reacción intradía es visible
  - y, mejor todavía, hay `halt` same-day

### 1.7 Contexto early-life de listing

**Fuente primaria**

- `additional.ipos`

**Fuentes secundarias**

- `reference`
- `halts`
- `quotes`
- `trades`

**Evidencia**

- [04_additional_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_causal_overlay_closeout.md)
- artefactos:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_ipo_market_link_candidates.parquet`
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_ipo_link_summary.parquet`

**Regla**

- usar `ipos` para distinguir:
  - fragilidad normal de listing reciente
  - frente a anomalía que requeriría otra explicación

### 1.8 Contexto fundamental lento

**Fuente primaria**

- `additional.financials_core`

**Fuentes secundarias**

- `reference`

**Evidencia**

- [03_additional_root_cause_audit_phase1_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\03_additional_root_cause_audit_phase1_closeout.md)
- [04_additional_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_closeout.md)
- artefactos:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_financials_summary.parquet`

**Regla**

- `financials_core` es capa de contexto y modelado lento
- no se usa para explicar intradía o halts puntualizados

### 1.9 Contexto macro

**Fuente primaria**

- `additional.economic`

**Fuentes secundarias**

- `daily`
- `ohlcv_1m`

**Evidencia**

- [04_additional_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_closeout.md)
- artefactos:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_macro_calendar_summary.parquet`

**Regla**

- `economic` sirve para régimen macro o ventanas calendario
- no debe forzarse como explicador ticker-level

## 2. Matriz de aportes entre bloques

### 2.1 `halts -> quotes / trades`

**Aporte**

- explica interrupciones, suspensiones y reopens

**Fuerza**

- `fuerte`

**Prueba**

- `halts_quotes_trades_visual_cases.parquet`
- viewer de `halts` en:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cell_code\01_halts_intraday_visual_overlay.py`

### 2.2 `reference -> trades`

**Aporte**

- explica parte real de `scale_suspect` mediante splits

**Fuerza**

- `fuerte`, pero quirúrgica

**Prueba**

- [04_reference_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_causal_overlay_closeout.md)
- `reference_split_market_link_candidates.parquet`

### 2.3 `reference -> halts`

**Aporte**

- `ticker_change_near_halt`

**Fuerza**

- `medio/fuerte`

**Prueba**

- `reference_event_halt_link_candidates.parquet`
- `775` casos `ticker_change_near_halt` documentados en el cierre causal de `reference`

### 2.4 `reference -> quotes`

**Aporte**

- `ticker_change_near_quotes_anomaly`

**Fuerza**

- `media`, más contextual que concluyente

**Prueba**

- `reference_event_quotes_link_candidates.parquet`
- cierre visual en [04_reference_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\04_reference_causal_overlay_closeout.md)

### 2.5 `short -> halts / market anomaly`

**Aporte**

- `short_flow_near_halt`
- `days_to_cover_spike_near_halt`

**Fuerza**

- `media`

**Prueba**

- `short_volume_halt_link_candidates.parquet`
- `short_volume_market_link_candidates.parquet`
- `short_interest_market_context_candidates.parquet`

### 2.6 `additional.news -> halts / quotes / trades`

**Aporte**

- explica contexto informacional same-day

**Fuerza**

- `media/fuerte` en `news_near_halt_market_event`
- `media` en `news_near_market_anomaly`

**Prueba**

- `additional_news_market_link_candidates.parquet`
- `04_additional_causal_overlay_closeout.md`

### 2.7 `additional.ipos -> halts / quotes / trades`

**Aporte**

- explica fragilidad early-life, sobre todo cuando el listing coincide con halts o mercado roto

**Fuerza**

- `media`

**Prueba**

- `additional_ipo_market_link_candidates.parquet`
- `04_additional_causal_overlay_closeout.md`

### 2.8 `additional corporate_actions -> reference`

**Aporte**

- confirmación secundaria o solape

**Fuerza**

- `débil/media`

**Prueba**

- `additional_corp_actions_reference_overlap.parquet`
- `additional_corp_actions_reference_overlap_summary.parquet`

## 3. Reglas de resolución de conflictos

### 3.1 `halts` vs `quotes/trades`

**Regla**

- si `halts` confirma un evento y `quotes/trades` están raros, clasificar como halt real con distinta calidad microestructural
- no reinterpretar la ausencia de reacción “bonita” como negación del halt

### 3.2 `reference` vs `additional corporate_actions`

**Regla**

- si `reference` y `additional` discrepan en split/dividend/event taxonomy, priorizar `reference`

**Justificación**

- `additional` aparece como capa redundante o secundaria en [04_additional_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\04_additional_causal_overlay_closeout.md)

### 3.3 `FINRA short` vs `Polygon short`

**Regla**

- priorizar `FINRA`

**Justificación**

- [04_short_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\04_short_closeout.md)
- `short_provider_comparison_summary.parquet`
- `venue_err_mean` documentado:
  - FINRA mucho mejor que Polygon

### 3.4 `news` same-day pero publicación tardía

**Regla**

- si el mercado ya estaba roto antes de `published_ny`, clasificar la noticia como contexto y no como detonante

**Justificación**

- viewer de `additional`:
  - `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cell_code\01_additional_causal_overlay.py`

### 3.5 `ipo` same-day pero mercado limpio

**Regla**

- `ipo_market_clean` no sube a explicación causal fuerte; se queda como contexto estructural de listing reciente

### 3.6 `days_to_cover` extremo con `ADV = 0`

**Regla**

- no promover a `good` por defecto

**Justificación**

- documentado en [04_short_causal_overlay_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\04_short_causal_overlay_closeout.md)
- ejemplos revisados manualmente: `AAMC`, `JSYN`, `DMN`

## 4. Artefactos canónicos por familia de pregunta

### 4.1 Para halts y reopens

- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cache_v2\halts_quotes_trades_visual_cases.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cache_v2\halt_event_windows.parquet`

### 4.2 Para identity y corporate actions

- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_identity_snapshot_summary.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_event_halt_link_candidates.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_event_quotes_link_candidates.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_split_market_link_candidates.parquet`

### 4.3 Para short context

- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2\short_volume_market_link_candidates.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2\short_volume_halt_link_candidates.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2\short_interest_market_context_candidates.parquet`

### 4.4 Para news / ipo context

- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_news_market_link_candidates.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_news_link_summary.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_ipo_market_link_candidates.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2\additional_ipo_link_summary.parquet`

### 4.5 Para microestructura primaria

- `quotes` closeout y notebook:
  - [04_quotes_full_C_D_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\04_quotes_full_C_D_closeout.md)
- `trades` closeout del bloque auditado existente
- `daily` y `ohlcv_1m` closeouts:
  - [04_daily_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\daily\04_daily_closeout.md)
  - [04_ohlcv_1m_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\ohlcv_1m\04_ohlcv_1m_closeout.md)

## 5. Guía de uso por escenario

### 5.1 Quiero explicar una anomalía intradía

Orden sugerido:

1. `quotes`
2. `trades`
3. `halts`
4. `reference`
5. `additional.news`
6. `short`
7. `additional.ipos`

### 5.2 Quiero explicar un scale mismatch o discontinuidad de precio

Orden sugerido:

1. `reference`
2. `daily`
3. `ohlcv_1m`
4. `trades`
5. `additional corporate_actions` como confirmación

### 5.3 Quiero explicar fragilidad de un ticker recién listado

Orden sugerido:

1. `additional.ipos`
2. `halts`
3. `quotes`
4. `trades`
5. `reference`

### 5.4 Quiero evaluar si el contexto short ayuda a explicar el caso

Orden sugerido:

1. `short` con FINRA
2. `halts`
3. `quotes`
4. `trades`
5. `additional.news`

### 5.5 Quiero construir features lentas

Orden sugerido:

1. `additional.financials_core`
2. `short_interest`
3. `additional.economic`
4. `reference`

## 6. Conclusión ejecutiva

La arquitectura de interpretación final queda así:

- `quotes/trades` dicen qué pasó en mercado
- `halts` dice si hubo interrupción formal y cómo leer la ventana de reopen
- `reference` dice si estamos mirando la entidad correcta y si hay corporate action que explique la distorsión
- `short` da contexto de crowding, no verdad primaria del evento
- `additional.news` da contexto informacional same-day
- `additional.ipos` explica parte del comportamiento early-life
- `additional.financials_core` y `economic` aportan contexto lento, no microestructura

La utilidad de este crosswalk es operativa:

- reduce contradicciones entre bloques
- fija prioridades de verdad
- y deja una guía común para explicar anomalías, construir features y volver a los artefactos concretos sin reabrir toda la auditoría bloque por bloque
