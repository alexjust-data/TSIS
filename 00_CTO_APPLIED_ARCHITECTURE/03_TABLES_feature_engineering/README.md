# 03_TABLES_feature_engineering

Status: `readme_v1_2_phase_b_core_four_materialization_authorization`
Date: `2026-07-22`

Esta seccion conecta tablas existentes, Objetos de Informacion, feature engineering, Market State, Event State, builders, validators y consumo downstream.

No es una autoridad operativa independiente.

La autoridad final vive en:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
G:\TSIS\data\data_foundation_outputs
builders
validators
manifests
tests
status matrices
```

---

## Pregunta Central

Todo trabajo en esta seccion debe responder:

```text
Que necesitamos saber
para describir correctamente
el estado del mercado
en un instante t?
```

Y tambien:

```text
Que informacion puede ayudar
a describir, explicar o investigar
el comportamiento futuro del mercado,
del instrumento o del contexto estudiado?
```

El objetivo no es acumular columnas.
El objetivo es admitir solo variables que representen informacion necesaria.

---

## TSIS Market Ontology v1 Freeze

```text
phase = TSIS Market Ontology Phase
status = CLOSED
ontology = TSIS Market Ontology v1
ontology_status = FROZEN
ontology_lock_status = LOCKED
phase_b_status = OPEN
phase_b_scope = governed_engineering
production_builder_development_authorized = false
state_consumption_authorized = false
```

El vertical de `Trading Activity` demostro el lifecycle completo, pero queda
clasificado como piloto de proceso. Operational Mapping y Builder Validation
design estan completos para los 12 Objetos de v1. Los gates experimentales de
contract, source binding, path, schema metadata, logical-to-physical binding,
bounded identity/temporal validation, bounded grain validation y bounded
quality/lineage validation, core-four builder execution, resolution record
acceptance, core-four integration design, core-four integration execution,
core-four materialization design y core-four materialization authorization
quedan cerrados o emitidos con restricciones.

El run vigente de integracion experimental es:

```text
experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z
```

Emitio 8 Market State candidate records no canonicos y rechazo 2 contextos
pre-bar bajo object atomicity.

El diseno vigente de materializacion es:

```text
core_four_market_state_materialization_design_v0_1
core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
```

La autorizacion experimental de materializacion core-four ya esta emitida con
restricciones para una futura ejecucion de maximo 8 filas candidatas. La
ejecucion, Market State parquet oficial, produccion y consumo downstream siguen
cerrados.

Regla:

```text
No production Market State Builder before governed Operational Mapping,
Builder Validation, Market State Integration and Operational Promotion gates.
```

---
## Estructura Activa

```text
03_TABLES_feature_engineering/
|
|-- 00_TABLES_MARKET_STATE_EVENT_STATE.md
|-- 01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
|-- 02_TABLE_REPRESENTATION_REVIEW/
|-- 03_INFORMATION_OBJECTS/
|-- 04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/
|-- 05_STATE_BUILDER_VALIDATION/
|-- 06_MARKET_STATE_INTEGRATION/
|-- 99_archive/
|-- CHANGELOG.md
`-- README.md
```

---

## Responsabilidad De Cada Parte

| Path | Funcion |
| --- | --- |
| `00_TABLES_MARKET_STATE_EVENT_STATE.md` | Explica por que existen Market State y Event State, y como consumen Objetos de Informacion. |
| `01_INFORMATION_OBJECT_ADMISSION_PROCESS.md` | Gobierna la admision de Objetos de Informacion como `Liquidity`, `Momentum` o `Trading Activity`. No audita tablas completas. |
| `02_TABLE_REPRESENTATION_REVIEW/` | Audita tablas completas `000-018`: responsabilidad, grano, frontera, atributos, faltantes, solapamientos y estado institucional. |
| `03_INFORMATION_OBJECTS/` | Guarda expedientes trazables de Objetos evaluados: candidatos, revisados, aceptados, aceptados con restricciones o rechazados. |
| `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/` | Phase B complete_for_v1. Puente gobernado: Objeto admitido -> modelos aprobados -> capacidades -> variables candidatas -> tablas fuente -> perfiles de State. |
| `05_STATE_BUILDER_VALIDATION/` | Builder Validation design completo para v1. El builder experimental core-four y la aceptacion de resolution records cerraron con restricciones. No autoriza builders de produccion, materializacion ni consumo State por si mismo. |
| `06_MARKET_STATE_INTEGRATION/` | Integracion core-four experimental, diseno de materializacion candidata y autorizacion acotada cerrados/emitidos con restricciones. Mantiene 8 candidatos JSONL no canonicos como input de una futura ejecucion candidata. No autoriza Market State oficial, consumo operativo ni promocion. |
| `99_archive/` | Documentos historicos, superseded o no activos. No son autoridad operativa. |

