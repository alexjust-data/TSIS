# Data Derivable Catalog By RAW Source v0.1

Status: `secondary_summary_v0_1`
Date: `2026-07-20`
Scope: `punto_2_informacion_derivable`
Authoritative source: `no`

Operational authority remains in:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations
```

---

## 1. Rol

Este documento crea un catalogo unico de informacion derivable por fuente RAW o fuente gobernada.

Responde:

```text
Que medidas observables puede calcular TSIS
a partir de cada fuente o combinacion de fuentes
que realmente existen en el proyecto?
```

No admite todavia Objetos de Informacion. No decide si `Liquidity`, `Momentum`, `Trading Activity` u otro Objeto merece existir. Eso vive en:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
```

Cadena correcta:

```text
RAW observable
-> informacion derivable
-> candidatos a Objetos de Informacion
-> admision de Objetos
-> variables aprobadas
-> tablas fuente
-> Market State
-> Event State
```

Este documento es una sintesis aplicada. No reemplaza contratos, schemas, registries, validators, manifests ni status matrices.

---

## 2. Documentos Base

### Autoridad RAW / derivacion

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\raw_data_authority_and_derivation_map.md
```

Define `RAW_VENDOR_ORIGINAL`, `RAW_STAGED`, `RAW_AUDITED`, `REFERENCE_DATA`, `CONTEXT_DATA`, `DERIVED_ETL_VIEW`, `FEATURE_LAYER` y `LABEL_TARGET_LAYER`.

### Estado de familias de datos

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_quality_report\family_status_matrix_v0_1.md
```

Cubre `daily`, `quotes`, `trades`, `ohlcv_1m_raw`, `ohlcv_1m_split_normalized`, `ohlcv_daily_adjusted`, `reference`, `Halts`, `short`, `short_review`, `financial`, `additional` e `intraday_regime_features`.

### Elegibilidad de observables

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md
```

### Formulas de derivadas

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_derived_observables_formula_contract_v0_1.md
```

Estado declarado:

```text
state_derived_observables_formula_contract_v0_1 = complete_for_contract_defined_scope
```

### Lineage RAW a consumo

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md
```

### Intradia y microestructura

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\intraday_regime_features_variable_taxonomy_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\microstructure_features_table_multi_window_materialization_plan_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\master_intraday_bar_table_schema_contract.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\microstructure_features_table_schema_contract.md
```

### Contexto as-of

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\news_context_table_schema_contract.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\fundamentals_asof_table_schema_contract.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\short_context_table_schema_contract.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\halts_table_schema_contract.md
```

### Auditoria RAW aplicada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\04_DATA_Raw_audit
```

Subfamilias relevantes: `000_TRADES`, `001_QUOTES`, `002_DAILY`, `004_1_MINUTE`, `005_1_MINUTE_SPLIT_NORMALIZED`, `006_ADDITIONALS`, `007_REFERENCE`, `008_HALTS`, `009_SHORT`, `010_SHORT_REVIEW`.

---

## 3. Estados Usados

| Estado | Significado |
| --- | --- |
| `existing_schema_observable` | Ya existe en schema/componente gobernado. |
| `eligible_now` | Puede entrar bajo reglas actuales. |
| `eligible_with_cutoff_restriction` | Puede entrar solo respetando cutoff/as-of/decision timestamp. |
| `formula_defined_for_state_builder_candidate` | Formula definida para futuro state builder, no necesariamente materializada oficial. |
| `formula_family_defined_requires_variant` | Familia definida; cada variante necesita ventana/version/cutoff. |
| `candidate_requires_formula` | Posible, pero falta formula, ventana, cutoff, lineage y gate. |
| `candidate_requires_materialization` | Requiere tabla/builder/materializacion. |
| `quality_only` | Calidad/gate/lineage, no alpha. |
| `support_only` | Soporte institucional; no variable causal por defecto. |
| `lineage_only` | Solo origen, run, schema, manifest o policy. |
| `blocked_no_source` | No hay fuente gobernada suficiente. |
| `blocked_requires_source` | Bloqueado hasta existir fuente. |
| `future_no_namespace` | Futuro posible, sin namespace oficial hoy. |
| `prohibited_as_feature` | No puede entrar como feature observable de estado. |

