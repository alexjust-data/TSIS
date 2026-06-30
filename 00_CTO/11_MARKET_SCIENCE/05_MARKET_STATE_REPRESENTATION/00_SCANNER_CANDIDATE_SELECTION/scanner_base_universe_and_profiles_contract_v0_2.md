# Scanner Base Universe And Profiles Contract v0.2

Fecha: 2026-06-30
Estado: candidate_policy
Owner layer: `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION`
Supersedes conceptually: two-independent-scanner reading from v0.1

## 1. Decision

TSIS debe usar un unico scanner base de candidatos y multiples perfiles de
ranking, inspeccion o research.

La lectura anterior separaba:

```text
trade_station_like_scanner_v0_1
broad_in_play_discovery_scanner_v0_1
```

Esa separacion sirvio para probar forma, lineage y replay controlado, pero
puede inducir una confusion peligrosa:

```text
dos scanners != dos universos cientificos distintos
```

La decision v0.2 es:

```text
base_in_play_universe
-> profiles / views / rankings
-> candidate state research
-> event_state / market_state
```

El scanner base define la poblacion observable minima.

Los perfiles responden preguntas operativas o cientificas sobre esa misma
poblacion.

## 2. Scanner base

El scanner base no es una senal.

El scanner base no es DAS.

El scanner base no es `market_state`.

El scanner base responde:

```text
Que instrumentos pertenecen a la poblacion smallcap/microcap observable que TSIS
debe considerar para candidate selection en una fecha/as-of?
```

Hard filters v0.2:

```yaml
common_stock: true
market_cap_usd_lt: 100000000
last_price_gt: 0.5
last_price_lte: 20
data_quality_allowed:
  - usable
  - review
```

Reglas:

- `market_cap_usd < 100M` es parte de la identidad economica del nicho que se
  quiere estudiar.
- `0.5 < last_price <= 20` separa el universo operacional smallcap de penny
  basura extrema y de large/medium caps fuera del playbook.
- `common_stock = true` evita mezclar warrants, units, preferreds, ETFs u otros
  instrumentos con mecanica distinta.
- `data_quality in usable/review` permite research con flags, pero conserva la
  obligacion de no presentar casos `review` como equivalentes a `good`.

No hard filter universal v0.2:

```text
volume_today >= 500000
pct_chg_1d top 25
relative_volume threshold
float threshold
news present
afterhours breakout present
premarket new high present
```

Esas variables pueden ser perfiles, rankings, razones, features o hipotesis.
No deben ser la puerta unica de entrada al denominador base.

## 3. Perfiles derivados

Un perfil es una vista reproducible sobre el scanner base.

Un perfil puede seleccionar, ordenar o etiquetar filas, pero no redefine la
poblacion base.

### 3.1 TradeStation-like profile

Pregunta:

```text
Que habria visto el operador en una hot list operativa similar a la que usa cada
dia?
```

Definicion conceptual:

```yaml
profile_id: trade_station_like_profile_v0_2
base_universe: base_in_play_universe_v0_2
filters:
  volume_today_gte: 500000
ranking:
  primary: pct_chg_1d_desc
selection:
  top_n: 25
display_fields:
  - pct_chg_1d
  - volume_today
  - relative_volume
  - market_cap_usd
  - float_shares_if_point_in_time_available
```

Uso:

- reconstruir visibilidad operativa humana;
- comparar research contra lo que el operador podia ver;
- medir llegada tardia de un filtro estrecho;
- preservar un baseline operacional conocido.

Limitacion:

```text
Puede llegar tarde para eventos frontside/DAS que nacen antes de 500k shares o
antes de entrar en top 25 por pct_chg_1d.
```

### 3.2 Relative-volume profile

Pregunta:

```text
Que instrumentos muestran expansion de actividad relativa dentro del universo
base?
```

Variables candidatas:

```text
rvol_to_time
volume_acceleration
volume_last_5m
volume_last_15m
volume_since_04_00
dollar_volume_to_time
volume_tier
```

Uso:

- estudiar timing de entrada al radar;
- medir si volumen alto es causa, consecuencia o solo proxy de atencion;
- encontrar candidatos tempranos sin convertir volumen en hard filter.

### 3.3 Percent-change profile

Pregunta:

```text
Que instrumentos son visibles por movimiento porcentual contra referencia
diaria?
```

