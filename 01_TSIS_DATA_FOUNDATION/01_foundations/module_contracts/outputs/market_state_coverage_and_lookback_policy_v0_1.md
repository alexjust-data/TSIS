# Market State Coverage And Lookback Policy v0.1

## 2026-07-07 Quotes Root Supersession

`D:/quotes -> E:/TSIS/data/quotes_` is closed and approved. The official quotes E-root for new downstream work is `E:/TSIS/data/quotes_`, backed by Phase A structural parity and Phase B SHA256 retry evidence. Historical artifacts built from `D:/quotes` remain pre-approval/provenance evidence and must be rebuilt against the approved E-root before promotion to an official downstream table. The legacy `E:/TSIS/data/quotes` tree remains incomplete for this decision.


## Estado

Tipo: coverage and lookback policy.

Modulo: `01_TSIS_DATA_FOUNDATION`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status:

```text
policy_defined
market_state_table_materialized = false
event_state_table_materialized = false
```

Este contrato fija una decision que no debe quedar solo en conversacion:

```text
No basta construir estados solo para el ticker-dia en play.
No se debe materializar microestructura pesada de forma ciega para todo el
universo-tiempo.
La arquitectura correcta combina contexto full-history compacto, candidatos
diarios/en-evento y microestructura pesada solo en ventanas gobernadas.
```

## Decision Central

TSIS debe separar tres coberturas:

```text
1. full_history_context
2. daily_in_play_candidates
3. event_window_microstructure
```

Regla:

```text
Full history para contexto ligero.
Window/event-driven para microestructura pesada.
Lookback features para memoria estrategica.
```

Esto evita dos errores opuestos:

- construir solo el ticker-dia y perder contexto historico relevante;
- intentar materializar todo tick/quote/trade para todo ticker/minuto/dia como
  si todo fuera estado consumible.

## Problema Que Resuelve

La operativa diaria filtra tickers en play. Un ejemplo operativo compatible con
la logica observada en una Hot List tipo `% Gainers - 1 Day` es:

```text
market_cap < 100M
volume_today > 500000
0.5 < last <= 20
rank by pct_chg_1d desc
top_n = 25
```

Ese scanner es util para descubrir candidatos del dia, pero no puede ser el
unico estado.

Ejemplo:

```text
Strategy = Short Into Resistance
```

Si el estado solo guarda el ticker-dia, puede perder:

- resistencia de 20, 60 o 90 sesiones;
- high anterior relevante;
- distancia al prior high;
- numero de toques previos;
- volumen relativo historico;
- tendencia diaria previa;
- contexto de gaps anteriores;
- splits, ticker changes o discontinuidades que alteran comparabilidad.

Por tanto, el estado de un evento debe traer memoria historica calculada de
forma as-of. No debe depender de que el modelo mire manualmente tres meses de
raw data en cada entrenamiento.

## Coberturas Permitidas

### 1. `full_history_context`

Uso:

```text
contexto compacto, denominadores, filtros, lookbacks, scanner recreation,
quality gates y joins as-of
```

Puede y debe ser amplia cuando la fuente lo permita:

```text
2005-2026
LT1B / universo gobernado
4800 tickers aproximadamente, segun fuente y cobertura
```

Tablas candidatas a cobertura amplia:

- `instrument_master`;
- `market_calendar`;
- `expected_data_calendar`;
- `corporate_actions_table`;
- `dataset_certification_matrix`;
- `master_daily_table`;
- `halts_table`;
- `event_windows_table`;
- `outcomes_table` como labels separados;
- `short_context_table`;
- `regime_context_table`;
- fundamentals/news as-of cuando sus contratos lo permitan.

Estas tablas son relativamente compactas frente a quotes/trades y son
necesarias para que el sistema no pierda contexto.

### 2. `daily_in_play_candidates`

Uso:

```text
reconstruir que tickers estaban en play cada dia bajo una definicion de scanner
```

Contrato objetivo:

```text
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
```