---

## 4. Matriz Ejecutiva

| Fuente | Informacion derivable | Estado general | Componente natural |
| --- | --- | --- | --- |
| `OHLCV Daily` | gaps, retornos, rangos, dollar volume, RVOL, volatilidad/rango lookback | mayormente contratado con cutoff | `004_master_daily_table`, `016_market_state_table` |
| `OHLCV 1m` | session-to-time, HOD/LOD, retornos intradia, range, missingness, speed/pace candidatos | contratado parcialmente; muchas variantes requieren formula | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table`, `016_market_state_table` |
| `Trades` | tape activity, volumen, dollar volume, tamanos, min/max/last, calidad de prints | seed/microstructure contratado por ventanas | `015_microstructure_features_table` |
| `Quotes L1` | spread, locked/crossed, top depth, staleness, quote activity, coverage | seed/microstructure contratado por ventanas | `015_microstructure_features_table` |
| `Trades + Quotes` | price impact proxy, liquidity texture, spread/trade response candidatos | parcialmente candidato; requiere alineacion/formulas | `015_microstructure_features_table` |
| `News` | presencia, conteos por ventana, freshness, keyword flags, texto/fuente | literal elegible con cutoff; derivados requieren variantes | `010_news_context_table`, `016`, `017` |
| `Fundamentals / SEC filings` | filing age, statement recency, statement values as-of | elegible con cutoff; ratios requieren variantes | `009_fundamentals_asof_table`, `016`, `017` |
| `Short` | short interest, days to cover, short volume ratio, short z-score candidato | elegible con lags; borrow/locate/SSR bloqueados | `011_short_context_table`, `016`, `017` |
| `Halts / SEC suspensions` | halted at t, time since halt/resume, halt taxonomy | candidato con availability contract | `006_halts_table`, `016`, `017` |
| `Reference / corporate actions` | identidad, lifecycle, split/dividend/ticker-change support, universe scope | support/lineage; no alpha por defecto | `000`, `005`, `016`, `017` |
| `Regime / market context` | returns/ranges/volume/vwap/bars observed de indices/ETFs/contexto | elegible con cutoff si source valid | `012_regime_context_table`, `016`, `017` |
| `MBO / L3 / order lifecycle` | queue position, cancel/add/modify por orden, true replenishment | no disponible como fuente gobernada general | futuro |

---

## 5. OHLCV Daily

Fuente: `daily`, `ohlcv_daily_adjusted`, `master_daily_table`.

Grano:

```text
instrument + session_date + price_view
```

Campos base documentados:

```text
open
high
low
close
volume
vwap
transaction_count
prior_close
price_view
session_date
quality fields
lineage fields
```

Informacion derivable:

| Medida | Inputs | Formula/patron | Estado | Caveat |
| --- | --- | --- | --- | --- |
| `gap_pct` | `open`, `prior_close` | `(open / prior_close) - 1` | `eligible_with_cutoff_restriction` | Legal despues de open y prior close disponible. |
| `daily_return_pct` | `close`, price ref | retorno declarado | `eligible_with_cutoff_restriction` | Same-session final solo tras cierre. |
| `intraday_return_pct` | current/session ref | retorno declarado | `eligible_with_cutoff_restriction` | Depende de cutoff. |
| `daily_range_pct` | `high`, `low` | rango relativo | `eligible_with_cutoff_restriction` | Same-session final solo tras cierre. |
| `dollar_volume` | price, `volume` | price * volume | `eligible_with_cutoff_restriction` | Precio/volumen deben pasar gate. |
| `volume_Nd_avg` | prior valid sessions | avg(volume) over prior N | `formula_family_defined_requires_variant` | N, min_periods y valid-row policy. |
| `rvol_Nd` | volume, `volume_Nd_avg` | volume / average volume | `formula_family_defined_requires_variant` | No usar volumen final antes de cierre. |
| `dollar_volume_Nd_avg` | prior dollar_volume | avg(dollar_volume) | `formula_family_defined_requires_variant` | Requiere formula dollar volume versionada. |
| `volatility_Nd` | declared daily returns | dispersion over prior N | `formula_family_defined_requires_variant` | Definir retorno, estadistico, N. |
| `range_Nd` | declared range metric | aggregate range over prior N | `formula_family_defined_requires_variant` | Definir input y estadistico. |

No confundir con:

```text
book state
tape state
execution state
future outcome
intraday live state antes del cutoff
```

---

## 6. OHLCV 1m

Fuente: `ohlcv_1m_raw`, `ohlcv_1m_split_normalized`, `ohlcv_1m_quote_guarded`, `master_intraday_bar_table`.

Grano:

```text
instrument + closed 1m bar + price_view
```

Campos base documentados:

```text
ts_utc
session_date
bar_size
open
high
low
close
volume
vwap
transaction_count
price_view
session_segment
quote_guarded_view
repair_state
repair_reason
source manifests
quality flags
```

Informacion derivable:

| Medida | Inputs | Formula/patron | Estado | Caveat |
| --- | --- | --- | --- | --- |
| `session_volume_to_time` | closed 1m `volume` | sum volume from session start to t | `formula_defined_for_state_builder_candidate` | Solo bars `<= t`. |
| `session_dollar_volume_to_time` | `volume`, `vwap`, `close` | sum(volume * coalesce(vwap, close)) | `formula_defined_for_state_builder_candidate` | VWAP puede estar bloqueado por calidad. |
| `bars_observed_to_time` | closed 1m bars | count closed bars `<= t` | `formula_defined_for_state_builder_candidate` | Comparar contra expected bars. |
| `high_so_far` | `high` | max(high) over bars `<= t` | `formula_defined_for_state_builder_candidate` | Ignorar invalid/null bajo policy. |
| `low_so_far` | `low` | min(low) over bars `<= t` | `formula_defined_for_state_builder_candidate` | Ignorar invalid/null bajo policy. |
| `range_so_far_ratio` | high_so_far, low_so_far | `(high_so_far / low_so_far) - 1` | `formula_defined_for_state_builder_candidate` | Null si denominador invalido. |
| `return_vs_prior_close_ratio` | price_ref, prior_close | `(price_ref / prior_close) - 1` | `formula_defined_for_state_builder_candidate` | Prior close legalmente disponible. |
| `return_vs_session_open_ratio` | price_ref, session open | `(price_ref / session_open) - 1` | `formula_defined_for_state_builder_candidate` | Session open observable y legal. |
| `return_vs_segment_open_ratio` | price_ref, segment open | `(price_ref / segment_open) - 1` | `formula_defined_for_state_builder_candidate` | Segmento declarado. |
| `bars_expected_to_time` | calendar/session clocks | expected closed bars until t | `formula_defined_for_state_builder_candidate` | Calendar valid requerido. |
| `missing_bar_count_to_time` | expected, observed | max(expected - observed, 0) | `formula_defined_for_state_builder_candidate` | Quality/coverage, no alpha. |
| `missing_bar_ratio_to_time` | missing, expected | missing / expected | `formula_defined_for_state_builder_candidate` | Quality/coverage. |
| `session_so_far_price_volume` | rolling closed OHLCV | window ending `<= t` | `candidate_requires_formula` | Requiere ventana/formula. |
| `returns_continuous` | rolling bars + daily refs | continuous return | `candidate_requires_formula` | Sin thresholds estrategicos. |
| `move_speed_W` | return_ref(t), return_ref(t-W) | delta / elapsed minutes | `formula_family_defined_requires_variant` | W y price_ref versionados. |
| `move_acceleration_W` | move speed | second difference | `formula_family_defined_requires_variant` | Variante obligatoria. |
| `pullback_ratio_W` | high_ref, current price | distance from high/ref | `formula_family_defined_requires_variant` | Anchor/ref declarados. |
| `retrace_ratio_W` | move anchor, current price | retrace from anchor | `formula_family_defined_requires_variant` | Anchor policy obligatoria. |
| `volume_pace_W` | volume_to_time, baseline | volume / expected baseline | `formula_family_defined_requires_variant` | Baseline prior/as-of, no futuro. |
| `dollar_volume_pace_W` | dollar_volume_to_time, baseline | dollar volume / baseline | `formula_family_defined_requires_variant` | Baseline versionado. |
| `time_context` | calendar/session clocks | session/segment position | `candidate_requires_formula` | No usa futuro. |
| `coverage_state` | expected/observed bars | coverage/missingness | `candidate_requires_formula` | Quality/state. |

Variables posibles no cerradas como formula oficial general:

```text
distance_to_VWAP
distance_to_HOD
distance_to_LOD
opening_range
compression
expansion
breakout_distance
pullback_depth
trend_persistence
volume_acceleration
```

Lectura: son derivables posibles desde 1m, pero no deben entrar en state oficial sin formula, ventana, cutoff, quality gate y version.

---

## 7. Trades

Fuente: `trades`.

Estado: `RAW/STAGED trade tape`, `complete_scoped`.

Grano:

```text
instrument + trade print / tape row
```

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `trades_rows` | trade rows | `eligible_with_cutoff_restriction` | Window `<= t`. |
| `trades_window_rows` | trade rows in window | `eligible_with_cutoff_restriction` | Window declarada. |
| `trades_first_ts_utc` | timestamps | `eligible_with_cutoff_restriction` | Source time quality. |
| `trades_last_ts_utc` | timestamps | `eligible_with_cutoff_restriction` | Source time quality. |
| `trades_invalid_price_rows` | price fields | `quality_only` | Calidad, no alpha. |
| `trades_invalid_size_rows` | size fields | `quality_only` | Calidad, no alpha. |
| `trades_odd_lot_ratio_pct` | trade size | `quality_only` / state-quality | Interpretar con policy. |
| `trades_duplicate_exact_ratio_pct` | trade identity | `quality_only` | Gate de tape. |
| `trades_off_regular_session_ratio_pct` | session flags/time | `quality_only` | Gate/session policy. |
| `trades_total_volume` | trade sizes | `eligible_with_cutoff_restriction` | Window legal. |
| `trades_dollar_volume` | price, size | `eligible_with_cutoff_restriction` | Price/size gates. |
| `trades_price_min` | price | `eligible_with_cutoff_restriction` | Window legal. |
| `trades_price_max` | price | `eligible_with_cutoff_restriction` | Window legal. |
| `trades_price_last` | timestamped price | `eligible_with_cutoff_restriction` | Time ordering policy. |
| `trades_size_median` | size | `eligible_with_cutoff_restriction` | Window rows/min rows. |
| `trades_size_p90` | size | `eligible_with_cutoff_restriction` | Window rows/min rows. |
| `trade_intensity_WINDOW` | rows / window seconds | `formula_family_defined_requires_variant` | Window versionada. |

No oficial sin contrato especifico:

```text
buy_sell_classification
aggressor_side
aggressor_imbalance
trade_clustering
tape_speed variants not declared
condition-decoded eligible tape primitives
```

Motivo: requieren decoding de condiciones, politica de elegibilidad, timestamp/sequence behavior y, en muchos casos, alineacion trade-quote.

---

## 8. Quotes L1

Fuente: `quotes`.

Estado: `RAW/STAGED book observations`, `usable_for_declared_scope`.

Grano:

```text
instrument + quote observation / book row
```

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `quotes_rows` | quote rows | `eligible_with_cutoff_restriction` | Window legal. |
| `quotes_window_rows` | quote rows in window | `eligible_with_cutoff_restriction` | Window declarada. |
| `quotes_first_ts_utc` | timestamps | `eligible_with_cutoff_restriction` | Source time policy. |
| `quotes_last_ts_utc` | timestamps | `eligible_with_cutoff_restriction` | Source time policy. |
| `quotes_ask_zero_pct` | ask/ask size | `quality_only` | Quality gate. |
| `quotes_bid_zero_pct` | bid/bid size | `quality_only` | Quality gate. |
| `quotes_ask_size_zero_pct` | ask size | `quality_only` | Quality gate. |
| `quotes_bid_size_zero_pct` | bid size | `quality_only` | Quality gate. |
| `quotes_two_sided_rows` | bid/ask present | `quality_only` / state-quality | Gate. |
| `quotes_crossed_rows` | bid/ask | `eligible_with_cutoff_restriction` | Puede ser state-quality. |
| `quotes_locked_rows` | bid/ask | `eligible_with_cutoff_restriction` | Puede ser state-quality. |
| `quotes_crossed_ratio_pct_all_rows` | crossed/all | `eligible_with_cutoff_restriction` | Quality and state. |
| `quotes_crossed_ratio_pct_two_sided` | crossed/two-sided | `eligible_with_cutoff_restriction` | Quality and state. |
| `quotes_locked_ratio_pct_two_sided` | locked/two-sided | `eligible_with_cutoff_restriction` | Quality and state. |
| `quotes_spread_bps_median` | bid/ask | `eligible_with_cutoff_restriction` | Formula/window declared. |
| `quotes_spread_bps_p90` | bid/ask | `eligible_with_cutoff_restriction` | Formula/window declared. |
| `quotes_top_depth_mean` | bid/ask sizes | `eligible_with_cutoff_restriction` | L1 depth only. |
| `quote_staleness_WINDOW` | quote timestamps | `formula_family_defined_requires_variant` | Window/timezone versionada. |
| `spread_stat_WINDOW_STAT` | spread bps | `formula_family_defined_requires_variant` | Window/stat/min rows. |

No oficial sin formula/version/cutoff:

```text
microprice
quote_lifetime
quote_update_rate variants
depth_replenishment
depth_depletion
bid_ask_imbalance variants
liquidity_recovery
```

Algunas son proxies derivables de L1. Otras requieren MBP/L2 o MBO/L3.

---

## 9. Trades + Quotes

Fuente combinada: `trades + quotes`.

Componente natural:

```text
015_microstructure_features_table
```

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `price_impact_proxy_WINDOW` | price move + liquidity/volume proxy | `formula_family_defined_requires_variant` | Sign policy y refs obligatorios. |
| `liquidity_texture_WINDOW` | spread/depth/trade/quote metrics | `formula_family_defined_requires_variant` | Requiere component formula ids. |
| `trade_volume_price_size_state` | trade window features | `eligible_with_cutoff_restriction` | Desde schema microstructure. |
| `spread_liquidity_state` | quote spread/depth window features | `eligible_with_cutoff_restriction` | Desde schema microstructure. |
| `multi_window_governance_state` | missingness/staleness/event roles | `candidate_requires_materialization` | Plan multi-window, no promocion general. |

Candidatos no oficiales todavia:

```text
OFI
effective_spread
realized_spread
trade_through_behavior
adverse_selection_proxy
aggressor_side_consumption
liquidity_response
```

Requieren alineacion trade-quote, politica participant/feed time, clasificacion de agresor, ventana, formula, cutoff y validacion contra raw.

---

## 10. News

Fuente: `additional_news`, `news_context_table`.

Grano:

```text
ticker + published_utc + article_id
```

Campos base:

```text
published_utc
as_of_utc
publisher_name
author
title
description
keywords
keywords_text
insights
ticker attribution
article_id
```

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `news_presence` | rows by ticker/window | `candidate_requires_formula` | Window/cutoff. |
| `news_article_count_WINDOW` | `published_utc`, ticker attribution | `formula_family_defined_requires_variant` | Attribution quality. |
| `news_freshness_minutes` | latest `published_utc` | `formula_family_defined_requires_variant` | Null if no article. |
| `news_keyword_flag` | title/description/keywords | `formula_family_defined_requires_variant` | Dictionary/version required. |
| `news_source_context` | publisher/author | `eligible_with_cutoff_restriction` | Known at publish/as-of time. |
| `news_text_context` | title/description/keywords/insights | `eligible_with_cutoff_restriction` | No future revision unless versioned. |

No oficial hoy:

```text
sentiment
topic model
novelty
repetition score
entity relevance score
information density
```

Estos requieren modelo, version, training data, cutoff, leakage gate y contrato antes de entrar en state.

---

## 11. Fundamentals / SEC Filings

Fuente: `financial`, `additional_financials`, `fundamentals_asof_table`, SEC filings como evidencia de disponibilidad.

Grano:

```text
ticker + statement_family + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe
```

Campos base:

```text
filing_date
as_of_date
period_end
statement_family
timeframe
fiscal_year
fiscal_quarter
cik
statement values
quality/leakage fields
```

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `filing_age_days` | filing/as_of date, decision date | `formula_defined_for_state_builder_candidate` | Availability date `<= decision_date`. |
| `statement_recency_days` | statement availability, decision date | `formula_defined_for_state_builder_candidate` | No usar `period_end` como availability. |
| `financial_statement_values` | statement fields | `eligible_with_cutoff_restriction` | Fundamentals quality valid. |
| `fundamentals_ratios` | statement fields | `formula_family_defined_requires_variant` | Filing/as-of cutoff required. |

Market cap y float:

```text
overview_market_cap no es feature diaria point-in-time.
lt1b_market_cap_t no equivale a membership diaria fully PIT.
float_context_table no existe oficialmente hoy.
float__point_in_time_share_state = future_no_namespace.
```

---

## 12. Short

Fuente: `short`, `short_review`, `short_context_table`.

Grano:

```text
short interest: ticker + settlement/as_of observation
short volume: ticker + date / venue scope
short context table: governed state component row
```

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `short_interest_state` | short_interest, avg_daily_volume, days_to_cover | `eligible_with_cutoff_restriction` | Source lag/as_of required. |
| `short_volume_state` | total_volume, short_volume, exempt_volume | `eligible_with_cutoff_restriction` | Source lag/as_of required. |
| `days_to_cover` | short_interest, avg_daily_volume | `formula_deferred_to_source_contract` | Not borrow truth. |
| `short_volume_ratio` | short_volume, total_volume | `formula_deferred_to_source_contract` | Null if denominator invalid. |
| `short_interest_z` | days_to_cover / short history | `formula_family_defined_requires_variant` | Window/min periods/source lag. |

Bloqueado:

```text
borrow availability
locate approval
hard-to-borrow state
SSR active state
```

Regla: short interest / short volume no equivale a borrow, locate, availability ni SSR.

---

## 13. Halts / SEC Suspensions

Fuente: `Halts`, `halts_table`, SEC suspensions.

Grano:

```text
halt/suspension event from normalized source feed
```

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `halt_is_halted_at_t` | halt start/resume timestamps, decision timestamp | `formula_defined_for_state_builder_candidate` | Requires decision-time availability contract. |
| `minutes_since_halt_start` | halt_start, t | `formula_defined_for_state_builder_candidate` | Null if not halted/unknown. |
| `minutes_since_resume` | resume, t | `formula_defined_for_state_builder_candidate` | Resume must be known by t. |
| `halt_event_taxonomy_state` | halt_code/type/reason/SEC flag | `eligible_with_cutoff_restriction` | Known at/after event availability. |
| `halt_leakage_gate_state` | availability metadata | `quality_only` | Halt cannot be alpha without availability proof. |

Limites:

```text
SEC suspension rows may be date-level or missing ticker.
An SEC event without intraday timestamp is not an operable intraday window.
```

---

## 14. Reference / Corporate Actions / Universe

Fuente: `reference`, `corporate_actions_table`, `instrument_master`, `lt1b_universe`.

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `identity_state` | ticker/instrument metadata | `support_only` | No alpha por defecto. |
| `security_type_state` | ticker types / reference | `support_only` | Universe/scope support. |
| `exchange_state` | exchanges/reference | `support_only` | Context/support. |
| `corporate_action_adjustment_state` | splits/dividends/ticker changes | `support_only` | Effective-date policy required. |
| `split_action_count` | splits | `support_only` | Support/state if legal. |
| `dividend_action_count` | dividends | `support_only` | Support/state if legal. |
| `ticker_change_action_count` | events/ticker changes | `support_only` | Lifecycle support. |
| `lt1b_scope_state` | lt1b universe derivation | `support_only` | Not full daily PIT membership. |
| `market_cap_t` | lt1b universe cutoff | `support_only` / restricted | Not broad market cap feature by default. |

Bloqueos:

```text
overview_market_cap as daily PIT feature = prohibited / restricted
float_shares as PIT state = future_no_namespace
```

---

## 15. Regime / Market / Economic Context

Fuente: `regime_indicators`, `regime_context_table`, `additional_economic`, market/economic context.

Informacion derivable:

| Medida | Inputs | Estado | Caveat |
| --- | --- | --- | --- |
| `regime_availability_cutoff_state` | as_of fields | `eligible_with_cutoff_restriction` | as_of <= decision timestamp. |
| `regime_price_return_state` | open/high/low/close/previous_close/returns/ranges | `eligible_with_cutoff_restriction` | Same-session final only after availability. |
| `regime_volume_coverage_state` | volume/vwap/bars_observed | `eligible_with_cutoff_restriction` | Only bars observed by t. |
| `economic_context_state` | economic subfamily fields | `candidate_requires_formula` | Requires specific source, lag and availability contract. |

Limite: regime/economic context describe entorno. No debe convertirse silenciosamente en signal, outcome o execution proxy.

---

## 16. MBO / L2 / L3 / Order-Level Data

No hay fuente historica gobernada full-universe de MBO/L3 en el estado actual de este catalogo.

Docs de investigacion/source:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_Live_Source\98_IB_L2_L3.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\08_EXPERIMENTS\000_EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\00_variables microestructurales.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\08_EXPERIMENTS\000_EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\00_OBJECTIVE.md
```

