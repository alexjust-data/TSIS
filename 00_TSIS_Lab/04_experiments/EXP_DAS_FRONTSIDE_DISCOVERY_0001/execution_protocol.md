# Execution Protocol - EXP_DAS_FRONTSIDE_DISCOVERY_0001

Fecha: 2026-07-05
Estado: draft_execution_protocol
Contrato base: `C:/TSIS_Data/00_TSIS_Lab/01_contracts/research_experiment_execution_protocol_v0_1.md`

## 1. Objetivo

Este documento define como debe ejecutarse el experimento `EXP_DAS_FRONTSIDE_DISCOVERY_0001` de forma reproducible.

La ejecucion oficial no debe depender de un notebook.

La regla es:

```text
Notebook = inspeccion humana / revision visual / diagnostico
Executor = verdad reproducible del experimento
Manifest = trazabilidad
Evidence report = conclusion cientifica exploratoria
```

## 2. Pregunta Que Ejecuta El Primer Sweep

El primer sweep no busca encontrar una estrategia rentable ni optimizar entradas.

La pregunta ejecutable es:

```text
Dentro del dominio DAS/frontside small cap,
donde empieza la zona minima de operabilidad del frontside para estudiar longs DAS?
```

Lectura del `+50%`:

```text
+50% = criba humana historica de operabilidad frontside
+50% != entrada
+50% != evento validado
+50% != threshold optimo
+50% != feature base de estado
```

Lectura de los buckets de `SWEEP_001`:

```text
20/30/40       = grupo de control bajo la frontera humana
50             = suelo operativo humano a auditar
60/75/100/150  = intensidad frontside creciente y posible sobreextension
```

## 3. Que Se Ejecuta

La unidad de ejecucion es:

```text
experiment.yaml
+ parameter_space.yaml
+ sweeps/SWEEP_001_frontside_operability_boundary.yaml
```

El executor debe resolver esos archivos y producir un run reproducible.

Comando objetivo futuro:

```powershell
python C:/TSIS_Data/00_TSIS_Lab/05_executors/run_research_experiment.py `
  --experiment-root C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001 `
  --sweep sweeps/SWEEP_001_frontside_operability_boundary.yaml `
  --adapter smallcaps `
  --output-root E:/TSIS/data/research_experiments
```

Mientras no exista el executor transversal del Lab, se permite un executor SmallCaps equivalente, siempre que lea los mismos YAML y escriba los mismos artefactos.

## 4. Inputs Gobernados

### 4.1. Configuracion

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/experiment.yaml
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/parameter_space.yaml
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/sweeps/SWEEP_001_frontside_operability_boundary.yaml
```

### 4.2. Fuente Intradia 1m Para Barras

Fuente logica preferida:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
```