Variables candidatas:

```text
pct_chg_1d
open_gap_pct
premarket_gap_pct
afterhours_gap_pct
range_expansion_pct
```

Uso:

- estudiar atencion/momentum visible;
- replicar rankings de hot lists;
- medir si el ranking por porcentaje llega tarde para after-hours y premarket.

### 3.4 Dollar-volume and tradability profile

Pregunta:

```text
Que instrumentos tienen actividad suficiente para estudiar ejecucion y
contrapartida?
```

Variables candidatas:

```text
dollar_volume_today
dollar_volume_to_time
spread_proxy
liquidity_tier
tradability_tier
```

Uso:

- separar interes estadistico de viabilidad operacional;
- no confundir alpha con ejecutabilidad;
- alimentar risk/execution gates posteriores.

### 3.5 DAS research profile

Pregunta:

```text
Dentro del universo base, que candidatos merecen reconstruccion DAS/frontside
experimental?
```

Regla:

```text
das_research_profile no detecta DAS y no etiqueta trade bueno.
```

Solo crea un denominador para estudiar:

```text
frontside_absent
frontside_dirty
frontside_sane
frontside_too_late_for_operator
frontside_afterhours_only
frontside_premarket_extension
frontside_failed_before_trigger
```

La estrategia DAS vive en strategy research. El scanner solo entrega el
conjunto donde mirar.

## 4. Float y market cap

TSIS quiere estudiar low float, pero no debe inventar point-in-time float.

Regla:

```text
float puede ser display field, feature o perfil solo si declara source,
publication timing, as-of legality y missingness.
```

Hasta auditar cobertura point-in-time:

```yaml
float_filter_status: blocked_as_hard_filter
float_display_status: allowed_with_availability_flag
float_research_status: allowed_as_provisional_feature
```

Market cap si puede ser hard filter porque ya forma parte de la definicion del
nicho `market_cap_usd < 100M`, siempre que la fuente as-of este gobernada.

## 5. Por que no aprender solo de buenos candidatos

TSIS no debe construir el dataset de DAS, ML o RL solo con winners.

Debe conservar tambien:

- candidatos que no hicieron frontside sano;
- candidatos que subieron pero eran inejecutables;
- candidatos que aparecieron tarde;
- candidatos con volumen bajo que si funcionaron;
- candidatos con volumen alto que fallaron;
- candidatos con gap diario que se destruyeron en regular hours;
- candidatos que tenian catalyst pero mala microestructura;
- candidatos sin catalyst que igual hicieron squeeze.

Motivo:

```text
Sin negativos y casos ambiguos, TSIS no aprende estado; aprende sesgo de
seleccion.
```

## 6. Relacion con state tables

El scanner base y sus perfiles producen denominadores y lineage.

No producen estados entrenables.

Flujo correcto:

```text
base_in_play_universe
-> profile flags/ranks/reasons
-> daily_scanner_candidates_table
-> strategy-specific candidate_state_table_experimental
-> event_state_candidate
-> market_state_candidate
-> institutional_market_state
```

Una fila de scanner puede ser parte del lineage de un estado, pero no puede
contener:

```text
outcome
PnL
fill
reward
action
future label
strategy decision
```

## 7. Evidencia cientifica directa

Formato:

```text
Decision TSIS -> Evidencia directa -> Obligacion tecnica -> Limitacion abierta
```

