# State Derived Observables Formula Contract v0.1

## Estado

Tipo: derived observables formula contract.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Fecha: 2026-07-04.

Status:

```text
contract_defined
formula_gate_complete_for_declared_scope = true
state_builder_materialized = false
market_state_table_materialized = false
event_state_table_materialized = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

Este contrato cierra el gate de formulas derivadas para el scope declarado por:

```text
state_observable_eligibility_contract_v0_1.md
```

No materializa datos. No crea un builder. No promociona `market_state_table` ni
`event_state_table`. No decide que ventana es cientificamente optima. Fija como
se deben definir, versionar y gobernar derivadas antes de que un state builder
las pueda consumir.

## Fuentes Normativas

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_master_daily_table.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_scanner_candidates_table_v0_1.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_microstructure_features_table.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_regime_context_table.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_short_context_table.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_daily_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md
```

## Principio Central

```text
derived observable = transformacion reproducible de inputs observables legales,
con formula, ventana, baseline, cutoff, missingness policy, quality gate,
lineage y version.
```

Un derivado puede ser simple o complejo, pero nunca puede introducir:

```text
outcome futuro
label
reward
accion
fill
PnL posterior
best threshold descubierto
seleccion de scanner como senal causal
conocimiento posterior al decision timestamp
```

## Regla Critica: Formula No Es Relevancia

Que una derivada exista no significa que sea la mejor variable para una
estrategia.

Ejemplo:

```text
rvol_20d existe porque master_daily_table lo materializa.
Eso no prueba que 20 sesiones sea la ventana optima.
```

Si un analisis, AlphaEvolve, ML, RL o una estadistica de estrategia propone una
variante:

```text
rvol_14d
rvol_60d
rvol_to_time_5m
spread_p90_30s
move_speed_7m
```

esa variante no sustituye silenciosamente al observable existente. Debe entrar
como nuevo observable candidato versionado.

## Regla De Identidad Versionada

No se permite cambiar una formula manteniendo el mismo nombre.

```text
same observable name = same formula + same inputs + same window + same baseline
                      + same cutoff + same missingness + same unit policy
```

Si cambia una pieza, cambia el observable.

Ejemplos:

```text
daily__rvol_20d                         # existente en master_daily_table
daily__rvol_14d_candidate_v0_1          # candidato nuevo
intraday__move_speed_5m_candidate_v0_1  # candidato nuevo
microstructure__spread_p90_30s_v0_1     # candidato nuevo
```

## Unit Policy

Este contrato evita mezclar ratios con puntos porcentuales.

Regla:

```text
ratio = fraccion decimal: 0.50 significa +50%.
pct_points = puntos porcentuales: 50.0 significa +50%.
```

Advertencia actual:

```text
master_daily_table usa nombres con sufijo _pct, pero el builder actual calcula
ratios fraccionales: gap_pct = open/prior_close - 1.
```

Por tanto, todo nuevo observable debe declarar unidad explicitamente. Para
nombres nuevos se prefiere:

```text
*_ratio        si almacena fraccion decimal
*_pct_points   si almacena puntos porcentuales
```

Los nombres heredados del schema se respetan, pero su unidad queda documentada
en este contrato.

## Modelo De Fila

Cada derivada debe declarar:

```text
area
observable_name
observable_role
source_component
source_inputs
formula_id
formula
unit
window
baseline
cutoff_rule
missingness_policy
quality_gate_required
lineage_required
allowed_for_market_state
allowed_for_event_state
allowed_for_ml
allowed_for_rl
allowed_for_alphaevolve
status
notes
```

## Status Vocabulary

| Status | Significado |
| --- | --- |
| `formula_defined_existing_schema` | columna derivada ya existe en schema/builder y la formula queda documentada aqui |
| `formula_defined_for_state_builder_candidate` | formula v0.1 definida para futuro state builder, pero no materializada todavia |
| `formula_family_defined_requires_variant` | familia permitida, pero cada ventana/baseline concreto debe crear variante versionada |
| `formula_deferred_to_source_contract` | se acepta como columna fuente/as-of, pero no se recomputa aqui |
| `blocked_requires_source` | formula posible pero falta fuente legal/as-of |
| `prohibited_as_state_formula` | no puede ser formula de estado base |

# 1. Daily Formulas

Fuente principal:

```text
source_component = master_daily_table_v0_1
builder = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_master_daily_table.py
```

Regla daily:

```text
Daily aporta memoria/contexto historico y cierre de sesiones.
Para decisiones intradia, los valores finales de la sesion actual no son legales
antes del cierre y disponibilidad.
```

| observable_name | source_inputs | formula | unit | window / baseline | cutoff_rule | missingness / quality | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `daily__gap_pct` | `open`, `prior_close` | `(open / prior_close) - 1` when `prior_close > 0` and `open is not null` | ratio despite `_pct` suffix | current open vs prior close | legal after current open and prior close availability | null if invalid; row price integrity required | `formula_defined_existing_schema` |
| `daily__daily_return_pct` | `close`, `prior_close` | `(close / prior_close) - 1` when `prior_close > 0` and `close is not null` | ratio despite `_pct` suffix | session close vs prior close | same-session only after close/availability; prior sessions allowed | null if invalid; row price integrity required | `formula_defined_existing_schema` |
| `daily__intraday_return_pct` | `close`, `open` | `(close / open) - 1` when `open > 0` and `close is not null` | ratio despite `_pct` suffix | session close vs open | same-session only after close/availability; prior sessions allowed | null if invalid; row price integrity required | `formula_defined_existing_schema` |
| `daily__daily_range_pct` | `high`, `low` | `(high / low) - 1` when `low > 0` and `high is not null` | ratio despite `_pct` suffix | session high vs low | same-session only after close/availability; prior sessions allowed | null if invalid; row price integrity required | `formula_defined_existing_schema` |
| `daily__dollar_volume` | `close`, `volume` | `close * volume` when both are not null | USD not adjusted for execution price | session | same-session only after close/availability; prior sessions allowed | null if missing; price and volume valid | `formula_defined_existing_schema` |
| `daily__volume_20d_avg` | `volume` | `avg(volume)` over valid rows `20 preceding` to `1 preceding`, partitioned by `ticker, price_view`, ordered by `session_date` | shares | 20 prior valid closed sessions | only prior sessions; never includes current session | valid rows only: `data_present`, no hard invalid price, no negative volume | `formula_defined_existing_schema` |
| `daily__rvol_20d` | `volume`, `volume_20d_avg` | `volume / volume_20d_avg` when `volume_20d_avg > 0` and `volume is not null` | ratio | current closed session vs prior 20 valid-session avg | current session only after close/availability; prior sessions allowed | null if baseline missing/zero | `formula_defined_existing_schema` |

## 1.1 Daily Adjustable Families

Estas formulas no son oficiales por aparecer aqui. Son familias permitidas para
candidatos versionados.

| candidate_family | formula pattern | required variant fields | status |
| --- | --- | --- | --- |
| `daily__volume_Nd_avg_candidate` | `avg(volume)` over prior `N` valid closed sessions | `N`, valid-row policy, price_view, min_periods | `formula_family_defined_requires_variant` |
| `daily__rvol_Nd_candidate` | `volume / daily__volume_Nd_avg_candidate` | `N`, min_periods, denominator policy | `formula_family_defined_requires_variant` |
| `daily__dollar_volume_Nd_avg_candidate` | `avg(dollar_volume)` over prior `N` valid closed sessions | `N`, dollar_volume formula version, min_periods | `formula_family_defined_requires_variant` |
| `daily__volatility_Nd_candidate` | dispersion of declared daily return over prior `N` sessions | return input, statistic, `N`, min_periods | `formula_family_defined_requires_variant` |
| `daily__range_Nd_candidate` | aggregate of declared range metric over prior `N` sessions | range input, statistic, `N`, min_periods | `formula_family_defined_requires_variant` |

# 2. Intradia 1m Formulas

Fuente principal:

```text
source_component = master_intraday_bar_table_v0_2_candidate_quote_guarded
upstream = raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet
```

Regla intradia:

```text
Solo barras cerradas `<= decision_timestamp_utc` pueden alimentar estado, salvo
policy explicita de decision dentro de barra. Los thresholds de scanner no son
formulas de estado base.
```
| observable_name | source_inputs | formula | unit | window / baseline | cutoff_rule | missingness / quality | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `intraday__session_volume_to_time` | closed 1m `volume` | `sum(coalesce(volume, 0))` ordered by `ts_utc` from session start to `t` | shares | session-to-time | bars `<= t` only | missing bars must be counted by coverage state | `formula_defined_for_state_builder_candidate` |
| `intraday__session_dollar_volume_to_time` | closed 1m `volume`, `vwap`, `close` | `sum(coalesce(volume,0) * coalesce(vwap, close))` from session start to `t` | USD proxy | session-to-time | bars `<= t` only | null/zero policy inherited from bar quality; missing bars counted separately | `formula_defined_for_state_builder_candidate` |
| `intraday__bars_observed_to_time` | closed 1m bars | `count(closed bars with ts_utc <= t)` | count | session-to-time | bars `<= t` only | expected bars compared in coverage formula | `formula_defined_for_state_builder_candidate` |
| `intraday__high_so_far` | closed 1m `high` | `max(high)` over bars `<= t` | price | session-to-time or declared segment | no future bars | ignore null invalid bars; quality gate required | `formula_defined_for_state_builder_candidate` |
| `intraday__low_so_far` | closed 1m `low` | `min(low)` over bars `<= t` | price | session-to-time or declared segment | no future bars | ignore null invalid bars; quality gate required | `formula_defined_for_state_builder_candidate` |
| `intraday__range_so_far_ratio` | `high_so_far`, `low_so_far` | `(high_so_far / low_so_far) - 1` when `low_so_far > 0` | ratio | session-to-time or declared segment | only bars `<= t` | null if invalid denominator | `formula_defined_for_state_builder_candidate` |
| `intraday__return_vs_prior_close_ratio` | last closed `close` or `high_so_far`, `prior_close` | `(price_ref / prior_close) - 1` where `price_ref` is declared | ratio | point-in-time | `prior_close` must be prior closed daily value; price ref `<= t` | null if prior_close missing/zero | `formula_defined_for_state_builder_candidate` |
| `intraday__return_vs_session_open_ratio` | last closed `close` or `high_so_far`, session open | `(price_ref / session_open) - 1` | ratio | point-in-time | session open observable and price ref `<= t` | null if open missing/zero | `formula_defined_for_state_builder_candidate` |
| `intraday__return_vs_segment_open_ratio` | last closed `close` or `high_so_far`, segment open | `(price_ref / segment_open) - 1` | ratio | declared segment | segment open observable and price ref `<= t` | null if segment open missing/zero | `formula_defined_for_state_builder_candidate` |
| `intraday__vwap_distance_ratio` | last closed `close`, cumulative/session VWAP | `(close / vwap_ref) - 1` when `vwap_ref > 0` | ratio | declared VWAP window | all VWAP inputs `<= t` | null if vwap missing/zero | `formula_family_defined_requires_variant` |
| `intraday__bars_expected_to_time` | market calendar/session clocks, `t`, bar_size | count expected closed bars from segment/session start through `t` | count | session/segment to time | calendar only; no market future data | market calendar required | `formula_defined_for_state_builder_candidate` |
| `intraday__missing_bar_count_to_time` | expected bars, observed bars | `max(expected - observed, 0)` | count | session/segment to time | expected/observed only through `t` | expected_data_calendar required | `formula_defined_for_state_builder_candidate` |
| `intraday__missing_bar_ratio_to_time` | expected bars, observed bars | `missing_bar_count / expected` when `expected > 0` | ratio | session/segment to time | through `t` only | null if expected zero | `formula_defined_for_state_builder_candidate` |

## 2.1 Intradia Shape/Pace Families

Estas familias son centrales para estrategias 1m, pero no fijan una ventana
unica. Cada variante debe nombrar ventana, price reference y baseline.

| candidate_family | formula pattern | required variant fields | status |
| --- | --- | --- | --- |
| `intraday__move_speed_W_candidate` | `(return_ref(t) - return_ref(t-W)) / elapsed_minutes` | `W`, return_ref, price_ref, segment/session scope | `formula_family_defined_requires_variant` |
| `intraday__move_acceleration_W_candidate` | `move_speed_W(t) - move_speed_W(t-W)` or declared second difference | `W`, speed formula id, elapsed policy | `formula_family_defined_requires_variant` |
| `intraday__pullback_ratio_W_candidate` | `(high_so_far - current_price) / high_so_far` or declared ref | `W`, high_ref, current_price_ref | `formula_family_defined_requires_variant` |
| `intraday__retrace_ratio_W_candidate` | retrace from declared move anchor to current price | `W`, anchor policy, price_ref | `formula_family_defined_requires_variant` |
| `intraday__volume_pace_W_candidate` | `volume_to_time / expected_volume_to_time_baseline` | `W`, baseline universe, historical sessions, min_periods | `formula_family_defined_requires_variant` |
| `intraday__dollar_volume_pace_W_candidate` | `dollar_volume_to_time / expected_dollar_volume_to_time_baseline` | `W`, baseline formula, historical sessions, min_periods | `formula_family_defined_requires_variant` |