---

## Dos Procesos Distintos

### Revision De Tablas

Gobernada por:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
```

Pregunta principal:

```text
Que responsabilidad tiene esta tabla
dentro de la representacion de TSIS?
```

La revision de tabla determina:

```text
responsabilidad
grano
clave primaria
inputs
outputs
fronteras
informacion minima
atributos reales
columnas no justificadas
faltantes
solapamientos
legalidad temporal
estado fisico / contractual / validado / promovido
candidatos a Objetos de Informacion
```

### Admision De Objetos De Informacion

Gobernada por:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
```

Pregunta principal:

```text
Esta informacion merece formar parte
de la representacion del estado?
```

Ejemplos:

```text
Liquidity
Momentum
Trading Activity
News Context
Market Regime
```

La revision de tabla puede descubrir candidatos.
La admision de Objetos decide si esos candidatos existen institucionalmente.

---

## Definicion De Objeto De Informacion

```text
Objeto de Informacion
=
unidad semantica de informacion que TSIS decide preservar
sobre uno o varios fenomenos observables,
independiente de su Modelo de Representacion
y de su implementacion fisica.
```

Ejemplo:

```text
Liquidity
= Objeto de Informacion

coste de negociacion + profundidad + disponibilidad
= Modelo de Representacion

spread_bps + depth + quote_count
= implementacion fisica / variables
```

Regla:

```text
El Objeto no es aun la representacion.
Es lo que debe ser representado.
```

---
## Taxonomias Separadas

No usar una unica columna llamada `family` para clasificar todo.
TSIS separa cuatro ejes:

| Eje | Pregunta | Ejemplos |
| --- | --- | --- |
| `information_object_family` | Que significado semantico tiene el Objeto? | `Price Dynamics`, `Trading Activity`, `Liquidity`, `Market Microstructure`, `Instrument Context`, `External Context`, `Market Context` |
| `source_domain` | De que fuente observable procede la evidencia? | `OHLCV`, `Trades`, `Quotes`, `News`, `Fundamentals`, `SEC`, `Short`, `Halts`, `Reference` |
| `temporal_resolution` | En que escala o ventana aplica? | `daily`, `intraday_bar`, `second`, `event_window`, `as_of` |
| `institutional_role` | Que papel cumple dentro de TSIS? | `observable`, `quality`, `lineage`, `governance`, `outcome` |

Regla:

```text
Information Object Family es solo semantica.
Feature Family, source family, dataset family, event family,
quality family u outcome family no deben mezclarse en el mismo campo.
```


## Object Discovery vs Object Admission

Hay dos direcciones validas, pero no tienen la misma autoridad.

### Object Discovery Process

Puede empezar desde abajo o desde cualquier evidencia disponible:

```text
tablas existentes
-> variables reales
-> capacidades derivables
-> posibles significados
-> Objeto de Informacion candidato
```

Sirve para descubrir candidatos.
No admite Objetos.
No autoriza variables para Market State.
No convierte una tabla existente en significado cientifico oficial.

### Object Admission Process

Siempre debe seguir la direccion cientifica:

```text
fenomeno o necesidad cientifica
-> Objeto de Informacion
-> Modelo de Representacion
-> implementacion fisica candidata
-> legalidad temporal
-> decision de admision
```

Sirve para decidir si el Objeto merece existir institucionalmente.
Solo despues de esta decision puede cerrarse un mapping operativo hacia variables, tablas fuente y State.

Regla:

```text
Las tablas pueden descubrir candidatos.
La admision define el significado.
```

