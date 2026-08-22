# Wake-up RTH oracle calibration — proceso end-to-end v0.1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `wake_up_rth_oracle_calibration_end_to_end` |
| `document_version` | `v0_1` |
| `document_role` | `MASTER_EXECUTION_AND_HANDOFF_PLAN` |
| `document_status` | `FULL_CANDIDATES_COMPLETE_PANEL_REPAIR_PENDING_HUMAN_LAUNCH` |
| `experiment_id` | `EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001` |
| `scope` | `DEVELOPMENT_ONLY_LEGACY_RTH` |
| `created_at` | `2026-08-17` |

## 1. Objetivo

Convertir la definición científica de Wake-up en un oracle retrospectivo,
neutral respecto de Binding A y Binding B, capaz de identificar dentro de RTH:

```text
acción observada dormida después de las 09:30 ET
-> transición de Trading Activity dentro de RTH
-> corroboración retrospectiva suficiente
-> label de investigación independiente
```

Este trabajo no redefine Wake-up, no selecciona el Binding ganador, no crea
In-Play y no utiliza outcomes de estrategia.

## 2. Autoridades y separación de responsabilidades

Autoridad semántica:

```text
C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/
01_DEFINITION/01_WAKE_UP_EVENT_DEFINITION.md
```

Contrato de clases y decisiones abiertas:

```text
C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/
03_LABELS/WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md
```

Contrato de outputs futuros:

```text
C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/
03_LABELS/WAKE_UP_LABEL_AND_DENOMINATOR_MATERIALIZATION_CONTRACT_v0_1.md
```

Implementación experimental y reproducible:

```text
C:/TSIS_Data/03_TSIS_Lab/04_experiments/
EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001/
```

Outputs pesados y runs:

```text
G:/TSIS/data/research_experiments/
EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001/runs/<run_id>/
```

Los documentos de autoridad viven en Git. Los Parquet, imágenes, logs y
manifests de ejecución viven en `G:/TSIS/data`.

## 3. Población y datos exactos

La calibración utiliza exclusivamente los 2.400 contextos TA-3 development:

```text
G:/TSIS/data/DATA_FOUNDATION_OUTPUTS/
trading_activity_ta3_stratified_sample/
trading_activity_ta3_stratified_sample_v0_1_20260807T175808Z/
selected_target_contexts_v0_1.parquet

rows = 2,400
SHA-256 = 55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220
```

Manifest de población y lineage:

```text
sample_manifest_v0_2.json
selected_target_g_source_audit_v0_1.parquet
```

Fuente física de trades:

```text
source_id = trades_ticks_prod_2005_2026_legacy_rth
root = G:/TSIS/data/trades_ticks_prod_2005_2026
```

Calendario:

```text
G:/TSIS/data/data_foundation_outputs/market_calendar/
market_calendar_v0_1.parquet
```

Se heredan sin reinterpretación:

```text
trade eligibility policy;
condition policy matrix;
simulated latency = 1000 ms;
RTH coverage and missingness;
instrument-session identity;
official-G-only source authority;
proxy population restrictions.
```

Las 159 sesiones target sin fichero oficial G permanecen `UNAVAILABLE`. No se
eliminan del denominator ni se convierten en negativas.

## 4. Prohibiciones anti-circularidad

La búsqueda, el panel y los revisores no pueden utilizar:

```text
variables, percentiles, kernels o scores de Binding A;
variables, durations, kernels o scores de Binding B;
scanner +50 % o 500k;
rebreak, HOD o dirección del precio;
retornos futuros, PnL, MFE, MAE o fills;
resultados de temporal validation o final OOS.
```

Se permite únicamente evidencia neutral de actividad realizada:

```text
raw eligible trades;
timestamp clusters;
trade count;
share volume;
dollar volume;
distribución temporal;
contexto PIT previo independiente;
coverage, duplicados y calidad fuente.
```

## 5. Descubrimiento de alta sensibilidad

Se recorre el grid completo de segundos RTH de cada target. La búsqueda no
emite labels. Emite candidatos de alta sensibilidad mediante la unión de
configuraciones development-only:

