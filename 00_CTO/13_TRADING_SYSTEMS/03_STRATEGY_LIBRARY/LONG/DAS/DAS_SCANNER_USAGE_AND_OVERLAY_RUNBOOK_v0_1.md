# DAS Scanner Usage And Overlay Runbook v0.1

Fecha: 2026-06-30
Estado: `strategy_research_runbook`
Scope: `00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/`

## 1. Rol

Este documento explica como debe usar DAS el scanner gobernado de TSIS.

El punto central:

```text
Data Foundation scanner = donde mirar
DAS overlay = que estado/frontside aparecio dentro de lo mirado
market_state/event_state futuro = estado institucional compuesto
```

Este runbook existe porque `notebooks/das_case_explorer.ipynb` y los primeros
runs DAS pueden construir muestras utiles, pero tambien pueden sesgar el
experimento si solo buscan casos positivos.

## 2. Autoridades

Autoridad operativa de scanner:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_2.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_2.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_daily_scanner_candidates_table_v0_2.py
```

Autoridad CTO de candidate selection:

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
```

Autoridad DAS local:

```text
STRATEGY.md
DAS_FRONTSIDE_STATE_AND_ALPHAEVOLVE_RESEARCH_PLAN_v0_1.md
DAS_CANDIDATE_STATE_TABLE_EXPERIMENTAL_SPEC_v0_1.md
```

## 3. Lo que existe hoy

Existe un builder gobernado de scanner diario:

```text
scripts/materialize_daily_scanner_candidates_table_v0_2.py
```

Existe evidencia controlada, no oficial:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_2_1_contract_aligned/
```

Ese replay prueba forma, lineage y semantica del scanner. No es todavia una
tabla oficial en `E:/TSIS/data`.

## 4. Capas Correctas

### 4.1. Daily scanner candidates

Tabla:

```text
daily_scanner_candidates_table_v0_2
```

Uso:

```text
denominador reproducible de ticker/session/as_of evaluados
```

No es:

```text
market_state
event_state
feature store ML
RL state
senal DAS
label
reward
orden
fill
PnL
```

### 4.2. DAS candidate state table experimental

Tabla local:

```text
das_candidate_state_table_experimental
```

Uso:

```text
leer patrones DAS/frontside dentro de candidatos o runs DAS
```

Debe incluir:

- positivos;
- falsos positivos;
- fallos;
- casos `review`;
- casos sin DAS sano;
- labels humanos separados;
- outcomes separados.

No debe construir solo una muestra de buenos trades.

### 4.3. Market/event state futuro

Futuro:

```text
market_state_table
event_state_table
```

Uso:

```text
estado institucional compuesto para ML/RL/backtest/evaluadores
```

El scanner y DAS no deben saltar directamente a ML/RL sin esa capa.

## 5. Como Ejecutar Un Replay De Scanner

### 5.1. Muestra pequena / lab / notebook

Usar `C:/TSIS_Data/tests/test_runs/`:

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_daily_scanner_candidates_table_v0_2.py" `
  --start-date 2025-01-02 `
  --end-date 2025-01-10 `
  --run-id daily_scanner_candidates_replay_20250102_20250110_v0_2_1_contract_aligned `
  --output-root "C:\TSIS_Data\tests\test_runs\2026-06-30\daily_scanner_candidates_replay_20250102_20250110_v0_2_1_contract_aligned" `
  --overwrite
```

El parquet queda en:

```text
<output-root>/daily_scanner_candidates_table_v0_2_candidate_replay/data.parquet
```

El manifest queda en:

```text
<output-root>/_daily_scanner_candidates_table_manifest_v0_2_candidate_replay.json
```

### 5.2. Replay largo / multi-year / 20 anos

Usar `E:/TSIS/data`:

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_daily_scanner_candidates_table_v0_2.py" `
  --start-date 2005-01-03 `
  --end-date 2025-12-31 `
  --run-id daily_scanner_candidates_replay_20050103_20251231_v0_2_1_contract_aligned `
  --output-root "E:\TSIS\data\data_foundation_outputs\daily_scanner_candidates_table\candidate_replays\daily_scanner_candidates_replay_20050103_20251231_v0_2_1_contract_aligned"
```

