# Data Storage Topology and Target State - Modulo 01

## 1. Rol del documento

Este documento fija la topologia general de almacenamiento de datos del modulo y el estado objetivo de convergencia operativa.

Su funcion es evitar tres errores:

- confundir fuentes primarias con materializaciones operativas;
- asumir que todo lo que existe en `C:\TSIS_Data\data`, `D:\` y `E:\TSIS\data`
  cumple el mismo rol;
- mezclar outputs de tests con raw data o tablas institucionales;
- y dejar a humanos o agentes sin una lectura minima de donde estan los datos, que semantica tienen y que capa deben consultar primero.

## 2. Principio rector

El proyecto no debe operar como una coleccion informal de carpetas.

Debe operar como una arquitectura con capas:

- capa de datos del proyecto;
- capa de materializacion operativa y staging;
- y capa institucional de contratos, consumo, validacion e inspeccion.

## 3. Topologia observada hoy

### 3.1 `C:\TSIS_Data\data`

Representa una capa legacy/historica de datos del proyecto.

No es la raiz objetivo para datos activos.
No es la raiz objetivo para outputs de tests.
No debe usarse para nuevas materializaciones institucionales.

Familias confirmadas:

- `additional`
- `quotes`
- `short`
- `trades_ticks_2019_2025`
- `trades_ticks_prod_2005_2026`
- `images`
- `short_review`

Lectura institucional:

- estas carpetas existen porque descargas, auditorias y builders historicos
  escribieron explicitamente contra `C:\TSIS_Data\data`;
- muchas evidencias, dossiers, registries y scripts antiguos todavia contienen
  referencias a esta raiz;
- por tanto no debe borrarse en bloque sin una auditoria de migracion;
- `additional`, `quotes`, `trades_ticks_*` y `short` pueden contener dato
  historico relevante, pero no son automaticamente la fuente activa preferida;
- `images` y `short_review` son capas auxiliares o documentales, no price views
  primarias.

Estado operativo:

```text
legacy / quarantine until migration audit
```

Regla:

```text
Ningun test nuevo debe escribir outputs bajo C:\TSIS_Data\data.
```

### 3.2 `D:\`

Representa hoy una capa muy utilizada de materializacion operativa y almacenamiento pesado.

Familias confirmadas:

- `ohlcv_daily`
- `ohlcv_1m`
- `quotes`
- `trades_ticks_prod_2005_2026`
- `Halts`
- `reference`
- `financial`
- `regime_indicators`

Lectura institucional:

- `D:\` no es una copia trivial;
- contiene materializaciones operativas y datasets de trabajo muy usados por research, inspeccion y builders.

Regla de convergencia:

```text
Todo raw/source-preserved relevante que permanezca bajo D:\ debe auditarse
contra su landing equivalente bajo E:\TSIS\data antes de considerar cerrada la
migracion fisica de datos.
```

El contrato operativo de esa auditoria vive en:

```text
01_foundations/module_contracts/transversal/raw_storage_parity_audit_requirement_v0_1.md
```

Esta regla aplica a todas las familias raw/source-preserved relevantes, no solo
a `quotes`.

### 3.3 `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION`

Representa la capa institucional del modulo.

Aqui viven:

- contratos
- politicas de consumo
- schemas
- validators
- dataset registry
- inspection dossiers
- scripts de builders e inspeccion

### 3.4 `E:\TSIS\data`

Representa el plano operativo activo preferido para datos actuales del modulo.

Lectura institucional:

- las familias raw/source-preserved viven en carpetas semanticas propias
  (`reference`, `ohlcv_daily`, `ohlcv_1m`, `quotes`,
  `trades_ticks_prod_2005_2026`, `Halts`, `additional`, etc.);
- los outputs derivados y gobernados de CAPA 1 deben agruparse bajo una raiz
  comun para no mezclarlos con raw/source folders.

Target state:

```text
E:\TSIS\data es la raiz operativa preferida.
D:\ puede existir como legacy/provenance/recovery mientras la auditoria de
paridad RAW no este cerrada.
```

Raiz comun para outputs de CAPA 1:

```text
E:\TSIS\data\data_foundation_outputs\
```

Layout objetivo:

```text
E:\TSIS\data\data_foundation_outputs\
  instrument_master\
  market_calendar\
  corporate_actions_table\
  dataset_certification_matrix\
  master_daily_table\
  master_intraday_bar_table\
  microstructure_features_table\
  real_time_corporate_event_alerts_table\
  halts_table\
  fundamentals_asof_table\
  news_context_table\
  short_context_table\
  regime_context_table\
  data_quality_report\