Prohibicion:

```text
first_cross_50_ts_utc no es formula base de estado.
Si se estudian cruces, el porcentaje y la ventana viven en scanner/evaluator o
candidate formula versionada, no en el observable base.
```

# 3. Microestructura Formulas

Fuente principal:

```text
source_component = microstructure_features_table
builder = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_microstructure_features_table.py
```

Regla microestructura:

```text
Toda formula depende de una ventana `[window_start_utc, window_end_utc)`.
Para estado pre-decision, `window_end_utc <= decision_timestamp_utc`, salvo
role explicito de event anchor con leakage gate.
```

| observable_name | source_inputs | formula | unit | window / baseline | cutoff_rule | missingness / quality | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `microstructure__quote_zero_pct` | bid/ask price/size columns | `count(value <= 0) / rows * 100` for each declared field | pct_points | declared quote window | quote rows inside window only | NaN if no rows; quote source present flag required | `formula_defined_existing_schema` |
| `microstructure__two_sided_rows` | `ask_price`, `bid_price` | `count(ask > 0 and bid > 0)` | count | quote window | quotes inside window only | zero if no valid rows | `formula_defined_existing_schema` |
| `microstructure__crossed_rows` | `ask_price`, `bid_price` | `count(ask > 0 and bid > 0 and ask < bid)` | count | quote window | quotes inside window only | zero if no valid rows | `formula_defined_existing_schema` |
| `microstructure__locked_rows` | `ask_price`, `bid_price` | `count(ask > 0 and bid > 0 and ask == bid)` | count | quote window | quotes inside window only | zero if no valid rows | `formula_defined_existing_schema` |
| `microstructure__crossed_ratio_pct_all_rows` | crossed rows, rows | `crossed_rows / rows * 100` | pct_points | quote window | quotes inside window only | NaN if denominator zero | `formula_defined_existing_schema` |
| `microstructure__crossed_ratio_pct_two_sided` | crossed rows, two-sided rows | `crossed_rows / two_sided_rows * 100` | pct_points | quote window | quotes inside window only | NaN if denominator zero | `formula_defined_existing_schema` |
| `microstructure__locked_ratio_pct_two_sided` | locked rows, two-sided rows | `locked_rows / two_sided_rows * 100` | pct_points | quote window | quotes inside window only | NaN if denominator zero | `formula_defined_existing_schema` |
| `microstructure__spread_bps` | ask, bid | `((ask - bid) / ((ask + bid) / 2)) * 10000` where ask > bid and mid > 0 | bps | quote row | quote timestamp inside window | NaN if invalid spread | internal row formula |
| `microstructure__quotes_spread_bps_median` | row spread_bps | `median(spread_bps)` | bps | quote window | quotes inside window only | NaN if no valid spread | `formula_defined_existing_schema` |
| `microstructure__quotes_spread_bps_p90` | row spread_bps | `quantile(spread_bps, 0.9)` | bps | quote window | quotes inside window only | NaN if no valid spread | `formula_defined_existing_schema` |
| `microstructure__top_depth_mean` | ask_size, bid_size | `mean(ask_size + bid_size)` over two-sided rows | shares/contracts as source | quote window | quotes inside window only | NaN if no two-sided rows | `formula_defined_existing_schema` |
| `microstructure__trades_odd_lot_ratio_pct` | trade size | `count(0 < size < 100) / rows * 100` | pct_points | trade window | trades inside window only | NaN if no rows | `formula_defined_existing_schema` |
| `microstructure__trades_duplicate_exact_ratio_pct` | timestamp, price, size, exchange, conditions | `count(duplicated exact key keep=false) / rows * 100` | pct_points | trade window | trades inside window only | NaN if no rows | `formula_defined_existing_schema` |
| `microstructure__trades_off_regular_session_ratio_pct` | trade timestamp NY clock | `count(not 09:30 <= local_time < 16:00) / rows * 100` | pct_points | trade window | trades inside window only | NaN if no rows | `formula_defined_existing_schema` |
| `microstructure__trades_total_volume` | trade size | `sum(size where size > 0)` | shares | trade window | trades inside window only | NaN if no rows | `formula_defined_existing_schema` |
| `microstructure__trades_dollar_volume` | price, size | `sum(price * size where price > 0 and size > 0)` | USD proxy | trade window | trades inside window only | NaN if no rows | `formula_defined_existing_schema` |
| `microstructure__trades_size_median` | trade size | `median(size where size > 0)` | shares | trade window | trades inside window only | NaN if no valid size | `formula_defined_existing_schema` |
| `microstructure__trades_size_p90` | trade size | `quantile(size where size > 0, 0.9)` | shares | trade window | trades inside window only | NaN if no valid size | `formula_defined_existing_schema` |

