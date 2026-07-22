# State RAW To Consumption Lineage Contract v0.1

## Estado

Tipo: contrato de trazabilidad RAW -> consumo de estado.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - DATA FOUNDATION / MARKET STATE`.
Fecha: 2026-07-05.

Status:

```text
state_raw_to_consumption_lineage_contract_v0_1 = complete_for_contract_defined_scope
raw_to_state_lineage_section_required = true
official_state_builder_implemented = false
market_state_table_materialized = false
event_state_table_materialized = false
```

## 1. Regla Obligatoria

A partir de este contrato, toda tabla, componente o derivada que pueda alimentar
`market_state_table`, `event_state_table`, strategy event states, ML/RL o
AlphaEvolve debe tener una seccion explicita de trazabilidad:

```text
RAW / staged source
-> derived view intermedia
-> componente gobernado
-> event/scanner/window si aplica
-> state builder
-> market_state/event_state
-> outcome/evaluator separado si aplica
```

La regla corta es:

```text
si no se puede explicar de donde sale desde RAW,
no puede entrar silenciosamente en una tabla de estado.
```

## 2. Que Debe Resolver La Trazabilidad

La seccion de trazabilidad debe permitir responder, sin leer codigo a ciegas:

```text
1. que fuente fisica original se uso;
2. si esa fuente es RAW, staged, derived, candidate o official;
3. que builders/contratos/manifests transformaron la data;
4. que columnas se preservan literales;
5. que columnas se derivan y con que formula/version;
6. que cutoff/as-of gobierna cada paso;
7. que calidad/coverage/lineage permite consumo;
8. que tabla consume a que tabla;
9. que queda fuera y por que;
10. que gaps de lineage quedan abiertos.
```

## 3. Seccion Obligatoria En Contratos

Cada contrato nuevo o revisado de tabla/componente de estado debe incluir una
seccion llamada exactamente:

```text
## Trazabilidad RAW -> Consumo De Estado
```

Esa seccion debe tener, como minimo, estos bloques:

| Bloque | Obligatorio | Que debe contener |
| --- | --- | --- |
| `Identidad del componente` | si | dataset_id, version, grano, price_view/session/window si aplica |
| `Rol en estado` | si | componente base, soporte legal, quality gate, event anchor, state final, representation candidate |
| `Cadena de lineage` | si | lista ordenada RAW -> intermedias -> componente -> state consumer |
| `Fuentes RAW/staged` | si | paths fisicos, familia, estado de autoridad, manifests si existen |
| `Fuentes derivadas intermedias` | si si existen | paths, builders, formulas, manifests/summaries, caveats |
| `Builders/scripts` | si | scripts, configs, command/run id si existe |
| `Contratos y schemas` | si | schema, dataset contract, policy, validators, registry |
| `Manifests/hashes` | si si existen | manifest path, sha/tree hash, build_run_id, created_at |
| `Transformaciones` | si | columnas literales, derivadas, joins, union, price views, windows |
| `Cutoff/as-of` | si | timestamp legal, session close/open, lag, availability, lookback closure |
| `Quality/coverage gates` | si | gates, hard fails, review flags, missingness, full_universe_claim |
| `Consumo permitido` | si | state/event_state/ML/RL/AlphaEvolve/backtest flags |
| `No es / no incluye` | si | outcomes, labels, rewards, fills, PnL, future info, raw replacement si aplica |
| `Evidencia de validacion` | si | tests, validator run, summary rows, hard_fail_count |
| `Gaps abiertos` | si | falta manifest, fuente provisional, candidate-only, no full universe, etc. |

## 4. Estados Permitidos De Lineage

Usar estos estados de forma uniforme:

| Estado | Significado |
| --- | --- |
| `raw_authority` | fuente RAW preservada o staged con autoridad primaria para esa familia |
| `derived_authority_declared_scope` | derivada oficial/promovida para un scope declarado |
| `candidate_controlled` | salida candidate controlada, no oficial |
| `fixture_only` | muestra pequena para tests, no consumo investigativo general |
| `provisional_lineage` | fuente aceptada solo como lineage provisional |
| `blocked_missing_source` | falta fuente, manifest o contrato |
| `support_only` | calendario/identidad/calidad; gobierna legalidad, no alpha |
| `quality_only` | gates/calidad; no feature causal |
| `lineage_only` | manifest/build/source path; no feature causal |

## 5. Plantilla Minima

```text
## Trazabilidad RAW -> Consumo De Estado