| Decision TSIS | Evidencia directa | Obligacion tecnica | Limitacion abierta |
| --- | --- | --- | --- |
| Usar scanner base + perfiles, no dos universos independientes. | Offline RL formaliza aprendizaje sobre estados/transiciones historicas y advierte que la cobertura del dataset condiciona la politica aprendida. Ver Levine et al. (2020). | Preservar un denominador base amplio y separar perfiles/rankings de estados entrenables. | El replay full historical del scanner base aun debe materializarse y validarse. |
| No usar `volume_today >= 500k` como hard filter universal. | TSIS Market Science define que en microcaps el mercado evoluciona en event time; volumen puede ser consecuencia de attention/order-flow, no causa estable. Causal ML y Causal Factor Investing advierten contra confundir proxy y mecanismo. | Guardar volumen como feature, tier, ranking y razon; medir empiricamente si llega tarde o filtra casos sanos. | Se requiere estudio DAS/frontside con negativos, winners y timing as-of. |
| No usar `% change 1D` como unica puerta de entrada. | DeepLOB y literatura LOB modelan el mercado como estructura espacio-temporal; una variable diaria no representa el estado microestructural. | `% change 1D` debe ser perfil/ranking, no definicion total del universo investigable. | Necesitamos perfiles after-hours, premarket y event-time mas ricos. |
| Separar scanner de `market_state` y `event_state`. | RL y decision models operan sobre estados; `daily_scanner_candidates_table` solo responde donde mirar. Ver Levine et al. (2020) y contrato Market State v0.1. | Validators deben impedir que scanner rows sean consumidos como estado ML/RL final. | Falta builder real de `market_state`/`event_state`. |
| Mantener negativos, ambiguos y casos tardios. | Causalidad y factor investing advierten sobre factor mirage, confounders y seleccion retrospectiva. Behavioral cloning/RL desde demostraciones puede aprovechar expertos, pero no elimina necesidad de cobertura y negativos. Ver CFA (2025) y Hester et al. (2017). | El scanner debe crear denominador; las tablas DAS deben registrar no-frontside, dirty-frontside y failures, no solo buenas entradas. | Falta diseno final de labels/outcomes por estrategia. |
| Medir microestructura despues del scanner, no meterla como requisito universal inicial. | Kyle (1985) conecta order flow, liquidez y price impact; Easley, Lopez de Prado y O'Hara conectan toxicidad/order-flow con riesgo para liquidity providers. | Microestructura debe entrar como estado/event window y execution/risk feature, no como filtro casual sin ventana. | Las ventanas microestructurales gobernadas aun no estan completas. |
| Tratar float como as-of-sensitive. | `RESEARCH_PHILOSOPHY.md` prohibe lookahead y exige mecanismos, no proxies fragiles; fundamentals point-in-time pueden llegar con delay y cobertura incompleta. | No usar float como hard filter hasta auditar source, publication timing y cobertura point-in-time. | Pendiente auditoria de float historical/as-of para todos los tickers. |

## 8. Referencias cientificas

- Levine, Kumar, Tucker, Fu (2020), "Offline Reinforcement Learning: Tutorial,
  Review, and Perspectives on Open Problems":
  https://arxiv.org/abs/2005.01643
- Hester et al. (2017), "Deep Q-learning from Demonstrations":
  https://arxiv.org/abs/1704.03732
- Scholkopf (2019/2022), "Causality for Machine Learning":
  https://arxiv.org/abs/1911.10500
- Lopez de Prado and Zoonekynd (2025), "Causality and Factor Investing: A
  Primer", CFA Institute Research Foundation:
  https://rpc.cfainstitute.org/research/foundation/2025/causality-factor-investing
- Zhang, Zohren, Roberts (2018/2020), "DeepLOB: Deep Convolutional Neural
  Networks for Limit Order Books":
  https://arxiv.org/abs/1808.03668
- Kyle (1985), "Continuous Auctions and Insider Trading", Econometrica:
  https://doi.org/10.2307/1913210
- Easley, Lopez de Prado, O'Hara (2012), "Flow Toxicity and Volatility in a
  High Frequency World", Review of Financial Studies:
  https://doi.org/10.1093/rfs/hhs053
- Lopez de Prado (2018), "Advances in Financial Machine Learning", Wiley.

## 9. Cambios operativos que deben seguir despues

Este documento no cambia todavia builders, schemas ni configs operativas.

Para que v0.2 gobierne `01_foundations`, hace falta un cambio separado:

1. Crear `base_in_play_universe_scanner_v0_2.yaml`.
2. Convertir `trade_station_like_scanner_v0_1` en
   `trade_station_like_profile_v0_2`.
3. Reemplazar `broad_in_play_discovery_scanner_v0_1` por perfiles explicitos
   de ranking/reason, no por un segundo universo.
4. Versionar schema si cambian columnas.
5. Actualizar dataset contract, consumption policy, registry, validators,
   builder, tests y notebook.
6. Conservar replay v0.1 como evidencia historica, no como arquitectura final.

## 10. Regla corta para agentes

```text
Un scanner base define a quien mirar.
Un perfil define como ordenar o inspeccionar.
Un estado define que sabia TSIS.
Una estrategia define que hacer.
Un outcome/reward se mide despues.
```

Si un agente mezcla estas cinco cosas, no debe modificar esta capa.
