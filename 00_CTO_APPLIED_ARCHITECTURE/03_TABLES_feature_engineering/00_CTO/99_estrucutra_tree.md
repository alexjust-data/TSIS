Tienes razón. Mi propuesta anterior colocaba el centro conceptual en `OBJECTS/`, cuando **el trabajo inmediato de esta carpeta es revisar las tablas `000–018` que ya existen** bajo los dos documentos que acabáis de construir.

Los dos documentos superiores establecen el nuevo criterio:

* `00_TABLES_MARKET_STATE_EVENT_STATE.md` explica cómo las tablas y sus variables terminan construyendo `Market State` y `Event State`. 
* `01_FEATURE_ADMISION_PROCESS.md` decide qué Objetos de Información y qué representaciones merecen ser admitidos. 

Las carpetas `000–018` son **el material heredado que ahora debe ser auditado con ese criterio**. No son todavía una biblioteca limpia de Objetos.

# La distinción correcta

```text
00 y 01
=
marco de revisión y gobierno

000–018
=
tablas existentes que deben revisarse

OBJECTS
=
Objetos de Información que han superado
el proceso de admisión
```

Por tanto, sí: yo metería `000–018` en una carpeta propia y dejaría `OBJECTS/` únicamente para los Objetos aceptados.

# Nombre de la carpeta de `000–018`

Mi opción preferida sería:

```text
02_TABLE_REPRESENTATION_REVIEW/
```

En español:

```text
02_REVISION_REPRESENTACION_TABLAS/
```

Pero, como el proyecto utiliza nombres técnicos en inglés, escogería:

```text
02_TABLE_REPRESENTATION_REVIEW/
```

Ese nombre expresa exactamente lo que ocurre:

> Revisar qué representa actualmente cada tabla, qué variables contiene, a qué Objetos podrían pertenecer, qué sobra, qué falta y qué debe modificarse.

No usaría:

```text
TABLES/
```

porque sería demasiado genérico.

Tampoco:

```text
TABLES_IMPLEMENTATION/
```

porque todavía no estás simplemente implementando: primero estás **revisando y rediseñando conceptualmente**.

Tampoco:

```text
TABLES_UNDER_REVIEW/
```

porque suena a estado temporal. `TABLE_REPRESENTATION_REVIEW` describe una función estable del proceso.