Lectura correcta:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
= superficie candidata de barras 1m quote-guarded
!= repair_manifest
!= tabla de estado
!= denominador poblacional
!= fuente full-universe disponible hoy
```

El `repair_manifest_lt1b_v0_1.parquet` es solo el overlay de reparacion:

```text
raw E:/TSIS/data/ohlcv_1m + repair_manifest_lt1b_v0_1.parquet = vista 1m quote-guarded
```

La tabla candidata `master_intraday_bar_table_v0_2_candidate_quote_guarded`, cuando existe para un scope, materializa esa lectura como barras 1m con:

```text
OHLCV 1m
price_view = 1m_raw / 1m_quote_guarded_raw
quote_guarded_repair_applied
repair_state
repair_reason
VWAP consumption state
lineage de raw + manifest + quotes
quality/ML/RL/full_universe gates
```

Estado fisico actual confirmado:

```text
path = E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
status = scoped_candidate_materialized_not_official
scope = AACT:2025-09, AAGR:2023-12, AAMC:2023-12
rows = 21670
price_views = 1m_raw:10835, 1m_quote_guarded_raw:10835
quote_guarded_repair_applied_rows = 96
full_universe_claim = false
valid_for_ml_feature_candidate = false
valid_for_rl_state_component_candidate = false
alphaevolve_evaluator_enabled = false
```

Por tanto, para ejecutar `SWEEP_001` sobre DAS, el E-root scoped candidate actual solo sirve como prueba de plumbing/lineage. No es suficiente como input historico del experimento.

El executor debe hacer una de estas dos cosas:

```text
1. materializar master_intraday_bar_table_v0_2_candidate_quote_guarded para el scope del denominador DAS;
2. o aplicar raw E:/TSIS/data/ohlcv_1m + repair_manifest_lt1b_v0_1 overlay on the fly para los ticker-months requeridos, generando manifest de run.
```

Uso correcto cuando exista para el scope requerido:

```text
barras 1m gobernadas para calcular momentum trigger, first push, first dip, rebreak y outcomes separados
```

### 4.3. Denominador Poblacional Requerido

```text
daily_scanner_candidates_table_v0_2_or_successor
```

Uso:

```text
saber que tickers/sesiones estaban vivos, visibles o in-play antes de buscar DAS
```

Lectura correcta:

```text
denominador poblacional = donde mirar
fuente 1m quote-guarded = que paso minuto a minuto
DAS detector = que estructura aparece dentro del denominador
outcomes separados = que ocurrio despues
```

El denominador responde esta pregunta:

```text
sobre que ticker/session/date tenia permiso TSIS de buscar el fenomeno DAS?
```

No responde estas preguntas:

```text
hubo first push?
hubo first dip?
hubo rebreak?
hubo secuencia DAS?
que outcome tuvo despues?
```

Esas preguntas se calculan con la fuente 1m gobernada:

```text
E:/TSIS/data/ohlcv_1m
+
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
```

o con `master_intraday_bar_table_v0_2_candidate_quote_guarded` solo cuando esa tabla candidata haya sido materializada para el scope DAS requerido.

Datos que debe aportar o referenciar el denominador, cuando existan:

```text
ticker
instrument_id
session_date
scanner_profile
candidate_source
candidate_ts_utc / first_seen_ts_utc si existe
price_at_visibility / price_observable_at_visibility
session_volume_at_visibility / volume_so_far si existe
dollar_volume_at_visibility si existe
market_cap_usd o referencia as-of al market cap
float_shares si existe y esta gobernado
session_scope
visibility_reason
price_range_gate_state
volume_gate_state
market_cap_gate_state
quality_state
lineage / source_manifest
```

Para `SWEEP_001`, el denominador debe fijar el conjunto base de ticker/sesion donde se busca el patron DAS/frontside. Las semillas actuales vienen del uso humano:

```text
market_cap_usd < 100M
session_volume >= 500k
0.5 <= price <= 20
session_scope = premarket
```

Pero la lectura cientifica es:

```text
market_cap_usd < 100M = frontera dura del dominio DAS SmallCaps para este experimento
session_volume, price band y session_scope = semillas declaradas que pueden investigarse en sweeps posteriores
```

Si `daily_scanner_candidates_table_v0_2_or_successor` no tiene timestamp intradia real, debe marcarse explicitamente:

```text
denominator_timestamp_precision = session_level_or_daily_only
```

En ese caso puede usarse como denominador ticker/session, pero no como evidencia intradia as-of. Si el experimento necesita `first_visible_ts`, el executor debe generarlo desde reglas intradia gobernadas o marcarlo como missing.

Regla:

```text
El run visual DAS existente NO es denominador poblacional.
```

Puede usarse como:

```text
shape reference
casebook humano
validacion visual del detector
```

No puede usarse como:

```text
poblacion completa
base estadistica final
prueba de edge
```

### 4.4. Inputs De Estado / Outcome Existentes

En v0.1 pueden existir como fixtures controlados:

```text
market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
```

Lectura:

```text
sirven para validar contratos y forma de X/y
no son full universe
no habilitan ML/RL/AlphaEvolve
```

## 5. Preflight Obligatorio

Antes de ejecutar `SWEEP_001`, el executor debe generar un preflight report.

Checks minimos:

```text
1. existen experiment.yaml, parameter_space.yaml y sweep yaml
2. los YAML parsean correctamente
3. el sweep pertenece al experiment_id correcto
4. el output_root se puede resolver
5. existe fuente intradia gobernada o queda marcada como missing
6. existe denominador poblacional o queda marcado como blocker
7. se declara que el run visual DAS no es poblacion
8. se declara price_view usado
9. se declara timezone/session calendar usado
10. se declara referencia de precio para trigger
11. se declara cutoff de cada objeto
12. se declara separacion X/y
13. se declaran baselines
14. se declaran gates de leakage/calidad/lineage
15. se declara renderer visual DAS usado para inspeccion
16. se declara disponibilidad de export PNG/kaleido o bloqueo equivalente
```

Estados permitidos del preflight:

```text
passed
passed_with_warnings
blocked_missing_population_denominator
blocked_missing_intraday_source
blocked_invalid_config
```

## 6. Como Se Detecta Cada Candidato Del Sweep

Para cada threshold de `momentum_trigger_pct`:

```text
[20, 30, 40, 50, 60, 75, 100, 150]
```

El executor debe calcular:

```text
momentum_trigger_ts = primer timestamp donde high_1m >= premarket_open * (1 + threshold_pct / 100)
```

Condiciones:

```text
solo barras 1m cerradas
solo datos <= timestamp evaluado
price_view declarado
session_scope = premarket en SWEEP_001
max_market_cap_usd < 100M como frontera de dominio
min_session_volume = 500k fijo en SWEEP_001
0.5 <= price <= 20 fijo en SWEEP_001
```

Los thresholds bajo 50% deben etiquetarse como:

```text
operability_bucket = control_below_operability
```

No deben etiquetarse como setups long DAS.

## 7. Embudo Que Debe Medirse

La metrica principal no es solo retorno final.

El executor debe medir el embudo:

```text
scanner seed
-> momentum trigger
-> first push
-> first dip
-> structural rebreak
-> DAS sequence
-> continuation/failure
```

Cada etapa debe tener conteo y ratio de attrition.

### 7.1. Funnel Metrics

```text
scanner_seed_count
momentum_trigger_count
first_push_detected_count
first_push_detected_rate
first_dip_detected_count
first_dip_detected_rate
rebreak_confirmed_count
rebreak_confirmed_rate
das_sequence_confirmed_count
das_sequence_confirmed_rate
attrition_between_scanner_and_momentum
attrition_between_momentum_and_first_push
attrition_between_first_push_and_first_dip
attrition_between_first_dip_and_rebreak
attrition_between_rebreak_and_das_sequence
```

### 7.2. Outcome Metrics Separados

```text
sample_size
coverage_ratio
missing_bar_ratio
structure_destroyed_rate
continuation_rate
failure_rate
MFE
MAE
return_30m
post_rebreak_MFE
post_rebreak_MAE
remaining_upside_after_rebreak
too_late_or_overextended_rate
```

### 7.3. Imagenes De Inspeccion Humana Obligatorias

Regla central:

```text
Toda senal que el sistema mide debe poder verse en una imagen de inspeccion humana.
```

Motivo:

```text
El funnel puede contar algo correcto en una tabla y aun asi estar midiendo mal el punto humano: first push, first dip, rebreak, DAS sequence, MFE o MAE.
```

Por eso, para cada ticker/session/candidate que contribuya a metricas del experimento, el executor debe producir una imagen de inspeccion. Si un ticker/session no llega a una etapa del funnel, la imagen debe mostrar hasta donde llego y marcar la etapa faltante en el manifest, no esconder el caso.

La imagen debe seguir la gramatica visual del casebook DAS existente, no una visualizacion nueva.

Fuentes de verdad visual actuales:

```text
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/_shared/strategy_widgets_common.py
C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py
```

Reglas que deben preservarse desde `strategy_widgets_common.py`:

```text
1m candles:
  green = rgb(16,185,129) / rgba(16,185,129,0.65)
  red   = rgb(239,68,68) / rgba(239,68,68,0.65)

