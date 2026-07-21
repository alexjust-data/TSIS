# Derivable Capability Status Matrix v0.1

Status: `compact_capability_status_matrix_v0_2_atomic_register`
Date: `2026-07-20`
Knowledge state: `secondary_summary`

## Rol

Vista rapida del estado operativo de las capacidades derivables atomicas definidas en:

```text
01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

No sustituye el register ni los contratos operativos.

## Regla De Lectura

```text
Una fila del register = una capacidad derivable canonica.
```

Esta matriz puede agrupar por fuente para lectura rapida, pero el gobierno operativo vive en las filas atomicas del register.

## Vocabulario

```text
existing
formula_defined
requires_variant
candidate
blocked_no_source
prohibited_as_feature
```

## Conteo Por Estado

| status | capability rows | lectura operativa |
|---|---:|---|
| `existing` | 63 | existe como observable/campo/materializacion conocida o candidata documentada |
| `formula_defined` | 21 | formula definida, pero puede requerir builder/materializacion posterior |
| `requires_variant` | 27 | capacidad canonica valida, pero exige declarar parametros como W, N, baseline, FIELD o FORMULA |
| `candidate` | 9 | posible, pero falta contrato/formula/alineacion/evidencia antes de consumo |
| `blocked_no_source` | 4 | no hay fuente legal/as-of suficiente hoy |
| `prohibited_as_feature` | 7 | no puede entrar como feature observable de estado |

## Conteo Por Bloque De Fuente

| source block | canonical capabilities | dominant status | usable for semantic review? | main blocker / condition |
|---|---:|---|---|---|
| OHLCV Daily | 20 | `existing` / `requires_variant` | yes | N/min_periods/statistic variants for non-fixed lookbacks |
| OHLCV 1m | 27 | `existing` / `formula_defined` / `requires_variant` | yes, scoped | closed-bar policy, quote-guarded scope, missing-bar policy |
| Trades | 16 | `existing` / `requires_variant` / `candidate` | yes, with caveats | condition decoding, window policy, trade quality |
| Quotes L1 | 18 | `existing` / `requires_variant` / `formula_defined` | yes, with L1 limits | quote quality, staleness, timestamp/sequence behavior |
| Trades + Quotes | 6 | `candidate` | partial | alignment policy, lag sensitivity, classification confidence |
| News | 7 | `existing` / `requires_variant` | yes, if PIT/as-of legal | attribution, source/filter scope, dictionary/model version |
| Fundamentals / SEC | 4 | `existing` / `formula_defined` / `requires_variant` | partial | financial source quality, PIT/as-of semantics |
| Short | 6 | `existing` / `requires_variant` / `blocked_no_source` | partial | source lag, borrow/locate/SSR missing |
| Halts | 4 | `existing` / `formula_defined` | yes | timestamp availability and resume knowledge by t |
| Reference / corporate actions | 5 | `existing` / `formula_defined` / `blocked_no_source` | partial | PIT float unavailable |
| Regime/context | 6 | `existing` | partial | daily regime data defect; scoped/pilot boundaries |
| Quality / lineage | 5 | `existing` / `formula_defined` / `requires_variant` | yes as support, not alpha | expected denominator and manifest consistency |
| Future / decision / execution | 7 | `prohibited_as_feature` | no | leakage, outcomes, actions, optimization result |

## Capacidades Que Requieren Variante

Estas filas son atomicas, pero todavia no son variables fisicas cerradas hasta declarar sus parametros.

| capability pattern | required variant fields |
|---|---|
| `daily__volume_Nd_avg` | N, min_periods, valid-row policy, price_view |
| `daily__rvol_Nd` | N, min_periods, denominator policy |
| `daily__dollar_volume_Nd_avg` | N, min_periods, dollar_volume formula id |
| `daily__volatility_Nd` | N, return input, statistic, min_periods |
| `daily__range_Nd` | N, range input, statistic, min_periods |
| `intraday__return_vs_prior_close_ratio` | price_ref |
| `intraday__return_vs_session_open_ratio` | price_ref |
| `intraday__return_vs_segment_open_ratio` | price_ref, segment policy |
| `intraday__vwap_distance_ratio` | vwap_ref, window, denominator policy |
| `intraday__bars_expected_to_time` | session/segment scope, bar_size |
| `intraday__missing_bar_count_to_time` | session/segment scope |
| `intraday__missing_bar_ratio_to_time` | session/segment scope |
| `intraday__move_speed_W` | W, return_ref, price_ref, session/segment scope |
| `intraday__move_acceleration_W` | W, speed formula id, elapsed policy |
| `intraday__pullback_ratio_W` | W, high_ref, current_price_ref |
| `intraday__retrace_ratio_W` | W, anchor policy, price_ref |
| `intraday__volume_pace_W` | W, baseline universe, historical sessions, min_periods |
| `intraday__dollar_volume_pace_W` | W, baseline formula, historical sessions, min_periods |
| `trades__trade_count_WINDOW` | window, session filter, min_rows |
| `trades__trade_rate_WINDOW` | window, session filter, min_rows |
| `quotes__quote_count_WINDOW` | window, min_rows |
| `quotes__quote_update_rate_WINDOW` | window, min_rows |
| `quotes__staleness_WINDOW` | window, timezone, gap definition |
| `quotes__lifetime_WINDOW` | window, sequence/timestamp policy |
| `news__article_count_WINDOW` | W, source filter, attribution scope |
| `news__freshness_minutes` | source/filter scope |
| `news__keyword_flag` | dictionary version, field scope |
| `news__sentiment_score` | model version, source scope |
| `news__novelty_score` | lookback, text model, source scope |
| `fundamentals__statement_value_FIELD` | FIELD, statement_family, source_dataset_id |
| `fundamentals__ratio_FORMULA` | FORMULA, fields, statement scope, availability policy |
| `short__short_interest_z_WINDOW` | window, min_periods, input metric |
| `reference__instrument_identity_asof` | identity fields, as_of policy |
| `reference__lifecycle_state_asof` | lifecycle fields, as_of policy |
| `reference__corporate_action_count_WINDOW` | action_type, window, availability policy |
| `reference__corporate_action_recency_days` | action_type, availability policy |
| `quality__coverage_ratio` | component, denominator, window |
| `quality__missing_count` | component, denominator, window |
| `lineage__source_hash_state` | source, manifest role |
| `lineage__build_policy_state` | source, manifest role |

## Bloqueadas O Prohibidas

| capability | status | reason |
|---|---|---|
| `short__borrow_availability_state` | `blocked_no_source` | falta fuente borrow gobernada/as-of |
| `short__locate_state` | `blocked_no_source` | falta fuente locate/broker gobernada/as-of |
| `short__ssr_state` | `blocked_no_source` | falta fuente SSR gobernada/as-of |
| `reference__float_pit_state` | `blocked_no_source` | falta fuente PIT float/shares gobernada |
| `future__future_return_H` | `prohibited_as_feature` | outcome futuro |
| `future__mfe_H` | `prohibited_as_feature` | outcome futuro |
| `future__mae_H` | `prohibited_as_feature` | outcome futuro |
| `execution__pnl_reward` | `prohibited_as_feature` | resultado/accion posterior |
| `decision__selected_by_scanner` | `prohibited_as_feature` | decision/seleccion, no observable neutral |
| `decision__best_threshold_found` | `prohibited_as_feature` | resultado de optimizacion |
| `decision__action_taken` | `prohibited_as_feature` | accion/policy, no estado observable |

## Proxima Capa

Las capacidades con estado `existing`, `formula_defined`, `requires_variant` o `candidate` pueden pasar a revision semantica solo si su condicion operativa esta explicitada.

La siguiente capa decide:

```text
information_family
candidate_information_object
representation_model
source_table_mapping
Market State / Event State inclusion
```

