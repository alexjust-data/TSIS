# Scanner Base And In-Play Momentum Contract v0.3

Fecha: 2026-06-30
Estado: `candidate_policy_promoted_to_foundation_contract_candidate`
Owner layer: `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION`
Supersedes conceptually: `scanner_base_universe_and_profiles_contract_v0_2.md`

## Decision

TSIS separa dos denominadores distintos:

```text
base_eligible_smallcap_denominator
  = a quien podemos mirar

in_play_momentum_candidate_denominator
  = que tickers merecen estudio/event/strategy ese dia
```

`base_eligible_smallcap_denominator` no significa que el ticker este in-play.
Solo significa que pertenece al universo observable micro/smallcap:

```text
common_stock = true
market_cap_usd < 100000000
0.5 < last_price <= 20
data_quality in usable/review
```

`in_play_momentum_candidate_denominator` exige:

```text
base_eligible_smallcap_denominator
+ movimiento fuerte
+ volumen/tradability minimo
```

## Movimiento Fuerte

Umbral inicial:

```text
minimum_push_move_pct = 50%
```

Para replay diario/EOD controlado, el proxy permitido es:

```text
daily_high_vs_prev_close_pct >= 50
OR pct_chg_1d >= 50
OR gap_pct >= 50
```

La metrica preferida es:

```text
daily_high_vs_prev_close_pct
```

porque `pct_chg_1d` de cierre puede perder pumps que subieron violentamente y
se destruyeron antes del close.

## Segmentos Intradia

La interpretacion cientifica completa requiere segmentar extended hours:

```text
premarket: 04:00-09:30 New York
regular:   09:30-16:00 New York
afterhours:16:00-20:00 New York
extended:  04:00-20:00 New York
```

Metricas requeridas para promocion intradia:

```text
move_vs_previous_close_pct
move_vs_segment_open_pct
first_cross_50_ts
first_push_segment
max_move_segment
```

Builder intradia/as-of inicial:

```text
intraday_scanner_candidates_table_v0_1
builder = scripts/materialize_intraday_scanner_candidates_table_v0_1.py
status = controlled_replay_candidate_not_official_e_root
```

Regla: cuando el timing del primer push importa, el daily/EOD proxy v0.3 no es
autoridad suficiente. Debe usarse el scanner intradia v0.1 o una version
posterior.

## Volumen y Tradability

El in-play momentum necesita actividad minima. Config inicial:

```text
volume_today >= 500000
OR dollar_volume_today >= 250000
```

Esta regla no prueba alpha. Solo evita convertir acciones sin contrapartida en
denominador principal de eventos/estrategias.

## Float

Float es informacion contextual importante, pero no filtro global.

Regla:

```text
float puede ser columna informativa cuando exista fuente point-in-time validada.
float no puede ser hard filter global sin contrato de fuente, as-of y cobertura.
float como filtro pertenece a overlays de estrategia.
```

Columnas esperadas:

```text
float_shares
float_asof_date
float_source
float_filter_state
```

### Pendiente: `float_context_table`

TSIS no tiene todavia float institucional point-in-time. Las columnas de float
en el scanner quedan reservadas y deben permanecer vacias o marcadas como no
usables hasta que exista una tabla gobernada de contexto de estructura de
acciones.

Tabla pendiente:

```text
float_context_table
```

Campos minimos requeridos:

```text
ticker
instrument_id
as_of_date
float_shares
shares_outstanding
free_float_pct
source
source_document
source_field
point_in_time_valid
quality_state
is_estimated
```

Regla:

```text
shares_outstanding no equivale a float.
overview_weighted_shares_outstanding no debe poblar float_shares.
float no puede filtrar el scanner ni overlays hasta que float_context_table
tenga source/as-of/cobertura auditados.
```

## Estrategias

El scanner global no contiene DAS ni ningun setup especifico.

Flujo correcto:

```text
base_eligible_smallcap_denominator
-> in_play_momentum_candidate_denominator
-> strategy_overlay
-> strategy_candidate_state_table_experimental
-> event_state / market_state
```

DAS, shorts, breakouts, backside y futuras estrategias consumen el
denominador in-play y aplican filtros propios despues.

## Evidencia Directa

| Decision TSIS | Evidencia directa | Obligacion tecnica | Limitacion abierta |
| --- | --- | --- | --- |
| Separar base elegible de in-play real. | Offline RL depende de soporte/cobertura del dataset y no debe aprender solo de muestras elegidas retrospectivamente. Ver Levine et al. (2020). | Preservar base elegible y marcar in-play como seleccion posterior. | Falta materializacion 20y con builder monitorizado. |
| Usar movimiento >=50% como criterio inicial de in-play momentum. | La tesis TSIS es que la volatilidad extrema es el edge operativo en microcaps; `pct_chg_1d` de cierre puede perder pumps intradia. | Usar high/gap/close en replay diario y segmentos 04:00-20:00 en builder intradia. | El umbral 50% es policy inicial; debe ser falsable por estudios posteriores. |
| Exigir volumen/tradability minimo. | La ejecucion realista exige contrapartida, spread y liquidez; una senal sin ejecutabilidad no vale. Ver `RESEARCH_PHILOSOPHY.md` y literatura de microestructura. | Guardar gate de volumen/tradability como requisito de denominador in-play. | El umbral puede requerir versionado tras estudio de capacidad/slippage. |
| Mantener float como contexto, no filtro global. | Fundamentals/float historico puede introducir lookahead si no es point-in-time. | No filtrar globalmente por float hasta validar source/as-of. | Pendiente fuente point-in-time de float. |
| Sacar DAS del scanner global. | Evento, estado y estrategia son capas distintas en TSIS. | DAS debe vivir en overlay de estrategia, no en Data Foundation scanner. | Falta overlay DAS institucional. |

## Referencias

- Levine et al. (2020), "Offline Reinforcement Learning: Tutorial, Review, and
  Perspectives on Open Problems": https://arxiv.org/abs/2005.01643
- Scholkopf et al. (2019), "Causality for Machine Learning":
  https://arxiv.org/abs/1911.10500
- Zhang, Zohren, Roberts (2018), "DeepLOB: Deep Convolutional Neural Networks
  for Limit Order Books": https://arxiv.org/abs/1808.03668
- Kyle (1985), "Continuous Auctions and Insider Trading":
  https://doi.org/10.2307/1913210
- Easley, Lopez de Prado, O'Hara (2012), "Flow Toxicity and Volatility in a
  High Frequency World": https://doi.org/10.1093/rfs/hhs053

## Regla Final

```text
base eligible no es in-play.
in-play no es estrategia.
estrategia no es estado.
estado no es outcome.
```