No es source of truth de estado completo.
Es una capa de seleccion/candidato.

Debe preservar:

- `scanner_definition_id`;
- universe filters;
- ranking method;
- `top_n`;
- timestamp o session del scanner;
- input price view;
- source data lineage;
- market cap source/as-of;
- volume and last price source;
- flags de calidad.

Ejemplo conceptual:

```text
small_cap_momentum_universe =
  market_cap < 100M
  volume_today > 500000
  0.5 < last <= 20
  ranked_by pct_chg_1d desc
```

No debe interpretarse como:

```text
todo el universo interesante
```

Solo representa una definicion concreta de in-play.

### 3. `event_window_microstructure`

Uso:

```text
microestructura pesada, quotes/trades/tape/book texture, spread, odd lots,
locked/crossed, liquidity stress, intensity, execution realism
```

No debe construirse como full-universe ciego de cada minuto/ticker.
Debe construirse por ventanas gobernadas:

- scanner candidates;
- event windows;
- strategy candidate events;
- halt windows;
- offering/news/filing windows cuando exista fuente;
- ventanas de pre-evento y respuesta definidas por contrato.

La tabla que materialice esta capa debe declarar:

- `event_window_id` o `state_window_id`;
- `decision_timestamp_utc`;
- ventana de observacion;
- fuente quotes/trades;
- root state de quotes;
- recomputation lineage;
- `full_universe_claim = false` salvo prueba contraria;
- flags de missingness y quality.

## Lookback Obligatorio Para Estados

Todo `market_state_table` o `event_state_table` real debe declarar su
`lookback_policy_id`.

Minimo recomendado para estados de estrategias microcap:

```text
lookback_daily_sessions = [5, 20, 60, 90, 252]
lookback_intraday_windows = [premarket, prior_session, event_pre_window, event_response_window]
price_views = [daily_raw, split_normalized, adjusted where legal]
```

El builder debe dejar claro:

- si el lookback fue calculado;
- si la fuente estaba ausente;
- si fue bloqueado por calidad;
- que price view se uso;
- si corporate actions afectan continuidad;
- que datos estaban disponibles as-of.

## Ejemplo Normativo: Short Into Resistance

Para `Short Into Resistance`, el estado no puede limitarse a:

```text
ticker + date + current price + volume today
```

Debe poder incluir, si las fuentes y calidad lo permiten:

- `resistance_high_20d`;
- `resistance_high_60d`;
- `resistance_high_90d`;
- `distance_to_resistance_pct`;
- `prior_high_date`;
- `prior_high_age_sessions`;
- `touch_count_near_resistance`;
- `current_gap_pct`;
- `current_pct_chg_1d`;
- `current_volume_vs_20d`;
- `float_or_market_cap_context`;
- `short_context_asof`;
- `halt_history_context`;
- `news/offering/catalyst_context_asof`;
- `intraday_spread_liquidity_context`;
- `quality_flags`.

Los nombres exactos pueden evolucionar por schema, pero el principio no:

```text
una estrategia que depende de memoria historica debe recibir esa memoria como
features as-of o como lineage reproducible, no como conocimiento oculto.
```

## Prohibiciones

Queda prohibido:

- tratar un top-25 scanner como universo completo;
- materializar estados solo con ticker-dia cuando la estrategia exige contexto
  historico;
- usar microestructura post-decision como feature pre-decision;
- incorporar outcomes, rewards, fills, PnL o acciones dentro del estado;
- presentar microstructure full-universe si solo existen ventanas gobernadas;
- entrenar ML/RL primario sobre candidatos con `full_universe_claim=false`
  como si fueran poblacion completa;
- reconstruir estados con `D:/quotes` sin marcar root provisional y rebuild
  obligatorio despues de paridad E.

## Implicaciones Para Tablas

### `master_daily_table`

Debe ser la base principal para lookbacks diarios e historicos.
Puede cubrir full history cuando sus fuentes y gates lo permitan.

### `daily_scanner_candidates_table`