Componente:
  dataset_id = ...
  version = ...
  grano = ...
  rol_en_estado = ...

Cadena:
  RAW/staged source A
  -> derived/source component B
  -> governed component C
  -> state builder namespace X
  -> market_state/event_state consumer

Fuentes RAW/staged:
  - path = ...
    estado = raw_authority | provisional_lineage | ...
    manifest = ... | not_available
    build_run_id = ... | not_available

Fuentes derivadas intermedias:
  - path = ...
    builder = ...
    formula_contract = ... | not_applicable
    manifest/summary = ...
    estado = derived_authority_declared_scope | candidate_controlled | ...

Builders/scripts:
  - builder = ...
  - config = ... | not_applicable
  - run_id = ... | not_available

Contratos/schemas/policies:
  - schema = ...
  - dataset_contract = ...
  - consumption_policy = ...
  - validators = ...
  - registry = ...

Transformaciones:
  literales = ...
  derivadas = ...
  joins = ...
  price_views/windows = ...

Cutoff/as-of:
  decision_timestamp_policy = ...
  availability_rule = ...
  lookback_rule = ...

Quality/coverage:
  gates = ...
  hard_fail_count = ...
  full_universe_claim = true|false

Consumo permitido:
  market_state = true|false
  event_state = true|false
  ml = true|false
  rl = true|false
  alphaevolve = true|false

No es / no incluye:
  - ...

Evidencia:
  - manifest = ...
  - summary = ...
  - validator/test = ...

Gaps abiertos:
  - ...