---

## Orden De Trabajo

```text
Phase A cerrada:
    pasos 1-7 completados para los 12 Information Objects principales,
    seguidos de revision transversal y ontology freeze.

Phase B abierta:
    pasos 8-9 ya cubren Operational Mapping y Builder Validation design
    para los 12 Objetos de v1; el builder experimental ya paso contract,
    source binding, path, schema metadata, logical-to-physical binding,
    bounded identity/temporal validation, bounded grain validation y bounded
    quality/lineage validation, core-four builder execution, acceptance review,
    integration design y integration execution con restricciones. El siguiente
    gate posible es `core_four_market_state_materialization_design`, todavia
    sin materializacion parquet ni consumo operativo.
```
```text
1. Revisar tablas existentes como tablas.
2. Identificar que informacion aportan.
3. Extraer candidatos a Objetos de Informacion.
4. Consolidar candidatos repetidos entre tablas.
5. Definir dominio, landscape y candidate object.
6. Revisar adversarialmente el candidato en object_admission_review.
7. Emitir Formal Admission en ACCEPTED / ACCEPTED_WITH_RESTRICTIONS / REJECTED.
8. Mapear Objeto -> modelos -> capacidades -> variables -> tablas -> perfiles de State.
9. Validar que el builder puede resolver el Objeto legalmente.
10. Disenar integracion en Market State.
11. Promover contratos, schemas o builders solo desde la autoridad operativa correspondiente.
12. Construir Event State reutilizando Market State cuando proceda.
```

Cadena logica:

```text
Tablas existentes
-> variables reales
-> Objetos de Informacion candidatos
-> Object Admission Review
-> Formal Admission
-> Operational Mapping
-> Builder Validation
-> Market State Integration
-> promocion operativa si procede
-> Event State
```

Market State no debe nacer de meter todas las columnas disponibles.
Debe nacer de Objetos de Informacion admitidos y legalmente observables en `decision_timestamp`.

## Event State: Rol Temporal Y Legalidad De Consumo

`Event State` usa dos clasificaciones independientes:

```text
state_role
= pre_event | at_event | post_event/post_event_review

consumption_legality
= decision_safe | research_only | outcome_adjacent | prohibited_as_input
```

`post_event` puede existir para investigacion, pero no puede alimentar X predictivo para una decision anterior o tomada en el evento.


## Market State No Es Mega-Tabla

`Market State` debe construirse desde Objetos de Informacion admitidos, pero eso no implica una unica tabla fisica con todos los atributos posibles.

Regla:

```text
canonicalidad
= misma semantica de estado
+ mismo identificador logico
+ reglas temporales comunes
+ perfiles fisicos compatibles

materializacion
= que perfil se construye,
con que cobertura,
resolucion y extension.
```

Perfiles fisicos permitidos conceptualmente:

```text
market_state_core
market_state_daily_context
market_state_intraday
market_state_microstructure_extension
market_state_news_extension
```

Llaves comunes obligatorias entre perfiles:

```text
market_state_id
instrument_id
decision_timestamp
representation_profile_version
```

Regla anti-ruido:

```text
Ningun consumidor justifica por si solo agrandar el Market State canonico.
Si un consumidor necesita informacion pesada o especializada, debe declararse
un perfil/extensibilidad gobernada, no inflar el core universal.
```


---

## Revision De Tablas 000-018

