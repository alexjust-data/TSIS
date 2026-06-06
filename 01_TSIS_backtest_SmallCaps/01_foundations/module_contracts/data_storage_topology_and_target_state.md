# Data Storage Topology and Target State - Modulo 01

## 1. Rol del documento

Este documento fija la topologia general de almacenamiento de datos del modulo y el estado objetivo de convergencia operativa.

Su funcion es evitar tres errores:

- confundir fuentes primarias con materializaciones operativas;
- asumir que todo lo que existe en `C:\TSIS_Data\data` y `D:\` cumple el mismo rol;
- y dejar a humanos o agentes sin una lectura minima de donde estan los datos, que semantica tienen y que capa deben consultar primero.

## 2. Principio rector

El proyecto no debe operar como una coleccion informal de carpetas.

Debe operar como una arquitectura con capas:

- capa de datos del proyecto;
- capa de materializacion operativa y staging;
- y capa institucional de contratos, consumo, validacion e inspeccion.

## 3. Topologia observada hoy

### 3.1 `C:\TSIS_Data\data`

Representa una capa estructural del proyecto con familias de datos activas y de soporte.

Familias confirmadas:

- `additional`
- `quotes`
- `short`
- `trades_ticks_2019_2025`
- `trades_ticks_prod_2005_2026`
- `images`
- `short_review`

Lectura institucional:

- `additional`, `quotes`, `trades_ticks_*` y `short` son familias de dato relevantes;
- `images` y `short_review` son capas auxiliares o documentales, no price views primarias.

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

### 3.3 `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Representa la capa institucional del modulo.

Aqui viven:

- contratos
- politicas de consumo
- schemas
- validators
- dataset registry
- inspection dossiers
- scripts de builders e inspeccion

## 4. Estado objetivo

La direccion operativa deseada del modulo es:

```text
unificar progresivamente la data activa en D:\
manteniendo en 01_foundations la semantica, el contrato y la gobernanza
```

Esto no significa:

- mover sin criterio toda carpeta a `D:\`;
- ni reescribir el lineage historico.

Significa:

- identificar que familias son activas;
- decidir que capa es fuente primaria y cual es materializacion;
- y converger hacia una disposicion donde la data de trabajo viva en un plano operativo claro.

## 5. Regla institucional de lectura para agentes

Todo agente que empiece a trabajar en el modulo debe asumir:

1. `01_foundations` contiene la verdad contractual e institucional;
2. `C:\TSIS_Data\data` y `D:\` contienen datos y materializaciones que deben interpretarse segun su rol;
3. no debe asumirse que dos carpetas con nombres parecidos representan la misma vista semantica;
4. toda lectura seria de datos debe pasar por:
   - identificacion de familia;
   - identificacion de semantica;
   - y comprobacion de si el dato es fuente primaria, derivado o soporte.

## 6. Politica transitoria mientras exista doble plano

Mientras convivan `C:\TSIS_Data\data` y `D:\`:

- debe dejarse explicitamente anotado en los documentos relevantes que plano se esta consumiendo;
- los builders y dossiers deben declarar la ruta o familia activa que usan;
- y cualquier plan de unificacion futura debe preservar trazabilidad, no solo ahorrar espacio o simplificar paths.

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