```

## 6. Gate Para State Builder

Todo `state_builder` debe validar que cada `source_component` declarado tenga
trazabilidad RAW -> consumo disponible o explicitamente bloqueada.

Regla de config:

```text
requires_raw_to_consumption_lineage = true
```

Hard fail:

```text
builder_source_component_without_lineage_contract
builder_source_component_missing_raw_or_declared_derived_authority
builder_source_component_missing_manifest_or_explicit_manifest_absence
builder_source_component_unknown_cutoff_rule
builder_source_component_unknown_consumption_gate
```

Excepcion permitida:

```text
fixture_only puede usar data sintetica/minima si declara que no viene de RAW y
no pretende representar evidencia de mercado real.
```

## 7. Ejemplo Cerrado: `master_daily_table_v0_1`

### Identidad Del Componente

```text
dataset_id = master_daily_table_v0_1
grain = instrument_id + ticker + session_date + price_view
role = componente diario/base daily__* para market_state/event_state
output = E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
manifest = E:/TSIS/data/data_foundation_outputs/master_daily_table/_master_daily_table_manifest_v0_1.json
summary = E:/TSIS/data/data_foundation_outputs/master_daily_table/_master_daily_table_summary_v0_1.csv
build_run_id = master_daily_table_v0_1_20260630T201044Z
```

### Cadena RAW -> Consumo

```text
E:/TSIS/data/ohlcv_daily
+ E:/TSIS/data/ohlcv_daily_adjusted
+ E:/TSIS/data/data_foundation_outputs/expected_data_calendar/expected_data_calendar_v0_1
+ E:/TSIS/data/data_foundation_outputs/corporate_actions_table/corporate_actions_table_v0_1.parquet
+ E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
-> C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_master_daily_table.py
-> E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
-> daily__* observables en futuros market_state/event_state builders
```

### Fuentes RAW / Staged / Derivadas

| Fuente | Path | Estado | Rol |
| --- | --- | --- | --- |
| Raw daily | `E:/TSIS/data/ohlcv_daily` | `raw_authority` | OHLCV diario bruto |
| Daily adjusted | `E:/TSIS/data/ohlcv_daily_adjusted` | `derived_authority_declared_scope` | split-normalized y adjusted OHLC |
| Expected calendar | `E:/TSIS/data/data_foundation_outputs/expected_data_calendar/expected_data_calendar_v0_1` | `support_only` | denominador esperado ticker/instrument/session |
| Corporate actions | `E:/TSIS/data/data_foundation_outputs/corporate_actions_table/corporate_actions_table_v0_1.parquet` | `support_only` | flags de split/dividend/ticker_change |
| Dataset certification matrix | `E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet` | `quality_only` | gates de consumo por familia |

### Derivacion De `ohlcv_daily_adjusted`

`master_daily_table_v0_1` no sale solo de RAW puro. Consume tambien
`ohlcv_daily_adjusted`, que es una vista derivada previa.

```text
D:/ohlcv_daily o E:/TSIS/data/ohlcv_daily segun materializacion/auditoria vigente
+ C:/TSIS_Data/data/additional/corporate_actions/splits
+ C:/TSIS_Data/data/additional/corporate_actions/dividends
-> C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_daily_adjusted.py
-> E:/TSIS/data/ohlcv_daily_adjusted
```

Columnas derivadas obligatorias de esa vista:

```text
future_split_factor
future_dividend_factor
future_adjustment_factor
o_split_normalized/h_split_normalized/l_split_normalized/c_split_normalized
o_adjusted/h_adjusted/l_adjusted/c_adjusted
source_daily_file
source_splits_file
source_dividends_file
```

### Transformaciones En `master_daily_table_v0_1`

El builder crea tres `price_view` por expected row:

| price_view | Precios | Volumen | VWAP |
| --- | --- | --- | --- |
| `daily_raw` | OHLC desde `ohlcv_daily` | raw volume | raw VWAP |
| `split_normalized` | OHLC desde columnas split-normalized de `ohlcv_daily_adjusted` | raw volume | `vwap = null`, conserva `source_raw_vwap` |
| `adjusted` | OHLC desde columnas adjusted de `ohlcv_daily_adjusted` | raw volume | `vwap = null`, conserva `source_raw_vwap` |

Derivadas diarias calculadas:

```text
prior_close
gap_pct
daily_return_pct
intraday_return_pct
daily_range_pct
dollar_volume
volume_20d_avg
rvol_20d
```

Lectura correcta:

```text
volume_20d_avg y rvol_20d son derivadas mecanicas versionadas.
No significan que 20d sea el unico horizonte cientificamente valido.
Variantes futuras deben vivir como formulas/representation candidates hasta contratarse.
```

### Cutoff / As-Of

```text
Uso daily EOD: solo despues de cierre/disponibilidad de la sesion.
Antes del cierre no puede usarse como si high/low/close/volume final fueran conocidos.
Lookbacks usan sesiones previas/presentes segun la regla declarada por el builder.
```

### Calidad / Cobertura / Evidencia

Manifest oficial:

```text
rows = 22109097
expected_daily_rows = 7369699
price_views = 3
tickers = 4824
instrument_ids = 4626
first_session = 2005-01-03
last_session = 2026-03-09
hard_fail_count = 0
tree_sha256 = 18a9905dc0ad7410fe0265241881019f2ad8f51fb44183f3eb750476720830e8
```

Limitaciones conocidas del manifest:

```text
family_level_quality_gate_only
row_level_daily_quality_labels_not_joined_in_v0_1
fundamentals_news_short_halts_regime_not_joined_in_v0_1
vwap_not_adjusted_for_split_or_dividend_views
```

### Consumo Permitido

```text
market_state daily__* candidate/official future = permitido bajo cutoff
state/event context daily = permitido bajo cutoff
daily scanner candidates = permitido como denominador/scanner, no como estado causal
ML/RL/AlphaEvolve = solo si state/event/outcome/evaluator gates posteriores pasan
```

No es:

```text
raw replacement universal
intraday 1m state
quotes/trades/microstructure
outcome table
label/reward/PnL/execution truth
```

## 8. Estado De Cobertura Del Contrato

| Area | Estado de trazabilidad | Proximo paso |
| --- | --- | --- |
| Daily / `master_daily_table_v0_1` | ejemplo cerrado en este contrato | copiar seccion resumida a contrato/schema si se revisa |
| Intradia 1m / `master_intraday_bar_table` | cerrado para upstream manifest lineage quote-guarded | `state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md`; materializacion candidate sigue pendiente |
| Microestructura | pendiente de seccion quotes/trades RAW -> window features -> state | completar antes de fixture event_state con microestructura |
| Contexto as-of | pendiente por componente | documentar fundamentals/news/short/regime/halts uno a uno |
| Event candidate/event windows daily controlado | cerrado para Camino A controlado | `state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md` |
| Event candidate/event windows intradia 1m controlado | cerrado para scope controlado | `state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1.md` |
| Event state intradia 1m controlado | cerrado para scope controlado | `state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md` |
| Event candidate tables wider/1m | pendiente para scope amplio | anadir trazabilidad scanner -> event -> event_windows por fuente real amplia |
| Market/event state final | bloqueado hasta builder candidate | debe listar todo componente source usado |


## 8.1 Lineage Ligado - Camino A Daily Event Windows Controlado

Documento ligado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md
```