Debe crearse antes de asumir que los tickers en play estan gobernados.
Su rol es reproducir scanners diarios y universos operativos.

Estado actual:

```text
target concept only
not materialized
```

### `strategy_candidate_events_table`

Debe separar la logica de seleccion por estrategia del estado final.
Un ticker puede estar en play para una estrategia y no para otra.

Estado actual:

```text
target concept only
not materialized
```

### `microstructure_features_table`

Debe crecer por ventanas gobernadas, no por scan ciego de todo quotes/trades.
Debe declarar si su cobertura es:

```text
seed_event_window_smoke
controlled_candidate
event_window_candidate
full_universe_claim=false
```

### `market_state_table`

Debe componer:

- identidad;
- calendario;
- contexto diario full-history;
- lookback features;
- contexto intradia legal;
- microestructura en ventanas;
- halts/news/fundamentals/short/regime as-of;
- quality flags;
- lineage.

No debe existir oficialmente hasta que el builder pueda declarar la cobertura y
los lookbacks usados.

### `event_state_table`

Debe anclar `market_state_table` a eventos/ventanas/roles de decision.
No debe inventar ventanas ni recalcular lookbacks con reglas privadas.

## Campos Obligatorios En Futuros Manifests

Toda materializacion candidata de estados debe incluir, como minimo:

```text
dataset_id
state_population_scope
state_population_denominator
full_universe_claim
scanner_definition_id
strategy_family_id
event_window_source
lookback_policy_id
lookback_daily_sessions
lookback_intraday_windows
price_view_policy
microstructure_window_policy
quotes_root_used
quotes_root_state
target_official_quotes_root
legacy_incomplete_e_quotes_root
requires_rebuild_after_quotes_root_approval
as_of_policy_version
leakage_guard_version
quality_policy_version
builder_version
source_manifests
```

## Promotion Gate

Una tabla de estados no puede pasar de candidate a validated si no demuestra:

- denominador declarado;
- cobertura real medida contra denominador;
- lookback policy declarada;
- recomputacion desde sources;
- tests de leakage/adversariales;
- separacion de labels/outcomes;
- lineage de roots y manifests;
- evidencia visual/forense representativa;
- status de consumo por `event_engine`, `backtest`, `ML/RL` y `execution`.

## Base Metodologica

Esta politica se apoya en la filosofia y contratos existentes de TSIS:

- `RESEARCH_PHILOSOPHY.md`: el estado no es solo precio-tiempo; los setups son
  transiciones de estado.
- `PROJECT_RULES.md`: las decisiones institucionales requieren justificacion
  directa y trazabilidad.
- `price_semantics_and_adjustment_policy.md`: las vistas de precio dependen del
  consumidor y del uso economico.
- `market_state_event_state_composition_contract_v0_1.md`: estado, label,
  reward, accion y fill son objetos separados.

Referencias externas ya compatibles con el marco TSIS:

- Marcos Lopez de Prado, *Beyond Econometrics: A Roadmap Towards Financial
  Machine Learning*: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3365282
- Gu, Kelly and Xiu, *Empirical Asset Pricing via Machine Learning*:
  https://www.nber.org/papers/w25398
- Zhang, Zohren and Roberts, *DeepLOB: Deep Convolutional Neural Networks for
  Limit Order Books*: https://arxiv.org/abs/1808.03668
- Byrd, Hybinette and Balch, *ABIDES: Towards High-Fidelity Multi-Agent Market
  Simulation*: https://arxiv.org/abs/1904.12066

Lectura TSIS:

```text
La literatura respalda separar labels de features, tratar microestructura como
estado temporal de alta dimension, y evitar validaciones que mezclen informacion
futura o universos no declarados.
```

## Regla Final

La operativa diaria puede empezar con tickers en play.

La ciencia de estados no puede terminar ahi.

El estado institucional debe preservar suficiente memoria historica para que una
estrategia dependiente de contexto, como `Short Into Resistance`, no quede ciega
por mirar solo el ticker-dia.
