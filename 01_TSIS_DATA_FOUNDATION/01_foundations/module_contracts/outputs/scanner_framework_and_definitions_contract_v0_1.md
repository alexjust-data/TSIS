# Scanner Framework And Definitions Contract v0.1

## Estado

Tipo: module contract.

Modulo: `01_TSIS_DATA_FOUNDATION`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status:

```text
contract_defined_not_materialized
```

Este contrato gobierna las definiciones iniciales de scanner que alimentaran:

```text
daily_scanner_candidates_table_v0_1
```

No materializa datos.
No crea senales de estrategia.
No sustituye `market_state_table` ni `event_state_table`.

## Decision Central

TSIS no debe tener un unico "scanner general" que mezcle visibilidad operativa,
research discovery y logica de estrategia.

La decision v0.1 es:

```text
scanner_framework
  -> trade_station_like_scanner_v0_1
  -> broad_in_play_discovery_scanner_v0_1
  -> future strategy overlays such as DAS
```

El framework define candidatos.
Las estrategias interpretan candidatos.
Data Foundation gobierna estados institucionales.

## Preguntas Que Responde Cada Scanner

### `trade_station_like_scanner_v0_1`

Responde:

```text
Que habria visto el operador en una hot list operativa similar a TradeStation?
```

Uso primario:

- reproducir visibilidad humana historica;
- medir retraso operativo;
- comparar si DAS aparece tarde en el scanner humano;
- documentar lo que una herramienta operativa habria mostrado.

No responde:

- todos los tickers vivos;
- todos los DAS tempranos;
- el universo completo de oportunidades;
- la verdad del estado de mercado.

### `broad_in_play_discovery_scanner_v0_1`

Responde:

```text
Que tickers empezaban a estar vivos aunque todavia no cumplieran el scanner humano?
```

Uso primario:

- discovery amplio;
- proteger research contra sesgo de llegada tardia;
- detectar DAS/frontside temprano;
- medir candidatos que no alcanzan todavia `volume_today > 500000`;
- construir denominadores mas honestos para estrategias de momentum temprano.

No responde:

- lo que el operador vio en TradeStation;
- una senal ejecutable;
- un label;
- un outcome;
- una decision de trading.

## Por Que No Basta `volume_today > 500000`

`volume_today > 500000` es util para replicar un scanner humano operativo, pero
puede llegar tarde para DAS.

En DAS/frontside, el patron puede activarse antes de que el volumen acumulado
alcance 500k. Si ese umbral se usa como filtro duro unico, el sistema puede
capturar el ticker despues de:

- el primer push;
- el dip bueno;
- el rebreak clave;
- o el momento en que el patron ya esta degradado.

Decision TSIS:

```text
volume_today_min = hard filter only for trade_station_like_scanner_v0_1
volume metrics = features/reasons for broad_in_play_discovery_scanner_v0_1
```

El scanner amplio debe registrar:

- `volume_to_time`;
- `volume_since_04_00`;
- `volume_last_5m`;
- `volume_last_15m`;
- `volume_acceleration`;
- `dollar_volume_to_time`;
- `rvol_to_time`;
- `volume_tier`.

Bandas canonicas iniciales:

```text
lt_100k
100k_250k
250k_500k
500k_1m
gt_1m
```

La pregunta que esta estructura permite medir es:

```text
Cuantos DAS buenos empezaron antes de 500k de volumen acumulado?
```

## Por Que No Basta `% Change 1D`

`pct_chg_1d` es util para rankings de momentum visible, pero puede perder
eventos que se activan por estructura intradia o after-hours.

En DAS/frontside, un candidato puede entrar por:

- after-hours breakout;
- premarket new high;
- prior day high reclaim;
- volume acceleration;
- range expansion;
- news/catalyst;
- halt/reopen context;
- short-pressure context when legally as-of.

Decision TSIS:

```text
pct_chg_1d = one ranking/reason
candidate_reasons = required multi-reason surface
```

## Hard Eligibility Comun

Ambos scanners deben respetar una elegibilidad comun minima:

```text
is_common_stock = true
0.5 < last_price <= 20
market_cap_usd <= scanner_config.market_cap_max_usd
data_quality_state not in hard bad/quarantine states
```

Notas:

- `trade_station_like_scanner_v0_1` usa `market_cap_max_usd = 100000000`.
- `broad_in_play_discovery_scanner_v0_1` puede usar un techo mas amplio
  configurable, inicialmente `300000000`, sin redefinir el universo canonico
  LT1B.
- El universo LT1B sigue siendo una source of truth separada; un scanner solo
  define candidatos bajo una regla.

## Soft/In-Play Reasons

El scanner amplio debe permitir inclusion cuando al menos una razon in-play
sea verdadera:

```text
reason_pct_chg_1d_move
reason_gap_pct_move
reason_volume_acceleration
reason_rvol_to_time
reason_afterhours_breakout
reason_premarket_new_high
reason_prior_day_high_reclaim
reason_unusual_range_expansion
reason_news_context
reason_halt_or_reopen_context
```

Las razones deben persistirse en output.
No basta guardar solo `selected = true`.

## Rankings Requeridos

Cuando existan los campos fuente, el output debe preservar rankings separados:

```text
rank_pct_chg_1d
rank_volume_acceleration
rank_dollar_volume_to_time
rank_rvol_to_time
rank_composite_in_play
```

Y flags separados:

```text
selected_trade_station_like_top25
selected_broad_discovery
selected_by_pct_chg_rank
selected_by_volume_acceleration_rank
selected_by_dollar_volume_rank
selected_by_composite_in_play_rank
```

