# Market Session Scope

## 1. Rol

Este documento fija el alcance canonico de sesion para los datasets de market data del modulo `01_TSIS_backtest_SmallCaps`.

Su funcion es dejar explicito:

- que tramo horario debe considerarse sesion operativa objetivo;
- para que bloques aplica;
- como debe leerse la diferencia entre sesion objetivo y material realmente observado;
- y donde quedan abiertas las excepciones o limitaciones por bloque.

No sustituye contratos de dataset concretos.
Los gobierna horizontalmente.

## 2. Regla canonica

Para market data intradia y agregados operativos de mercado, la sesion institucional objetivo del modulo es:

- `premarket -> regular -> afterhours`

Traducido a semantica operativa US equities:

- `04:00-20:00 America/New_York`

Esta regla debe entenderse como alcance objetivo de observacion y no como afirmacion automatica de que todos los datasets materializados ya cumplan perfectamente ese alcance en todos los bloques.

## 3. Bloques a los que aplica

Esta regla aplica, como minimo, a:

- `quotes`
- `trades`
- `ohlcv_1m`

Y condiciona la lectura operativa de:

- `daily`

en la medida en que `daily` resume el comportamiento agregado de sesiones que nacen de ese alcance de mercado.

## 4. Lectura correcta de la regla

La regla correcta no es:

- "todo dato fuera de regular market hours es ruido"

La regla correcta es:

- el modulo quiere observar y razonar sobre la sesion extendida completa;
- por tanto, `premarket` y `afterhours` forman parte del alcance institucional esperado;
- y cualquier bloque que no lo refleje o lo refleje de forma incompleta debe declararlo explicitamente.

## 5. Relacion con expected / present / healthy / usable

La sesion objetivo afecta a las cuatro capas de certificacion:

- `expected`
  - que parte de la sesion deberia existir para ese bloque

- `present`
  - que parte de la sesion esta materializada de hecho

- `healthy`
  - si lo presente es defendible en esa sesion

- `usable_for`
  - para que uso queda aprobado ese material, dada su cobertura y calidad de sesion

## 6. Regla para contratos de dataset

Todo contrato de dataset de market data debe declarar explicitamente:

- si su sesion objetivo es `04:00-20:00 America/New_York`;
- si la materializacion real cubre o no ese alcance;
- que limitaciones de sesion siguen abiertas;
- y como impactan esas limitaciones sobre `backtest_core`, `research`, `ml` o `forensic_only`.

## 7. Estado actual por bloque

### `quotes`

Debe leerse ya bajo esta sesion objetivo.
El bloque de `quotes` se usa para describir el estado observado del libro a lo largo de la sesion extendida.

### `ohlcv_1m`

Debe leerse tambien bajo esta sesion objetivo, salvo limitacion explicita que el contrato del bloque deba dejar anotada.

### `daily`

No es un dataset intradia, pero su lectura operativa queda condicionada por como se construye y resume la actividad observada a lo largo de la sesion.

### `trades`

Aqui existe una limitacion abierta importante.
La regla canonica de sesion sigue siendo `premarket -> regular -> afterhours`, pero la traduccion exacta de esa regla al bloque `trades` queda explicitamente abierta para una fase posterior.

Por tanto:

- `trades` no queda exento de la regla general;
- pero su cierre contractual de sesion aun no debe darse por resuelto.

## 8. Regla de excepcion

Si un bloque no puede alinearse todavia con esta sesion objetivo, debe declararse explicitamente:

- que parte de la sesion queda fuera;
- por que queda fuera;
- si eso es limitacion estructural, limitacion de proveedor o decision metodologica;
- y que impacto tiene sobre el uso permitido del bloque.

## 9. Principio final

La sesion extendida no es un adorno contextual del modulo.
Forma parte de la semantica operativa de la market data que TSIS quiere auditar, certificar y consumir.

Por tanto:

- `premarket`
- `regular`
- `afterhours`

deben tratarse como alcance institucional objetivo por defecto, salvo limitacion explicitamente declarada y gobernada.