```

Regla:

```text
No crear outputs de CAPA 1 directamente como hermanos de raw/source folders si
pertenecen al conjunto de tablas gobernadas del contrato de outputs.
```

Excepcion:

```text
raw_alert_log y otros logs append-only de ingesta live no son tablas limpias de
Data Foundation. Deben vivir bajo una raiz separada de ingesta, por ejemplo:

E:\TSIS\data\live_ingestion\raw_alert_log\
```

### 3.5 `C:\TSIS_Data\tests`

Representa la raiz canonica para tests del monorepo y sus outputs.

No es raw data.
No es tabla institucional.
No es staging de datos productivos.

Rutas canonicas:

```text
C:\TSIS_Data\tests\test_runs\
C:\TSIS_Data\tests\fixtures\
C:\TSIS_Data\tests\third_party_evidence\
```

Lectura institucional:

- `test_runs` guarda ejecuciones fechadas con metadata;
- `fixtures` guarda muestras pequenas, sinteticas o congeladas;
- `third_party_evidence` guarda snapshots externos cacheados para tests
  independientes;
- los tests de modulo pueden vivir bajo el modulo, pero sus outputs raiz
  auditables deben poder enlazarse desde `C:\TSIS_Data\tests\test_runs`.

Regla:

```text
Los outputs de tests no deben escribirse en E:\TSIS\data ni en
C:\TSIS_Data\data.
```

## 4. Estado objetivo

La direccion operativa deseada del modulo es:

```text
unificar progresivamente la data activa en E:\TSIS\data
manteniendo en 01_foundations la semantica, el contrato y la gobernanza
```

Esto no significa:

- mover sin criterio toda carpeta a `E:\TSIS\data`;
- ni reescribir el lineage historico.

Significa:

- identificar que familias son activas;
- decidir que capa es fuente primaria y cual es materializacion;
- y converger hacia una disposicion donde la data de trabajo viva en un plano operativo claro.

## 5. Regla institucional de lectura para agentes

Todo agente que empiece a trabajar en el modulo debe asumir:

1. `01_foundations` contiene la verdad contractual e institucional;
2. `E:\TSIS\data` es el plano operativo activo preferido para datos actuales;
3. `C:\TSIS_Data\data` es legacy/quarantine hasta auditoria de migracion;
4. `C:\TSIS_Data\tests` es la raiz para outputs de tests, fixtures y evidencia
   externa cacheada;
5. `D:\` puede contener materializaciones historicas o staging que deben
   interpretarse segun contrato;
6. no debe asumirse que dos carpetas con nombres parecidos representan la misma vista semantica;
7. toda lectura seria de datos debe pasar por:
   - identificacion de familia;
   - identificacion de semantica;
   - y comprobacion de si el dato es fuente primaria, derivado o soporte.

## 6. Politica transitoria mientras exista multiple plano

Mientras convivan `C:\TSIS_Data\data`, `D:\` y `E:\TSIS\data`:

- debe dejarse explicitamente anotado en los documentos relevantes que plano se esta consumiendo;
- los builders y dossiers deben declarar la ruta o familia activa que usan;
- cualquier plan de unificacion futura debe preservar trazabilidad, no solo
  ahorrar espacio o simplificar paths;
- antes de borrar `C:\TSIS_Data\data`, debe existir una auditoria de migracion
  que confirme por familia:
  - existencia de contraparte en `E:\TSIS\data`;
  - conteos o hashes comparables;
  - scripts o dossiers todavia dependientes;
  - decision explicita para familias sin contraparte;
  - plan de reemplazo de rutas hardcodeadas;
  - copia de seguridad o ventana de rollback.

Decision actual:

```text
C:\TSIS_Data\data no se considera raiz valida para nuevos tests.
C:\TSIS_Data\data no debe borrarse en bloque hasta completar auditoria.
```

## 7. Relacion con otros documentos

Este documento debe leerse junto con:

- `price_semantics_and_adjustment_policy.md`
- `price_views_registry.md`
- `corporate_actions_adjustment_methodology.md`
- `event_families_and_reference_inventory.md`

## 8. Conclusion

La topologia de datos del modulo ya no puede tratarse como un detalle operativo.

Es una pieza de infraestructura.

La regla correcta es:

- entender primero donde vive cada familia;
- despues que semantica tiene;
- y solo entonces decidir como se consume, se valida o se promueve.