1m volume panel:
  green = rgba(16,185,129,0.75)
  red   = rgba(239,68,68,0.75)

VWAP:
  color = rgb(37,99,235)
  width = 1.4
  source = calculated o raw, siempre declarado
  calculated = cumulative ((high + low + close) / 3 * volume) / cumulative volume
  raw = columna px_vw cuando existe y es > 0

EMA/Wilder:
  EMA8 y Wilder8 calculados sobre close 1m
  bullish = verde, banda rgba(16,185,129,0.18)
  bearish = rojo, banda rgba(239,68,68,0.16)
  EMA8 width = 1.2
  Wilder8 width = 1.9

fondos de sesion:
  premarket = rgba(255,174,66,0.25)
  afterhours = rgba(90,140,255,0.16)

x-axis:
  New York time
  observed 1m bars
  non-trading gaps compressed
```

Reglas que deben preservarse desde `das_widgets.py`:

```text
chart base = make_das_chart
ventana principal = event-day 03:30-10:00 NY detail
export historico = 03_event_day_premarket_detail.png
tamano export = 1530x1530, scale=2
price panel domain = 0.22 a 1.00
volume panel domain = 0.00 a 0.20
price panel y volume panel separados
prior close visible
first push high como linea roja fina discontinua
PM open -> first push como linea fina con porcentaje
PM open -> extension high como linea fina con porcentaje
scanner trigger y momentum trigger con marcador circular y etiqueta compacta
```

La version de inspeccion del experimento debe mantener el grafico limpio, pero debe mostrar las mediciones que alimentan las metricas. Reglas de etiqueta:

```text
linea fina apuntando al inicio o punto exacto del calculo
una etiqueta compacta por calculo inicial o metrica clave
ninguna etiqueta debe solaparse con otra etiqueta
ninguna etiqueta debe tapar velas criticas si existe espacio alternativo
si no hay espacio, usar desplazamiento externo con flecha
la etiqueta debe mostrar el dato medido, no solo el nombre del evento
```

Senales minimas a etiquetar cuando existan:

```text
scanner_seed / first_visible point
momentum_trigger
first_push_start
first_push_high
first_dip_start
first_dip_low
rebreak_level
rebreak_confirmed_ts
DAS_sequence_confirmed_ts
outcome_window_start
outcome_window_end
MFE point
MAE point
failure_or_continuation point si aplica
```

Ejemplos de contenido de etiqueta:

```text
PM open +52.4%
Prior close +52.5%
$5.7000
vol 3k
momentum trigger

