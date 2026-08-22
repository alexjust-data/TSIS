# 03_TSIS_Lab

Fecha: 2026-07-05
Estado: skeleton operativo inicial

## Rol

`03_TSIS_Lab` es el laboratorio operativo central de TSIS.

No es el CTO, no es el modulo SmallCaps y no es un repositorio de outputs pesados.

Su funcion es organizar experimentos cientificos reproducibles que puedan ser propuestos por:

```text
human_researcher
alphaevolve_or_optimizer
future_research_agent
```

Todos deben usar la misma estructura:

```text
Research Question
-> Research Experiment
-> Execution
-> Evidence
-> Scientific Validation
-> Knowledge Object
-> Validated Knowledge
-> Operational Component
```

## Separacion De Responsabilidades

```text
C:/TSIS_Data/00_CTO
= filosofia, arquitectura, autoridad, reglas y mapas

C:/TSIS_Data/03_TSIS_Lab
= contratos operativos, registros, templates y experimentos reproducibles

C:/TSIS_Data/01_TSIS_DATA_FOUNDATION
= modulo operativo SmallCaps: foundations, builders, investigacion, event discovery, feature engine, backtests clasicos, strategy research y datos gobernados

G:/TSIS/data
= outputs pesados, materializaciones y runs voluminosos
```

## Regla Central

El corazon de TSIS no es AlphaEvolve.

El corazon de TSIS es:

```text
Scientific Validation Pipeline
```

AlphaEvolve, un humano u otro generador solo pueden proponer candidatos. La aceptacion del conocimiento la decide la validacion cientifica versionada.


## Regla Local Obligatoria

Antes de trabajar con experimentos, charts, eventos o estados que consuman velas 1m, todo agente debe leer:

```text
LOCAL_RULES.md
```

Regla corta: `ohlcv_1m` raw no es verdad visual ni estado oficial por si solo. Toda vela 1m usada en el Lab debe declarar vista, repair/guard state, lineage y guard de escala raw/quotes cuando aplique.

## Carpetas

```text
01_contracts/
  contratos operativos del laboratorio

02_registries/
  registros humanos de experimentos y knowledge objects

03_templates/
  plantillas YAML/Markdown para experiments, sweeps y evidencia

04_experiments/
  experimentos concretos, versionados y reproducibles

05_adapters/
  puentes tecnicos hacia modulos concretos como SmallCaps; no sustituyen esos modulos

06_validators/
  validadores ejecutables de evidencia, calidad, leakage, lineage y trazabilidad visual
```

## No-Goals

Esta carpeta no debe contener:

```text
raw data
parquet pesados
modelos entrenados pesados
backtests clasicos aislados
estrategias discrecionales como verdad
outputs sin manifest
```

## Experimento Activo Inicial

### EXP_DAS_FRONTSIDE_DISCOVERY_0001

```text
04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001
```

Objetivo: convertir la observacion visual humana DAS/frontside en un experimento reproducible con `research_design.md`, `parameter_space.yaml` y sweeps por capas.

Lectura correcta:

```text
DAS/frontside = experimento strategy-seeded
+50% = sampling probe humano investigable
first push -> dip -> rebreak -> DAS sequence = gramatica de objetos medibles
```


### EXP_DAS_FRONTSIDE_DISCOVERY_0002

```text
04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0002
```

Objetivo: medir por poblacion completa de scanner por que algunos tickers recuperan el primer dip y otros se destruyen, y descubrir zonas de threshold/filtros con coste de oportunidad controlado.

Lectura correcta:

```text
0001 = anchors visuales y gramatica DAS/frontside
0002 = estadistica de recovery/destruction, threshold sensitivity y oportunidad antes/despues de rebreak
```

## Experimentos Archivados

### EXP_INTRADAY_MOMENTUM_EXTENSION_0001

```text
04_experiments/_archive/superseded_2026_07_05/EXP_INTRADAY_MOMENTUM_EXTENSION_0001
```

Lectura: semilla generica inicial superseded por `EXP_DAS_FRONTSIDE_DISCOVERY_0001` para la ruta operativa actual. El concepto `intraday_momentum_extension` puede seguir existiendo como familia generica futura, pero no es el experimento activo que vamos a ejecutar ahora.

## Wake-up RTH oracle calibration

### EXP_WAKE_UP_RTH_ORACLE_CALIBRATION_0001

```text
role
=
binding-neutral development-only oracle calibration

population
=
2,400 frozen TA-3 development instrument-sessions

status
=
full candidate run complete; blind-panel repair probe PASS;
full panel rebuild pending human launch
```

This experiment builds a stratified blind candidate/control panel, a
price-path-free gallery, independent review/adjudication artifacts and evidence
for WUL-D01..D08. The candidate run completed 2,400/2,400; its initial blind
panel was invalidated because all 240 cases fell in the close RTH bucket. The
repair probe passed 25/25 and the full panel-only rebuild remains human-owned.
It does not freeze D07 automatically, read temporal validation/final OOS,
implement Binding B or authorize A/B comparison.