## 3.1 Microstructure Adjustable Families

| candidate_family | formula pattern | required variant fields | status |
| --- | --- | --- | --- |
| `microstructure__spread_stat_WINDOW_STAT_candidate` | aggregate row `spread_bps` over declared window | window length, statistic, min_rows, source root state | `formula_family_defined_requires_variant` |
| `microstructure__quote_staleness_WINDOW_candidate` | time since last quote or max quote gap in window | window, staleness definition, timezone | `formula_family_defined_requires_variant` |
| `microstructure__trade_intensity_WINDOW_candidate` | `trades_window_rows / window_seconds` | window, session filter, min_rows | `formula_family_defined_requires_variant` |
| `microstructure__price_impact_proxy_WINDOW_candidate` | declared price move divided by declared liquidity/volume proxy | price ref, liquidity ref, window, sign policy | `formula_family_defined_requires_variant` |
| `microstructure__liquidity_texture_WINDOW_candidate` | composition of spread/depth/trade/quote metrics | component formula ids and weights | `formula_family_defined_requires_variant` |

`microstructure__price_impact_proxy` is not an execution truth and cannot use
real fills or future prints.
# 4. Contexto As-Of Formulas

Regla general:

```text
Contexto as-of puede ser literal o derivado, pero cada componente conserva su
propio lag, source scope y availability semantics.
```

## 4.1 Fundamentals

Fuente:

```text
source_component = fundamentals_asof_table_v0_1
```

| observable_name | source_inputs | formula | unit | window / baseline | cutoff_rule | missingness / quality | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `fundamentals__filing_age_days` | `filing_date` or governed `as_of_date`, decision date | `decision_date - availability_date` | days | point-in-time | availability date must be `<= decision_date` | null if availability missing | `formula_defined_for_state_builder_candidate` |
| `fundamentals__statement_recency_days` | governed statement availability, decision date | `decision_date - statement_available_date` | days | point-in-time | no use of `period_end` as availability | null if availability missing | `formula_defined_for_state_builder_candidate` |
| fundamentals ratios | financial statement fields | no v0.1 official formula family except explicit future candidates | varies | varies | filing/as_of cutoff required | fundamentals quality gates | `formula_family_defined_requires_variant` |

## 4.2 News

Fuente:

```text
source_component = news_context_table_v0_1
```

| observable_name | source_inputs | formula | unit | window / baseline | cutoff_rule | missingness / quality | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `news__article_count_WINDOW_candidate` | `published_utc`, ticker attribution | `count(articles where t-W <= published_utc <= t)` | count | declared window W | `published_utc <= decision_timestamp_utc` | ticker attribution and news quality required | `formula_family_defined_requires_variant` |
| `news__freshness_minutes_candidate` | latest `published_utc`, decision timestamp | `(decision_timestamp_utc - max(published_utc)) in minutes` | minutes | declared source/filter scope | latest article must be `<= t` | null if no article in scope | `formula_family_defined_requires_variant` |
| `news__keyword_flag_candidate` | keywords/title/description | declared boolean/string match policy | boolean/count | declared dictionary and window | only text known by `published_utc <= t` | no causal proof by itself | `formula_family_defined_requires_variant` |

News formulas do not prove causality. They only represent information available
as-of.