# Estructura que ahora sí veo correcta

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\
03_TABLES_feature_engineering\
│
├── 00_TABLES_MARKET_STATE_EVENT_STATE.md
├── 01_FEATURE_ADMISION_PROCESS.md
│
├── 02_TABLE_REPRESENTATION_REVIEW/
│   ├── README.md
│   │
│   ├── 000_instrument_master/
│   ├── 001_market_calendar/
│   ├── 002_expected_data_calendar/
│   ├── 003_dataset_certification_matrix/
│   ├── 004_master_daily_table/
│   ├── 005_corporate_actions_table/
│   ├── 006_halts_table/
│   ├── 007_event_windows_table/
│   ├── 008_outcomes_table/
│   ├── 009_fundamentals_asof_table/
│   ├── 010_news_context_table/
│   ├── 011_short_context_table/
│   ├── 012_regime_context_table/
│   ├── 013_ohlcv_1m_quote_guarded/
│   ├── 014_master_intraday_bar_table/
│   ├── 015_microstructure_features_table/
│   ├── 016_market_state_table/
│   ├── 017_event_state_table/
│   └── 018_intraday_scanner_candidates_table/
│
├── 03_INFORMATION_OBJECTS/
│   ├── README.md
│   ├── TEMPLATE.md
│   │
│   ├── ACCEPTED/
│   │   ├── liquidity.md
│   │   ├── momentum.md
│   │   └── ...
│   │
│   ├── ACCEPTED_WITH_RESTRICTIONS/
│   │   └── ...
│   │
│   ├── CANDIDATES/
│   │   └── ...
│   │
│   └── REJECTED/
│       └── ...
│
└── 90_ARCHIVE/
```

Aunque tú proponías `OBJECTS/`, yo usaría:

```text
03_INFORMATION_OBJECTS/
```

porque `OBJECTS` solo puede confundirse con objetos de software, artefactos o entidades generales. `INFORMATION_OBJECTS` conserva el significado científico exacto.

# Una corrección importante: no pondría solo lo válido en `OBJECTS/`

Entiendo tu idea:

```text
OBJECTS/
=
todo lo que demos por válido
```

Conceptualmente es correcta, pero operativamente conviene conservar también los candidatos y rechazos.

¿Por qué?

Porque durante la revisión de `000–018` aparecerán propuestas como:

```text
Liquidity
Momentum
Trading Activity
Price Position
Temporal Context
Data Quality
Market Regime
Buying Pressure
```

No todas estarán inmediatamente aceptadas.

Si solo guardas las aceptadas, perderás trazabilidad sobre:

* qué candidato se estudió;
* por qué se rechazó;
* qué evidencia faltaba;
* qué representación equivalente ya existía;
* cuándo debe revisarse.

Por eso haría:

```text
03_INFORMATION_OBJECTS/
├── ACCEPTED/
├── ACCEPTED_WITH_RESTRICTIONS/
├── CANDIDATES/
└── REJECTED/
```

La plantilla ya contempla exactamente esos estados. 

# El flujo real de trabajo

Ésta es la parte que aclara la confusión:

```text
TABLA EXISTENTE
↓
revisión de responsabilidad y columnas
↓
identificación de información representada
↓
propuesta de Objeto de Información candidato
↓
proceso de admisión
↓
Objeto aceptado o rechazado
↓
modelo de representación aprobado
↓
variables físicas aprobadas
↓
decisión sobre dónde deben materializarse
↓
corrección de la tabla
↓
integración posterior en Market State/Event State
```

Ejemplo con `004_master_daily_table`:

```text
004_master_daily_table
↓
contiene:
gap_percent
daily_volume
dollar_volume
rvol_20d
daily_range
...
↓
pregunta:
¿Qué información preservan realmente?
↓
candidatos:
Overnight Dislocation
Trading Activity
Liquidity Context
Daily Volatility
...
↓
cada candidato pasa por 01_FEATURE_ADMISION_PROCESS
↓
solo los aceptados entran en INFORMATION_OBJECTS/ACCEPTED
↓
se decide qué variables de 004 implementan cada modelo
↓
se revisa 004:
qué permanece
qué cambia
qué falta
qué sobra
```

Esto es distinto de empezar inventando Objetos en abstracto.

# No todas las tablas `000–018` producirán Objetos de Información

Ésta es otra distinción esencial.

Hay tablas con información económica del mercado:

```text
004 master_daily
009 fundamentals
010 news
011 short context
012 regime
014 intraday
015 microstructure
```

Estas sí pueden implementar Objetos como:

```text
Liquidity
Momentum
Trading Activity
News Context
Fundamental Context
Market Regime
```

Pero otras tablas cumplen funciones estructurales o de gobernanza:

```text
000 instrument_master
001 market_calendar
002 expected_data_calendar
003 dataset_certification_matrix
```

No todo lo que contienen debe convertirse en un Objeto de Información económico.

Por ejemplo:

```text
instrument_id
valid_from
valid_to
schema_version
certification_status
source_path
lineage_hash
```

son necesarios para construir y gobernar el estado, pero no necesariamente representan propiedades económicas del mercado.

Por eso la auditoría de cada tabla debe clasificar sus columnas al menos en:

```text
1. Información del mercado
   → puede implementar un Objeto de Información.

2. Identidad y claves
   → infraestructura de ensamblaje.

3. Legalidad temporal
   → control point-in-time/as-of.

4. Calidad y cobertura
   → gates y confianza.

5. Lineage y gobernanza
   → reproducibilidad institucional.

6. Outcomes o información futura
   → prohibida en Market State.
```

Esta clasificación evitará intentar convertir cada columna en un Objeto.

# Cómo organizaría cada carpeta de tabla

Dentro de cada `000–018` mantendría algo muy sencillo:

```text
004_master_daily_table/
│
├── 004_master_daily_table.md
├── REPRESENTATION_REVIEW.md
├── OBJECT_MAPPING.md
└── archive/
```

## Documento principal de la tabla

```text
004_master_daily_table.md
```

Describe el estado físico/documental actual:

* propósito;
* grano;
* claves;
* columnas;
* sources;
* builders;
* contratos;
* materialización;
* status.

## `REPRESENTATION_REVIEW.md`

Responde:

```text
¿Qué responsabilidad debería tener esta tabla?

¿Qué información económica representa?

¿Qué columnas son identidad, calidad, lineage o as-of?

¿Qué columnas son candidatas a representar Objetos?

¿Qué sobra?

¿Qué falta?

¿Qué viola la frontera de la tabla?
```

Aquí se consolidarían las actuales auditorías duplicadas.

## `OBJECT_MAPPING.md`

Este documento sería el puente entre la tabla y los Objetos:

```text
Objeto aceptado:
Trading Activity

