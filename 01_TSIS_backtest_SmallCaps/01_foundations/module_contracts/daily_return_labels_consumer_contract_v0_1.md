# Daily Return Labels Consumer Contract `v0_1`

## 1. Rol

Este documento define el primer consumidor real recomendado para `daily_adjusted`.

No define todavia el modelo ML completo.

Define solo la capa de objetivo economico diario que usara ese modelo o research posterior.

## 2. Consumidor

Consumidor:

- generador de labels diarios de retorno

Clase de consumidor:

- `ml_primary`
- `research_only`
- y mas adelante `backtest_core` como soporte de evaluacion

## 3. Vista de precio obligatoria

La vista obligatoria para este consumidor es:

- `daily_adjusted`

Columna primaria:

- `c_adjusted`

No debe usar como columna primaria:

- `c` raw

## 4. Por que esta regla es obligatoria

Si el generador de labels trabaja sobre `c raw`:

- un split o reverse split puede parecer un retorno enorme;
- un dividendo puede parecer una caida economica falsa;
- y el objetivo de ML aprende corporate actions como si fueran alpha.

Por eso el objeto correcto para labels diarios es:

- el cambio economico entre cierres ajustados

no:

- el cambio mecanico entre cierres raw

## 5. Labels iniciales recomendados

La primera familia minima recomendada es:

- `ret_1d`
- `ret_3d`
- `ret_5d`

Definiciones:

- `ret_1d = c_adjusted[t+1] / c_adjusted[t] - 1`
- `ret_3d = c_adjusted[t+3] / c_adjusted[t] - 1`
- `ret_5d = c_adjusted[t+5] / c_adjusted[t] - 1`

## 6. Interpretacion correcta

Estos labels no representan:

- retorno realizado de la estrategia intradia
- ni calidad de ejecucion
- ni microestructura

Representan:

- retorno economico diario comparable del activo

## 7. Para que sirve este consumidor

Sirve para:

- research diario lento
- tareas ML que usen contexto diario
- filtros previos de direccion o regimen lento
- y evaluacion economica base

## 8. Para que no sirve

No sirve directamente para:

- decidir la entrada de un scalp en segundos
- medir slippage
- modelar cola de ejecucion
- modelar regime intradia fino desde tape

Es una capa lenta, no el motor del alpha intradia principal.

## 9. Condicion minima de implementacion

Para declarar este consumidor como conectado de verdad deben existir:

- una lectura real de `daily_adjusted`
- una generacion reproducible de `ret_1d`, `ret_3d`, `ret_5d`
- y una prueba explicita de que no trabaja sobre `c raw`

## 10. Estado actual del piloto

Esta condicion minima ya queda satisfecha a nivel de piloto semantico.

Evidencia:

- script operativo ejecutado:
  - `scripts/materialize_daily_return_labels.py`
- fuente usada:
  - `E:\TSIS\data\ohlcv_daily_adjusted`
- salida materializada:
  - `E:\TSIS\data\daily_return_labels`
- universo piloto:
  - `A`
  - `AAME`
  - `ABEO`
  - `ABIO`
  - `ABTX`
  - `BBW`
  - `CASS`
  - `CVLY`
  - `SELF`
  - `SGC`
- columnas verificadas en un parquet real:
  - `c_adjusted`
  - `ret_1d`
  - `ret_3d`
  - `ret_5d`
  - `label_source_view = daily_adjusted_v0_1`
  - `label_contract = daily_return_labels_consumer_contract_v0_1`

## 11. Veredicto final

Este consumidor es el primer aterrizaje correcto porque:

- usa exactamente la parte de `daily_adjusted` que mas importa validar;
- evita el error mas peligroso de semantica economica;
- y no obliga todavia a abrir toda la complejidad del backtest o del motor intradia principal.