## 4.3 Short Context

Fuente:

```text
source_component = short_context_table_v0_1
builder = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_short_context_table.py
```

| observable_name | source_inputs | formula | unit | window / baseline | cutoff_rule | missingness / quality | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `short_context__days_to_cover` | source `days_to_cover` | accepted as source field; recomputation formula if needed is `short_interest / avg_daily_volume` | days | source observation scope | source availability lag/as_of required | null if source missing; not borrow truth | `formula_deferred_to_source_contract` |
| `short_context__short_volume_ratio` | source `short_volume_ratio`, or `short_volume`, `total_volume` | source field accepted; recomputation formula if needed is `short_volume / total_volume * 100` | pct_points | source observation scope | source availability lag/as_of required | null if denominator missing/zero; not SSR/borrow truth | `formula_deferred_to_source_contract` |
| `short_context__short_interest_z_candidate` | days_to_cover/short_interest history | `(value - rolling_mean) / rolling_std` | z-score | declared historical window | only observations available by `t` | needs min_periods and source lag | `formula_family_defined_requires_variant` |

Short context never implies:

```text
borrow availability
locate approval
hard-to-borrow state
SSR active state
execution feasibility
```

## 4.4 Regime

Fuente:

```text
source_component = regime_context_table_v0_1
builder = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_regime_context_table.py
```

| observable_name | source_inputs | formula | unit | window / baseline | cutoff_rule | missingness / quality | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `regime__intraday_return` | `close_price`, `open_price` | `(close_price / open_price) - 1` when `open_price > 0` | ratio | session aggregate | current same-session only after regime as_of availability | null if invalid denominator | `formula_defined_existing_schema` |
| `regime__close_to_previous_close_return` | `close_price`, `previous_close_price` | `(close_price / previous_close_price) - 1` when previous close > 0 | ratio | session aggregate | same-session only after as_of availability | null if invalid denominator | `formula_defined_existing_schema` |
| `regime__high_to_open_return` | `high_price`, `open_price` | `(high_price / open_price) - 1` when open > 0 | ratio | session aggregate | same-session only after as_of availability | null if invalid denominator | `formula_defined_existing_schema` |
| `regime__low_to_open_return` | `low_price`, `open_price` | `(low_price / open_price) - 1` when open > 0 | ratio | session aggregate | same-session only after as_of availability | null if invalid denominator | `formula_defined_existing_schema` |
| `regime__intraday_range_pct` | `high_price`, `low_price`, `open_price` | `(high_price - low_price) / open_price` when open > 0 | ratio despite `_pct` suffix | session aggregate | same-session only after as_of availability | null if invalid denominator | `formula_defined_existing_schema` |
| `regime__bar_coverage_state` | `bars_observed` | bucket: `>=360 regular_session_like_or_better`, `>=60 partial_session_like`, else `sparse` | enum | session aggregate | only observed bars/as_of | regime quality required | `formula_defined_existing_schema` |

Intraday regime state before session close requires a separate intraday regime
formula variant; session-close aggregate cannot be used as if known earlier.

## 4.5 Halts

Fuente:

```text
source_component = halts_table_v0_1
```

| observable_name | source_inputs | formula | unit | window / baseline | cutoff_rule | missingness / quality | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `halt__is_halted_at_t_candidate` | halt start/resume timestamps, decision timestamp | `halt_start <= t and (resume is null or resume > t)` | boolean | point-in-time | halt timestamps must be known by decision timestamp | requires decision-time availability contract | `formula_defined_for_state_builder_candidate` |
| `halt__minutes_since_halt_start_candidate` | halt start, decision timestamp | `(t - halt_start)` in minutes | minutes | point-in-time | halt_start known by t | null if not halted/unknown | `formula_defined_for_state_builder_candidate` |
| `halt__minutes_since_resume_candidate` | resume timestamp, decision timestamp | `(t - resume)` in minutes | minutes | point-in-time | resume known by t | null if not resumed/unknown | `formula_defined_for_state_builder_candidate` |

Halts are event context, not alpha by themselves. A halt/resume timestamp learned
after the decision cannot be used as pre-decision state.

# 5. Short Constraints, Float Y Live Alerts