Las carpetas `000-018` viven bajo:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW
```

No son Objetos de Informacion.
Son expedientes tecnicos y auditorias de tablas/salidas.

Su finalidad es determinar:

```text
responsabilidad de la tabla
grano
fronteras
informacion minima
atributos fisicos
candidatos a Objetos de Informacion
redundancias
faltantes
estado institucional
```

| Carpeta | Tabla / salida | Lectura correcta |
| --- | --- | --- |
| `000_instrument_master` | `instrument_master_v0_1` | Identidad/universo de instrumentos. |
| `001_market_calendar` | `market_calendar_v0_1` | Infraestructura temporal canonica. No representa liquidez, momentum o presion compradora. |
| `002_expected_data_calendar` | `expected_data_calendar_v0_1` | Denominador esperado de cobertura. |
| `003_dataset_certification_matrix` | `dataset_certification_matrix_v0_1` | Gobernanza/calidad. No representa un fenomeno de mercado. |
| `004_master_daily_table` | `master_daily_table_v0_1` | Contexto diario del instrumento para su scope declarado. |
| `005_corporate_actions_table` | `corporate_actions_table_v0_1` | Splits, dividendos y cambios de ticker. |
| `006_halts_table` | `halts_table_v0_1` | Halts/suspensions para su scope declarado. |
| `007_event_windows_table` | `event_windows_table_v0_1` | Ventanas de eventos gobernadas. |
| `008_outcomes_table` | `outcomes_table_v0_1` | Outcomes/labels posteriores. No debe alimentar X observable. |
| `009_fundamentals_asof_table` | `fundamentals_asof_table_v0_1` | Contexto fundamental point-in-time/as-of. |
| `010_news_context_table` | `news_context_table_v0_1` | Contexto de noticias con restricciones temporales. |
| `011_short_context_table` | `short_context_table_v0_1` | Short interest/short volume por fuente y lag. |
| `012_regime_context_table` | `regime_context_table_v0_1` | Contexto de regimen observable/as-of. |
| `013_ohlcv_1m_quote_guarded` | `ohlcv_1m_quote_guarded` | Overlay/view quote-guarded sobre raw 1m; no muta raw. |
| `014` | `master_intraday_bar_table` | Representacion intradia basada en barras. |
| `015` | `microstructure_features_table` | Representacion microestructural basada principalmente en trades, quotes y ventanas/timestamps gobernados. |
| `016` | `market_state_table` | Integracion legal en decision_timestamp. No asumir promovido. |
| `017` | `event_state_table` | Market State contextualizado respecto a evento. No asumir promovido. |
| `018` | `intraday_scanner_candidates_table` | Superficie de candidatos/scanners intradia cuando aplique legalmente. |

---

## Objetos De Informacion

Los expedientes viven en:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS
```

Estructura:

```text
03_INFORMATION_OBJECTS/
|-- CANDIDATES/
|-- ACCEPTED/
|-- ACCEPTED_WITH_RESTRICTIONS/
`-- REJECTED/
```

Regla:

```text
todo Objeto de Informacion formalmente evaluado
=
un expediente propio y trazable
```

Un Objeto rechazado tambien debe conservar ficha.

---

## Relacion Correcta 013-018

No debe leerse como una cadena lineal simple.

`014` y `015` son principalmente superficies hermanas.

```text
raw OHLCV 1m
+ 013 quote-guarded overlay
+ corporate actions
+ quality
        |
        v
014 master_intraday_bar_table
```

En paralelo:

```text
raw trades
+ raw quotes
+ eligibility policies
+ quality gates
+ decision timestamps / event windows
        |
        v
015 microstructure_features_table
```

Despues:

```text
000-015 contextos y observables
+ 018 scanner candidates cuando corresponda y sea temporalmente legal
        |
        v
016 market_state_table
```

Y:

```text
016 market_state_table
+ source events
+ 007 event_windows_table
        |
        v
017 event_state_table
```

`008 outcomes_table` permanece separado:

```text
008 outcomes_table
= resultados posteriores / labels / evaluacion
= no input observable directo de Market State
```

---

## Archive

Los documentos en:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\99_archive
```

son historicos, superseded o no activos.

No son autoridad activa.
Solo pueden reutilizarse mediante nueva revision y decision explicita de promocion.

---

## Regla De Consumo

Antes de consumir cualquier salida para research, backtest, ML/RL, Event State o Market State:

```text
leer contrato
leer schema
leer registry
leer consumption policy
leer validators
leer manifest/resumen fisico
confirmar status y scope
```

Nada en esta carpeta, por si solo, promueve una tabla.

---

## Raices Fisicas Relevantes

Raiz fisica verificada en esta instalacion:

```text
G:\TSIS\data\data_foundation_outputs
```

Algunos contratos historicos pueden referenciar:

```text
E:\TSIS\data
```

Antes de afirmar cobertura fisica, verificar la raiz efectiva de esta instalacion.