Modelo:
Daily activity relative to historical baseline

Variables implementadas aquí:
daily_volume
dollar_volume
rvol_20d

Estado:
accepted
```

Otro ejemplo:

```text
Objeto candidato:
Daily Liquidity Context

Variables candidatas:
dollar_volume
transaction_count

Estado:
pending admission

No autorizado todavía para Market State.
```

Así se conserva una separación limpia:

```text
La especificación del Objeto vive en INFORMATION_OBJECTS.

La tabla solo referencia qué parte de ese Objeto materializa.
```

# `016` y `017` necesitan un tratamiento distinto

`016_market_state_table` y `017_event_state_table` no son tablas fuente comunes.

Son tablas integradoras.

Su revisión debe ocurrir **después** de revisar suficientemente los Objetos y las tablas fuente.

Orden lógico:

```text
Primero:
000–015 y 018

Después:
Objetos admitidos y modelos aprobados

Después:
016 Market State

Finalmente:
017 Event State
```

Porque `016` debe saber:

```text
qué Objetos están aceptados;
qué modelos están vigentes;
qué variables los implementan;
en qué tablas viven;
qué legalidad temporal tienen.
```

Y `017` debe reutilizar `016` y añadir el contexto del evento. Eso ya queda definido en vuestro documento superior. 

# Orden práctico de revisión

Yo no revisaría estrictamente `000, 001, 002...` como una secuencia numérica ciega.

Lo haría en grupos:

## Grupo 1 — Infraestructura y legalidad

```text
000 instrument_master
001 market_calendar
002 expected_data_calendar
003 dataset_certification_matrix
005 corporate_actions
```

Pregunta:

```text
¿Qué infraestructura necesita cualquier representación válida?
```

## Grupo 2 — Contexto observable ya materializado

```text
004 master_daily
006 halts
009 fundamentals
010 news
011 short context
012 regime
```

Pregunta:

```text
¿Qué Objetos de Información ya están parcial
o completamente representados?
```

## Grupo 3 — Eventos y resultados

```text
007 event_windows
008 outcomes
018 scanner candidates
```

Pregunta:

```text
¿Qué es evento, selección y outcome?
¿Qué puede entrar en State y qué debe quedar separado?
```

## Grupo 4 — Intradía y microestructura

```text
013 quote-guarded
014 master intraday
015 microstructure
```

Pregunta:

```text
¿Qué Objetos faltan para representar correctamente
el mercado intradía y el tape?
```

## Grupo 5 — Integración

```text
016 market_state
017 event_state
```

Pregunta:

```text
¿Cómo integrar solamente Objetos admitidos
con legalidad temporal y sin duplicación?
```

# Estructura mínima que te recomiendo ahora

No necesitas crear diez capas nuevas. Puedes empezar con esto:

```text
03_TABLES_feature_engineering/
│
├── 00_TABLES_MARKET_STATE_EVENT_STATE.md
├── 01_FEATURE_ADMISION_PROCESS.md
│
├── 02_TABLE_REPRESENTATION_REVIEW/
│   ├── 000_instrument_master/
│   ├── ...
│   └── 018_intraday_scanner_candidates_table/
│
├── 03_INFORMATION_OBJECTS/
│   ├── README.md
│   ├── TEMPLATE.md
│   ├── CANDIDATES/
│   ├── ACCEPTED/
│   ├── ACCEPTED_WITH_RESTRICTIONS/
│   └── REJECTED/
│
└── 90_ARCHIVE/
```

Eso representa exactamente el trabajo actual:

```text
Revisamos las tablas existentes
↓
descubrimos candidatos a Objetos
↓
los evaluamos
↓
registramos los válidos
↓
rediseñamos las tablas
↓
construimos Market State/Event State
```

# Mi recomendación definitiva

Sí, mueve `000–018` a:

```text
02_TABLE_REPRESENTATION_REVIEW/
```

Crea:

```text
03_INFORMATION_OBJECTS/
```

Y no des por supuesto que los Objetos de ejemplo de los dos documentos ya están aprobados. Hasta completar su ficha y decisión formal, deberían vivir en:

```text
03_INFORMATION_OBJECTS/CANDIDATES/
```

La frase que ordena toda la carpeta es:

```text
00 y 01 gobiernan.

02 revisa lo que existe.

03 registra lo que se admite.

016 y 017 integran el resultado.
```

Ésa creo que es la organización que realmente corresponde al estado actual del proyecto.