No usar el root oficial reservado salvo promocion explicita:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/daily_scanner_candidates_table_v0_2/
```

## 6. Una Ejecucion De 20 Anos Basta?

Respuesta precisa:

```text
Si, para tener un denominador canonico de esa version del scanner y esas fuentes.
No, para siempre.
```

Una ejecucion 20y sirve como base si:

- no cambian los contratos;
- no cambian las configs;
- no cambia `master_daily_table`;
- no se activa intraday/as-of relative volume;
- no se corrige una fuente upstream relevante;
- no se cambia el universo o price view.

Hay que ejecutar otra version si:

- cambia el umbral de market cap/precio/calidad;
- se cambia un perfil;
- se anade un nuevo source;
- se repara una fuente base;
- se necesita intraday/as-of;
- se pasa de replay diario a live-like;
- se promociona un nuevo contrato.

Las estrategias nuevas no deben forzar necesariamente un rerun del scanner base.
Primero deben crear un overlay sobre el denominador existente.

## 7. Como Usar Scanner En DAS

### 7.1. Pregunta correcta

No preguntar:

```text
que buenos DAS encuentro?
```

Preguntar:

```text
dentro de los candidatos evaluados, que estructuras DAS/frontside aparecen,
cuales fallan y por que?
```

### 7.2. Denominadores permitidos

Todo estudio DAS debe declarar uno de estos denominadores:

```text
all_filters_passed
selected_any_profile
selected_trade_station_like_profile
selected_percent_change_profile
selected_dollar_volume_tradability_profile
selected_das_research_profile
manual_human_seed
conditional_on_current_das_detector
```

Interpretacion:

- `all_filters_passed`: universo smallcap elegible; util para ausencia/fallos.
- `selected_any_profile`: candidatos vistos por algun perfil generico.
- `selected_trade_station_like_profile`: replica aproximada de pantalla humana.
- `selected_percent_change_profile`: movimiento diario minimo + ranking.
- `selected_dollar_volume_tradability_profile`: actividad economica/tradability.
- `selected_das_research_profile`: semilla provisional, no scanner DAS final.
- `manual_human_seed`: muestra humana; no poblacional.
- `conditional_on_current_das_detector`: muestra del detector DAS actual; puede
  estar sesgada y debe declararlo.

### 7.3. Notebook DAS

`notebooks/das_case_explorer.ipynb` puede:

- leer un parquet de `daily_scanner_candidates_table_v0_2`;
- filtrar por denominador declarado;
- renderizar charts;
- exportar casos visuales;
- lanzar builders DAS experimentales;
- comparar positivos, fallos y review.

No debe:

- inventar un scanner silencioso;
- ocultar thresholds en celdas;
- seleccionar solo ganadores;
- reportar estadisticas poblacionales si el input fue un run DAS sesgado;
- escribir resultados institucionales en `E:/TSIS/data` sin contrato.

## 8. Si Una Estrategia Nueva Necesita Filtros Propios

Regla:

```text
No modificar el scanner base para resolver una hipotesis de estrategia.
```

Proceso:

1. Usar `daily_scanner_candidates_table_v0_2` como denominador.
2. Crear un overlay de estrategia bajo la carpeta de la estrategia.
3. Documentar cada filtro como hipotesis, no como verdad de Data Foundation.
4. Incluir positivos, negativos, fallos y review.
5. Guardar columnas namespaced:

```text
scanner__
daily__
intraday__
frontside__
das__
quality__
human_label__
outcome__
```

6. Separar features de labels/outcomes:

```text
human_label__* != feature
outcome__* != feature
```

7. Solo si un filtro demuestra utilidad general y estable, proponer promocion a:

```text
Data Foundation generic profile
strategy-specific scanner contract
market_state/event_state component
```

## 9. Como Leer La Tabla En Un Notebook

Ejemplo minimo:

```python
from pathlib import Path
import duckdb

run_root = Path(r"C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_2_1_contract_aligned")
parquet = run_root / "daily_scanner_candidates_table_v0_2_candidate_replay" / "data.parquet"

con = duckdb.connect()

df = con.sql(f"""
select
    session_date,
    ticker,
    as_of_utc,
    all_filters_passed,
    selected_any_profile,
    selected_trade_station_like_profile,
    selected_percent_change_profile,
    selected_dollar_volume_tradability_profile,
    selected_das_research_profile,
    candidate_reasons,
    pct_chg_1d,
    volume_today,
    dollar_volume_today,
    scanner_selection_state
from read_parquet('{parquet.as_posix()}')
where selected_any_profile
order by session_date, ticker
""").fetchdf()

display(df.head(50))
```

Para estudiar sesgo, cambiar `where selected_any_profile` por:

```sql
where all_filters_passed
```

y medir cuantos candidatos NO tuvieron estructura DAS sana.

## 10. Estado Actual De DAS

Estado correcto hoy:

```text
DAS tiene detector/notebook experimental.
DAS tiene spec de tabla experimental.
DAS todavia no tiene scanner especifico institucional.
```

Por tanto:

```text
das_research_profile_v0_2 != DAS scanner final
```

El siguiente paso serio para DAS es:

```text
daily_scanner_candidates_table_v0_2 replay
-> das_candidate_state_table_experimental
-> estadisticas con denominador declarado
-> visual casebook de positivos/fallos/review
-> propuesta de overlay DAS v0.2
```