```text
prior observed dormancy windows = 15m, 30m, 60m
retrospective confirmation horizons = 30s, 60s, 120s, 300s
relative anomaly = varios niveles amplios
corroboration companions = trade count + distinct clusters
                           + temporal dispersion + dollar volume
```

La selección inicial utiliza rankings y máximos locales de contrastes neutrales
de actividad. Es una reducción de carga, no el oracle. Un candidato no es un
positivo.

## 6. Controles y panel estratificado

El candidate generator no puede definir el denominator. Deben añadirse casos de
control extraídos del mismo grid elegible:

```text
intervalos completamente dormidos;
un único print o cluster;
actividad alta pero contextualmente normal;
actividad con corroboración insuficiente;
calidad degradada o artefactos;
intervalos aleatorios sin candidato.
```

El panel se estratifica, como mínimo, por:

```text
cohorte D1/D2/D3/D4;
hora RTH;
price band;
market-cap proxy band;
prior activity stratum;
source-quality state;
candidate morphology/control type.
```

Clases de revisión:

```text
POSITIVE_WAKE_UP
NEGATIVE_ONE_PRINT
NEGATIVE_INSUFFICIENT_CORROBORATION
NEGATIVE_CONTEXT_NORMAL_HIGH_ACTIVITY
NEGATIVE_DATA_ARTIFACT
AMBIGUOUS
UNAVAILABLE
```

## 7. Evidencia visual

El run genera una galería HTML local navegable:

```text
<run_root>/visuals/index.html
```

La vista de sesión completa muestra:

```text
09:30–16:00 ET;
trade count por segundo;
dollar volume por segundo;
distinct timestamp clusters por segundo;
candidatos y controles marcados;
franja de coverage/calidad.
```

La vista ampliada de cada candidato muestra:

```text
periodo previo observado;
intervalo candidato;
horizonte de corroboración;
event raster;
trade/cluster/dollar activity;
valores raw y reason codes necesarios para auditoría.
```

La galería primaria no muestra precio ni outcomes. Una visualización de precio
posterior podría existir como contexto separado después del freeze, pero no
puede participar en la adjudicación primaria de Trading Activity.

Cada imagen y página debe proceder de las mismas coordenadas y métricas que
figuran en el manifest visual. No se permiten marcas colocadas a ojo.

## 8. Revisión ciega

Dos revisores reciben `case_id` ciego y evidencia raw/quality. No reciben ticker
si la anonimización es compatible con la auditoría, identidad de Binding,
scores A/B ni outcomes económicos.

Cada revisor registra:

```text
reviewer_id;
case_id;
proposed_label_class;
onset interval, si es identificable;
confidence;
reason codes;
review timestamp;
protocol version.
```

Los desacuerdos pasan a adjudicación separada. `AMBIGUOUS` y `UNAVAILABLE` se
preservan y nunca se fuerzan a negativo.

## 9. Decisiones que debe resolver la calibración

```text
WUL-D01 = retrospective confirmation horizon
WUL-D02 = prior dormant-regime estimator/lookback
WUL-D03 = relative-anomaly rule
WUL-D04 = de-minimis economic floor
WUL-D05 = distinct timestamp cluster/source quorum
WUL-D06 = minimum source coverage/timestamp resolution
WUL-D07 = episode close, dormant reset and rearm
WUL-D08 = deterministic vs adjudicated primary oracle
```

Se buscará una región estable de parámetros respecto a acuerdo humano,
abstenciones, robustez por strata y sensibilidad. No se elegirá el punto que
mejor favorezca a A o B.

## 10. Outputs del run

```text
<run_root>/
  pre_manifest.json
  pid_manifest.json
  heartbeat_latest.json
  heartbeat_history.jsonl
  live.log
  session_metrics/
  candidate_shards/
  candidate_pool.parquet
  control_intervals.parquet
  blind_panel_manifest.parquet
  visuals/index.html
  visuals/full_sessions/
  visuals/candidate_zoom/
  reviewer_01_labels.parquet
  reviewer_02_labels.parquet
  adjudicated_labels.parquet
  calibration_grid_results.parquet
  decision_readout.json
  final_manifest.json
```