Esto permite medir si un candidato:

- era visible para el operador;
- era visible solo para discovery;
- entro por ranking de momentum;
- entro por aceleracion de volumen;
- o entro por estructura after-hours/premarket.

## Relacion Con DAS

DAS puede consumir candidatos de ambos scanners, pero debe distinguirlos.

Regla:

```text
DAS puede prototipar estados.
Data Foundation gobierna estados institucionales.
```

La ruta correcta es:

```text
daily_scanner_candidates_table
  -> das_candidate_state_table_experimental
  -> future market_state_table / event_state_table
```

DAS no debe escribir directamente `market_state_table`.

## Column Namespace Implications

El output `daily_scanner_candidates_table_v0_1` debe poder contener:

```text
scanner__candidate_reasons
scanner__volume_tier
scanner__rank_pct_chg_1d
scanner__rank_volume_acceleration
scanner__rank_dollar_volume_to_time
scanner__rank_composite_in_play
scanner__selected_trade_station_like_top25
scanner__selected_broad_discovery
```

Si el schema fisico no usa prefijo `scanner__`, debe preservar semantica
equivalente mediante nombres canonicos sin colision.

## Configs Versionadas

Las definiciones vivas v0.1 son:

```text
configs/data_foundation_outputs/scanner_definitions/trade_station_like_scanner_v0_1.yaml
configs/data_foundation_outputs/scanner_definitions/broad_in_play_discovery_scanner_v0_1.yaml
```

Un builder no debe esconder filtros dentro de codigo o notebooks.
Debe leer una definicion versionada o escribir su copia efectiva en el
manifest del run.

## Tests Obligatorios Antes De Uso

Antes de materializar un replay controlado:

1. validar que las configs existen y son parseables;
2. validar que `scanner_definition_id` coincide con el filename;
3. validar que no hay threshold oculto en codigo;
4. validar que los dos scanners producen razones separadas;
5. validar que `volume_today > 500000` solo es hard filter para
   `trade_station_like_scanner_v0_1`;
6. validar que `broad_in_play_discovery_scanner_v0_1` conserva candidates por
   razones alternativas;
7. validar que `candidate_reasons` no contiene outcomes, labels, rewards,
   PnL, fills ni decisiones de estrategia;
8. validar que toda fila declara `as_of_utc`, source lineage y denominator;
9. validar que cualquier full-session value usado intradia queda bloqueado si
   no existe cutoff/as-of policy.

## Primer Replay Controlado Recomendado

No se debe empezar con un full historical blind run.

Primer scope recomendado:

```text
2025/2026 controlled replay
7 to 30 sessions
DAS known days + random control days
both scanner definitions
full_universe_claim = false unless denominator proof is complete
```

Metricas de comparacion obligatorias:

```text
das_good_cases_seen_by_trade_station_like
das_good_cases_seen_by_broad_discovery
das_good_cases_missed_by_volume_500k
das_good_cases_missed_by_pct_chg_rank
minutes_from_frontside_awakening_to_trade_station_visibility
minutes_from_frontside_awakening_to_broad_discovery_visibility
```

## Prohibited Uses

Queda prohibido:

- usar `trade_station_like_scanner_v0_1` como universo completo;
- usar `broad_in_play_discovery_scanner_v0_1` como senal de trading;
- tratar candidates como estados finales;
- entrenar ML/RL directamente con scanner rows;
- mezclar labels/outcomes dentro del scanner;
- llamar "DAS detectado" a un ticker solo porque paso el scanner general;
- ocultar seleccion manual bajo scanner automatico.

## Scientific And Institutional Basis

Este contrato implementa reglas ya aceptadas en TSIS:

```text
PROJECT_RULES.md
RESEARCH_PHILOSOPHY.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```

Decision TSIS -> Evidencia directa -> Obligacion tecnica -> Limitacion abierta:

| Decision TSIS | Evidencia directa | Obligacion tecnica | Limitacion abierta |
| --- | --- | --- | --- |
| Separar scanner humano de discovery amplio. | `RESEARCH_PHILOSOPHY.md` define setups como transiciones de estado y advierte contra representaciones pobres de precio/volumen. | Mantener `trade_station_like` y `broad_discovery` como definiciones distintas. | Los thresholds broad v0.1 son candidate policy y deben calibrarse con replay controlado. |
| No usar `volume_today > 500k` como unico filtro general. | Evidencia DAS interna: senales tempranas pueden aparecer antes de volumen acumulado alto. | Persistir volumen como features, tiers y razones; no como hard filter universal. | Requiere builder intradia/as-of para medir volumen a tiempo real historico. |
| No usar `% change 1D` como unica razon de inclusion. | El proyecto define eventos por attention, liquidez, premarket, after-hours, catalysts y halts, no solo daily return. | Persistir `candidate_reasons` y rankings separados. | Algunas razones dependen de tablas aun en maduracion: news, halts, short context. |
| Mantener scanner fuera de labels/outcomes. | `VERSIONING_STANDARDS.md` y output contracts exigen separar features, labels, rewards y decisions. | Bloquear columnas outcome/label/reward/action/fill/pnl en validators. | La tabla DAS experimental puede tener labels, pero separados y fuera del scanner general. |

## Final Rule

El scanner general de TSIS no es una hot list unica.

Es una capa reproducible de candidate generation con definiciones versionadas:

```text
operational visibility replay + broad research discovery
```

Solo asi DAS puede medir patrones tempranos sin perder la comparacion contra lo
que el operador realmente habria visto.