Cubre:

```text
master_daily_table_v0_1 + instrument_master + market_calendar + scanner definitions
-> daily_scanner_candidates_table_v0_3_candidate_replay
-> daily_strategy_candidate_events_table_v0_1 controlled candidate
-> event_windows_table_v0_1_candidate_daily_strategy_events
-> futuro controlled market_state/event_state fixture
```

Estado:

```text
complete_for_controlled_scope
full_universe_claim = false
official_e_root_materialization = false
intraday_1m_claim = false
```

## 8.2 Lineage Ligado - Intradia 1m Quote-Guarded

Documento ligado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
```

Cubre:

```text
E:/TSIS/data/ohlcv_1m
+ D:/quotes provisional lineage
-> repair shards quote-guarded
-> repair_manifest_lt1b_v0_1.parquet PASS
-> futura vista ohlcv_1m_quote_guarded
-> futura master_intraday_bar_table_v0_2_candidate_quote_guarded
-> futuros intraday__* para state builder
```

Estado:

```text
complete_for_upstream_manifest_lineage_scope
quote_guarded_manifest_gate = passed
master_intraday_bar_table_v0_2_candidate_materialized = false
intraday_scanner_candidates_table_v0_2_materialized = false
```

Lectura correcta: cierra la trazabilidad upstream del overlay 1m quote-guarded.
No materializa la tabla intradia candidate ni habilita ML/RL/AlphaEvolve.

## 9. Regla Para AlphaEvolve / RL / ML

AlphaEvolve, RL o ML pueden proponer:

```text
nuevas formulas derivadas;
nuevas representaciones;
nuevos detectores de eventos;
nuevas transiciones;
nuevas politicas.
```

Pero no pueden introducir un observable, representacion o tabla si no existe una
trazabilidad RAW -> consumo declarada.

Regla final:

```text
AlphaEvolve puede mutar la representacion.
No puede mutar silenciosamente la verdad de lineage.
```

C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1.md
-> intraday_1m_strategy_candidate_events_table_v0_1_candidate
-> event_windows_table_v0_1_candidate_intraday_1m_strategy_events

C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md
-> market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
-> event_windows_table_v0_1_candidate_intraday_1m_strategy_events
-> event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