No derivable hoy de forma oficial:

```text
true queue position
individual order lifecycle
add/cancel/modify by order_id
iceberg detection as fact
spoofing detection as fact
true replenishment by order identity
order-level adverse selection
full depth order book memory
```

Estado:

```text
future / blocked_no_source
```

Lectura: L1 quotes pueden producir proxies. MBO/L3 produce observaciones de orden individual. No son equivalentes.

---

## 17. Derivables Prohibidos Como Feature De Estado

No deben entrar como feature observable de estado:

```text
winner / loser
reward
PnL posterior
fill posterior
MFE / MAE
future returns
selected_by_scanner as causal feature
first_cross_50_ts_utc as base state
best threshold found by ML/RL/AlphaEvolve
action taken: enter / exit / hold / scale
daily close/high/low/volume final antes de cierre
halt/resume conocido despues de decision
live news/corporate alert sin received_utc gobernado
borrow/locate/SSR inferred from short volume/interest
semantic labels without formula/version/cutoff
```

---

## 18. Gaps Actuales

| Gap | Estado | Implicacion |
| --- | --- | --- |
| Catalogo unico de derivables | este documento lo crea como sintesis | No sustituye contratos. |
| Variantes de ventanas intradia | `formula_family_defined_requires_variant` | Cada W requiere version. |
| OFI/microprice oficiales | no cerrados como formula oficial general | Requieren formula, alignment y gate. |
| Aggressor classification | no oficial | Requiere trade-condition/alignment policy. |
| News sentiment/topic/novelty | no oficial | Requiere modelo/version/cutoff. |
| Float PIT | `future_no_namespace` | No usar hasta fuente/schema. |
| Borrow/locate/SSR | `blocked_no_source` | No inferir desde short. |
| MBO/L3 | futuro/no source full-history | Solo research/future acquisition. |
| Economic context | parcial | Requiere lag/source-specific contracts. |

---

## 19. Uso Correcto

Para construir una tabla, builder o state component:

```text
1. Elegir fuente RAW o gobernada.
2. Buscar la medida derivable en este catalogo.
3. Verificar su estado.
4. Leer el contrato operativo citado.
5. Si el estado es candidate/requires_variant, crear formula/version/cutoff.
6. Si el estado es blocked/future, no usar como feature.
7. Solo despues mapear a tabla fisica o state builder.
```

Para `Market State`:

```text
No meter todas las columnas.
Consumir solo observables elegibles,
con formula y cutoff,
que representen Objetos de Informacion admitidos.
```

Para `Event State`:

```text
No crear eventos dentro de Event State.
Consumir Market State y source events/event windows gobernados.
Contextualizar el estado respecto al evento.
```

---

## 20. Estado Final

```text
data_derivable_catalog_by_raw_source_v0_1 = created
authority = secondary_summary
operational_source_of_truth = 01_foundations
object_admission_status = not_started_in_this_document
market_state_authorization = not_granted_by_this_document
event_state_authorization = not_granted_by_this_document
```