first push high
push = +140.6%

first dip low
dip = 11.5%

rebreak confirmed
rebreak_ts = 08:14 NY
```

Requisitos de trazabilidad visual:

```text
cada imagen debe tener visual_case_id
cada etiqueta debe tener label_id
cada label_id debe apuntar al campo medido en el manifest
cada label debe guardar timestamp, precio, metrica, formula_version, detector_version y source_row_id cuando exista
cada imagen debe enlazarse desde candidate_manifest o visual_inspection_manifest
cada PNG debe declarar renderer_source_path y renderer_source_hash
```

La inspeccion visual es un gate de calidad, no una feature de modelo:

```text
visual_label = evidencia humana/QC
visual_label != feature causal
visual_label != outcome
visual_label != training label
```

Si una metrica de funnel no puede representarse visualmente, el run debe marcar:

```text
visual_evidence_status = missing_or_incomplete
promotion_blocked = true
```

## 8. Como Sabe El Humano O AlphaEvolve Si Hay Mejora

En este experimento, evolucionar no significa maximizar un unico numero.

Una variante es mejor candidata solo si mejora evidencia sin romper gates.

Orden de lectura:

```text
1. pasa leakage/quality/lineage
2. tiene muestra suficiente
3. mantiene cobertura suficiente
4. bate baselines declarados
5. reduce attrition en el embudo DAS
6. deja upside despues del rebreak
7. no aumenta MAE de forma inaceptable
8. no aumenta sobreextension/llegada tarde
9. es estable por tiempo/regimen cuando exista esa particion
10. no exige complejidad injustificada
```

No hay ganador oficial en `SWEEP_001`.

Resultados permitidos:

```text
zone_rejected
zone_needs_followup
zone_candidate_for_next_sweep
zone_possible_overextension
insufficient_evidence
```

Resultados prohibidos:

```text
validated_event
validated_strategy
production_signal
alphaevolve_enabled
rl_ready
ml_ready
```

## 9. Baselines Minimos

El run debe comparar cada threshold contra:

```text
random_time_same_domain
scanner_seed_without_momentum_probe
gap_only
volume_only
time_of_day_baseline
```

Cada baseline debe compartir el mismo dominio y la misma politica de datos.

Si no puede calcularse un baseline, el run debe marcar:

```text
baseline_status = missing
promotion_blocked = true
```

## 10. Gates Anti-Basura

El executor debe rechazar o marcar como no promocionable cualquier variante que viole:

```text
no_future_state_features
no_outcomes_inside_X
no_post_event_window_as_feature
no_visual_label_as_model_feature
no_rebreak_as_feature_before_rebreak_timestamp
quote_guarded_lineage_required_for_candidate_execution
coverage_report_required
missingness_report_required
raw_to_consumption_lineage_required
visual_evidence_required_for_measured_signals
renderer_drift_requires_review
```

Reglas especificas DAS:

```text
no usar casebook positivo como poblacion
no tratar thresholds bajo 50% como setups long DAS
no tratar +50% como entrada
no seleccionar el mejor threshold como estrategia
no cambiar metricas despues de ver resultados
no promover sin follow-up sweeps
```

## 11. Output Root Y Estructura De Run

Output pesado esperado:

```text
E:/TSIS/data/research_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/runs/<run_id>/
```

Formato de `run_id`:

```text
RUN_YYYYMMDD_HHMMSSZ_SWEEP_001_frontside_operability_boundary
```

Estructura minima:

```text
resolved_config.yaml
run_manifest.json
input_lineage.json
candidate_manifest.parquet
sweep_cases.parquet
funnel_metrics.parquet
outcome_metrics.parquet
baseline_metrics.parquet
visual_inspection_manifest.parquet
visual_qc_report.md
visual_inspection/
  threshold=<threshold_pct>/
    images/
    labels/
