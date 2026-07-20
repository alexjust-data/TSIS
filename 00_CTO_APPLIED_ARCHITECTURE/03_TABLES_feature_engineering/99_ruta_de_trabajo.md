Ahora mismo tienes **dos unidades de análisis diferentes** y no deben mezclarse:

```text
Objeto de Información
≠
Tabla
```

## 1. `01_FEATURE_ADMISION_PROCESS.md`

Este documento gobierna la admisión de una unidad conceptual:

```text
Liquidity
Momentum
Trading Activity
News Context
Market Regime
```

La pregunta que responde es:

```text
¿Esta información merece formar parte
de la representación del estado?
```

Su resultado puede ser:

```text
Objeto aceptado
Objeto aceptado con restricciones
Objeto pendiente
Objeto rechazado
```

Y solo después define:

```text
modelo de representación
variables
tablas donde se materializa
```

Por tanto, no debe utilizarse como plantilla para auditar una tabla completa.

---

## 2. `01_TABLE_REPRESENTATION_REVIEW`

Esta carpeta analiza una entidad física y arquitectónica completa:

```text
000_instrument_master
001_market_calendar
002_expected_data_calendar
...
```

La pregunta que responde es distinta:

```text
¿Qué responsabilidad tiene esta tabla
dentro de la representación de TSIS?
```

Y las seis preguntas de `LOCAL_RULES.md` tienen sentido para este nivel:

```text
1. ¿Qué fenómeno o representación queremos materializar?
2. ¿Por qué merece existir como entidad propia?
3. ¿Qué preguntas científicas debe responder?
4. ¿Qué otras representaciones la consumen?
5. ¿Qué información mínima necesita contener?
6. Ahora sí: ¿qué atributos debe tener?
```

Estas preguntas no están admitiendo directamente un Objeto de Información.

Están examinando si una **tabla completa** tiene:

* una responsabilidad propia;
* un grano propio;
* una frontera correcta;
* información mínima suficiente;
* atributos coherentes con esa responsabilidad.

# La relación correcta entre ambos procesos

No son procesos competidores.  
Uno está dentro del otro:

```text
REVISIÓN DE UNA TABLA
↓
identifica las clases de información presentes
↓
detecta posibles Objetos de Información
↓
cada Objeto candidato pasa por
01_FEATURE_ADMISION_PROCESS.md
↓
los Objetos aceptados se asignan a variables
↓
se decide qué variables deben permanecer en la tabla
```

Ejemplo:

```text
004_master_daily_table
```

La revisión de tabla puede concluir:

```text
Responsabilidad:
preservar contexto diario point-in-time del instrumento.
```

Dentro de sus columnas aparecen posibles representaciones:

```text
gap_percent
daily_range
dollar_volume
rvol_20d
transaction_count
```

Estas columnas sugieren candidatos:

```text
Overnight Dislocation
Daily Volatility
Trading Activity
Liquidity Context
```

Pero la revisión de `004` no debería declarar automáticamente que esos cuatro Objetos están aceptados.

Cada candidato debe pasar posteriormente por:

```text
01_FEATURE_ADMISION_PROCESS.md
```



# Flujo de trabajo recomendado

Yo no modificaría aún las tablas.

Primero haría este proceso:

```text
FASE 1
Cerrar la plantilla de revisión de tablas
en LOCAL_RULES.md
```

Debe quedar estable antes de seguir auditando, porque si la plantilla cambia continuamente, las auditorías `000–012` dejarán de ser comparables.

```text
FASE 2
Revisar las auditorías ya realizadas de 000–012
contra la plantilla cerrada
```

No significa rehacerlas todas desde cero. Significa comprobar:

* si responden las seis preguntas;
* si distinguen responsabilidad de variables;
* si separan Objetos de infraestructura;
* si identifican atributos injustificados;
* si registran faltantes y solapamientos.

```text
FASE 3
Crear un inventario de candidatos a Objetos
extraídos de todas las tablas
```

Ejemplo:

```text
Liquidity
aparece potencialmente en:
004
014
015

Trading Activity
aparece potencialmente en:
004
014
015

Temporal Context
aparece en:
001
007
012
014
```

Esto evita crear varios Objetos con nombres distintos para la misma información.

```text
FASE 4
Aplicar 01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
a cada candidato consolidado
```

No por tabla, sino por Objeto.

```text
FASE 5
Crear INFORMATION_OBJECTS/
solo con expedientes trazables
```

```text
03_INFORMATION_OBJECTS/
├── CANDIDATES/
├── ACCEPTED/
├── ACCEPTED_WITH_RESTRICTIONS/
└── REJECTED/
```

```text
FASE 6
Volver a las tablas
y cerrar el mapping definitivo
```

Por ejemplo:

```text
Liquidity
↓
modelo aprobado
↓
variables aprobadas
↓
004 aporta contexto diario
014 aporta actividad intradía
015 aporta coste y profundidad L1
```

```text
FASE 7
Modificar contratos, schemas y builders
solo después de cerrar el mapping
```


# Estructura que recomiendo

```text
03_TABLES_feature_engineering/
│
├── 00_TABLES_MARKET_STATE_EVENT_STATE.md
├── 01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
│
├── 02_TABLE_REPRESENTATION_REVIEW/
│   ├── LOCAL_RULES.md
│   ├── README.md
│   ├── 000_instrument_master/
│   ├── 001_market_calendar/
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

# Conclusión

Tu estructura de pensamiento 

```text
LOCAL_RULES
gobierna la revisión de tablas completas.

01_INFORMATION_OBJECT_ADMISSION_PROCESS
gobierna la admisión de Objetos de Información.

Las revisiones de tablas descubren candidatos.

El proceso de admisión decide cuáles existen.

Los Objetos aceptados determinan después
qué variables y tablas forman Market State.
```

No reemplazaría ahora las auditorías `000–012` por fichas de Objetos. Primero hay que terminar de revisar las tablas como tablas. Después se extraen y consolidan los Objetos candidatos. Ese orden evita rediseñar las tablas a partir de intuiciones y evita también admitir el mismo Objeto varias veces con nombres distintos.