Los outputs de reviewer, adjudicación y calibración solo existirán cuando las
acciones humanas correspondientes hayan ocurrido. No se fabricarán para cerrar
un run automáticamente.

## 11. Secuencia end-to-end

```text
01 freeze RTH observation profile and calibration protocol
02 preflight 2,400 targets, hashes, source paths and disk
03 build complete eligible RTH symbol-second accounting
04 high-recall binding-neutral candidate discovery
05 add candidate-free controls and typed quality cases
06 deterministic stratified blind-panel selection
07 render full-session and candidate-zoom visual gallery
08 independent blind review by two reviewers
09 adjudicate disagreements
10 calibrate WUL-D01…D08 on development only
11 explicit human scientific freeze
12 materialize complete development labels and denominator
13 independent validation, hashes, leakage and class accounting
14 compare Binding A and Binding B under common detector protocol
```

## 12. Operaciones largas

El full scan cumple `LONG_RUNNING_OPERATIONS_CONTRACT.md`. Por tanto:

```text
agente prepara código, smoke, comando y monitor;
humano autoriza y lanza el full run;
run escribe pre-manifest antes del trabajo costoso;
heartbeat y monitor muestran sesiones procesadas y restantes;
resume valida hashes de config, código, población y policies;
final manifest distingue COMPLETE, FAILED y STOPPED.
```

## 13. Frontera OOS

Solo development puede calibrar el oracle:

```text
development = 2011-01-03 .. 2022-12-30
temporal validation = 2023-01-03 .. 2024-12-31
engineering-exposed embargo = 2025-01-02 .. 2025-03-14
final test = 2025-03-17 .. 2026-03-09
```

Las imágenes ya observadas de 2024–2026 pueden conservarse como ilustraciones
que motivaron la ontología, pero quedan prohibidas para calibrar thresholds,
escoger WUL-D01…D08 o decidir qué Binding gana.

## 14. Condición de cierre

El proceso no está completo cuando aparece una galería. Está completo únicamente
cuando existen:

```text
code and config hashes;
bounded production-equivalent probe PASS;
candidate and control accounting;
blind review and adjudication evidence;
WUL-D01…D08 frozen by explicit human gate;
development label/denominator manifests;
independent validator PASS;
no validation/final-OOS reads;
final manifest and handoff.
```

Hasta ese momento el estado correcto es:

```text
RESEARCH_EXPERIMENT_IN_PROGRESS
LABEL_AUTHORITY_NOT_YET_FROZEN
A_B_COMPARISON_NOT_AUTHORIZED
```

## 19. Estado implementado a 2026-08-17

```text
implementation and unit tests       = COMPLETE
production-equivalent probe D1..D4  = PASS
terminal probe validation           = 20/20 PASS
full preflight                      = PASS, 2,400 targets
full candidate run                  = COMPLETE 2,400/2,400; 4,447 candidates
initial blind panel                 = INVALID 240/240 CLOSE_240M_PLUS
repair probe                        = 25/25 PASS
next gate                           = HUMAN_LAUNCH_FULL_PANEL_REBUILD_ONLY
```

La evidencia exacta, los incidentes corregidos, los hashes congelados y los
comandos de lanzamiento, monitor y resume viven en:

```text
WAKE_UP_RTH_ORACLE_CALIBRATION_IMPLEMENTATION_AND_PROBE_READOUT_v0_1.md
```

El full candidate scan no se repite. La revisión ciega sigue bloqueada hasta
que el rebuild del panel pase. El incidente y el comando gobernado viven en:

```text
WAKE_UP_RTH_BLIND_PANEL_STRATIFICATION_INCIDENT_AND_REPAIR_READOUT_v0_1.md
```

El PASS del rebuild solo abre la revisión ciega; no congela WUL-D01..D08 ni
autoriza la comparación A/B.