| area | formula rule | status |
| --- | --- | --- |
| `short_constraints__ssr_state` | formula blocked until SSR source/as_of model exists | `blocked_requires_source` |
| `short_constraints__borrow_state` | formula blocked until broker/vendor borrow availability source exists | `blocked_requires_source` |
| `short_constraints__locate_state` | formula blocked until locate approval/source and account scope exist | `blocked_requires_source` |
| `float__point_in_time_share_state` | no formula until point-in-time float/shares table exists | `blocked_requires_source` |
| `corporate_alert__live_event_state` | no formula until live feed, `received_utc` and latency semantics exist | `blocked_requires_source` |

# 6. Quality, Coverage Y Lineage Formulas

Quality and lineage are not alpha, but they are required to make state legal.

| observable_name | formula | status |
| --- | --- | --- |
| `quality__presence_state` | declared present/missing flags from component source and expected calendar | `formula_deferred_to_source_contract` |
| `quality__coverage_ratio_candidate` | `observed_count / expected_count` with declared denominator | `formula_family_defined_requires_variant` |
| `quality__missing_count_candidate` | `expected_count - observed_count` with floor at 0 | `formula_family_defined_requires_variant` |
| `lineage__source_hash_state` | source hash copied from manifest/source file metadata | `formula_deferred_to_source_contract` |
| `lineage__build_policy_state` | build/schema/policy ids copied from source manifests | `formula_deferred_to_source_contract` |

# 7. AlphaEvolve / ML / Strategy Statistics Protocol

AlphaEvolve, ML, RL or strategy statistics may propose new formulas, windows or
representations, but they cannot mutate base state silently.

Allowed discovery objects:

```text
lookback length
window length
baseline definition
aggregation statistic
normalization
threshold
semantic representation
transition detector
policy over state
```

Required path:

```text
1. propose candidate formula/variant
2. assign versioned observable name
3. declare inputs, formula, unit, window, baseline and cutoff
4. run reproducible replay/evaluator
5. compare against locked baseline
6. record promotion/rejection decision
7. only then allow state builder consumption
```

Example:

```text
existing:  daily__rvol_20d
candidate: daily__rvol_14d_candidate_v0_1
candidate: daily__rvol_60d_candidate_v0_1
```

If a candidate wins, it is not renamed over the old observable. It becomes a
new governed observable or a new version.

# 8. Prohibited Formulas

| formula/concept | reason | status |
| --- | --- | --- |
| `winner/loser` | outcome future | `prohibited_as_state_formula` |
| `reward` | RL target, not state | `prohibited_as_state_formula` |
| `PnL`, real fill result | execution/outcome posterior | `prohibited_as_state_formula` |
| `best_threshold_found` | optimizer result | `prohibited_as_state_formula` |
| `selected_by_scanner` as causal feature | selection/decision, not neutral observable | `prohibited_as_state_formula` |
| `first_cross_50_ts_utc` as base state | fixed scanner threshold; can be event/scanner output, not neutral state | `prohibited_as_state_formula` |
| `attention/crowding/fragility` without formula/version | semantic representation not contracted | `prohibited_as_state_formula` |

# 9. Acceptance Criteria v0.1

| criterio | estado |
| --- | --- |
| Daily existing derived formulas traced to current builder | `done` |
| Daily adjustable lookback families defined as versioned candidates | `done` |
| Intradia 1m state-builder candidate formulas defined without scanner thresholds | `done` |
| Intradia shape/pace families defined as variant-required candidates | `done` |
| Microstructure existing window aggregate formulas traced to current builder | `done` |
| Microstructure adjustable families defined as variant-required candidates | `done` |
| Contexto as-of formulas/lags separated by component | `done` |
| Short constraints/float/live alerts left blocked until source exists | `done` |
| Quality/coverage/lineage separated from alpha | `done` |
| AlphaEvolve/ML/statistics protocol for formula variants defined | `done` |
| Prohibited formulas documented | `done` |

Estado final:

```text
state_derived_observables_formula_contract_v0_1 = complete_for_contract_defined_scope
```

Lo que queda fuera de este contrato:

```text
1. implementar state builder que consuma eligibility + formula contracts
2. materializar fixtures controlados de market_state/event_state
3. crear validators de leakage/formula parity
4. crear outcomes separados
5. crear evaluadores bloqueados para AlphaEvolve/ML/RL
6. promover o rechazar variantes descubiertas en evaluadores posteriores
```