validation_report.md
validation_report.json
evidence_report.md
promotion_recommendation.md
```

Artefactos ligeros opcionales dentro del experimento:

```text
reports/
manifests/
configs/
```

Pero la fuente de verdad del run debe ser el output root en `E:/TSIS/data/research_experiments`.

## 12. Memoria Del Experimento

Cada candidato/variante debe guardar como minimo:

```text
candidate_id
parent_experiment_id
sweep_id
threshold_pct
operability_bucket
resolved_config_hash
source_data_versions
code_version_or_executor_version
lineage_hash
sample_size
metrics_json
baseline_metrics_json
validation_status
promotion_status
created_at
```

Esta memoria sirve para que un humano o AlphaEvolve sepan:

```text
que se probo
con que datos
con que reglas
que fallo
que mejoro
que no puede promocionarse
que debe mutarse despues
```

## 13. Relacion Con AlphaEvolve

En v0.1:

```text
alphaevolve_enabled = false
optimizer_mutable = false
```

AlphaEvolve no puede ejecutar ni mutar este experimento hasta que existan:

```text
executor reproducible
preflight validator
run manifest
validation report
evidence report
promotion gates
candidate memory
```

Cuando se habilite, AlphaEvolve solo podra proponer cambios dentro de superficies declaradas:

```text
sampling_probe
parameter_grid
reference_price
window_definition
representation_builder_candidate
event_detector_candidate
```

No puede mutar:

```text
raw data
outcome truth
canonical state truth
leakage gates
quality gates
lineage history
promotion status
```

## 14. Escalado Del Experimento

Ruta correcta:

```text
1. config/preflight local
2. fixture controlado
3. sample reproducible
4. E-root scoped run
5. universo historico amplio
6. SWEEP_001 evidence report
7. follow-up sweeps
8. exploratory validation
9. candidate knowledge object si procede
10. locked validation solo despues
```

No se permite saltar de `SWEEP_001` a evaluador bloqueado.

## 15. Validacion Visual Ejecutable

Validador oficial inicial:

```text
C:/TSIS_Data/00_TSIS_Lab/06_validators/validate_visual_inspection_manifest.py
```

Uso esperado sobre un run:

```powershell
python C:/TSIS_Data/00_TSIS_Lab/06_validators/validate_visual_inspection_manifest.py `
  --run-dir <run_dir> `
  --write-report
```

Este validador exige:

```text
visual_inspection_manifest.parquet
label_id unico por etiqueta
signal_name por metrica medida
source_field que conecta etiqueta y dato medido
bbox/anchor en pixeles
imagenes existentes y no vacias
renderer_source_path + renderer_source_hash
no solape de labels dentro de la misma imagen
```

Resultado del smoke `XAGE 2025-04-14` despues de adaptar el exporter DAS:

```text
deteccion DAS = passed
export PNG = passed
visual_inspection_manifest label-level = generated
visual_contract_compliance = PASS
labels = 5
visual_cases = 1
images = 1
```

Lectura correcta:

```text
EXPORT_MANIFEST.csv no es suficiente.
El renderer debe producir evidencia visual label-level antes de promocionar el run experimental.
```

## 16. Estado Actual

```text
execution_protocol = definido
legacy_DAS_smoke_XAGE = passed
visual_manifest_validator = creado
visual_contract_compliance = PASS
executor = pendiente
preflight = pendiente
first_official_lab_run = pendiente
population_denominator = pendiente
alphaevolve = deshabilitado
promotion = bloqueada
```

Siguiente paso operativo:

```text
integrar esta salida visual label-level en el futuro executor oficial del Lab y extenderla desde el smoke XAGE a un sample multi-caso/multi-threshold
```

