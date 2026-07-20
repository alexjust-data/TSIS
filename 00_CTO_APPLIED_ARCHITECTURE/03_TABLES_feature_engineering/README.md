# 03_TABLES_feature_engineering

Status: `readme_v0_3_operational_map`
Date: `2026-07-20`

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

## Estructura Activa

```text
03_TABLES_feature_engineering/
|
|-- 00_TABLES_MARKET_STATE_EVENT_STATE.md
|-- 01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
|-- 02_TABLE_REPRESENTATION_REVIEW/
|-- 03_INFORMATION_OBJECTS/
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
| `03_INFORMATION_OBJECTS/` | Guarda expedientes trazables de Objetos evaluados: candidatos, aceptados, aceptados con restricciones o rechazados. |
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

## Orden De Trabajo

```text
1. Revisar tablas existentes como tablas.
2. Identificar que informacion aportan.
3. Extraer candidatos a Objetos de Informacion.
4. Consolidar candidatos repetidos entre tablas.
5. Evaluar cada Objeto con 01_INFORMATION_OBJECT_ADMISSION_PROCESS.md.
6. Registrar cada expediente en 03_INFORMATION_OBJECTS.
7. Mapear Objeto -> variables -> tabla fuente.
8. Revisar si las tablas actuales bastan.
9. Modificar contratos, schemas y builders solo si el mapping lo exige.
10. Construir Market State.
11. Construir Event State.
```

Cadena logica:

```text
Tablas existentes
-> variables reales
-> Objetos de Informacion candidatos
-> Objetos admitidos
-> mapping operativo
-> tablas fuente ajustadas si hace falta
-> Market State
-> Event State
```

Market State no debe nacer de meter todas las columnas disponibles.
Debe nacer de Objetos de Informacion admitidos y legalmente observables en `decision_timestamp`.

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
